from __future__ import annotations

import cv2
import numpy as np


class EdgeProcessor:
    def clean(self, rgb: np.ndarray, alpha: np.ndarray, strength: float = 0.55, remove_halo: bool = True) -> np.ndarray:
        source = rgb.astype(np.float32)
        if not remove_halo or strength <= 0:
            return source.astype(np.uint8)
        edge = (alpha > 0.02) & (alpha < 0.98)
        if not np.any(edge):
            return source.astype(np.uint8)
        border_pixels = np.concatenate((source[0], source[-1], source[:, 0], source[:, -1]), axis=0)
        background = np.median(border_pixels, axis=0)
        a = np.maximum(alpha[..., None], 0.08)
        decontaminated = (source - background * (1 - a)) / a
        decontaminated = np.clip(decontaminated, 0, 255)
        distance = cv2.distanceTransform((alpha > 0.02).astype(np.uint8), cv2.DIST_L2, 3)
        weight = np.clip((3.0 - distance) / 3.0, 0, 1) * edge * strength
        result = source * (1 - weight[..., None]) + decontaminated * weight[..., None]
        return np.clip(result, 0, 255).astype(np.uint8)

