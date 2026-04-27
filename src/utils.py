import base64
from typing import Optional

import cv2
import numpy as np


def decode_data_url_image(data_url: str) -> Optional[np.ndarray]:
    if "," not in data_url:
        return None
    _, encoded = data_url.split(",", 1)
    try:
        binary = base64.b64decode(encoded)
    except (ValueError, base64.binascii.Error):
        return None
    arr = np.frombuffer(binary, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return image
