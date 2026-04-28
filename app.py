import time

from flask import Flask, jsonify, request
from flask_cors import CORS

from src.depth_estimator import DepthEstimator
from src.detector import ObjectDetector
from src.lstm_predictor import LSTMPredictor
from src.navigation_logic import get_navigation_cue
from src.optical_flow import VisualOdometry
from src.risk_scorer import RiskScorer
from src.scene_classifier import SceneClassifier
from src.tracker import ObjectTracker
from src.utils import decode_data_url_image
from src.visualizer import encode_frame_to_data_url, render_annotations

app = Flask(__name__)
CORS(app, origins="*")

detector = ObjectDetector()
depth_estimator = DepthEstimator()
risk_scorer = RiskScorer()
tracker = ObjectTracker()
lstm_predictor = LSTMPredictor()
scene_classifier = SceneClassifier()
visual_odometry = VisualOdometry()

obstacle_pins = []
last_route = {"steps": [], "coordinates": []}
OBSTACLE_PIN_TTL_SECONDS = 30
DEPTH_EVERY_N_FRAMES = 2
SCENE_EVERY_N_FRAMES = 3
frame_counter = 0
last_zone_depths = {"left": 0.5, "center": 0.5, "right": 0.5}
last_scene_type = "urban"


def get_active_obstacle_pins():
    now = time.time()
    obstacle_pins[:] = [p for p in obstacle_pins if now - p["timestamp"] <= OBSTACLE_PIN_TTL_SECONDS]
    return obstacle_pins


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "service": "smarthelmet-nav",
            "models": {
                "detector_loaded": detector.is_model_loaded(),
                "depth_midas_loaded": depth_estimator.is_model_loaded(),
                "depth_adabins_loaded": depth_estimator.is_adabins_loaded(),
                "risk_loaded": risk_scorer.is_model_loaded(),
                "lstm_loaded": lstm_predictor.is_model_loaded(),
                "scene_loaded": scene_classifier.is_model_loaded(),
            },
        }
    )


@app.post("/api/process_frame")
def process_frame():
    global frame_counter, last_zone_depths, last_scene_type, last_route
    payload = request.get_json(silent=True) or {}
    frame_data = payload.get("frame")
    
    # Track route updates from frontend
    if "route" in payload:
        last_route = payload.get("route", {})
    
    if not isinstance(frame_data, str) or not frame_data:
        return jsonify({"error": "Missing required field: frame"}), 400

    frame = decode_data_url_image(frame_data)
    if frame is None:
        return jsonify({"error": "Invalid frame payload"}), 400

    frame = depth_estimator.resize_for_pipeline(frame)
    frame_counter += 1
    detections = detector.detect(frame)

    if frame_counter % DEPTH_EVERY_N_FRAMES == 0:
        _, zone_depths = depth_estimator.estimate(frame)
        last_zone_depths = zone_depths
    else:
        zone_depths = last_zone_depths

    risk_score = risk_scorer.score(detections, zone_depths)

    if frame_counter % SCENE_EVERY_N_FRAMES == 0:
        scene_type = scene_classifier.classify(frame)
        last_scene_type = scene_type
    else:
        scene_type = last_scene_type
    lstm_predictor.update(risk_score, len(detections), zone_depths["center"])
    lstm_risk = lstm_predictor.predict()
    lstm_alert = lstm_predictor.get_alert()

    lat = payload.get("lat")
    lng = payload.get("lng")
    
    cue = get_navigation_cue(
        detections, 
        zone_depths, 
        risk_score, 
        scene_type,
        user_lat=lat,
        user_lng=lng,
        route_steps=last_route.get("steps", []),
        lstm_risk=lstm_risk
    )
    trajectories = tracker.update(detections)

    dx, dy, cum_x, cum_y = visual_odometry.update(frame)
    odometry_trajectory = visual_odometry.get_trajectory()[-50:]
    feature_quality = visual_odometry.get_feature_quality()[-50:]
    motion_magnitude = visual_odometry.get_motion_magnitude()[-50:]

    get_active_obstacle_pins()
    if risk_score > 60 and isinstance(lat, (int, float)) and isinstance(lng, (int, float)):
        label = detections[0]["label"] if detections else "obstacle"
        obstacle_pins.append({"lat": lat, "lng": lng, "label": label, "timestamp": time.time()})
        if len(obstacle_pins) > 200:
            del obstacle_pins[:-200]

    motion_vector = {"dx": dx, "dy": dy}
    annotated = render_annotations(frame, detections, cue, risk_score, trajectories, odometry_trajectory, motion_vector, feature_quality, motion_magnitude)

    response = {
        "cue": cue,
        "detections": detections,
        "zone_depths": zone_depths,
        "risk_score": risk_score,
        "trajectories": trajectories,
        "annotated_frame": encode_frame_to_data_url(annotated),
        "lstm_risk": lstm_risk,
        "lstm_alert": lstm_alert,
        "scene_type": scene_type,
        "motion_vector": motion_vector,
        "odometry_position": {"x": cum_x, "y": cum_y},
        "odometry_trajectory": odometry_trajectory,
        "feature_quality": feature_quality,
        "motion_magnitude": motion_magnitude,
        "odom_x": cum_x,
        "odom_y": cum_y,
        "obstacle_geo_pins": get_active_obstacle_pins()[-50:],
    }
    return jsonify(response)


if __name__ == "__main__":
    print(
        "[app.py] Model status | YOLO="
        f"{detector.is_model_loaded()} "
        f"Depth(MiDaS)={depth_estimator.is_model_loaded()} "
        f"Depth(AdaBins)={depth_estimator.is_adabins_loaded()} "
        f"RiskMLP={risk_scorer.is_model_loaded()} "
        f"LSTM={lstm_predictor.is_model_loaded()} "
        f"Scene={scene_classifier.is_model_loaded()}"
    )
    print("[app.py] SmartHelmet Nav backend starting on 0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
