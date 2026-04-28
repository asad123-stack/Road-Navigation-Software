import React from "react";
import MapView from "./MapView";
import { X, Activity, Shield, Navigation2, Target, BarChart3, Clock, Map as MapIcon, Image as ImageIcon } from "lucide-react";

export default function MetricsModal({ 
  isOpen, 
  onClose, 
  metrics, 
  cue, 
  sceneType, 
  detections, 
  trajectories,
  zoneDepths,
  lstmRisk,
  featureQuality,
  motionMagnitude,
  odomPosition,
  userPosition,
  destination,
  route,
  obstaclePins,
  annotatedFrame,
  sessionSummary,
}) {
  if (!isOpen) return null;

  const riskColor = (score) => {
    if (score >= 75) return "#ef4444";
    if (score >= 50) return "#f59e0b";
    if (score >= 25) return "#3b82f6";
    return "#10b981";
  };

  const qualityColor = (quality) => {
    if (quality >= 80) return "#10b981";
    if (quality >= 50) return "#f59e0b";
    if (quality >= 25) return "#3b82f6";
    return "#ef4444";
  };

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: "rgba(15, 23, 42, 0.4)",
        backdropFilter: "blur(4px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 9999,
        padding: "20px"
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: "#ffffff",
          border: "1px solid #e2e8f0",
          borderRadius: "12px",
          padding: "32px",
          width: "100%",
          maxWidth: "1100px",
          maxHeight: "90vh",
          overflowY: "auto",
          color: "#1e293b",
          boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "32px", borderBottom: "1px solid #f1f5f9", paddingBottom: "16px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <BarChart3 size={24} color="#0f172a" />
            <h2 style={{ margin: 0, fontSize: "20px", fontWeight: "700", color: "#0f172a" }}>Session Analysis Report</h2>
          </div>
          <button
            onClick={onClose}
            style={{
              background: "#f1f5f9",
              border: "none",
              borderRadius: "50%",
              color: "#64748b",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              width: "32px",
              height: "32px",
              cursor: "pointer",
              transition: "all 0.2s"
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Main Grid: Visuals + Metrics */}
        <div style={{ display: "grid", gridTemplateColumns: "1.2fr 0.8fr", gap: "32px", marginBottom: "32px" }}>
          {/* Left Column: Visual Overlays */}
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            {/* Annotated Frame */}
            {annotatedFrame && (
              <div style={{ border: "1px solid #e2e8f0", borderRadius: "8px", overflow: "hidden", background: "#f8fafc" }}>
                <div style={{ fontSize: "12px", fontWeight: "600", color: "#64748b", padding: "10px 16px", background: "#ffffff", borderBottom: "1px solid #e2e8f0", display: "flex", alignItems: "center", gap: "8px" }}>
                  <ImageIcon size={14} /> Last Processed Viewport
                </div>
                <img 
                  src={annotatedFrame} 
                  alt="Annotated Frame" 
                  style={{ width: "100%", display: "block", maxHeight: "400px", objectFit: "contain", background: "#000" }}
                />
              </div>
            )}

            {/* Map Area */}
            {userPosition && (
              <div style={{ border: "1px solid #e2e8f0", borderRadius: "8px", overflow: "hidden", background: "#f8fafc", height: "400px" }}>
                <div style={{ fontSize: "12px", fontWeight: "600", color: "#64748b", padding: "10px 16px", background: "#ffffff", borderBottom: "1px solid #e2e8f0", display: "flex", alignItems: "center", gap: "8px" }}>
                  <MapIcon size={14} /> Tactical Route Geometry
                </div>
                <div style={{ height: "calc(100% - 37px)", width: "100%" }}>
                  <MapView
                    userPosition={userPosition}
                    destination={destination}
                    route={route}
                    obstaclePins={obstaclePins}
                    riskSegments={[]}
                    readOnly={true}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Right Column: Detailed Telemetry */}
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            {/* Primary KPI Grid */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
              <div style={{ border: "1px solid #e2e8f0", borderRadius: "8px", padding: "16px", background: "#f8fafc" }}>
                <h3 style={{ marginTop: 0, marginBottom: "12px", color: "#64748b", fontSize: "11px", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.05em", display: "flex", alignItems: "center", gap: "6px" }}>
                  <Activity size={12} /> System Performance
                </h3>
                <div style={{ fontSize: "12px", display: "flex", flexDirection: "column", gap: "8px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between" }}><strong>Throughput:</strong> <span style={{ color: "#0f172a" }}>{metrics?.fps || "0"} FPS</span></div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}><strong>Latency:</strong> <span style={{ color: "#0f172a" }}>{metrics?.latency || "0"}ms</span></div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}><strong>Processing:</strong> <span style={{ color: "#0f172a" }}>{metrics?.processingTime || "0"}ms</span></div>
                </div>
              </div>

              <div style={{ border: "1px solid #e2e8f0", borderRadius: "8px", padding: "16px", background: "#f8fafc" }}>
                <h3 style={{ marginTop: 0, marginBottom: "12px", color: "#64748b", fontSize: "11px", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.05em", display: "flex", alignItems: "center", gap: "6px" }}>
                  <Shield size={12} /> Safety Assessment
                </h3>
                <div style={{ fontSize: "12px", display: "flex", flexDirection: "column", gap: "8px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <strong>Risk Level:</strong>{" "}
                    <span style={{ color: riskColor(metrics?.riskScore || 0), fontWeight: "700", fontSize: "14px" }}>
                      {metrics?.riskScore || 0}%
                    </span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}><strong>LSTM Prediction:</strong> <span style={{ color: lstmRisk > 0.6 ? "#ef4444" : "#10b981", fontWeight: "600" }}>{(lstmRisk * 100).toFixed(1)}%</span></div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}><strong>Environment:</strong> <span style={{ color: "#0f172a", textTransform: "capitalize" }}>{sceneType}</span></div>
                </div>
              </div>
            </div>

            {/* Proximity Analysis (Depth) */}
            <div style={{ border: "1px solid #e2e8f0", borderRadius: "8px", padding: "20px", background: "#f8fafc" }}>
              <h3 style={{ marginTop: 0, marginBottom: "16px", color: "#64748b", fontSize: "11px", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Proximity Analysis (Spatial Awareness)
              </h3>
              <div style={{ fontSize: "12px", display: "flex", flexDirection: "column", gap: "12px" }}>
                {["Left", "Center", "Right"].map((zone) => (
                  <div key={zone} style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                    <strong style={{ minWidth: "60px" }}>{zone}:</strong>
                    <div style={{ flex: 1, height: "8px", background: "#e2e8f0", borderRadius: "4px", overflow: "hidden" }}>
                      <div 
                        style={{ 
                          width: `${Math.min((zoneDepths?.[zone.toLowerCase()] || 0) * 10, 100)}%`, 
                          height: "100%", 
                          background: zone === "Center" ? "#f59e0b" : "#3b82f6",
                          transition: "width 0.5s ease" 
                        }} 
                      />
                    </div>
                    <span style={{ color: "#0f172a", fontWeight: "600", minWidth: "45px", textAlign: "right" }}>
                      {(zoneDepths?.[zone.toLowerCase()] || 0).toFixed(2)}m
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Navigation & Entity Tracking */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
              <div style={{ border: "1px solid #e2e8f0", borderRadius: "8px", padding: "16px", background: "#f8fafc" }}>
                <h3 style={{ marginTop: 0, marginBottom: "12px", color: "#64748b", fontSize: "11px", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.05em", display: "flex", alignItems: "center", gap: "6px" }}>
                  <Navigation2 size={12} /> Instructions
                </h3>
                <div style={{ padding: "12px", background: "#ffffff", borderRadius: "6px", border: "1px solid #e2e8f0", borderLeft: `4px solid ${cue?.color || "#3b82f6"}` }}>
                  <div style={{ fontSize: "14px", fontWeight: "700", color: "#0f172a" }}>{cue?.icon || "↑"} {cue?.cue || "Go Straight"}</div>
                  <div style={{ fontSize: "10px", color: "#64748b", marginTop: "4px" }}>Confidence: {cue?.confidence || 0}%</div>
                </div>
              </div>

              <div style={{ border: "1px solid #e2e8f0", borderRadius: "8px", padding: "16px", background: "#f8fafc" }}>
                <h3 style={{ marginTop: 0, marginBottom: "12px", color: "#64748b", fontSize: "11px", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.05em", display: "flex", alignItems: "center", gap: "6px" }}>
                  <Target size={12} /> Entity Tracking
                </h3>
                <div style={{ fontSize: "12px", display: "flex", flexDirection: "column", gap: "6px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between" }}><strong>Detected Entities:</strong> <span style={{ color: "#0f172a", fontWeight: "600" }}>{detections?.length || 0}</span></div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}><strong>Active Trajectories:</strong> <span style={{ color: "#0f172a", fontWeight: "600" }}>{trajectories?.length || 0}</span></div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}><strong>Feature Quality:</strong> <span style={{ color: qualityColor(featureQuality), fontWeight: "600" }}>{featureQuality || 0}%</span></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Summary */}
        <div style={{ borderTop: "1px solid #f1f5f9", paddingTop: "20px", marginTop: "8px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontSize: "12px", color: "#94a3b8", display: "flex", alignItems: "center", gap: "8px" }}>
            <Clock size={14} /> Session duration analysis: <strong>{metrics?.processingTime ? Math.round(metrics.processingTime / 100) : "?"} units</strong>
          </div>
          <div style={{ fontSize: "12px", color: "#94a3b8" }}>
            Generated on {new Date().toLocaleDateString()} at {new Date().toLocaleTimeString()}
          </div>
        </div>

        {/* Action Button */}
        <div style={{ textAlign: "center", marginTop: "32px" }}>
          <button
            onClick={onClose}
            style={{
              background: "#0f172a",
              color: "white",
              border: "none",
              padding: "12px 48px",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "14px",
              fontWeight: "600",
              transition: "all 0.2s",
              boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.background = "#1e293b";
              e.currentTarget.style.transform = "translateY(-1px)";
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = "#0f172a";
              e.currentTarget.style.transform = "translateY(0)";
            }}
          >
            Acknowledge & Close
          </button>
        </div>
      </div>
    </div>
  );
}
