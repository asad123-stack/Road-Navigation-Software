export default function LSTMRiskBar({ score, alert }) {
  const value = score ?? 0;
  const color = alert ? "#ef4444" : "#22c55e";
  return (
    <div style={{ marginTop: 10 }}>
      <div>Risk in 3s: {score === null ? "warming up" : value}</div>
      <div style={{ height: 10, background: "#1f2937", borderRadius: 8 }}>
        <div style={{ width: `${value}%`, height: "100%", borderRadius: 8, background: color }} />
      </div>
      {alert && <div style={{ color: "#ef4444", marginTop: 4 }}>DANGER AHEAD</div>}
    </div>
  );
}
