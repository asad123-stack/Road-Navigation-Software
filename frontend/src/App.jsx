import { useEffect, useMemo, useRef, useState } from "react";
import DetectedObjects from "./components/DetectedObjects";
import InputPanel from "./components/InputPanel";
import LSTMRiskBar from "./components/LSTMRiskBar";
import MapView from "./components/MapView";
import Navbar from "./components/Navbar";
import NavigationCue from "./components/NavigationCue";
import OledSimulator from "./components/OledSimulator";
import RiskScore from "./components/RiskScore";
import SceneBadge from "./components/SceneBadge";
import VideoFeed from "./components/VideoFeed";
import { processFrame } from "./api/helmetApi";

export default function App() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const loopBusyRef = useRef(false);

  const [annotatedFrame, setAnnotatedFrame] = useState(null);
  const [inputMode, setInputMode] = useState("upload");
  const [isProcessing, setIsProcessing] = useState(false);
  const [cameraError, setCameraError] = useState("");
  const [currentCue, setCurrentCue] = useState("GO STRAIGHT");
  const [detections, setDetections] = useState([]);
  const [riskScore, setRiskScore] = useState(0);
  const [lstmRisk, setLstmRisk] = useState(null);
  const [lstmAlert, setLstmAlert] = useState(false);
  const [sceneType, setSceneType] = useState("urban");
  const [userPosition, setUserPosition] = useState(null);
  const [destination, setDestination] = useState(null);
  const [route, setRoute] = useState({ coordinates: [], steps: [] });
  const [obstaclePins, setObstaclePins] = useState([]);
  const [riskSegments, setRiskSegments] = useState([]);
  const [segmentCursor, setSegmentCursor] = useState(0);
  const nextStep = useMemo(() => {
    const step = route.steps?.[0];
    if (!step) return "";
    const maneuver = step.maneuver?.modifier ? `${step.maneuver.type} ${step.maneuver.modifier}` : step.maneuver?.type;
    const distance = typeof step.distance === "number" ? `${Math.round(step.distance)}m` : "";
    return [maneuver, distance].filter(Boolean).join(" • ");
  }, [route.steps]);

  async function handleFrame(frameDataUrl) {
    const result = await processFrame(frameDataUrl, userPosition?.lat, userPosition?.lng);
    setAnnotatedFrame(result.annotated_frame ?? null);
    setCurrentCue(result.cue?.cue ?? "GO STRAIGHT");
    setDetections(result.detections ?? []);
    setRiskScore(result.risk_score ?? 0);
    setLstmRisk(result.lstm_risk ?? null);
    setLstmAlert(Boolean(result.lstm_alert));
    setSceneType(result.scene_type ?? "urban");
    setObstaclePins(result.obstacle_geo_pins ?? []);
    if (riskSegments.length > 0) {
      const idx = Math.min(segmentCursor, riskSegments.length - 1);
      setRiskSegments((prev) => prev.map((seg, i) => (i === idx ? { ...seg, risk: result.risk_score ?? 0 } : seg)));
      setSegmentCursor((prev) => Math.min(prev + 1, riskSegments.length - 1));
    }
  }

  useEffect(() => {
    const coords = route.coordinates ?? [];
    if (coords.length < 2) {
      setRiskSegments([]);
      setSegmentCursor(0);
      return;
    }
    const next = [];
    for (let i = 0; i < coords.length - 1; i += 1) {
      const [lng1, lat1] = coords[i];
      const [lng2, lat2] = coords[i + 1];
      next.push({ coords: [[lat1, lng1], [lat2, lng2]], risk: 0 });
    }
    setRiskSegments(next);
    setSegmentCursor(0);
  }, [route.coordinates]);

  function capturePhoneFrame() {
    const video = videoRef.current;
    if (!video || !video.videoWidth || !video.videoHeight) return null;
    if (!canvasRef.current) {
      canvasRef.current = document.createElement("canvas");
    }
    const canvas = canvasRef.current;
    const targetWidth = 640;
    const scale = Math.min(1, targetWidth / video.videoWidth);
    canvas.width = Math.max(1, Math.round(video.videoWidth * scale));
    canvas.height = Math.max(1, Math.round(video.videoHeight * scale));
    const ctx = canvas.getContext("2d");
    if (!ctx) return null;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/jpeg", 0.5);
  }

  useEffect(() => {
    async function startCamera() {
      if (inputMode !== "phone") return;
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: { ideal: "environment" } },
          audio: false,
        });
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play();
        }
        setCameraError("");
      } catch (err) {
        setCameraError("Could not access phone camera.");
        setIsProcessing(false);
      }
    }

    startCamera();
    return () => {
      setIsProcessing(false);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
      }
    };
  }, [inputMode]);

  useEffect(() => {
    if (!isProcessing || inputMode !== "phone") return;
    const timer = setInterval(async () => {
      if (loopBusyRef.current) return;
      const frame = capturePhoneFrame();
      if (!frame) return;
      loopBusyRef.current = true;
      try {
        await handleFrame(frame);
      } finally {
        loopBusyRef.current = false;
      }
    }, 1000);

    return () => {
      clearInterval(timer);
      loopBusyRef.current = false;
    };
  }, [isProcessing, inputMode, userPosition]);

  return (
    <>
      <Navbar />
      <div className="app-grid">
        <div className="panel left-panel">
          <InputPanel
            onUploadFrame={handleFrame}
            inputMode={inputMode}
            setInputMode={setInputMode}
            isProcessing={isProcessing}
            setIsProcessing={setIsProcessing}
            videoRef={videoRef}
            cameraError={cameraError}
          />
          <NavigationCue cue={currentCue} nextStep={nextStep} />
          <RiskScore score={riskScore} />
          <LSTMRiskBar score={lstmRisk} alert={lstmAlert} />
          <SceneBadge scene={sceneType} />
          <OledSimulator cue={currentCue} />
          <DetectedObjects detections={detections} />
        </div>
        <div className="panel visuals-panel">
          <div className="visuals-grid">
            <MapView
              userPosition={userPosition}
              setUserPosition={setUserPosition}
              destination={destination}
              setDestination={setDestination}
              route={route}
              setRoute={setRoute}
              obstaclePins={obstaclePins}
              riskSegments={riskSegments}
            />
            <VideoFeed frame={annotatedFrame} />
          </div>
        </div>
      </div>
    </>
  );
}
