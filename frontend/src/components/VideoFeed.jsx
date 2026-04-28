import { Eye } from "lucide-react";

export default function VideoFeed({ frame, videoRef }) {
  return (
    <div className="visual-card" style={{ flex: 1, minHeight: 0 }}>
      <div className="visual-title">
        <Eye size={14} /> Augmented Visual Analysis
      </div>
      <div style={{ 
        position: "relative", 
        width: "100%", 
        height: "100%", 
        background: "#f1f5f9",
        border: "1px solid #e2e8f0",
        borderRadius: "6px",
        overflow: "hidden"
      }}>
        {/* Raw video stream */}
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          style={{
            width: "100%",
            height: "100%",
            display: "block",
            objectFit: "contain",
            opacity: 0.9,
            background: "#000"
          }}
        />

        {/* Annotated overlay */}
        {frame && (
          <img
            src={frame}
            alt="AI Visual Analysis"
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              objectFit: "contain",
              zIndex: 5
            }}
          />
        )}

        {/* Status Badge */}
        <div style={{
          position: "absolute",
          top: "16px",
          left: "16px",
          background: "#ffffff",
          color: "#0f172a",
          padding: "4px 12px",
          fontSize: "11px",
          fontWeight: "600",
          borderRadius: "4px",
          border: "1px solid #e2e8f0",
          boxShadow: "0 1px 2px 0 rgba(0,0,0,0.05)",
          zIndex: 11
        }}>
          Live Analysis Active
        </div>

        {!frame && (
          <div style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            color: "#94a3b8",
            fontSize: "13px",
            fontWeight: "500"
          }}>
            Synchronizing data feed...
          </div>
        )}
      </div>
    </div>
  );
}
