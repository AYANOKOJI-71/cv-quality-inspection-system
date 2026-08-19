# Local Operations

## Purpose and safety boundary

VisionLine is a **decision-support prototype**, not a safety-certified release-control system. Its three outcomes are `accept`, `manual_review`, and `reject`; production teams should retain a human quality-control approval step, archive calibration evidence, and establish a rollback procedure.

The API performs all inference locally. It has no outbound model calls and retains uploaded images only in the local `runtime/` directory or Docker named volume.

## Start a portfolio demonstration

1. Obtain KSDD directly from the official source and accept its non-commercial license.
2. Extract the archive outside the repository and run `make fixture SOURCE=/path/to/extracted/KolektorSDD`.
3. Run `make api` in one terminal and `make web` in another.
4. Open `http://127.0.0.1:5188`.

The console calibrates the PyTorch reference scorer against the selected defect-free images, shows fixture-only evaluation metrics, and renders OpenCV residual heatmaps with localized regions.

## Docker deployment

For a workstation with Docker Engine, use `docker compose up --build` and open the web console at port 5188. The fixture directory is mounted read-only; uploaded inspection evidence is written into the isolated `inspection-runtime` volume.

## Production checklist

| Control | Required action |
|---|---|
| Data rights | Replace KSDD with company-owned or properly licensed imagery. |
| Calibration | Create a representative normal-reference set for each product and camera configuration. |
| Evaluation | Measure false accepts, false rejects, latency, and localization quality on held-out site data. |
| Human review | Keep manual review for borderline scores and unrecognized product configurations. |
| Retention | Encrypt stored images as appropriate and define a retention/deletion schedule. |
