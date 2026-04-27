import base64
import requests

import cv2
import numpy as np


def make_dummy_frame() -> str:
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(img, "SMARTHELMET TEST", (120, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
    ok, buf = cv2.imencode(".jpg", img)
    if not ok:
        raise RuntimeError("Failed to encode test frame")
    return "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode("utf-8")


def run_tests():
    payload = {"frame": make_dummy_frame(), "lat": 18.5204, "lng": 73.8567}
    response = requests.post("http://127.0.0.1:5000/api/process_frame", json=payload, timeout=30)
    data = response.json()

    assert response.status_code == 200
    assert "lstm_risk" in data
    assert "scene_type" in data
    assert "motion_vector" in data
    assert data["scene_type"] in ["tunnel", "urban", "open_road", "indoor"]
    lstm = data["lstm_risk"]
    assert lstm is None or (0 <= lstm <= 100)
    print("PASS: backend v2.0 response contract")


if __name__ == "__main__":
    run_tests()
