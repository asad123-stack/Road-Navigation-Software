import { ArrowUp, ArrowUpLeft, ArrowUpRight, AlertTriangle, Navigation2 } from "lucide-react";

const getIcon = (cueText) => {
  const lower = cueText.toLowerCase();
  if (lower.includes("left")) return <ArrowUpLeft size={18} />;
  if (lower.includes("right")) return <ArrowUpRight size={18} />;
  if (lower.includes("straight") || lower.includes("go")) return <ArrowUp size={18} />;
  return <Navigation2 size={18} />;
};

export default function NavigationCue({ cue, nextStep }) {
  if (!cue) return null;

  const isString = typeof cue === "string";
  const cueText = isString ? cue : cue.cue;
  const confidence = !isString && cue.confidence ? cue.confidence : 0;
  const color = !isString && cue.color ? cue.color : "#3b82f6";
  const secondaryAlerts = !isString && cue.secondary_alerts ? cue.secondary_alerts : [];
  const hasWarning = !isString && cue.lstm_warning;

  return (
    <div style={{ marginTop: 12 }}>
      <p className="section-title">Navigation Instruction</p>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "12px",
          padding: "12px 16px",
          background: "#f8fafc",
          border: `1px solid #e2e8f0`,
          borderLeft: `4px solid ${color}`,
          borderRadius: "6px",
          marginBottom: "8px",
        }}
      >
        <div style={{ color: color }}>{getIcon(cueText)}</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: "600", color: "#0f172a", fontSize: "15px" }}>
            {cueText}
          </div>
          {confidence > 0 && (
            <div style={{ fontSize: "11px", color: "#64748b", marginTop: "2px" }}>
              Confidence Level: {confidence}%
            </div>
          )}
        </div>
      </div>

      {secondaryAlerts.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
          {secondaryAlerts.map((alert, idx) => (
            <div
              key={idx}
              style={{
                padding: "8px 12px",
                background: "#fef2f2",
                color: "#991b1b",
                border: "1px solid #fee2e2",
                display: "flex",
                alignItems: "center",
                gap: "8px",
                fontWeight: "600",
                fontSize: "12px",
                borderRadius: "6px"
              }}
            >
              <AlertTriangle size={14} />
              {alert.cue}
            </div>
          ))}
        </div>
      )}

      {hasWarning && (
        <div style={{
          marginTop: "8px",
          padding: "8px",
          border: "1px solid #fef3c7",
          background: "#fffbeb",
          color: "#92400e",
          fontSize: "11px",
          fontWeight: "600",
          textAlign: "center",
          borderRadius: "6px"
        }}>
          Potential Hazard Detected Ahead
        </div>
      )}

      {nextStep && (
        <div style={{
          marginTop: "12px",
          fontSize: "11px",
          color: "#64748b",
          borderTop: "1px solid #f1f5f9",
          paddingTop: "10px",
          display: "flex",
          justifyContent: "space-between"
        }}>
          <strong>Upcoming Step:</strong> <span>{nextStep}</span>
        </div>
      )}
    </div>
  );
}
