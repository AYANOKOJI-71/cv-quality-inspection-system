# VisionLine Quality Inspection

**VisionLine** is a local-first computer-vision quality-inspection system built to demonstrate an industrial image workflow end to end: OpenCV image conditioning, PyTorch feature scoring, localized residual overlays, confidence-aware decisions, FastAPI inference, and a React operator console.

![Architecture](https://img.shields.io/badge/architecture-local--first-2c493b) ![Inference](https://img.shields.io/badge/inference-PyTorch%20%2B%20OpenCV-7abf7a) ![API](https://img.shields.io/badge/API-FastAPI-009688)

## What it demonstrates

| Capability | Implementation |
|---|---|
| Image preparation | OpenCV resize, grayscale normalization, CLAHE contrast equalization, and denoising |
| Model path | CPU-friendly PyTorch reference-feature scorer calibrated from defect-free surface images |
| Defect localization | Pixel residual heatmaps, morphological cleanup, bounded defect regions, and operator overlays |
| Decision support | `accept`, `manual_review`, and `reject` dispositions with calibrated thresholds and confidence |
| Service deployment | FastAPI upload API with type, size, and fixture-readiness guardrails |
| Operator experience | React/Vite console for visual evidence review and image upload |
| Engineering | Pytest, Ruff, Vitest, Docker Compose, and GitHub Actions |

## Demonstration dataset

The optional fixture uses the [Kolektor Surface-Defect Dataset (KSDD)](https://www.vicos.si/resources/kolektorsdd/). It has 399 real controlled-production images, 52 with visible defects, and fine annotations. KSDD is licensed under **CC BY-NC-SA 4.0**, so this repository does not bundle its imagery and the fixture selector is strictly for non-commercial portfolio demonstration.

Read [dataset license guidance](docs/DATASET_LICENSE.md) before downloading or demonstrating KSDD. Production use must replace it with company-owned or appropriately licensed imagery.

## Quick start

```bash
# First install the CPU PyTorch wheel, then project dependencies.
make install

# After obtaining and extracting KSDD yourself:
make fixture SOURCE=/path/to/KolektorSDD

# In separate terminals:
make api
make web
```

Open `http://127.0.0.1:5188`. Alternatively, use `docker compose up --build` on a Docker-enabled workstation.

## API

| Endpoint | Purpose |
|---|---|
| `GET /health` | Returns local service state and fixture readiness. |
| `GET /v1/dashboard` | Returns model description, fixture-only evaluation, and recent demo evidence. |
| `POST /v1/inspect` | Uploads one JPEG, PNG, or BMP up to 12 MB and returns the overlay evidence. |

