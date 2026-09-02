from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
from PIL import Image


class BackgroundRemovalModel(ABC):
    @abstractmethod
    def load(self) -> None:
        """Load model weights once for reuse by a worker process."""

    @abstractmethod
    def predict(self, image: Image.Image) -> np.ndarray:
        """Return a continuous float32 alpha matte in the original resolution."""

    @abstractmethod
    def get_model_name(self) -> str:
        pass

    @abstractmethod
    def get_model_version(self) -> str:
        pass

