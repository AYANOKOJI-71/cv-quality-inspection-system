from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum


class Disposition(StrEnum):
    ACCEPT = "accept"
    REVIEW = "manual_review"
    REJECT = "reject"


@dataclass(frozen=True)
class DefectRegion:
    x: int
    y: int
    width: int
    height: int
    area_px: int
    score: float


@dataclass(frozen=True)
class InspectionResult:
    inspection_id: str
    filename: str
    disposition: Disposition
    anomaly_score: float
    confidence: float
    defect_regions: list[DefectRegion]
    source_url: str
    overlay_url: str
    decision_reason: str

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["disposition"] = self.disposition.value
        return payload


@dataclass(frozen=True)
class EvaluationMetrics:
    evaluated_images: int
    accepted_normal_images: int
    detected_defect_images: int
    normal_acceptance_rate: float
    defect_detection_rate: float
    note: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
