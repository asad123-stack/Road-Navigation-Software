import { Shield, Settings, Activity, User } from "lucide-react";

export default function Navbar() {
  return (
    <div className="panel" style={{ margin: "24px 24px 0 24px", display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px 32px", borderRadius: "8px", border: "1px solid #e2e8f0", background: "#ffffff" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        <div style={{ padding: "8px", background: "#f1f5f9", borderRadius: "6px" }}>
          <Shield size={22} color="#0f172a" />
        </div>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <strong style={{ fontSize: "18px", letterSpacing: "0.02em", fontWeight: 700, color: "#0f172a" }}>
            SmartHelmet <span style={{ color: "#3b82f6" }}>Navigator</span>
          </strong>
          <span style={{ fontSize: "11px", color: "#64748b", fontWeight: 500 }}>Enterprise Management Console v2.0</span>
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: "32px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", fontSize: "12px", fontWeight: 600, color: "#10b981" }}>
          <Activity size={16} />
          System Operational
        </div>
        <div style={{ display: "flex", gap: "20px", color: "#64748b" }}>
          <Settings size={20} style={{ cursor: "pointer" }} />
          <User size={20} style={{ cursor: "pointer" }} />
        </div>
      </div>
    </div>
  );
}
