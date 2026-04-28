from __future__ import annotations

from typing import Dict, Tuple

import cv2
import numpy as np

try:
    import torch
    import torch.nn.functional as F
    from transformers import DPTForDepthEstimation, DPTImageProcessor, AutoImageProcessor, AutoModelForDepthEstimation
except ModuleNotFoundError:
    torch = None
    F = None
    DPTForDepthEstimation = None
    DPTImageProcessor = None
    AutoImageProcessor = None
    AutoModelForDepthEstimation = None


class DepthEstimator:
    def __init__(self) -> None:
        self._processor_midas = None
        self._model_midas = None
        self._model_midas_loaded = False
        
        self._processor_adabins = None
        self._model_adabins = None
        self._model_adabins_loaded = False
        
        self._last_midas_depth = None
        self._frame_counter = 0
        
        self._load_midas()
        self._load_adabins()

    def _load_midas(self) -> None:
        if torch is None or DPTForDepthEstimation is None or DPTImageProcessor is None:
            return
        model_id = "Intel/dpt-hybrid-midas"
        try:
            self._processor_midas = DPTImageProcessor.from_pretrained(model_id)
            self._model_midas = DPTForDepthEstimation.from_pretrained(model_id)
            self._model_midas.eval()
            self._model_midas_loaded = True
        except (OSError, ValueError, RuntimeError, ConnectionError):
            self._processor_midas = None
            self._model_midas = None
            self._model_midas_loaded = False

    def _load_adabins(self) -> None:
        if torch is None or AutoModelForDepthEstimation is None or AutoImageProcessor is None:
            return
        model_id = "vinvino02/AdaBins"
        try:
            self._processor_adabins = AutoImageProcessor.from_pretrained(model_id)
            self._model_adabins = AutoModelForDepthEstimation.from_pretrained(model_id)
            self._model_adabins.eval()
            self._model_adabins_loaded = True
        except (OSError, ValueError, RuntimeError, ConnectionError):
            self._processor_adabins = None
            self._model_adabins = None
            self._model_adabins_loaded = False

    def is_model_loaded(self) -> bool:
        return self._model_midas_loaded or self._model_adabins_loaded

    def is_adabins_loaded(self) -> bool:
        return self._model_adabins_loaded

    def resize_for_pipeline(self, frame: np.ndarray) -> np.ndarray:
        return cv2.resize(frame, (640, 480))

    def estimate(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict[str, float]]:
        self._frame_counter += 1
        
        midas_depth = None
        adabins_depth = None
        use_midas = (self._frame_counter % 3 == 0)
        
        if use_midas and self._model_midas is not None and self._processor_midas is not None and torch is not None and F is not None:
            midas_depth, _ = self._estimate_with_midas(frame)
            self._last_midas_depth = midas_depth
        elif self._last_midas_depth is not None:
            midas_depth = self._last_midas_depth
        
        if self._model_adabins is not None and self._processor_adabins is not None and torch is not None:
            adabins_depth, _ = self._estimate_with_adabins(frame)
        
        if midas_depth is not None and adabins_depth is not None:
            blended = self._blend_depths(midas_depth, adabins_depth)
            return blended, self._zone_depths(blended)
        elif midas_depth is not None:
            return midas_depth, self._zone_depths(midas_depth)
        elif adabins_depth is not None:
            return adabins_depth, self._zone_depths(adabins_depth)
        else:
            return self._estimate_fallback(frame)

    def _estimate_with_midas(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict[str, float]]:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        inputs = self._processor_midas(images=rgb, return_tensors="pt")
        with torch.no_grad():
            outputs = self._model_midas(**inputs)
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

    def _estimate_with_adabins(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict[str, float]]:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        inputs = self._processor_adabins(images=rgb, return_tensors="pt")
        with torch.no_grad():
            outputs = self._model_adabins(**inputs)
            predicted_depth = outputs.predicted_depth
            
            depth_map = F.interpolate(
                predicted_depth.unsqueeze(1),
                size=frame.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze(1)

        depth_np = depth_map.squeeze(0).cpu().numpy().astype(np.float32)
        
        min_v = float(depth_np.min())
        max_v = float(depth_np.max())
        if max_v - min_v <= 1e-6:
            clearance = np.zeros_like(depth_np, dtype=np.float32)
        else:
            depth_norm = (depth_np - min_v) / (max_v - min_v)
            clearance = depth_norm

        return clearance, self._zone_depths(clearance)

    def _blend_depths(self, midas_depth: np.ndarray, adabins_depth: np.ndarray, midas_weight: float = 0.6) -> np.ndarray:
        """
        Blend MiDaS (accurate, slower) with AdaBins (faster, every frame).
        MiDaS given higher weight due to better accuracy.
        """
        adabins_weight = 1.0 - midas_weight
        blended = midas_weight * midas_depth + adabins_weight * adabins_depth
        
        min_v = float(blended.min())
        max_v = float(blended.max())
        if max_v - min_v <= 1e-6:
            return np.zeros_like(blended, dtype=np.float32)
        
        normalized = (blended - min_v) / (max_v - min_v)
        return normalized.astype(np.float32)

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
