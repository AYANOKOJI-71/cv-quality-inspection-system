from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
import torch

from inspection.contracts import DefectRegion, Disposition


@dataclass(frozen=True)
class ReferenceProfile:
    mean_image: np.ndarray
    feature_center: torch.Tensor
    feature_scale: torch.Tensor
    review_threshold: float
    reject_threshold: float


@dataclass(frozen=True)
class ScoredInspection:
    disposition: Disposition
    anomaly_score: float
    confidence: float
    regions: list[DefectRegion]
    heatmap: np.ndarray
    decision_reason: str


class TorchReferenceScorer:
    """CPU-friendly reference scorer using PyTorch feature tensors and OpenCV localization."""

    def fit(self, normal_images: list[np.ndarray]) -> ReferenceProfile:
        if len(normal_images) < 2:
            raise ValueError("At least two defect-free reference images are required.")
        stack = np.stack([image.astype(np.float32) for image in normal_images])
        mean_image = np.mean(stack, axis=0)
        feature_matrix = torch.stack([self._features(image) for image in normal_images])
        center = feature_matrix.mean(dim=0)
        scale = feature_matrix.std(dim=0).clamp_min(0.01)
        distances = torch.linalg.vector_norm((feature_matrix - center) / scale, dim=1)
        reference_scores = [
            0.55 * distance.item() + 0.45 * self._residual_score(image, mean_image)
            for image, distance in zip(normal_images, distances, strict=True)
        ]
        baseline = max(reference_scores)
        return ReferenceProfile(
            mean_image=mean_image,
            feature_center=center,
            feature_scale=scale,
            review_threshold=max(1.35, baseline + 0.25),
            reject_threshold=max(1.85, baseline + 0.65),
        )

    def score(self, image: np.ndarray, profile: ReferenceProfile) -> ScoredInspection:
        normalized_delta = (self._features(image) - profile.feature_center) / profile.feature_scale
        feature_distance = torch.linalg.vector_norm(normalized_delta)
        residual = cv2.absdiff(image.astype(np.uint8), profile.mean_image.astype(np.uint8))
        heatmap = cv2.GaussianBlur(residual, (0, 0), 5)
        residual_score = self._residual_score(image, profile.mean_image)
        anomaly_score = round(float(0.55 * feature_distance.item() + 0.45 * residual_score), 3)
        regions = self._regions(heatmap) if anomaly_score >= profile.review_threshold else []
        confidence = round(min(0.99, 0.52 + anomaly_score / 5.2), 3)
        if anomaly_score >= profile.reject_threshold or any(region.area_px >= 450 for region in regions):
            return ScoredInspection(
                Disposition.REJECT,
                anomaly_score,
                confidence,
                regions,
                heatmap,
                "Anomaly score or localized surface residual exceeded the calibrated reject threshold.",
            )
        if anomaly_score >= profile.review_threshold or regions:
            return ScoredInspection(
                Disposition.REVIEW,
                anomaly_score,
                confidence,
                regions,
                heatmap,
                "A localized variance requires operator review before the part can be released.",
            )
        return ScoredInspection(
            Disposition.ACCEPT,
            anomaly_score,
            confidence,
            regions,
            heatmap,
            "Surface pattern remains within the calibrated defect-free reference band.",
        )

    @staticmethod
    def _features(image: np.ndarray) -> torch.Tensor:
        tensor = torch.tensor(image, dtype=torch.float32).unsqueeze(0).unsqueeze(0) / 255.0
        sobel_x = torch.tensor([[[[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]]]])
        sobel_y = torch.tensor([[[[-1.0, -2.0, -1.0], [0.0, 0.0, 0.0], [1.0, 2.0, 1.0]]]])
        edge_x = torch.nn.functional.conv2d(tensor, sobel_x, padding=1)
        edge_y = torch.nn.functional.conv2d(tensor, sobel_y, padding=1)
        magnitude = torch.sqrt(edge_x.square() + edge_y.square())
        return torch.stack([tensor.mean(), tensor.std(), magnitude.mean(), magnitude.std()])

    @staticmethod
    def _residual_score(image: np.ndarray, mean_image: np.ndarray) -> float:
        residual = cv2.absdiff(image.astype(np.uint8), mean_image.astype(np.uint8))
        heatmap = cv2.GaussianBlur(residual, (0, 0), 5)
        return float(np.percentile(heatmap, 99) / 48.0)

    @staticmethod
    def _regions(heatmap: np.ndarray) -> list[DefectRegion]:
        threshold = max(20, int(np.percentile(heatmap, 97.5) * 0.72))
        binary = cv2.threshold(heatmap, threshold, 255, cv2.THRESH_BINARY)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        regions: list[DefectRegion] = []
        for contour in cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]:
            x, y, width, height = cv2.boundingRect(contour)
            area = int(cv2.contourArea(contour))
            if area < 80:
                continue
            region_heat = heatmap[y : y + height, x : x + width]
            regions.append(DefectRegion(x, y, width, height, area, round(float(region_heat.mean() / 255), 3)))
        return regions[:5]
