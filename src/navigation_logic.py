from __future__ import annotations

from typing import Dict, List

def get_distance_to_next_turn(user_lat: float, user_lng: float, route_steps: List[dict]) -> Dict:
    """
    Calculate distance to next turn using route data.
    Returns distance and turn direction.
    """
    if not route_steps or len(route_steps) == 0:
        return {"distance": None, "direction": None}
    
    try:
        next_step = route_steps[0]
        distance = next_step.get("distance", 0)
        maneuver = next_step.get("maneuver", {})
        turn_type = maneuver.get("type", "straight")
        direction = maneuver.get("modifier", "")
        
        return {
            "distance": round(distance),
            "direction": direction,
            "type": turn_type,
            "instruction": f"{turn_type.upper()} {direction}".strip()
        }
    except:
        return {"distance": None, "direction": None}

def get_navigation_cue(
    detections: List[dict], 
    zone_depths: Dict[str, float], 
    risk_score: int, 
    scene_type: str = "urban",
    user_lat: float = None,
    user_lng: float = None,
    route_steps: List[dict] = None,
    lstm_risk: float = None
) -> Dict[str, object]:
    
    threshold_table = {
        "open_road": {"center_slow_down": 0.75},
        "urban": {"center_slow_down": 0.60},
        "tunnel": {"center_slow_down": 0.45},
        "indoor": {"center_slow_down": 0.50},
    }
    
    thresholds = threshold_table.get(scene_type, threshold_table["urban"])
    center_threshold = thresholds["center_slow_down"]
    center_depth = zone_depths["center"]
    
    # Direction mapping
    direction_arrows = {
        "left": "↙",
        "right": "↘",
        "straight": "↑",
        "sharp left": "⬅️",
        "sharp right": "➡️",
        "slight left": "↖️",
        "slight right": "↗️",
    }
    
    # Get route-based prediction
    route_info = get_distance_to_next_turn(user_lat, user_lng, route_steps or [])
    next_turn_distance = route_info.get("distance")
    next_turn_direction = route_info.get("direction", "")
    
    # Determine primary cue
    secondary_alerts = []
    
    if risk_score >= 75:
        primary_cue = "OBSTACLE AHEAD"
        color = "#ef4444"
        icon = "⚠️"
        confidence = 92
    elif lstm_risk and lstm_risk > 0.7:
        primary_cue = "DANGER PREDICTED"
        color = "#f97316"
        icon = "🚨"
        confidence = 88
        if center_depth < center_threshold:
            secondary_alerts.append({
                "cue": "SLOW DOWN",
                "confidence": 84,
                "color": "#f97316",
                "reason": "Close obstacle"
            })
    elif center_depth < center_threshold:
        primary_cue = "SLOW DOWN"
        color = "#f97316"
        icon = "🛑"
        confidence = 84
    elif next_turn_distance and next_turn_distance < 200:
        # Route-based turn prediction
        arrow = direction_arrows.get(next_turn_direction.lower(), "↑")
        primary_cue = f"TURN {next_turn_direction.upper()} in {next_turn_distance}m"
        color = "#38bdf8"
        icon = arrow
        confidence = 82
    elif detections and zone_depths["left"] > zone_depths["right"] + 0.08:
        primary_cue = "TURN LEFT"
        color = "#38bdf8"
        icon = "↙"
        confidence = 76
    elif detections and zone_depths["right"] > zone_depths["left"] + 0.08:
        primary_cue = "TURN RIGHT"
        color = "#38bdf8"
        icon = "↘"
        confidence = 76
    else:
        primary_cue = "GO STRAIGHT"
        color = "#22c55e"
        icon = "↑"
        confidence = 70
    
    # Add secondary alerts if risk is moderate
    if risk_score >= 50 and "OBSTACLE" not in primary_cue:
        secondary_alerts.append({
            "cue": "HIGH RISK",
            "confidence": risk_score,
            "color": "#f97316",
            "reason": f"Risk score: {risk_score}"
        })
    
    return {
        "cue": primary_cue,
        "icon": icon,
        "confidence": confidence,
        "color": color,
        "risk_score": risk_score,
        "secondary_alerts": secondary_alerts,
        "next_turn_distance": next_turn_distance,
        "lstm_warning": lstm_risk > 0.6 if lstm_risk else False
    }
