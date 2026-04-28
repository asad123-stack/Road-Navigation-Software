export default function OledSimulator({ cue }) {
  const isString = typeof cue === "string";
  const cueText = isString ? cue : cue?.cue ?? "GO STRAIGHT";
  const confidence = !isString && cue?.confidence ? cue.confidence : 0;

  return (
    <div style={{ marginTop: 16 }}>
      <p className="section-title">Heads-Up Display (HUD)</p>
      <div
        style={{
          position: "relative",
          background: "#ffffff",
          color: "#0f172a",
          fontFamily: "inherit",
          border: "1px solid #e2e8f0",
          borderRadius: "8px",
          padding: "16px",
          textAlign: "center",
          overflow: "hidden",
          boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
        }}
      >
        <div style={{ fontSize: "11px", fontWeight: "600", color: "#64748b", borderBottom: "1px solid #f1f5f9", paddingBottom: "6px", marginBottom: "10px" }}>
          Active Viewport Interface
        </div>

        <div style={{ fontSize: "24px", fontWeight: "700", margin: "12px 0", color: "#3b82f6" }}>
          {cueText}
        </div>
        
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", fontWeight: "500", color: "#94a3b8", marginTop: "10px" }}>
          <span>System Stable</span>
          <span>Reliability: {confidence}%</span>
        </div>
      </div>
    </div>
  );
}
