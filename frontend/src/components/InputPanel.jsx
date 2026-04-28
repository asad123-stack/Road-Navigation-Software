import { useRef } from "react";
import { Upload, Camera, Play, Square } from "lucide-react";

export default function InputPanel({
  onUploadFrame,
  inputMode,
  setInputMode,
  isProcessing,
  setIsProcessing,
  videoRef,
  cameraError,
  onStopAnalysis,
}) {
  const ref = useRef(null);

  function readFile(file) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => onUploadFrame(String(reader.result));
    reader.readAsDataURL(file);
  }

  function handleStopClick() {
    if (isProcessing && onStopAnalysis) {
      onStopAnalysis();
    }
    setIsProcessing((v) => !v);
  }

  return (
    <div className="input-panel" style={{ display: "flex", flexDirection: "column", flex: 1, minHeight: 0 }}>
      <p className="section-title">Data Source</p>
      <div className="mode-buttons" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", marginBottom: "16px" }}>
        <button
          type="button"
          className={`btn-pointed ${inputMode === "upload" ? "active" : ""}`}
          onClick={() => setInputMode("upload")}
        >
          <Upload size={14} /> Local File
        </button>
        <button
          type="button"
          className={`btn-pointed ${inputMode === "phone" ? "active" : ""}`}
          onClick={() => setInputMode("phone")}
        >
          <Camera size={14} /> Camera Feed
        </button>
      </div>

      <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>
        {inputMode === "upload" ? (
          <div style={{ padding: "16px", border: "1px dashed #e2e8f0", borderRadius: "8px", background: "#f8fafc", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <input
              className="file-input"
              ref={ref}
              type="file"
              accept="image/*"
              onChange={(e) => readFile(e.target.files?.[0])}
              style={{ fontSize: "12px", color: "#64748b" }}
            />
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: "12px" }}>
            <div style={{ flex: 1, background: "#f1f5f9", border: "1px solid #e2e8f0", borderRadius: "8px", position: "relative", overflow: "hidden" }}>
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit: "contain",
                  background: "#000"
                }}
              />
              {cameraError && (
                <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)", color: "var(--danger)", fontSize: "12px", textAlign: "center", width: "80%" }}>
                  {cameraError}
                </div>
              )}
            </div>
            <button
              type="button"
              className={`btn-pointed ${isProcessing ? "stop" : "start"}`}
              onClick={handleStopClick}
              style={{ padding: "12px", fontWeight: "600" }}
            >
              {isProcessing ? <><Square size={14} /> Stop Analysis</> : <><Play size={14} /> Start Real-time Analysis</>}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
