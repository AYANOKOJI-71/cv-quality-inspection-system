from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

from inspection.preprocess import prepare_image


def load_fixture_manifest(root: Path) -> dict[str, object]:
    manifest_path = root / "manifest.json"
    if not manifest_path.exists():
        return {
            "available": False,
            "message": "Run scripts/prepare_ksdd_fixture.py to prepare the non-commercial demo fixture.",
        }
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def load_reference_images(root: Path, manifest: dict[str, object]) -> list[np.ndarray]:
    references = manifest.get("reference_images", [])
    prepared: list[np.ndarray] = []
    for filename in references:
        image = cv2.imread(str(root / str(filename)))
        if image is not None:
            prepared.append(prepare_image(image))
    return prepared
