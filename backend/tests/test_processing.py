from __future__ import annotations

import numpy as np

from app.ai.pipeline.image_pipeline import ImageProcessingPipeline
from app.ai.processing.mask import MaskRefinementOptions, MaskRefiner
from app.ai.quality import QualityAnalyzer


def test_alpha_compositing_preserves_continuous_alpha():
    foreground = np.array([[[0, 0, 0], [200, 100, 0]]], dtype=np.uint8)
    alpha = np.array([[0.5, 0.25]], dtype=np.float32)
    result = ImageProcessingPipeline.composite_white(foreground, alpha)
    assert result[0, 0].tolist() == [127, 127, 127]
    assert result[0, 1].tolist() == [241, 216, 191]


def test_mask_refinement_removes_only_small_island_and_keeps_soft_edge():
    alpha = np.zeros((40, 40), dtype=np.float32)
    alpha[8:34, 8:34] = 1
    alpha[7, 10:30] = 0.45
    alpha[2, 2] = 1
    result = MaskRefiner().refine(alpha, MaskRefinementOptions(min_component_area=10, feather=0, smoothness=0))
    assert result[2, 2] == 0
    assert np.isclose(result[7, 15], 0.45)
    assert result[20, 20] == 1


def test_quality_analyzer_is_deterministic_and_flags_empty_foreground():
    rgb = np.full((64, 64, 3), 255, dtype=np.uint8)
    alpha = np.zeros((64, 64), dtype=np.float32)
    first = QualityAnalyzer().analyze(rgb, alpha)
    second = QualityAnalyzer().analyze(rgb, alpha)
    assert first == second
    assert first.score < 85
    assert "FOREGROUND_TOO_SMALL" in first.flags

