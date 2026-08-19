"""Select a compact non-commercial KSDD fixture from an official local archive.

The KSDD archive is CC BY-NC-SA 4.0. This script is intentionally opt-in and does
not download or commit benchmark imagery. It copies a few normal and defective
source/mask pairs into a local ignored fixture folder for portfolio demonstration.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import cv2


def choose_files(source_root: Path) -> tuple[list[Path], list[Path]]:
    images = sorted(path for path in source_root.rglob("*.jpg") if "_label" not in path.name)
    labels = sorted(source_root.rglob("*_label.bmp"))
    if len(images) < 8 or len(labels) < 2:
        raise ValueError("KSDD archive layout was not recognized; expected JPG images and *_label.bmp masks.")
    normal: list[Path] = []
    defective: list[Path] = []
    for image in images:
        label = image.with_name(f"{image.stem}_label.bmp")
        mask = cv2.imread(str(label), cv2.IMREAD_GRAYSCALE)
        if mask is not None and cv2.countNonZero(mask) > 0:
            defective.append(image)
        else:
            normal.append(image)
    if len(normal) < 4 or len(defective) < 2:
        raise ValueError("The source archive does not contain enough normal and defective examples.")
    return normal[:4], defective[:2]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True, help="Extracted official KSDD archive root")
    parser.add_argument("--output", type=Path, default=Path("data/fixtures"))
    args = parser.parse_args()
    normal, defective = choose_files(args.source)
    args.output.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    reference_images: list[str] = []
    demo_images: list[str] = []
    for prefix, sources, destination in [
        ("reference", normal, reference_images),
        ("defect", defective, demo_images),
    ]:
        for index, source in enumerate(sources, start=1):
            target = args.output / f"{prefix}_{index}.jpg"
            shutil.copy2(source, target)
            copied.append(target.name)
            destination.append(target.name)
            label = source.with_name(f"{source.stem}_label.bmp")
            if label.exists():
                shutil.copy2(label, args.output / f"{target.stem}_mask.bmp")
    manifest = {
        "available": True,
        "dataset": "Kolektor Surface-Defect Dataset (KSDD)",
        "license": "CC BY-NC-SA 4.0; portfolio demo only; do not use the fixture commercially.",
        "reference_images": reference_images,
        "demo_images": demo_images,
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
