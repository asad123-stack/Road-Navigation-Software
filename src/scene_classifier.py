from __future__ import annotations

from typing import Dict

import cv2
import numpy as np

try:
    import torch
    from torchvision import models, transforms
except ModuleNotFoundError:
    torch = None
    models = None
    transforms = None

try:
    from transformers import AutoImageProcessor, AutoModelForImageClassification
except ModuleNotFoundError:
    AutoImageProcessor = None
    AutoModelForImageClassification = None

from src.model_hub import ensure_model_file
from src.model_paths import SCENE_WEIGHTS

SCENE_LABELS = ["tunnel", "urban", "open_road", "indoor"]


class SceneClassifier:
    def __init__(self) -> None:
        self._model = None
        self._transform = None
        self._model_loaded = False
        self._hf_processor = None
        self._hf_model = None
        self._load_model()

    def _load_model(self) -> None:
        if torch is None or models is None or transforms is None:
            self._load_hf_fallback()
            return

        scene_weight_path = ensure_model_file(SCENE_WEIGHTS.name)
        if scene_weight_path.exists():
            model = models.mobilenet_v2(weights=None)
            model.classifier[1] = torch.nn.Linear(1280, 4)
            try:
                state = torch.load(scene_weight_path, map_location="cpu")
                model.load_state_dict(state)
                model.eval()
                self._model = model
                self._transform = transforms.Compose(
                    [
                        transforms.ToPILImage(),
                        transforms.Resize((224, 224)),
                        transforms.ToTensor(),
                        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
                    ]
                )
                self._model_loaded = True
                return
            except (OSError, RuntimeError, ValueError):
                self._model = None
                self._transform = None
                self._model_loaded = False

        self._load_hf_fallback()

    def _load_hf_fallback(self) -> None:
        if AutoImageProcessor is None or AutoModelForImageClassification is None:
            return
        model_id = "google/mobilenet_v2_1.0_224"
        try:
            self._hf_processor = AutoImageProcessor.from_pretrained(model_id)
            self._hf_model = AutoModelForImageClassification.from_pretrained(model_id)
            self._hf_model.eval()
            self._model_loaded = True
        except (OSError, RuntimeError, ValueError):
            self._hf_processor = None
            self._hf_model = None
            self._model_loaded = False

    def is_model_loaded(self) -> bool:
        return self._model_loaded

    def classify(self, frame: np.ndarray) -> str:
        if self._model is not None and self._transform is not None and torch is not None:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            tensor = self._transform(rgb).unsqueeze(0)
            with torch.no_grad():
                logits = self._model(tensor)
                idx = int(torch.argmax(logits, dim=1).item())
            return SCENE_LABELS[idx]

        if self._hf_model is not None and self._hf_processor is not None and torch is not None:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            inputs = self._hf_processor(images=rgb, return_tensors="pt")
            with torch.no_grad():
                logits = self._hf_model(**inputs).logits
                idx = int(torch.argmax(logits, dim=-1).item())
            label = self._hf_model.config.id2label.get(idx, "").lower()
            return self._map_generic_label(label)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        brightness = float(hsv[..., 2].mean())
        saturation = float(hsv[..., 1].mean())
        if brightness < 65:
            return "tunnel"
        if brightness > 165 and saturation < 60:
            return "open_road"
        if saturation > 95:
            return "urban"
        return "indoor"

    def _map_generic_label(self, label: str) -> str:
        tunnel_k = ("tunnel", "subway", "cave")
        urban_k = ("street", "city", "building", "traffic", "car", "bus", "crosswalk")
        open_k = ("road", "highway", "mountain", "valley", "coast", "desert", "field")
        indoor_k = ("room", "kitchen", "office", "bedroom", "library", "classroom", "corridor", "hall")
        if any(k in label for k in tunnel_k):
            return "tunnel"
        if any(k in label for k in indoor_k):
            return "indoor"
        if any(k in label for k in open_k):
            return "open_road"
        if any(k in label for k in urban_k):
            return "urban"
        return "urban"

    def get_threshold_adjustments(self, scene: str) -> Dict[str, float]:
        table = {
            "open_road": {"center_slow_down": 0.75},
            "urban": {"center_slow_down": 0.60},
            "tunnel": {"center_slow_down": 0.45},
            "indoor": {"center_slow_down": 0.50},
        }
        return table.get(scene, table["urban"])
