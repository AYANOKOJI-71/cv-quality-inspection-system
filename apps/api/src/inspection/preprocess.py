from __future__ import annotations

import cv2
import numpy as np


def load_bgr(image_bytes: bytes) -> np.ndarray:
    array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("The uploaded file is not a readable image.")
    return image


def prepare_image(image_bgr: np.ndarray, size: tuple[int, int] = (256, 640)) -> np.ndarray:
    resized = cv2.resize(image_bgr, size, interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    normalized = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    return cv2.GaussianBlur(normalized, (3, 3), 0)


def make_overlay(source_bgr: np.ndarray, heatmap: np.ndarray, regions: list[tuple[int, int, int, int]]) -> np.ndarray:
    overlay = source_bgr.copy()
    heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    blend = cv2.addWeighted(overlay, 0.68, heatmap_color, 0.32, 0)
    for x, y, width, height in regions:
        cv2.rectangle(blend, (x, y), (x + width, y + height), (48, 238, 142), 2)
    return blend
