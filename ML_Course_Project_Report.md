# SmartHelmet Nav v2.0  
## AI/ML Course Project Report

**Student Project:** Vision-Based Navigation Assistant  
**Project Type:** Full-stack AI/ML system (Computer Vision + Time-Series + Geospatial UI)  
**Current Version:** v2.0 (software-only prototype)  

---

## Abstract

SmartHelmet Nav v2.0 is a mobile-first navigation safety system that combines computer vision, depth estimation, risk prediction, scene understanding, and map-based guidance. A phone camera captures periodic snapshots and sends them to a Flask backend. The backend runs object detection, monocular depth estimation, risk modeling, scene classification, and visual odometry, then returns annotated results and navigation cues. A React frontend displays a live map, detected risks, and annotated frames.

The implementation emphasizes practical deployment for course demonstration: model fallbacks, robust API contracts, trajectory overlays, and phone-ready UI. The project demonstrates integration of multiple ML modules into a single decision pipeline rather than isolated model demos.

---

## 1. Introduction to Project

### 1.1 Problem Statement
Pedestrians and riders often face dynamic hazards (vehicles, obstacles, low visibility, crowded intersections). Traditional navigation apps provide route directions but not real-time scene-aware safety cues. The project addresses this gap by combining route guidance with AI perception and risk scoring.

### 1.2 Objectives
1. Detect obstacles and relevant objects in live camera frames.
2. Estimate depth from monocular images to assess near-field danger.
3. Compute a frame-level risk score and a short-horizon future risk.
4. Classify scene context (urban/open road/tunnel/indoor) and adapt cue thresholds.
5. Estimate camera motion and show trajectory/odometry.
6. Visualize results on a phone UI with map, route, cues, and annotated frames.

### 1.3 Scope
- **In scope:** software-only system, phone camera snapshots, cloud/local inference, map overlay, route interaction.
- **Out of scope:** hardware helmet integration, production-grade SLAM, certified autonomous safety guarantees.

### 1.4 Key Contributions
- End-to-end full-stack implementation with ML pipeline orchestration.
- Hybrid model strategy (local custom weights + Hugging Face/Ultralytics fallbacks).
- Real-time annotated visualization including object trajectories and odometry overlay.
- Phone-friendly deployment with optimized frame throughput.

---

## 2. Theory

### 2.1 Object Detection (YOLOv8)
YOLOv8 is a one-stage detector that predicts class probabilities and bounding boxes in a single forward pass, making it suitable for near-real-time use. In this project:
- Primary: custom/local `models/yolov8n.pt`
- Fallback: pretrained `yolov8n.pt` auto-download via Ultralytics

### 2.2 Monocular Depth Estimation (MiDaS / AdaBins Context)
Depth from a single RGB frame is estimated via learned monocular priors.  
- Implemented model: Hugging Face `Intel/dpt-hybrid-midas`  
- Depth output is normalized to derive zone-wise clearance (`left`, `center`, `right`), used by navigation and risk modules.  
- AdaBins remains a future extension for stronger metric-depth alignment.

### 2.3 Risk Scoring (MLP)
A feedforward neural network maps scene features to a risk value:
- Features: number of objects, center depth, minimum zone depth
- Output: scalar risk score (0–100)
- If custom weights are missing, rule-based fallback keeps output contract stable.

### 2.4 Temporal Threat Prediction (LSTM)
A sequence model predicts near-future risk from recent frame history:
- Input sequence: 10 timesteps of `[risk_score, num_objects, center_depth]`
- Output: predicted risk in ~3 seconds
- Alert threshold: future risk > 70

### 2.5 Scene Classification
Scene semantics improve context-aware decisions:
- Classes: `tunnel`, `urban`, `open_road`, `indoor`
- Priority: custom `scene_classifier.pth`
- Fallback: Hugging Face `google/mobilenet_v2_1.0_224` with label mapping to 4 classes

### 2.6 Visual Odometry (Optical Flow)
Lucas-Kanade sparse optical flow tracks feature displacement between frames:
- Calculates frame-to-frame motion vector `(dx, dy)`
- Maintains cumulative trajectory
- Used for both API output and annotated-frame odometry overlay

### 2.7 Decision Layer
Navigation cue logic combines:
- risk score
- center-zone depth threshold
- detection distribution
- scene-aware thresholds  

Output cues include: **GO STRAIGHT, TURN LEFT, TURN RIGHT, SLOW DOWN, OBSTACLE AHEAD**.

---

## 3. Tools Used for Project

### 3.1 Software Stack

| Layer | Tools |
|---|---|
| Frontend | React 18, Vite, Axios, React-Leaflet, Leaflet |
| Backend | Python, Flask, Flask-CORS |
| CV/ML | OpenCV, PyTorch, Torchvision, Ultralytics, Transformers, HuggingFace Hub |
| Routing/Map | OpenStreetMap tiles, OSRM public API |
| Testing | Python test client, API smoke scripts |

### 3.2 Development Environment
- OS: Windows
- Runtime: Python virtual environment + Node.js
- Device testing: desktop browser + phone browser on same Wi-Fi

### 3.3 Project Structure (Core)
```text
smarthelmet-nav/
  app.py
  src/
    detector.py
    depth_estimator.py
    risk_scorer.py
    lstm_predictor.py
    scene_classifier.py
    optical_flow.py
    tracker.py
    visualizer.py
  frontend/
  models/
  training-guides/
```

---

## 4. Datasets and Training Plan (Sample Datasets Included)

### 4.1 YOLOv8 Detector Dataset
**Goal:** obstacle/person/vehicle detection in target environment.

**Recommended:**
1. Roboflow custom dataset from phone-captured frames.
2. Public road-scene object sets (Roboflow Universe) as base.

**Suggested split:** 70% train / 20% val / 10% test  
**Target size:** 300–1000 labeled images for a course demo.

### 4.2 Risk Scorer (MLP) Dataset
**Practical approach:** synthetic feature generation (already documented in training guide).  
Generate tuples:
- `num_objects`
- `center_depth`
- `min_zone_depth`
- target `risk_score`

This is a fast and reproducible ML dataset for coursework.

### 4.3 LSTM Threat Dataset
**Approach:** synthetic sequence data from scenario evolution rules.  
Each sample:
- sequence length = 10
- features per step = 3
- label = risk at next step (proxy for +3s future risk)

### 4.4 Scene Classification Dataset
**Classes:** tunnel, urban, open_road, indoor

**Sample sources:**
- Indoor: MIT Indoor Scenes (subset)
- Urban/Open road: BDD100K/KITTI extracted frames
- Tunnel: curated public images + own captures

**Training strategy:** transfer learning with MobileNetV2 (freeze backbone then unfreeze fine-tuning).

### 4.5 Depth Model
For this project, MiDaS is used pretrained from Hugging Face (no mandatory custom training for baseline).  
AdaBins can be integrated later as an advanced depth extension.

---

## 5. Implementation Summary (What Has Been Built)

### 5.1 Backend
- Flask API with:
  - `GET /health`
  - `POST /api/process_frame`
- Model loading with robust fallback chain:
  - YOLO local/custom -> pretrained auto-download
  - MiDaS HF model load
  - Risk/LSTM/Scene local weights or fallback behavior
- Stable API response schema for frontend compatibility.

### 5.2 Frontend
- Mobile-aware React UI
- Input modes: upload / phone camera
- Live map with tap-to-route and risk-segment coloring
- Annotated frame viewer
- Scene/risk cue widgets
- Cleaner vibrant UI styling with side-by-side map + frame layout.

### 5.3 Performance Improvements
- Phone frame downscaling before upload
- Reduced JPEG quality for faster transfer
- Faster snapshot cycle with overlap guard
- Heavy model throttling (depth/scene not recomputed every frame)

### 5.4 Visualization Upgrades
- Object trajectory lines with track IDs
- Odometry trajectory mini-panel
- Motion vector arrow directly on annotated frame

---

## 6. Results and Discussion (Test Cases)

### 6.1 Test Case Table

| Test ID | Test Description | Expected | Observed |
|---|---|---|---|
| TC-01 | Health endpoint | HTTP 200 + model flags | **Pass** (`/health` responds with detector/depth/risk/lstm/scene flags) |
| TC-02 | Frame processing API | HTTP 200 + full JSON fields | **Pass** (`cue`, `detections`, `zone_depths`, `risk_score`, `annotated_frame`, etc.) |
| TC-03 | YOLO load fallback | detector loads without manual weight setup | **Pass** (pretrained download + `detector_loaded: true`) |
| TC-04 | MiDaS HF integration | depth model load and zone depths returned | **Pass** (`depth_loaded: true`) |
| TC-05 | Optical flow stability | No 500 errors during repeated calls | **Pass after fix** (point-shape bug corrected) |
| TC-06 | Trajectory overlay visibility | Track + odometry visible on frames | **Pass** (thicker path lines + odom panel + motion arrow) |
| TC-07 | Frontend map-frame layout | map and annotated frame side-by-side | **Pass** |
| TC-08 | Phone capture mode | periodic snapshots processed | **Pass** (start/stop loop functional) |

### 6.2 Discussion
- The largest stability issue encountered was an optical flow indexing mismatch (`IndexError`) in point-array handling. This was fixed by robust reshape/validation.
- Depth and scene inference can be computationally expensive, so periodic recompute + cached reuse significantly improved practical responsiveness.
- Visual trajectory overlays needed stronger rendering contrast and scaling to become user-visible in real-world motion.

### 6.3 Current Model Runtime Status
From backend logs:
- YOLO: loaded
- MiDaS: loaded
- Risk MLP: loaded
- Scene classifier: loaded
- LSTM: pending custom weight file (`lstm_threat.pth`) unless provided

---

## 7. Conclusion

This project successfully delivers a complete AI/ML navigation-assistance prototype suitable for an ML course project demonstration. It combines multiple perception and prediction components into one end-to-end system with practical UX and deployment considerations.

The implementation demonstrates:
1. Multi-model inference integration.
2. Real-time API and frontend coordination.
3. Robust fallback engineering.
4. Meaningful visualization and testing workflow.

Overall, the project meets the academic goals of applying ML theory to a full-stack real-world use case.

---

## 8. Limitations

1. LSTM depends on trained custom weights to fully enable future-risk prediction quality.
2. Scene fallback model is generic; best accuracy requires custom fine-tuned scene weights.
3. Depth is monocular and relative (not guaranteed metric depth in all cases).
4. Current tracker is lightweight and may drift in dense scenes.
5. System uses development server; production serving stack not finalized yet.

---

## 9. Future Work

1. Train and integrate final LSTM model (`lstm_threat.pth`).
2. Fine-tune scene classifier with balanced custom dataset.
3. Add optional AdaBins depth branch and compare against MiDaS.
4. Upgrade object tracking (Kalman + appearance embeddings).
5. Add quantitative benchmarking (latency/FPS per module).
6. Deploy backend on HF Spaces and frontend on Vercel with final environment config.

---

## 10. Reproducibility / How to Run

### Backend
```bat
cd smarthelmet-nav
run_backend.bat
```

### Frontend
```bat
cd smarthelmet-nav
run_frontend.bat
```

### API Test
```bat
python test_backend.py
```

### Optional model repo auto-download
Set:
```text
SMARTHELMET_MODELS_REPO=<your_hf_repo_id>
```

---

## 11. References (Suggested)

1. Ultralytics YOLOv8 Documentation  
2. MiDaS / DPT (Intel) model card on Hugging Face  
3. PyTorch official documentation  
4. OpenCV optical flow references (Lucas-Kanade)  
5. OSRM routing API documentation  
6. Leaflet and React-Leaflet documentation  

---

## Appendix A: Training Guides Created in This Project

Available under `training-guides/`:
- `01_yolo_detector_training.md`
- `02_risk_scorer_mlp_training.md`
- `03_lstm_threat_training.md`
- `04_scene_classifier_training.md`

These include Colab-ready steps, sample dataset strategy, and output filenames for the `models/` folder.
