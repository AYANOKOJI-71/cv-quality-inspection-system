import { describe, expect, it } from "vitest";
import type { Inspection } from "./api";

describe("inspection API contract", () => {
  it("keeps the evidence fields required by the visual-review card", () => {
    const result: Inspection = {
      inspection_id: "demo-1", filename: "part.jpg", disposition: "manual_review", anomaly_score: 1.8, confidence: 0.79,
      defect_regions: [{ x: 1, y: 2, width: 3, height: 4, area_px: 12, score: 0.9 }], source_url: "/media/source.jpg", overlay_url: "/media/overlay.jpg", decision_reason: "Review",
    };
    expect(result.defect_regions[0].area_px).toBe(12);
    expect(result.overlay_url).toContain("/media/");
  });
});
