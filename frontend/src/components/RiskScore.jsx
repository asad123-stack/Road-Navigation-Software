export default function RiskScore({ score }) {
  const getColor = (s) => {
    if (s > 70) return "#ef4444";
    if (s > 40) return "#f59e0b";
    return "#10b981";
  };

  return (
    <div style={{ marginTop: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
        <p className="section-title" style={{ margin: 0 }}>Safety Assessment</p>
        <span style={{ fontSize: "12px", fontWeight: "600", color: getColor(score) }}>{score.toFixed(0)}% Risk</span>
      </div>
      <div style={{ height: "6px", background: "#f1f5f9", borderRadius: "10px", overflow: "hidden", border: "1px solid #e2e8f0" }}>
        <div
          style={{
            height: "100%",
            width: `${score}%`,
            background: getColor(score),
            transition: "width 0.5s ease"
          }}
        />
      </div>
    </div>
  );
}
