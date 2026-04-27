from __future__ import annotations

from collections import deque
from typing import Deque, Optional, Tuple

import numpy as np

try:
    import torch
    from torch import nn
except ModuleNotFoundError:
    torch = None
    nn = object

from src.model_paths import LSTM_WEIGHTS
from src.model_hub import ensure_model_file


if torch is not None:
    class _ThreatLSTM(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.lstm = nn.LSTM(input_size=3, hidden_size=32, num_layers=2, batch_first=True, dropout=0.1)
            self.fc = nn.Linear(32, 1)
            self.out = nn.Sigmoid()

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            seq_out, _ = self.lstm(x)
            last = seq_out[:, -1, :]
            return self.out(self.fc(last))


class LSTMPredictor:
    def __init__(self) -> None:
        self.buffer: Deque[Tuple[float, float, float]] = deque(maxlen=10)
        self._last_pred: Optional[float] = None
        self._model = None
        self._model_loaded = False
        self._load_model()

    def _load_model(self) -> None:
        weight_path = ensure_model_file(LSTM_WEIGHTS.name)
        if torch is None or not weight_path.exists():
            return
        model = _ThreatLSTM()
        try:
            state = torch.load(weight_path, map_location="cpu")
            model.load_state_dict(state)
            model.eval()
            self._model = model
            self._model_loaded = True
        except (OSError, RuntimeError, ValueError):
            self._model = None
            self._model_loaded = False

    def is_model_loaded(self) -> bool:
        return self._model_loaded

    def update(self, risk_score: float, num_objects: float, center_depth: float) -> None:
        self.buffer.append((float(risk_score), float(num_objects), float(center_depth)))

    def predict(self) -> Optional[float]:
        if len(self.buffer) < 10:
            self._last_pred = None
            return None

        if self._model is not None and torch is not None:
            arr = np.array(self.buffer, dtype=np.float32)
            arr[:, 0] = arr[:, 0] / 100.0
            tensor = torch.tensor(arr, dtype=torch.float32).unsqueeze(0)
            pred = float(self._model(tensor).item()) * 100.0
            self._last_pred = round(max(0.0, min(100.0, pred)), 2)
            return self._last_pred

        values = [v[0] for v in self.buffer]
        trend = values[-1] - values[0]
        weighted = sum(v * (i + 1) for i, v in enumerate(values)) / sum(range(1, 11))
        pred = max(0.0, min(100.0, weighted + 0.25 * trend))
        self._last_pred = round(pred, 2)
        return self._last_pred

    def get_alert(self) -> bool:
        return bool(self._last_pred is not None and self._last_pred > 70)
