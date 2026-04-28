export default function LSTMRiskBar({ score, alert }) {
  const value = score ?? 0;
  const color = alert ? "#ef4444" : "#10b981";
  
  return (
    <div style={{ marginTop: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
        <p className="section-title" style={{ margin: 0 }}>Risk Prediction (3s)</p>
        <span style={{ fontSize: "11px", fontWeight: "600", color: "#64748b" }}>
          {score === null ? "Analyzing..." : `${value.toFixed(0)}% Probability`}
        </span>
      </div>
      <div style={{ height: "6px", background: "#f1f5f9", borderRadius: "10px", overflow: "hidden", border: "1px solid #e2e8f0" }}>
        <div
          style={{
            height: "100%",
            width: `${value}%`,
            background: color,
            transition: "width 0.8s ease"
          }}
        />
      </div>
      {alert && (
        <div style={{ color: "#ef4444", fontSize: "11px", fontWeight: "600", marginTop: "8px" }}>
          Critical Obstacle Prediction
        </div>
      )}
    </div>
  );
}
