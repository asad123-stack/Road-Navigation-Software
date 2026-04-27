# Scene Classifier (MobileNetV2 Fine-Tuning, Colab)

## Final output file
- `models\scene_classifier.pth`

## Goal
Classify each frame into:
- `tunnel`
- `urban`
- `open_road`
- `indoor`

## Easiest option (recommended)
Fine-tune pretrained MobileNetV2 on a small curated dataset (transfer learning).

## Dataset options
1. **Recommended mix**
   - `indoor`: MIT Indoor Scenes (subset)
   - `urban` + `open_road`: BDD100K / KITTI frames
   - `tunnel`: tunnel image sets (Kaggle/Google/OpenImages curation)
2. **Fast fallback**
   - Manually collect ~400 images/class from free sources and your own phone captures.

Use folder structure:
```text
dataset/
  train/
    tunnel/
    urban/
    open_road/
    indoor/
  val/
    tunnel/
    urban/
    open_road/
    indoor/
```

## Colab steps
### 1) Setup
```python
!pip -q install torch torchvision
import torch
import torch.nn as nn
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
```

### 2) Data transforms
```python
train_tf = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
])
val_tf = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
])
```

### 3) Load data
```python
train_ds = datasets.ImageFolder("/content/dataset/train", transform=train_tf)
val_ds = datasets.ImageFolder("/content/dataset/val", transform=val_tf)
train_dl = DataLoader(train_ds, batch_size=32, shuffle=True, num_workers=2)
val_dl = DataLoader(val_ds, batch_size=32, shuffle=False, num_workers=2)
print(train_ds.class_to_idx)  # ensure order matches your labels
```

### 4) Build model (transfer learning)
```python
device = "cuda" if torch.cuda.is_available() else "cpu"
model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
model.classifier[1] = nn.Linear(1280, 4)
model = model.to(device)

# freeze backbone first
for p in model.features.parameters():
    p.requires_grad = False

opt = torch.optim.Adam(model.classifier.parameters(), lr=1e-3)
loss_fn = nn.CrossEntropyLoss()
```

### 5) Train (2-stage fine-tuning)
```python
def run_epoch(loader, train=True):
    model.train(train)
    total, correct, loss_sum = 0, 0, 0.0
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        with torch.set_grad_enabled(train):
            out = model(x)
            loss = loss_fn(out, y)
            if train:
                opt.zero_grad(); loss.backward(); opt.step()
        loss_sum += loss.item() * x.size(0)
        pred = out.argmax(1)
        correct += (pred == y).sum().item()
        total += x.size(0)
    return loss_sum/total, correct/total

# Stage 1: head only
for e in range(10):
    tr = run_epoch(train_dl, True)
    va = run_epoch(val_dl, False)
    print(f"[Head] {e+1:02d} train={tr} val={va}")

# Stage 2: unfreeze all
for p in model.features.parameters():
    p.requires_grad = True
opt = torch.optim.Adam(model.parameters(), lr=1e-4)

for e in range(10):
    tr = run_epoch(train_dl, True)
    va = run_epoch(val_dl, False)
    print(f"[Full] {e+1:02d} train={tr} val={va}")
```

### 6) Save + download
```python
torch.save(model.state_dict(), "scene_classifier.pth")
from google.colab import files
files.download("scene_classifier.pth")
```

## Put in project
- `smarthelmet-nav\models\scene_classifier.pth`

## Important mapping check
Backend expects labels exactly: `["tunnel", "urban", "open_road", "indoor"]`.  
If your dataset class order differs, adjust class-folder names/order before training.
