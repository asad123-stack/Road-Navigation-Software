# Risk Scorer MLP (Colab Guide)

## Final output files
- `models\risk_scorer.pth`
- `models\risk_scaler.npz`

## Goal
Train the MLP that maps frame-level features to risk score (0-100).

## Features used (match backend)
- `num_objects`
- `center_depth`
- `min_zone_depth` (minimum of left/center/right)

## Easiest option
Use synthetic data generation with rule-based labels, then train a small MLP.  
This is fast, reproducible, and enough for semester-project demos.

## Colab steps
### 1) Setup
```python
!pip -q install torch scikit-learn numpy
import numpy as np
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
```

### 2) Generate training data
```python
np.random.seed(42)
n = 12000
num_objects = np.random.randint(0, 15, size=n).astype(np.float32)
center_depth = np.random.uniform(0.1, 1.0, size=n).astype(np.float32)
min_zone_depth = np.minimum(center_depth, np.random.uniform(0.05, 1.0, size=n).astype(np.float32))

# Rule-based risk label (0..1)
risk = 0.05 + 0.06 * num_objects + 0.55 * (1.0 - center_depth) + 0.35 * (1.0 - min_zone_depth)
risk = np.clip(risk, 0, 1).astype(np.float32)

X = np.stack([num_objects, center_depth, min_zone_depth], axis=1)
y = risk.reshape(-1, 1)
```

### 3) Scale + split
```python
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_val, y_train, y_val = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
```

### 4) Define model
```python
class RiskMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(3, 16), nn.ReLU(),
            nn.Linear(16, 8), nn.ReLU(),
            nn.Linear(8, 1), nn.Sigmoid()
        )
    def forward(self, x):
        return self.net(x)

model = RiskMLP()
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
loss_fn = nn.MSELoss()
```

### 5) Train
```python
Xtr = torch.tensor(X_train, dtype=torch.float32)
ytr = torch.tensor(y_train, dtype=torch.float32)
Xva = torch.tensor(X_val, dtype=torch.float32)
yva = torch.tensor(y_val, dtype=torch.float32)

for epoch in range(1, 151):
    model.train()
    pred = model(Xtr)
    loss = loss_fn(pred, ytr)
    opt.zero_grad(); loss.backward(); opt.step()

    if epoch % 15 == 0:
        model.eval()
        with torch.no_grad():
            vloss = loss_fn(model(Xva), yva).item()
        print(f"Epoch {epoch:03d} | train={loss.item():.4f} val={vloss:.4f}")
```

### 6) Save + download
```python
torch.save(model.state_dict(), "risk_scorer.pth")
np.savez("risk_scaler.npz", data_min_=scaler.data_min_, data_max_=scaler.data_max_)

from google.colab import files
files.download("risk_scorer.pth")
files.download("risk_scaler.npz")
```

## Put in project
- `smarthelmet-nav\models\risk_scorer.pth`
- `smarthelmet-nav\models\risk_scaler.npz`

## Optional real-data upgrade
- Log real features from backend runs.
- Replace synthetic labels with human-reviewed/derived risk labels.
- Fine-tune same architecture for better realism.
