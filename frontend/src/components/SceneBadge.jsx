import { Building2, Trees, Landmark, Warehouse } from "lucide-react";

const sceneConfig = {
  tunnel: { color: "#64748b", icon: <Warehouse size={14} /> },
  urban: { color: "#3b82f6", icon: <Building2 size={14} /> },
  open_road: { color: "#10b981", icon: <Trees size={14} /> },
  indoor: { color: "#f59e0b", icon: <Landmark size={14} /> },
};

export default function SceneBadge({ scene }) {
  const config = sceneConfig[scene] ?? sceneConfig.urban;
  
  return (
    <div style={{ marginTop: 16 }}>
      <p className="section-title">Environment Classification</p>
      <div style={{ 
        display: "inline-flex", 
        alignItems: "center", 
        gap: "8px", 
        background: "#f8fafc", 
        color: config.color,
        border: `1px solid #e2e8f0`,
        padding: "6px 12px", 
        borderRadius: "6px",
        fontSize: "12px",
        fontWeight: "600",
        textTransform: "capitalize"
      }}>
        {config.icon}
        {scene.replace("_", " ")}
      </div>
    </div>
  );
}
