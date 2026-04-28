from __future__ import annotations

from typing import Dict, List, Tuple
import numpy as np


class KalmanFilter1D:
    """1D Kalman Filter for trajectory smoothing."""
    
    def __init__(self, process_variance: float = 0.01, measurement_variance: float = 4.0):
        """
        Initialize Kalman filter for 1D position tracking.
        
        Args:
            process_variance: How much the process varies (lower = smoother)
            measurement_variance: How much to trust measurements (lower = trust more)
        """
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.estimate = 0.0
        self.estimate_error = 1.0
        self.kalman_gain = 0.0
        self._initialized = False
        
    def update(self, measurement: float) -> float:
        """Update filter with new measurement and return smoothed estimate."""
        # On first measurement, just use it directly
        if not self._initialized:
            self.estimate = measurement
            self._initialized = True
            return self.estimate
        
        # Prediction step
        prior_estimate = self.estimate
        prior_error = self.estimate_error + self.process_variance
        
        # Update step (Kalman gain)
        self.kalman_gain = prior_error / (prior_error + self.measurement_variance)
        
        # Update estimate: blend prior prediction with measurement
        self.estimate = prior_estimate + self.kalman_gain * (measurement - prior_estimate)
        
        # Update error estimate
        self.estimate_error = (1.0 - self.kalman_gain) * prior_error
        
        return self.estimate


class ObjectTrack:
    """Single object track with Kalman filtering."""
    
    def __init__(self, track_id: int, label: str, cx: float, cy: float):
        self.id = track_id
        self.label = label
        self.measured_points: List[List[float]] = [[cx, cy]]
        self.smoothed_points: List[List[float]] = [[cx, cy]]
        self.kalman_x = KalmanFilter1D(process_variance=0.01, measurement_variance=4.0)
        self.kalman_y = KalmanFilter1D(process_variance=0.01, measurement_variance=4.0)
        
        # Initialize with first measurement
        self.kalman_x.estimate = cx
        self.kalman_y.estimate = cy
        self.age = 1
        self.consecutive_misses = 0
        self._max_history = 20

    def update(self, cx: float, cy: float) -> None:
        """Update track with new measurement and apply Kalman smoothing."""
        self.measured_points.append([cx, cy])
        if len(self.measured_points) > self._max_history:
            del self.measured_points[0]
        
        # Apply Kalman filter
        smoothed_x = self.kalman_x.update(cx)
        smoothed_y = self.kalman_y.update(cy)
        
        self.smoothed_points.append([smoothed_x, smoothed_y])
        if len(self.smoothed_points) > self._max_history:
            del self.smoothed_points[0]
        
        self.age += 1
        self.consecutive_misses = 0

    def predict_next_position(self) -> Tuple[float, float]:
        """Predict next position based on velocity."""
        if len(self.smoothed_points) < 2:
            return self.smoothed_points[-1][0], self.smoothed_points[-1][1]
        
        # Estimate velocity from last 3 frames
        recent = self.smoothed_points[-3:]
        vx = (recent[-1][0] - recent[0][0]) / (len(recent) - 1)
        vy = (recent[-1][1] - recent[0][1]) / (len(recent) - 1)
        
        # Predict next position
        px = recent[-1][0] + vx
        py = recent[-1][1] + vy
        
        return px, py

    def miss(self) -> None:
        """Mark that this track was not matched in current frame."""
        self.consecutive_misses += 1

    def get_trajectory(self) -> List[List[float]]:
        """Return smoothed trajectory."""
        return self.smoothed_points[:]


class ObjectTracker:
    def __init__(self) -> None:
        self.tracks: List[dict] = []
        self._next_id = 1
        self._active_tracks: Dict[int, ObjectTrack] = {}
        self._match_distance = 100
        self._max_consecutive_misses = 3

    def update(self, detections: List[dict]) -> List[dict]:
        """Update tracker with new detections."""
        centers: List[Tuple[str, float, float, int]] = []
        for i, det in enumerate(detections):
            x1, y1, x2, y2 = det["bbox"]
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0
            centers.append((det["label"], cx, cy, i))

        # Match detections to existing tracks
        matched_tracks = set()
        matched_detections = set()
        
        for track_id, track in list(self._active_tracks.items()):
            best_det_idx = None
            best_dist = float("inf")
            
            for label, cx, cy, det_idx in centers:
                if det_idx in matched_detections:
                    continue
                if track.label != label:
                    continue
                
                # Use predicted position for matching
                pred_x, pred_y = track.predict_next_position()
                dist = ((cx - pred_x) ** 2 + (cy - pred_y) ** 2) ** 0.5
                
                if dist < best_dist and dist <= self._match_distance:
                    best_dist = dist
                    best_det_idx = det_idx
            
            if best_det_idx is not None:
                # Matched: update track
                label, cx, cy, _ = centers[best_det_idx]
                track.update(cx, cy)
                matched_tracks.add(track_id)
                matched_detections.add(best_det_idx)
            else:
                # Not matched: increment misses
                track.miss()

        # Remove stale tracks
        stale_ids = [
            tid for tid, track in self._active_tracks.items()
            if track.consecutive_misses > self._max_consecutive_misses
        ]
        for tid in stale_ids:
            del self._active_tracks[tid]

        # Create new tracks for unmatched detections
        for label, cx, cy, det_idx in centers:
            if det_idx not in matched_detections:
                track_id = self._next_id
                self._next_id += 1
                self._active_tracks[track_id] = ObjectTrack(track_id, label, cx, cy)
                matched_tracks.add(track_id)

        # Build output
        updated: List[dict] = []
        for track_id in matched_tracks:
            if track_id in self._active_tracks:
                track = self._active_tracks[track_id]
                updated.append({
                    "id": track_id,
                    "label": track.label,
                    "predicted_path": track.get_trajectory(),
                    "age": track.age
                })

        self.tracks = updated
        return self.tracks
