from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class QualityResult:
    score: float
    flags: list[str]


class QualityAnalyzer:
    """Conservative heuristics used to route uncertain results to a human."""

    def analyze(self, rgb: np.ndarray, alpha: np.ndarray) -> QualityResult:
        flags: list[str] = []
        penalties = 0.0
        foreground = alpha > 0.08
        coverage = float(foreground.mean())
        if coverage < 0.008:
            flags.append("FOREGROUND_TOO_SMALL")
            penalties += 55
        elif coverage > 0.97:
            flags.append("BACKGROUND_NOT_REMOVED")
            penalties += 55

        touches = float(np.concatenate((alpha[0], alpha[-1], alpha[:, 0], alpha[:, -1])).mean())
        if touches > 0.16:
            flags.append("FOREGROUND_TOUCHES_BORDER")
            penalties += min(18, touches * 24)

        uncertain_ratio = float(((alpha > 0.05) & (alpha < 0.95)).mean())
        if uncertain_ratio > 0.28:
            flags.append("EXCESSIVE_SOFT_ALPHA")
            penalties += min(18, uncertain_ratio * 30)

        binary = (alpha > 0.12).astype(np.uint8)
        count, _, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
        islands = [stats[i, cv2.CC_STAT_AREA] for i in range(1, count) if stats[i, cv2.CC_STAT_AREA] < 40]
        if len(islands) >= 8:
            flags.append("POSSIBLE_BACKGROUND_RESIDUE")
            penalties += min(16, len(islands) * 0.8)

        edge_band = (alpha > 0.08) & (alpha < 0.92)
        if edge_band.any():
            edge_colors = rgb[edge_band].astype(np.float32)
            near_white = np.mean(np.min(edge_colors, axis=1) > 238)
            near_black = np.mean(np.max(edge_colors, axis=1) < 18)
            if near_white > 0.22:
                flags.append("POSSIBLE_WHITE_HALO")
                penalties += 10
            if near_black > 0.22:
                flags.append("POSSIBLE_BLACK_HALO")
                penalties += 10

        score = round(max(0.0, min(100.0, 100.0 - penalties)), 1)
        return QualityResult(score=score, flags=flags)

