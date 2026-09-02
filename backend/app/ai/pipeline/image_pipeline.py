from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np
from PIL import Image, ImageOps

from app.ai.models.base import BackgroundRemovalModel
from app.ai.processing import EdgeProcessor, MaskRefiner
from app.ai.processing.mask import MaskRefinementOptions
from app.ai.quality import QualityAnalyzer


@dataclass(frozen=True)
class PipelineResult:
    mask_path: Path
    transparent_path: Path
    white_png_path: Path
    white_jpg_path: Path
    thumbnail_path: Path
    quality_score: float
    quality_flags: list[str]
    processing_time_ms: int
    width: int
    height: int


class ImageProcessingPipeline:
    def __init__(self, model: BackgroundRemovalModel) -> None:
        self.model = model
        self.refiner = MaskRefiner()
        self.edges = EdgeProcessor()
        self.quality = QualityAnalyzer()

    @staticmethod
    def load_image(path: Path) -> Image.Image:
        with Image.open(path) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
            image.load()
        return image

    @staticmethod
    def composite_white(rgb: np.ndarray, alpha: np.ndarray) -> np.ndarray:
        a = np.clip(alpha[..., None], 0, 1).astype(np.float32)
        return np.clip(rgb.astype(np.float32) * a + 255.0 * (1.0 - a), 0, 255).astype(np.uint8)

    def process(self, original_path: Path, output_root: Path, stem: str, settings: dict[str, Any]) -> PipelineResult:
        started = perf_counter()
        image = self.load_image(original_path)
        rgb = np.asarray(image, dtype=np.uint8)
        alpha = self.model.predict(image)
        if alpha.shape != (image.height, image.width):
            raise RuntimeError(f"Model returned mask shape {alpha.shape}, expected {(image.height, image.width)}")

        options = MaskRefinementOptions(
            remove_small_islands=bool(settings.get("remove_small_islands", True)),
            fill_holes=bool(settings.get("fill_holes", True)),
            smoothness=float(settings.get("mask_smoothness", 0.35)),
            feather=float(settings.get("feather", 0.8)),
            erosion=int(settings.get("erosion", 0)),
            dilation=int(settings.get("dilation", 0)),
            min_component_area=int(settings.get("min_component_area", 24)),
            max_hole_area=int(settings.get("max_hole_area", 64)),
        )
        refined = self.refiner.refine(alpha, options)
        cleaned_rgb = self.edges.clean(
            rgb,
            refined,
            strength=float(settings.get("edge_cleanup", 0.55)),
            remove_halo=bool(settings.get("remove_halo", True)),
        )
        quality = self.quality.analyze(cleaned_rgb, refined)

        paths = {
            "mask": output_root / "masks" / f"{stem}.png",
            "transparent": output_root / "transparent" / f"{stem}.png",
            "white_png": output_root / "white_png" / f"{stem}.png",
            "white_jpg": output_root / "white_jpg" / f"{stem}.jpg",
            "thumbnail": output_root / "thumbnails" / f"{stem}.jpg",
        }
        for path in paths.values():
            path.parent.mkdir(parents=True, exist_ok=True)
        alpha_u8 = np.rint(refined * 255).astype(np.uint8)
        Image.fromarray(alpha_u8, mode="L").save(paths["mask"], optimize=True)
        rgba = np.dstack((cleaned_rgb, alpha_u8))
        transparent = Image.fromarray(rgba, mode="RGBA")
        transparent.save(paths["transparent"], optimize=True)
        white = Image.fromarray(self.composite_white(cleaned_rgb, refined), mode="RGB")
        white.save(paths["white_png"], optimize=True)
        white.save(paths["white_jpg"], quality=94, subsampling=0, optimize=True)
        thumbnail = white.copy()
        thumbnail.thumbnail((520, 520), Image.Resampling.LANCZOS)
        thumbnail.save(paths["thumbnail"], quality=88, optimize=True)
        duration = int((perf_counter() - started) * 1000)
        return PipelineResult(
            mask_path=paths["mask"],
            transparent_path=paths["transparent"],
            white_png_path=paths["white_png"],
            white_jpg_path=paths["white_jpg"],
            thumbnail_path=paths["thumbnail"],
            quality_score=quality.score,
            quality_flags=quality.flags,
            processing_time_ms=duration,
            width=image.width,
            height=image.height,
        )

