from __future__ import annotations

import cv2
import numpy as np
from inspection.contracts import Disposition
from inspection.model import TorchReferenceScorer


def reference_images() -> list[np.ndarray]:
    base = np.full((640, 256), 116, dtype=np.uint8)
    return [cv2.GaussianBlur(base + offset, (3, 3), 0) for offset in (0, 1, 2, 3)]


def test_reference_scorer_accepts_reference_like_surface() -> None:
    scorer = TorchReferenceScorer()
    profile = scorer.fit(reference_images())

    result = scorer.score(np.full((640, 256), 117, dtype=np.uint8), profile)

    assert result.disposition is Disposition.ACCEPT
    assert result.anomaly_score < profile.review_threshold


def test_reference_scorer_localizes_prominent_surface_deviation() -> None:
    scorer = TorchReferenceScorer()
    profile = scorer.fit(reference_images())
    candidate = np.full((640, 256), 116, dtype=np.uint8)
    cv2.rectangle(candidate, (80, 250), (160, 330), 245, thickness=-1)

    result = scorer.score(candidate, profile)

    assert result.disposition in {Disposition.REVIEW, Disposition.REJECT}
    assert result.anomaly_score >= profile.review_threshold
    assert result.regions


def test_reference_scorer_requires_multiple_reference_images() -> None:
    scorer = TorchReferenceScorer()
    try:
        scorer.fit([np.zeros((640, 256), dtype=np.uint8)])
    except ValueError as error:
        assert "At least two" in str(error)
    else:
        raise AssertionError("Expected insufficient reference images to be rejected.")
