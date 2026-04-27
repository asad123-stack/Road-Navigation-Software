from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = REPO_ROOT / "models"

YOLO_WEIGHTS = MODELS_DIR / "yolov8n.pt"
RISK_MODEL_WEIGHTS = MODELS_DIR / "risk_scorer.pth"
RISK_SCALER_FILE = MODELS_DIR / "risk_scaler.npz"
LSTM_WEIGHTS = MODELS_DIR / "lstm_threat.pth"
SCENE_WEIGHTS = MODELS_DIR / "scene_classifier.pth"
