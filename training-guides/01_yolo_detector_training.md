# YOLOv8 Object Detector (Colab Guide)

## Final output file
- `models\yolov8n.pt`

## Goal
Detect road-relevant obstacles (`person`, `car`, `bus`, `truck`, `motorbike`, `bicycle`, optional `obstacle`).

## Easiest option
1. Start from pretrained YOLOv8n.
2. Fine-tune for a few epochs on your custom dataset.
3. Export `best.pt` and rename it to `yolov8n.pt`.

If you are short on time, you can directly use pretrained `yolov8n.pt` (no training), but fine-tuning improves your demo domain accuracy.

## Dataset options
1. **Recommended:** Roboflow custom dataset (capture phone images from your use case, label in Roboflow).
2. **Fallback:** Public road object datasets from Roboflow Universe.
3. Keep classes small and practical for your demo.

## Colab steps
### 1) Setup
```python
!pip -q install ultralytics roboflow
from ultralytics import YOLO
```

### 2) Download dataset (Roboflow)
```python
from roboflow import Roboflow
rf = Roboflow(api_key="YOUR_API_KEY")
project = rf.workspace("YOUR_WORKSPACE").project("YOUR_PROJECT")
dataset = project.version(1).download("yolov8")  # creates data.yaml
```

### 3) Train (fine-tune)
```python
model = YOLO("yolov8n.pt")
model.train(
    data=f"{dataset.location}/data.yaml",
    epochs=50,
    imgsz=640,
    batch=16,
    patience=15,
    project="smarthelmet_yolo",
    name="exp"
)
```

### 4) Validate
```python
metrics = model.val()
print(metrics)
```

### 5) Save + download
```python
import shutil
best_path = "smarthelmet_yolo/exp/weights/best.pt"
shutil.copy(best_path, "yolov8n.pt")
from google.colab import files
files.download("yolov8n.pt")
```

## Put in project
Place downloaded file at:
- `smarthelmet-nav\models\yolov8n.pt`

## Practical tips
- Start with 300-1000 labeled images.
- Prefer varied lighting and angles from your phone camera.
- Keep class list stable once backend integration is live.
