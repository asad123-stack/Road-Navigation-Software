export default function DetectedObjects({ detections }) {
  const top = detections.slice(0, 4);
  return (
    <div style={{ marginTop: 12 }}>
      <div className="section-title">Detected Objects</div>
      {top.length === 0 ? (
        <div style={{ opacity: 0.7 }}>None</div>
      ) : (
        top.map((d, i) => (
          <div key={i} className="detection-row">
            {d.label} ({Math.round((d.confidence ?? 0) * 100)}%)
          </div>
        ))
      )}
    </div>
  );
}
