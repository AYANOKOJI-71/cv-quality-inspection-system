export type Disposition = "accept" | "manual_review" | "reject";

export interface Inspection {
  inspection_id: string;
  filename: string;
  disposition: Disposition;
  anomaly_score: number;
  confidence: number;
  defect_regions: Array<{ x: number; y: number; width: number; height: number; area_px: number; score: number }>;
  source_url: string;
  overlay_url: string;
  decision_reason: string;
}

export interface Dashboard {
  system: { name: string; inspection_line: string; model: string; deployment: string };
  fixture: { available: boolean; dataset?: string; license?: string; message?: string };
  evaluation: {
    evaluated_images: number;
    accepted_normal_images: number;
    detected_defect_images: number;
    normal_acceptance_rate: number;
    defect_detection_rate: number;
    note: string;
  } | null;
  recent_inspections: Inspection[];
}

async function response<T>(path: string, options?: RequestInit): Promise<T> {
  const result = await fetch(`/api${path}`, options);
  if (!result.ok) {
    const detail = await result.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(detail.detail ?? "Request failed");
  }
  return result.json() as Promise<T>;
}

export const getDashboard = () => response<Dashboard>("/v1/dashboard");

export async function inspectImage(file: File): Promise<Inspection> {
  const payload = new FormData();
  payload.append("image", file);
  return response<Inspection>("/v1/inspect", { method: "POST", body: payload });
}
