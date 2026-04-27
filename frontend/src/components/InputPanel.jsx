import { useRef } from "react";

export default function InputPanel({
  onUploadFrame,
  inputMode,
  setInputMode,
  isProcessing,
  setIsProcessing,
  videoRef,
  cameraError,
}) {
  const ref = useRef(null);

  function readFile(file) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => onUploadFrame(String(reader.result));
    reader.readAsDataURL(file);
  }

  return (
    <div className="input-panel">
      <p className="section-title">Input Mode</p>
      <div className="mode-buttons">
        <button
          type="button"
          className={`btn-pointed ${inputMode === "upload" ? "active" : ""}`}
          onClick={() => setInputMode("upload")}
        >
          Upload
        </button>
        <button
          type="button"
          className={`btn-pointed ${inputMode === "phone" ? "active" : ""}`}
          onClick={() => setInputMode("phone")}
        >
          Phone Camera
        </button>
      </div>

      {inputMode === "upload" ? (
        <input className="file-input" ref={ref} type="file" accept="image/*" onChange={(e) => readFile(e.target.files?.[0])} />
      ) : (
        <>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="camera-preview"
          />
          {cameraError && <div className="error-text">{cameraError}</div>}
          <button
            type="button"
            className={`btn-pointed action ${isProcessing ? "stop" : "start"}`}
            onClick={() => setIsProcessing((v) => !v)}
          >
            {isProcessing ? "Stop" : "Start"}
          </button>
        </>
      )}
    </div>
  );
}
