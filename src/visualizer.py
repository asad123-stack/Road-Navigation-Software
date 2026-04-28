from __future__ import annotations

import base64

import cv2
import numpy as np


def _draw_object_trajectories(canvas: np.ndarray, trajectories: list) -> None:
    for tr in trajectories:
        pts = tr.get("predicted_path", [])
        if len(pts) < 2:
            if len(pts) == 1:
                x, y = pts[0]
                cv2.circle(canvas, (int(x), int(y)), 4, (0, 255, 255), -1)
            continue
        arr = np.array(pts, dtype=np.int32).reshape((-1, 1, 2))
        cv2.polylines(canvas, [arr], isClosed=False, color=(0, 255, 255), thickness=3)
        end_x, end_y = pts[-1]
        cv2.putText(
            canvas,
            f"ID {tr.get('id', '?')}",
            (int(end_x) + 4, int(end_y) - 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 255, 255),
            1,
        )


def _draw_odometry(canvas: np.ndarray, odometry_trajectory: list, feature_quality: list = None, motion_magnitude: list = None) -> None:
    if len(odometry_trajectory) < 1:
        return
    h, w = canvas.shape[:2]
    panel_w, panel_h = 300, 200
    panel_x, panel_y = 8, h - panel_h - 8
    
    cv2.rectangle(canvas, (panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h), (20, 20, 20), -1)
    cv2.rectangle(canvas, (panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h), (210, 80, 230), 2)

    points = []
    xs = [float(p[0]) for p in odometry_trajectory]
    ys = [float(p[1]) for p in odometry_trajectory]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(max_x - min_x, 1e-3)
    span_y = max(max_y - min_y, 1e-3)

    for i, (x, y) in enumerate(odometry_trajectory):
        nx = (x - min_x) / span_x
        ny = (y - min_y) / span_y
        px = int(panel_x + 12 + nx * (panel_w - 24))
        py = int(panel_y + panel_h - 12 - ny * (panel_h - 24))
        points.append([px, py])

    if len(points) >= 2:
        for i in range(len(points) - 1):
            age = i / max(len(points), 1)
            brightness = int(50 + age * 200)
            color_intensity = int(100 + age * 155)
            color = (brightness, 80, color_intensity)
            
            cv2.line(canvas, tuple(points[i]), tuple(points[i + 1]), color, 2)
    
    cv2.circle(canvas, tuple(points[-1]), 6, (255, 255, 255), -1)
    
    avg_quality = int(np.mean(feature_quality[-50:])) if feature_quality and len(feature_quality) > 0 else 0
    avg_speed = float(np.mean(motion_magnitude[-50:])) if motion_magnitude and len(motion_magnitude) > 0 else 0.0
    
    cv2.putText(canvas, "ODOM PATH", (panel_x + 8, panel_y + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (230, 180, 255), 1)
    cv2.putText(canvas, f"Quality: {avg_quality}%", (panel_x + 8, panel_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 200, 255), 1)
    cv2.putText(canvas, f"Speed: {avg_speed:.2f}px/f", (panel_x + 8, panel_y + 58), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 200, 255), 1)
    cv2.putText(canvas, f"X: {xs[-1]:.1f} Y: {ys[-1]:.1f}", (panel_x + 8, panel_y + 76), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)
    
    confidence_color = (0, 255, 0) if avg_quality > 50 else (0, 165, 255) if avg_quality > 25 else (0, 0, 255)
    cv2.circle(canvas, (panel_x + panel_w - 12, panel_y + 12), 5, confidence_color, -1)



def _draw_motion_vector(canvas: np.ndarray, motion_vector: dict) -> None:
    dx = float(motion_vector.get("dx", 0.0))
    dy = float(motion_vector.get("dy", 0.0))
    mag = (dx * dx + dy * dy) ** 0.5
    if mag < 0.25:
        return
    h, w = canvas.shape[:2]
    start = (w // 2, h // 2)
    scale = 8.0
    end = (int(start[0] + dx * scale), int(start[1] + dy * scale))
    cv2.arrowedLine(canvas, start, end, (255, 255, 255), 2, tipLength=0.25)
    cv2.putText(canvas, f"d=({dx:.2f},{dy:.2f})", (start[0] + 10, start[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)


def render_annotations(
    frame: np.ndarray,
    detections: list,
    cue: dict,
    risk_score: int,
    trajectories: list,
    odometry_trajectory: list,
    motion_vector: dict,
    feature_quality: list = None,
    motion_magnitude: list = None,
) -> np.ndarray:
    canvas = frame.copy()
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 0, 255), 2)
        label = f"{det['label']} {det['confidence']:.2f}"
        cv2.putText(canvas, label, (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    _draw_object_trajectories(canvas, trajectories)
    _draw_odometry(canvas, odometry_trajectory, feature_quality, motion_magnitude)
    _draw_motion_vector(canvas, motion_vector)

    cue_text = cue["cue"] if isinstance(cue, dict) else str(cue)
    cv2.putText(canvas, cue_text, (14, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (50, 220, 50), 2)
    cv2.putText(canvas, f"Risk: {risk_score}", (14, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 180, 255), 2)
    return canvas


def encode_frame_to_data_url(frame: np.ndarray) -> str:
    ok, jpg = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 65])
    if not ok:
        raise ValueError("Failed to encode frame")
    encoded = base64.b64encode(jpg.tobytes()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"
