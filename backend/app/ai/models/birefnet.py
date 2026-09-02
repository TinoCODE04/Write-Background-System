from __future__ import annotations

import logging
from typing import Any

import numpy as np
from PIL import Image

from app.ai.models.base import BackgroundRemovalModel
from app.core.config import get_settings


logger = logging.getLogger(__name__)


class BiRefNetModel(BackgroundRemovalModel):
    def __init__(self, model_name: str | None = None, device: str | None = None, input_size: int | None = None) -> None:
        settings = get_settings()
        self.model_name = model_name or settings.model_name
        self.requested_device = device or settings.device
        self.input_size = input_size or settings.model_input_size
        self.device = "cpu"
        self.model: Any = None
        self.torch: Any = None
        self.version = "huggingface"

    def load(self) -> None:
        if self.model is not None:
            return
        try:
            import torch
            from transformers import AutoModelForImageSegmentation
        except ImportError as exc:
            raise RuntimeError(
                "BiRefNet dependencies are missing. Install backend/requirements.txt with Python 3.11 or 3.12."
            ) from exc

        if self.requested_device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA is unavailable. Running inference on CPU; processing will be slower.")
        use_cuda = self.requested_device != "cpu" and torch.cuda.is_available()
        self.device = "cuda" if use_cuda else "cpu"
        if self.device == "cpu":
            logger.warning("CUDA is unavailable. Running inference on CPU; processing will be slower.")
        logger.info("Loading background removal model", extra={"model": self.model_name, "device": self.device})
        model = AutoModelForImageSegmentation.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            use_safetensors=True,
        )
        self.model = model.to(self.device).eval()
        self.torch = torch
        commit = getattr(getattr(model, "config", None), "_commit_hash", None)
        self.version = commit[:12] if isinstance(commit, str) else "huggingface"

    def _extract_tensor(self, output: Any) -> Any:
        if isinstance(output, dict):
            for key in ("logits", "pred", "out"):
                if key in output:
                    return self._extract_tensor(output[key])
            return self._extract_tensor(next(iter(output.values())))
        if isinstance(output, (list, tuple)):
            return self._extract_tensor(output[-1])
        return output

    def predict(self, image: Image.Image) -> np.ndarray:
        self.load()
        torch = self.torch
        rgb = image.convert("RGB")
        original_width, original_height = rgb.size
        resized = rgb.resize((self.input_size, self.input_size), Image.Resampling.LANCZOS)
        array = np.asarray(resized, dtype=np.float32) / 255.0
        array = (array - np.array([0.485, 0.456, 0.406], dtype=np.float32)) / np.array(
            [0.229, 0.224, 0.225], dtype=np.float32
        )
        tensor = torch.from_numpy(array.transpose(2, 0, 1)).unsqueeze(0).to(self.device)
        with torch.inference_mode():
            if self.device == "cuda":
                with torch.autocast(device_type="cuda", dtype=torch.float16):
                    output = self.model(tensor)
            else:
                output = self.model(tensor)
            logits = self._extract_tensor(output)
            if logits.ndim == 3:
                logits = logits.unsqueeze(1)
            matte = torch.nn.functional.interpolate(
                logits.float(), size=(original_height, original_width), mode="bicubic", align_corners=False
            ).sigmoid()[0, 0]
            result = matte.clamp(0, 1).cpu().numpy().astype(np.float32)
        del tensor, output, logits, matte
        return result

    def get_model_name(self) -> str:
        return self.model_name

    def get_model_version(self) -> str:
        return self.version

