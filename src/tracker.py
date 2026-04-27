from __future__ import annotations

from typing import Dict, List, Tuple


class ObjectTracker:
    def __init__(self) -> None:
        self.tracks: List[dict] = []
        self._next_id = 1
        self._track_points: Dict[int, List[List[int]]] = {}
        self._track_label: Dict[int, str] = {}
        self._max_history = 20
        self._match_distance = 80

    def update(self, detections: List[dict]) -> List[dict]:
        centers: List[Tuple[str, int, int]] = []
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            centers.append((det["label"], int((x1 + x2) / 2), int((y1 + y2) / 2)))

        updated: List[dict] = []
        used_ids = set()
        for label, cx, cy in centers:
            track_id = self._match_track(label, cx, cy, used_ids)
            used_ids.add(track_id)

            pts = self._track_points.setdefault(track_id, [])
            pts.append([cx, cy])
            if len(pts) > self._max_history:
                del pts[:-self._max_history]
            self._track_label[track_id] = label

            updated.append({"id": track_id, "label": label, "predicted_path": pts[:]})

        self.tracks = updated
        active_ids = {t["id"] for t in updated}
        stale_ids = [tid for tid in self._track_points if tid not in active_ids]
        for tid in stale_ids:
            del self._track_points[tid]
            self._track_label.pop(tid, None)
        return self.tracks

    def _match_track(self, label: str, cx: int, cy: int, used_ids: set) -> int:
        best_id = None
        best_dist = float("inf")
        for tid, pts in self._track_points.items():
            if tid in used_ids:
                continue
            if self._track_label.get(tid) != label:
                continue
            if not pts:
                continue
            px, py = pts[-1]
            dist = ((cx - px) ** 2 + (cy - py) ** 2) ** 0.5
            if dist < best_dist and dist <= self._match_distance:
                best_dist = dist
                best_id = tid

        if best_id is not None:
            return best_id
        tid = self._next_id
        self._next_id += 1
        return tid
