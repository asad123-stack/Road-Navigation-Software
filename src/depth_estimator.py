from __future__ import annotations

from typing import Dict, Tuple

import cv2
import numpy as np

try:
    import torch
    import torch.nn.functional as F
    from transformers import DPTForDepthEstimation, DPTImageProcessor
except ModuleNotFoundError:
    torch = None
    F = None
    DPTForDepthEstimation = None
    DPTImageProcessor = None


class DepthEstimator:
    def __init__(self) -> None:
        self._processor = None
        self._model = None
        self._model_loaded = False
        self._load_model()

    def _load_model(self) -> None:
        if torch is None or DPTForDepthEstimation is None or DPTImageProcessor is None:
            return
        model_id = "Intel/dpt-hybrid-midas"
        try:
            self._processor = DPTImageProcessor.from_pretrained(model_id)
            self._model = DPTForDepthEstimation.from_pretrained(model_id)
            self._model.eval()
            self._model_loaded = True
        except (OSError, ValueError, RuntimeError, ConnectionError):
            self._processor = None
            self._model = None
            self._model_loaded = False

    def is_model_loaded(self) -> bool:
        return self._model_loaded

    def resize_for_pipeline(self, frame: np.ndarray) -> np.ndarray:
        return cv2.resize(frame, (640, 480))

    def estimate(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict[str, float]]:
        if self._model is not None and self._processor is not None and torch is not None and F is not None:
            return self._estimate_with_midas(frame)
        return self._estimate_fallback(frame)

    def _estimate_with_midas(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict[str, float]]:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        inputs = self._processor(images=rgb, return_tensors="pt")
        with torch.no_grad():
            outputs = self._model(**inputs)
            prediction = outputs.predicted_depth
            prediction = F.interpolate(
                prediction.unsqueeze(1),
                size=frame.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze(1)

        inv_depth = prediction.squeeze(0).cpu().numpy().astype(np.float32)
        min_v = float(inv_depth.min())
        max_v = float(inv_depth.max())
        if max_v - min_v <= 1e-6:
            clearance = np.zeros_like(inv_depth, dtype=np.float32)
        else:
            inv_norm = (inv_depth - min_v) / (max_v - min_v)
            clearance = 1.0 - inv_norm

        return clearance, self._zone_depths(clearance)

    def _estimate_fallback(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict[str, float]]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        clearance = gray
        return clearance, self._zone_depths(clearance)

    def _zone_depths(self, depth_map: np.ndarray) -> Dict[str, float]:
        h, w = depth_map.shape
        left = float(depth_map[:, : w // 3].mean())
        center = float(depth_map[:, w // 3 : 2 * w // 3].mean())
        right = float(depth_map[:, 2 * w // 3 :].mean())
        return {"left": round(left, 3), "center": round(center, 3), "right": round(right, 3)}
