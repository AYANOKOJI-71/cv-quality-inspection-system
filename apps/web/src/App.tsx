import { ChangeEvent, useEffect, useMemo, useState } from "react";
import { Dashboard, Inspection, getDashboard, inspectImage } from "./api";

function formatDisposition(value: Inspection["disposition"]) {
  return value === "accept" ? "Accept" : value === "manual_review" ? "Review" : "Reject";
}

function InspectionCard({ item }: { item: Inspection }) {
  return (
    <article className="inspection-card">
      <div className="inspection-image-wrap">
        <img src={item.overlay_url} alt={`Defect overlay for ${item.filename}`} />
        <span className={`status status-${item.disposition}`}>{formatDisposition(item.disposition)}</span>
      </div>
      <div className="card-body">
        <div className="file-row"><strong>{item.filename}</strong><span>{Math.round(item.confidence * 100)}% confidence</span></div>
        <div className="score-track"><span style={{ width: `${Math.min(100, item.anomaly_score * 35)}%` }} /></div>
        <p>{item.decision_reason}</p>
        <div className="region-note">{item.defect_regions.length} localized region{item.defect_regions.length === 1 ? "" : "s"} · anomaly score {item.anomaly_score.toFixed(2)}</div>
      </div>
    </article>
  );
}

export default function App() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [latest, setLatest] = useState<Inspection | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    getDashboard()
      .then(setDashboard)
      .catch((reason: Error) => setError(reason.message))
      .finally(() => setLoading(false));
  }, []);

  const inspections = useMemo(() => (latest ? [latest, ...(dashboard?.recent_inspections ?? [])] : dashboard?.recent_inspections ?? []), [dashboard, latest]);

  async function onUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      setLatest(await inspectImage(file));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Inspection could not be completed.");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  if (loading) return <main className="loading">Calibrating inspection console…</main>;
  const evaluation = dashboard?.evaluation;

  return (
    <main>
      <header className="topbar">
        <div className="brand"><span className="brand-mark">◉</span><span>VISIONLINE</span><small>QUALITY INSPECTION</small></div>
        <div className="line-status"><i /> Inference line online <span>·</span> CPU reference model</div>
      </header>
      <section className="hero">
        <div><p className="eyebrow">OPERATOR CONSOLE / LOCAL DEMO</p><h1>See the deviation.<br /><em>Decide with evidence.</em></h1><p className="hero-copy">A confidence-aware visual inspection workflow for controlled industrial surfaces. Every decision carries the localized evidence an operator needs to review.</p></div>
        <label className={`upload-tile ${uploading ? "busy" : ""}`}>
          <input type="file" accept="image/jpeg,image/png,image/bmp" onChange={onUpload} disabled={uploading || !dashboard?.fixture.available} />
          <span className="upload-icon">↗</span><strong>{uploading ? "Inspecting surface…" : "Inspect an image"}</strong><small>JPEG, PNG, or BMP · max 12 MB</small>
        </label>
      </section>
      {error && <div className="alert">{error}</div>}
      {!dashboard?.fixture.available && <div className="alert">{dashboard?.fixture.message} The public demo fixture is intentionally optional and never committed.</div>}
      <section className="metric-grid">
        <div className="metric"><span>Fixture images evaluated</span><strong>{evaluation?.evaluated_images ?? "—"}</strong><small>held-out demonstration subset</small></div>
        <div className="metric"><span>Normal acceptance</span><strong>{evaluation ? `${Math.round(evaluation.normal_acceptance_rate * 100)}%` : "—"}</strong><small>reference-surface band</small></div>
        <div className="metric"><span>Defect detection</span><strong>{evaluation ? `${Math.round(evaluation.defect_detection_rate * 100)}%` : "—"}</strong><small>fixture-only measurement</small></div>
        <div className="metric model"><span>Decision policy</span><strong>3-tier</strong><small>accept · review · reject</small></div>
      </section>
      <section className="inspection-section">
        <div className="section-heading"><div><p className="eyebrow">RECENT INSPECTIONS</p><h2>Evidence queue</h2></div><p>{dashboard?.system.model}</p></div>
        <div className="inspection-grid">{inspections.length ? inspections.map((item) => <InspectionCard key={item.inspection_id} item={item} />) : <div className="empty-state">Prepare the licensed fixture to populate the evidence queue.</div>}</div>
      </section>
      <footer><span>DATASET: {dashboard?.fixture.dataset ?? "Awaiting local fixture"}</span><span>LOCAL-FIRST · NO EXTERNAL INFERENCE</span><span>{dashboard?.fixture.license ?? "Use company-owned data in production."}</span></footer>
    </main>
  );
}
