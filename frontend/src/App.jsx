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
import MetricsModal from "./components/MetricsModal";
import { processFrame } from "./api/helmetApi";

export default function App() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const loopBusyRef = useRef(false);
  const lastFrameTimeRef = useRef(0);

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
  const [zoneDepths, setZoneDepths] = useState({ left: 0.5, center: 0.5, right: 0.5 });
  const [trajectories, setTrajectories] = useState([]);
  const [metricsData, setMetricsData] = useState(null);
  const [showMetricsModal, setShowMetricsModal] = useState(false);
  const [featureQuality, setFeatureQuality] = useState(0);
  const [motionMagnitude, setMotionMagnitude] = useState(0);
  const [odomPosition, setOdomPosition] = useState({ x: 0, y: 0 });
  const [sessionEvents, setSessionEvents] = useState([]);
  const [sessionStartTime, setSessionStartTime] = useState(null);
  const [lastCue, setLastCue] = useState(null);
  const [sessionSummary, setSessionSummary] = useState(null);

  const nextStep = useMemo(() => {
    const step = route.steps?.[0];
    if (!step) return "";
    const maneuver = step.maneuver?.modifier ? `${step.maneuver.type} ${step.maneuver.modifier}` : step.maneuver?.type;
    const distance = typeof step.distance === "number" ? `${Math.round(step.distance)}m` : "";
    return [maneuver, distance].filter(Boolean).join(" • ");
  }, [route.steps]);

  async function handleFrame(frameDataUrl) {
    const frameStartTime = performance.now();
    const result = await processFrame(frameDataUrl, userPosition?.lat, userPosition?.lng, route);
    const frameEndTime = performance.now();
    const latency = frameEndTime - frameStartTime;
    const currentFps = lastFrameTimeRef.current > 0 ? 1000 / (frameStartTime - lastFrameTimeRef.current) : 0;
    lastFrameTimeRef.current = frameStartTime;

    setAnnotatedFrame(result.annotated_frame ?? null);
    setCurrentCue(result.cue);
    setDetections(result.detections ?? []);
    setRiskScore(result.risk_score ?? 0);
    setLstmRisk(result.lstm_risk ?? null);
    setLstmAlert(Boolean(result.lstm_alert));
    setSceneType(result.scene_type ?? "urban");
    setZoneDepths(result.zone_depths ?? { left: 0.5, center: 0.5, right: 0.5 });
    setTrajectories(result.trajectories ?? []);
    setObstaclePins(result.obstacle_geo_pins ?? []);

    const avgMotion = result.motion_magnitude ? (Array.isArray(result.motion_magnitude) ? result.motion_magnitude.reduce((a, b) => a + b, 0) / result.motion_magnitude.length : result.motion_magnitude) : 0;
    const avgQuality = result.feature_quality ? (Array.isArray(result.feature_quality) ? result.feature_quality.reduce((a, b) => a + b, 0) / result.feature_quality.length : result.feature_quality) : 0;

    setMotionMagnitude(avgMotion);
    setFeatureQuality(avgQuality);
    setOdomPosition({ x: result.odom_x || 0, y: result.odom_y || 0 });

    setMetricsData({
      fps: Math.round(currentFps),
      latency: Math.round(latency),
      processingTime: Math.round(latency * 0.8),
      frameQueue: 0,
      riskScore: result.risk_score ?? 0,
    });

    // Track events for session log
    const currentCue = result.cue?.cue || "GO STRAIGHT";
    if (lastCue !== currentCue) {
      const isTurn = currentCue.includes("TURN");
      const eventType = isTurn ? "turn" : "state_change";

      setSessionEvents((prev) => [
        ...prev,
        {
          timestamp: new Date(),
          type: eventType,
          cue: currentCue,
          position: userPosition,
          riskScore: result.risk_score,
          detections: result.detections?.length || 0,
          zoneDepths: result.zone_depths,
        }
      ]);
      setLastCue(currentCue);
    }

    // Log obstacle detection events
    if ((result.detections?.length || 0) > 0) {
      result.detections.forEach((det) => {
        const existingEvent = sessionEvents.find(
          (e) => e.type === "obstacle" && e.label === det.label && Date.now() - new Date(e.timestamp).getTime() < 1000
        );
        if (!existingEvent) {
          setSessionEvents((prev) => [
            ...prev,
            {
              timestamp: new Date(),
              type: "obstacle",
              label: det.label,
              confidence: det.confidence,
              position: userPosition,
              riskScore: result.risk_score,
            }
          ]);
        }
      });
    }

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
    return canvas.toDataURL("image/jpeg", 0.3);
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
        setCameraError("Unable to access camera feed.");
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

    // Start session on first isProcessing
    if (sessionStartTime === null) {
      setSessionStartTime(new Date());
      setSessionEvents([]);
    }

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
    }, 300);

    return () => {
      clearInterval(timer);
      loopBusyRef.current = false;
    };
  }, [isProcessing, inputMode, userPosition]);

  function handleStopAnalysis() {
    const endTime = new Date();
    const duration = sessionStartTime ? (endTime - sessionStartTime) / 1000 : 0;

    const turns = sessionEvents.filter((e) => e.type === "turn");
    const obstacles = sessionEvents.filter((e) => e.type === "obstacle");
    const maxRisk = sessionEvents.length > 0 ? Math.max(...sessionEvents.map((e) => e.riskScore || 0)) : 0;
    const avgRisk = sessionEvents.length > 0 ? sessionEvents.reduce((sum, e) => sum + (e.riskScore || 0), 0) / sessionEvents.length : 0;

    const summary = {
      startTime: sessionStartTime,
      endTime: endTime,
      durationSeconds: Math.round(duration),
      totalFrames: Math.round(duration / 0.3),
      totalTurns: turns.length,
      turnEvents: turns,
      obstaclesEncountered: obstacles.length,
      obstacleDetails: obstacles,
      maxRiskScore: Math.round(maxRisk),
      avgRiskScore: Math.round(avgRisk),
      allEvents: sessionEvents,
    };

    setSessionSummary(summary);
    setShowMetricsModal(true);
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
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
            onStopAnalysis={handleStopAnalysis}
          />
          <NavigationCue cue={currentCue} nextStep={nextStep} />
          <RiskScore score={riskScore} />
          <LSTMRiskBar score={lstmRisk} alert={lstmAlert} />
          <SceneBadge scene={sceneType} />
          <OledSimulator cue={currentCue} />
          <DetectedObjects detections={detections} />

          <div className="metrics-display">
            {[
              { label: "Throughput", value: "~3 FPS" },
              { label: "Latency", value: "~300ms" },
              { label: "Safety Index", value: (100 - riskScore).toFixed(0) },
              { label: "Entities", value: detections.length },
              { label: "Environment", value: sceneType.toUpperCase() },
              { label: "Projection", value: lstmRisk?.toFixed(2) ?? "N/A" },
            ].map((m, i) => (
              <div key={i} className="metric-item">
                <div className="metric-label">{m.label}</div>
                <div className="metric-value">{m.value}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="panel visuals-panel">
          <div className="visuals-grid">
            <VideoFeed frame={annotatedFrame} videoRef={videoRef} />
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
          </div>
        </div>
      </div>

      <MetricsModal
        isOpen={showMetricsModal}
        onClose={() => setShowMetricsModal(false)}
        metrics={metricsData}
        cue={currentCue}
        sceneType={sceneType}
        detections={detections}
        trajectories={trajectories}
        zoneDepths={zoneDepths}
        lstmRisk={lstmRisk}
        featureQuality={featureQuality}
        motionMagnitude={motionMagnitude}
        odomPosition={odomPosition}
        userPosition={userPosition}
        destination={destination}
        route={route}
        obstaclePins={obstaclePins}
        annotatedFrame={annotatedFrame}
        sessionSummary={sessionSummary}
      />
    </div>
  );
}
