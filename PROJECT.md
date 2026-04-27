# SmartHelmet Nav v2.0 (Kickoff Scaffold)

This is the initial working scaffold for the SmartHelmet Nav v2.0 guide.

## What is already set up
- Flask backend with:
  - `GET /health`
  - `POST /api/process_frame` returning the full v2.0 response schema
- `src/` modules for detector, depth, risk, cue logic, scene classification, LSTM risk, visual odometry, tracking, and visualization
- React + Vite frontend shell with:
  - map-oriented state
  - API client contract
  - all guide-listed components as placeholders
- Windows run scripts (`run_backend.bat`, `run_frontend.bat`, `run_all.bat`)

## Run backend
```bat
cd smarthelmet-nav
run_backend.bat
```

## Run frontend
```bat
cd smarthelmet-nav
run_frontend.bat
```

## Quick API test
1. Start backend (`python app.py`).
2. Run:
```bat
python test_backend.py
```

## Next implementation pass
- Replace placeholder ML logic with real YOLO/MiDaS/MLP/LSTM/MobileNet models.
- Implement full phone camera snapshot loop (`getUserMedia`) and real Leaflet routing + segment coloring.

## Model files for upgraded inference
Place trained weights in `smarthelmet-nav\models\`:
- `yolov8n.pt`
- `risk_scorer.pth`
- `risk_scaler.npz`
- `lstm_threat.pth`
- `scene_classifier.pth`

YOLO now auto-loads in this order:
1. `models\yolov8n.pt` (your custom/fine-tuned weight),
2. fallback to pretrained `yolov8n.pt` auto-download via Ultralytics.

Depth now uses Hugging Face MiDaS (`Intel/dpt-hybrid-midas`) and downloads on first run.

Other model loading:
- `risk_scorer.pth`, `risk_scaler.npz`, `lstm_threat.pth`, `scene_classifier.pth` load from local `models\`.
- If not local, they can auto-download from a Hugging Face repo by setting:
  - `SMARTHELMET_MODELS_REPO=<your_hf_repo_id>`
- Scene classifier also has a Hugging Face generic fallback (`google/mobilenet_v2_1.0_224`) when custom scene weights are absent.

If files/models are missing, the backend still preserves API shape with fallback inference logic.
