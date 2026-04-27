from __future__ import annotations

from typing import List, Tuple

import cv2
import numpy as np


class VisualOdometry:
    def __init__(self) -> None:
        self.prev_gray = None
        self.prev_pts = None
        self.x = 0.0
        self.y = 0.0
        self.trajectory: List[List[float]] = [[0.0, 0.0]]
        self.feature_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)
        self.lk_params = dict(
            winSize=(15, 15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03),
        )

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
        dx = float(np.median(delta[:, 0]))
        dy = float(np.median(delta[:, 1]))
        self.x += dx
        self.y += dy
        self.trajectory.append([round(self.x, 3), round(self.y, 3)])

        self.prev_gray = gray
        self.prev_pts = new_xy.reshape(-1, 1, 2)
        return round(dx, 3), round(dy, 3), round(self.x, 3), round(self.y, 3)

    def get_trajectory(self) -> List[List[float]]:
        return self.trajectory

    def reset(self) -> None:
        self.prev_gray = None
        self.prev_pts = None
        self.x = 0.0
        self.y = 0.0
        self.trajectory = [[0.0, 0.0]]
