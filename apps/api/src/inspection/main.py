from __future__ import annotations

import os
import uuid
from pathlib import Path

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from inspection.contracts import EvaluationMetrics, InspectionResult
from inspection.fixtures import load_fixture_manifest, load_reference_images
from inspection.model import ReferenceProfile, TorchReferenceScorer
from inspection.preprocess import load_bgr, make_overlay, prepare_image

PROJECT_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_DIR = Path(os.getenv("INSPECTION_FIXTURE_DIR", PROJECT_ROOT / "data/fixtures"))
RUNTIME_DIR = PROJECT_ROOT / "runtime"
RUNTIME_DIR.mkdir(exist_ok=True)

app = FastAPI(title="VisionLine Quality Inspection", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5188", "http://localhost:5188"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/media/runtime", StaticFiles(directory=str(RUNTIME_DIR)), name="runtime")
app.mount("/media/fixtures", StaticFiles(directory=str(FIXTURE_DIR), check_dir=False), name="fixtures")

scorer = TorchReferenceScorer()
INSPECTION_FILE = File(...)


def profile_for_fixture() -> ReferenceProfile | None:
    manifest = load_fixture_manifest(FIXTURE_DIR)
    if not manifest.get("available"):
        return None
    references = load_reference_images(FIXTURE_DIR, manifest)
    return scorer.fit(references) if len(references) >= 2 else None


def inspect_bgr(image_bgr: np.ndarray, filename: str, source_url: str, profile: ReferenceProfile) -> InspectionResult:
    prepared = prepare_image(image_bgr)
    scored = scorer.score(prepared, profile)
    overlay = make_overlay(
        cv2.resize(image_bgr, (256, 640), interpolation=cv2.INTER_AREA),
        scored.heatmap,
        [(region.x, region.y, region.width, region.height) for region in scored.regions],
    )
    inspection_id = uuid.uuid4().hex[:12]
    overlay_name = f"{inspection_id}_overlay.jpg"
    cv2.imwrite(str(RUNTIME_DIR / overlay_name), overlay)
    return InspectionResult(
        inspection_id=inspection_id,
        filename=filename,
        disposition=scored.disposition,
        anomaly_score=scored.anomaly_score,
        confidence=scored.confidence,
        defect_regions=scored.regions,
        source_url=source_url,
        overlay_url=f"/media/runtime/{overlay_name}",
        decision_reason=scored.decision_reason,
    )


def fixture_results() -> list[dict[str, object]]:
    manifest = load_fixture_manifest(FIXTURE_DIR)
    profile = profile_for_fixture()
    if profile is None:
        return []
    items: list[dict[str, object]] = []
    for filename in manifest.get("demo_images", []):
        path = FIXTURE_DIR / str(filename)
        image = cv2.imread(str(path))
        if image is None:
            continue
        source_url = f"/media/fixtures/{path.name}"
        result = inspect_bgr(image, path.name, source_url, profile).to_dict()
        items.append(result)
    return items


@app.get("/health")
def health() -> dict[str, object]:
    manifest = load_fixture_manifest(FIXTURE_DIR)
    return {"status": "ok", "fixture_ready": bool(manifest.get("available")), "mode": "local-first"}


@app.get("/v1/dashboard")
def dashboard() -> dict[str, object]:
    manifest = load_fixture_manifest(FIXTURE_DIR)
    demo_results = fixture_results()
    return {
        "system": {
            "name": "VisionLine Quality Inspection",
            "inspection_line": "Electrical commutator surface",
            "model": "PyTorch reference feature scorer + OpenCV residual localization",
            "deployment": "Local FastAPI inference service",
        },
        "fixture": manifest,
        "evaluation": evaluate_fixture(manifest).to_dict() if manifest.get("available") else None,
        "recent_inspections": demo_results,
    }


@app.post("/v1/inspect")
async def inspect_upload(image: UploadFile = INSPECTION_FILE) -> dict[str, object]:
    if image.content_type not in {"image/jpeg", "image/png", "image/bmp"}:
        raise HTTPException(status_code=415, detail="Upload a JPEG, PNG, or BMP inspection image.")
    profile = profile_for_fixture()
    if profile is None:
        raise HTTPException(
            status_code=503,
            detail="No licensed reference fixture is ready. Prepare a local reference set first.",
        )
    payload = await image.read()
    if len(payload) > 12_000_000:
        raise HTTPException(status_code=413, detail="Image exceeds the 12 MB local-inspection limit.")
    image_bgr = load_bgr(payload)
    inspection_id = uuid.uuid4().hex[:12]
    source_name = f"{inspection_id}_source.jpg"
    cv2.imwrite(str(RUNTIME_DIR / source_name), image_bgr)
    result = inspect_bgr(image_bgr, image.filename or source_name, f"/media/runtime/{source_name}", profile)
    return result.to_dict()


def evaluate_fixture(manifest: dict[str, object]) -> EvaluationMetrics:
    profile = profile_for_fixture()
    if profile is None:
        raise ValueError("Fixture is not ready.")
    normal_results = []
    for filename in manifest.get("reference_images", []):
        image = cv2.imread(str(FIXTURE_DIR / str(filename)))
        if image is not None:
            normal_results.append(scorer.score(prepare_image(image), profile))
    defect_results = []
    for filename in manifest.get("demo_images", []):
        image = cv2.imread(str(FIXTURE_DIR / str(filename)))
        if image is not None:
            defect_results.append(scorer.score(prepare_image(image), profile))
    accepted = sum(result.disposition.value == "accept" for result in normal_results)
    detected = sum(result.disposition.value != "accept" for result in defect_results)
    return EvaluationMetrics(
        evaluated_images=len(normal_results) + len(defect_results),
        accepted_normal_images=accepted,
        detected_defect_images=detected,
        normal_acceptance_rate=round(accepted / max(1, len(normal_results)), 3),
        defect_detection_rate=round(detected / max(1, len(defect_results)), 3),
        note="Fixture-only evaluation; production performance must be validated on controlled site data.",
    )
