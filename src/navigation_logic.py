from __future__ import annotations

from typing import Dict, List

def get_navigation_cue(detections: List[dict], zone_depths: Dict[str, float], risk_score: int, scene_type: str = "urban") -> Dict[str, object]:
    threshold_table = {
        "open_road": {"center_slow_down": 0.75},
        "urban": {"center_slow_down": 0.60},
        "tunnel": {"center_slow_down": 0.45},
        "indoor": {"center_slow_down": 0.50},
    }
    thresholds = threshold_table.get(scene_type, threshold_table["urban"])
    center_threshold = thresholds["center_slow_down"]
    center_depth = zone_depths["center"]

    if risk_score >= 75:
        return {"cue": "OBSTACLE AHEAD", "confidence": 92, "color": "#ef4444", "risk_score": risk_score}
    if center_depth < center_threshold:
        return {"cue": "SLOW DOWN", "confidence": 84, "color": "#f97316", "risk_score": risk_score}
    if detections and zone_depths["left"] > zone_depths["right"] + 0.08:
        return {"cue": "TURN LEFT", "confidence": 76, "color": "#38bdf8", "risk_score": risk_score}
    if detections and zone_depths["right"] > zone_depths["left"] + 0.08:
        return {"cue": "TURN RIGHT", "confidence": 76, "color": "#38bdf8", "risk_score": risk_score}
    return {"cue": "GO STRAIGHT", "confidence": 70, "color": "#22c55e", "risk_score": risk_score}
