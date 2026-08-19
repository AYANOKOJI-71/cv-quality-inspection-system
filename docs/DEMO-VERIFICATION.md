# VisionLine Demo Verification

## Verified local state

The local FastAPI service and React operator console were exercised with the compact, ignored Kolektor Surface-Defect Dataset fixture prepared from the official non-commercial benchmark. The dashboard was reached through the same-origin Vite proxy using the temporary review hostname.

| Check | Verified result |
|---|---|
| Reference calibration | 4 of 4 defect-free fixture images were accepted |
| Defect detection | 2 of 2 fixture defect images were flagged |
| Fixture evaluation | 6 images evaluated; normal acceptance rate 1.000; defect detection rate 1.000 |
| Manual API upload | `defect_1.jpg` returned `reject`, an anomaly score of `2.307`, confidence of `0.964`, and 5 localized evidence regions |
| Visual output | The API generated a heatmap overlay with green evidence rectangles at `runtime/9d110b824e31_overlay.jpg` |

These measurements validate only this small, controlled demonstration fixture. They do not establish production performance, where threshold calibration and model validation must be performed on controlled site-specific data.
