import { Target, Scan } from "lucide-react";

export default function DetectedObjects({ detections }) {
  const top = detections.slice(0, 5);
  
  return (
    <div style={{ marginTop: 20 }}>
      <p className="section-title" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <Target size={14} /> Detected Entities
      </p>
      
      <div style={{ display: "flex", flexDirection: "column", gap: "8px", minHeight: "100px" }}>
        {top.length === 0 ? (
          <div style={{ fontSize: "12px", color: "#94a3b8", fontStyle: "italic", padding: "12px", border: "1px solid #f1f5f9", borderRadius: "8px" }}>
            Scanning environment...
          </div>
        ) : (
          top.map((d, i) => (
            <div
              key={`${d.label}-${i}`}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "10px 14px",
                background: "#f8fafc",
                borderRadius: "6px",
                border: "1px solid #e2e8f0"
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <Scan size={14} color="#3b82f6" />
                <span style={{ fontSize: "13px", fontWeight: "600", color: "#1e293b", textTransform: "capitalize" }}>{d.label}</span>
              </div>
              <div style={{ fontSize: "12px", fontWeight: "700", color: "#3b82f6" }}>
                {Math.round((d.confidence ?? 0) * 100)}%
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
