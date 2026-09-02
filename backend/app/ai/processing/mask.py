from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class MaskRefinementOptions:
    remove_small_islands: bool = True
    fill_holes: bool = True
    smoothness: float = 0.35
    feather: float = 0.8
    erosion: int = 0
    dilation: int = 0
    min_component_area: int = 24
    max_hole_area: int = 64


class MaskRefiner:
    def refine(self, alpha: np.ndarray, options: MaskRefinementOptions) -> np.ndarray:
        matte = np.clip(alpha.astype(np.float32), 0, 1)
        support = (matte >= 0.04).astype(np.uint8)
        core = (matte >= 0.9).astype(np.uint8)

        if options.remove_small_islands and options.min_component_area > 0:
            count, labels, stats, _ = cv2.connectedComponentsWithStats(support, connectivity=8)
            keep = np.zeros_like(support)
            for label in range(1, count):
                if stats[label, cv2.CC_STAT_AREA] >= options.min_component_area:
                    keep[labels == label] = 1
            matte *= keep

        if options.fill_holes and options.max_hole_area > 0:
            background = (support == 0).astype(np.uint8)
            count, labels, stats, _ = cv2.connectedComponentsWithStats(background, connectivity=8)
            for label in range(1, count):
                component = labels == label
                touches_border = bool(
                    component[0].any() or component[-1].any() or component[:, 0].any() or component[:, -1].any()
                )
                if not touches_border and stats[label, cv2.CC_STAT_AREA] <= options.max_hole_area:
                    matte[component] = 1.0

        if options.erosion:
            kernel = np.ones((3, 3), np.uint8)
            matte = cv2.erode(matte, kernel, iterations=options.erosion)
        if options.dilation:
            kernel = np.ones((3, 3), np.uint8)
            matte = cv2.dilate(matte, kernel, iterations=options.dilation)
        if options.smoothness > 0:
            sigma = 0.35 + options.smoothness * 1.8
            smoothed = cv2.GaussianBlur(matte, (0, 0), sigmaX=sigma)
            # Preserve confident regions while smoothing only the uncertain matte.
            uncertain = (matte > 0.02) & (matte < 0.98)
            matte[uncertain] = smoothed[uncertain]
        if options.feather > 0:
            softened = cv2.GaussianBlur(matte, (0, 0), sigmaX=max(0.1, options.feather))
            edge = (matte > 0.01) & (matte < 0.99)
            matte[edge] = softened[edge]
        return np.clip(matte, 0, 1).astype(np.float32)
