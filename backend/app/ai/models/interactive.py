from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
from PIL import Image


class InteractiveSegmentationModel(ABC):
    """Extension point for a future SAM2 keep/remove correction workflow."""

    @abstractmethod
    def refine(self, image: Image.Image, mask: np.ndarray, points: list[tuple[int, int, bool]]) -> np.ndarray:
        pass

