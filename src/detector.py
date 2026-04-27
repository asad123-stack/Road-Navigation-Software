from __future__ import annotations

from typing import List

import numpy as np
try:
    from ultralytics import YOLO
except ModuleNotFoundError:
    YOLO = None

from src.model_paths import YOLO_WEIGHTS


class ObjectDetector:
    def __init__(self) -> None:
        self._model = None
        self._model_loaded = False
        if YOLO is not None:
            self._try_load(str(YOLO_WEIGHTS))
            if self._model is None:
                # Ultralytics will auto-download pretrained weights if not cached.
                self._try_load("yolov8n.pt")

    def is_model_loaded(self) -> bool:
        return self._model_loaded

    def _try_load(self, source: str) -> None:
        try:
            self._model = YOLO(source)
            self._model_loaded = True
        except (FileNotFoundError, OSError, RuntimeError, ValueError):
            self._model = None
            self._model_loaded = False

    def detect(self, frame: np.ndarray) -> List[dict]:
        if self._model is not None:
            return self._detect_with_yolo(frame)
        return self._detect_heuristic(frame)

    def _detect_with_yolo(self, frame: np.ndarray) -> List[dict]:
        results = self._model.predict(frame, verbose=False, conf=0.35)
        if not results:
            return []
        names = results[0].names
        detections: List[dict] = []
        for box in results[0].boxes:
            conf = float(box.conf.item())
            cls_id = int(box.cls.item())
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
            label = str(names.get(cls_id, "object")) if isinstance(names, dict) else str(names[cls_id])
            detections.append(
                {
                    "label": label,
                    "confidence": round(conf, 4),
                    "bbox": [x1, y1, x2, y2],
                }
            )
        return detections

    def _detect_heuristic(self, frame: np.ndarray) -> List[dict]:
        h, w = frame.shape[:2]
        mean_brightness = float(frame.mean())
        detections: List[dict] = []

        if mean_brightness < 90:
            detections.append(
                {
                    "label": "obstacle",
                    "confidence": 0.62,
                    "bbox": [int(w * 0.35), int(h * 0.35), int(w * 0.65), int(h * 0.85)],
                }
            )
        if mean_brightness > 150:
            detections.append(
                {
                    "label": "person",
                    "confidence": 0.58,
                    "bbox": [int(w * 0.2), int(h * 0.25), int(w * 0.45), int(h * 0.9)],
                }
            )
        return detections
