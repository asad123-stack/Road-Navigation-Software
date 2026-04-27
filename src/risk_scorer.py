from __future__ import annotations

from typing import Dict, List

import numpy as np
try:
    import torch
    from torch import nn
except ModuleNotFoundError:
    torch = None
    nn = object

from src.model_paths import RISK_MODEL_WEIGHTS, RISK_SCALER_FILE
from src.model_hub import ensure_model_file


if torch is not None:
    class _RiskMLP(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(3, 16),
                nn.ReLU(),
                nn.Linear(16, 8),
                nn.ReLU(),
                nn.Linear(8, 1),
                nn.Sigmoid(),
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.net(x)


class RiskScorer:
    def __init__(self) -> None:
        self._model = None
        self._model_loaded = False
        self._scaler_min = None
        self._scaler_max = None
        self._load_scaler()
        self._load_model()

    def is_model_loaded(self) -> bool:
        return self._model_loaded

    def _load_scaler(self) -> None:
        scaler_path = ensure_model_file(RISK_SCALER_FILE.name)
        if not scaler_path.exists():
            return
        data = np.load(scaler_path)
        if "data_min_" in data and "data_max_" in data:
            self._scaler_min = data["data_min_"].astype(np.float32)
            self._scaler_max = data["data_max_"].astype(np.float32)

    def _load_model(self) -> None:
        weight_path = ensure_model_file(RISK_MODEL_WEIGHTS.name)
        if not weight_path.exists():
            return
        if torch is None:
            return
        model = _RiskMLP()
        try:
            state = torch.load(weight_path, map_location="cpu")
            model.load_state_dict(state)
            model.eval()
            self._model = model
            self._model_loaded = True
        except (OSError, RuntimeError, ValueError):
            self._model = None
            self._model_loaded = False

    def _feature_vector(self, detections: List[dict], zone_depths: Dict[str, float]) -> np.ndarray:
        num_objects = float(len(detections))
        center_depth = float(zone_depths["center"])
        min_zone_depth = float(min(zone_depths["left"], zone_depths["center"], zone_depths["right"]))
        return np.array([num_objects, center_depth, min_zone_depth], dtype=np.float32)

    def _scale(self, feats: np.ndarray) -> np.ndarray:
        if self._scaler_min is None or self._scaler_max is None:
            return feats
        denom = np.maximum(self._scaler_max - self._scaler_min, 1e-6)
        return (feats - self._scaler_min) / denom

    def score(self, detections: List[dict], zone_depths: Dict[str, float]) -> int:
        if self._model is not None and torch is not None:
            feats = self._feature_vector(detections, zone_depths)
            scaled = self._scale(feats)
            tensor = torch.tensor(scaled, dtype=torch.float32).unsqueeze(0)
            pred = float(self._model(tensor).item())
            return int(max(0, min(100, round(pred * 100))))

        obj_term = min(len(detections) * 18, 55)
        center_threat = int((1.0 - zone_depths["center"]) * 45)
        score = max(0, min(100, obj_term + center_threat))
        return int(score)
