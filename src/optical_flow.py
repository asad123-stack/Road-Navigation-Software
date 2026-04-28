from __future__ import annotations

from typing import List, Tuple

import cv2
import numpy as np


class KalmanMotionFilter:
    """Smooths motion vectors using Kalman filtering."""
    
    def __init__(self, process_variance=0.01, measurement_variance=0.1):
        self.dt = 1.0
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        
        self.kf_x = cv2.KalmanFilter(2, 1)
        self.kf_y = cv2.KalmanFilter(2, 1)
        
        for kf in [self.kf_x, self.kf_y]:
            kf.measurementMatrix = np.array([[1, 0]], dtype=np.float32)
            kf.transitionMatrix = np.array([[1, self.dt], [0, 1]], dtype=np.float32)
            kf.processNoiseCov = np.eye(2, dtype=np.float32) * process_variance
            kf.measurementNoiseCov = np.array([[measurement_variance]], dtype=np.float32)
            kf.statePost = np.zeros((2, 1), dtype=np.float32)
    
    def filter(self, dx: float, dy: float) -> Tuple[float, float]:
        """Apply Kalman filtering to motion vector."""
        self.kf_x.predict()
        self.kf_y.predict()
        
        measurement_x = np.array([[dx]], dtype=np.float32)
        measurement_y = np.array([[dy]], dtype=np.float32)
        
        self.kf_x.correct(measurement_x)
        self.kf_y.correct(measurement_y)
        
        smoothed_dx = float(self.kf_x.statePost[0, 0])
        smoothed_dy = float(self.kf_y.statePost[0, 0])
        
        return smoothed_dx, smoothed_dy


class VisualOdometry:
    def __init__(self) -> None:
        self.prev_gray = None
        self.prev_pts = None
        self.x = 0.0
        self.y = 0.0
        self.trajectory: List[List[float]] = [[0.0, 0.0]]
        self.feature_quality: List[int] = [100]
        self.motion_magnitude: List[float] = [0.0]
        
        self.feature_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)
        self.lk_params = dict(
            winSize=(15, 15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03),
        )
        
        self.kalman = KalmanMotionFilter(process_variance=0.01, measurement_variance=0.15)

    def update(self, frame: np.ndarray) -> Tuple[float, float, float, float]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.prev_gray is None:
            self.prev_gray = gray
            self.prev_pts = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
            return 0.0, 0.0, self.x, self.y

        if self.prev_pts is None or len(self.prev_pts) < 5:
            self.prev_pts = cv2.goodFeaturesToTrack(self.prev_gray, mask=None, **self.feature_params)
            self.prev_gray = gray
            return 0.0, 0.0, self.x, self.y

        next_pts, status, _ = cv2.calcOpticalFlowPyrLK(self.prev_gray, gray, self.prev_pts, None, **self.lk_params)
        if next_pts is None or status is None:
            self.prev_gray = gray
            self.prev_pts = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
            return 0.0, 0.0, self.x, self.y

        valid = status.flatten() == 1
        good_old = self.prev_pts[valid]
        good_new = next_pts[valid]
        if len(good_old) == 0 or len(good_new) == 0:
            self.prev_gray = gray
            self.prev_pts = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
            return 0.0, 0.0, self.x, self.y

        old_xy = good_old.reshape(-1, 2)
        new_xy = good_new.reshape(-1, 2)
        if old_xy.shape[0] == 0 or new_xy.shape[0] == 0:
            self.prev_gray = gray
            self.prev_pts = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
            return 0.0, 0.0, self.x, self.y

        delta = new_xy - old_xy
        dx_raw = float(np.median(delta[:, 0]))
        dy_raw = float(np.median(delta[:, 1]))
        
        dx_smooth, dy_smooth = self.kalman.filter(dx_raw, dy_raw)
        
        self.x += dx_smooth
        self.y += dy_smooth
        
        magnitude = np.sqrt(dx_smooth**2 + dy_smooth**2)
        self.trajectory.append([round(self.x, 3), round(self.y, 3)])
        self.motion_magnitude.append(magnitude)
        
        feature_quality = int((len(good_old) / 100.0) * 100)
        self.feature_quality.append(feature_quality)

        self.prev_gray = gray
        self.prev_pts = new_xy.reshape(-1, 1, 2)
        return round(dx_smooth, 3), round(dy_smooth, 3), round(self.x, 3), round(self.y, 3)

    def get_trajectory(self) -> List[List[float]]:
        return self.trajectory
    
    def get_feature_quality(self) -> List[int]:
        return self.feature_quality
    
    def get_motion_magnitude(self) -> List[float]:
        return self.motion_magnitude

    def reset(self) -> None:
        self.prev_gray = None
        self.prev_pts = None
        self.x = 0.0
        self.y = 0.0
        self.trajectory = [[0.0, 0.0]]
        self.feature_quality = [100]
        self.motion_magnitude = [0.0]
        self.kalman = KalmanMotionFilter(process_variance=0.01, measurement_variance=0.15)

