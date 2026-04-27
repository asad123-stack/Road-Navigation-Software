# LSTM Threat Predictor (Colab Guide)

## Final output file
- `models\lstm_threat.pth`

## Goal
Predict risk ~3 seconds ahead from a sequence of last 10 timesteps:
- `[risk_score, num_objects, center_depth]` per timestep.

## Easiest option
Generate synthetic temporal sequences from your MLP risk logic and train an LSTM.  
No external dataset is required.

## Colab steps
### 1) Setup
```python
!pip -q install torch numpy scikit-learn
import numpy as np
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
```

### 2) Generate sequence dataset
```python
np.random.seed(42)
N = 5000
SEQ = 10

X = np.zeros((N, SEQ, 3), dtype=np.float32)
y = np.zeros((N, 1), dtype=np.float32)

for i in range(N):
    num_objects = np.random.randint(0, 10)
    center_depth = np.random.uniform(0.2, 1.0)
    risk = np.random.uniform(10, 60)

    for t in range(SEQ + 1):
        # random walk dynamics
        num_objects = np.clip(num_objects + np.random.randint(-2, 3), 0, 15)
        center_depth = np.clip(center_depth + np.random.uniform(-0.08, 0.08), 0.05, 1.0)
        rule_risk = 5 + 5.5 * num_objects + 45 * (1 - center_depth)
        risk = np.clip(0.7 * risk + 0.3 * rule_risk, 0, 100)

        if t < SEQ:
            X[i, t] = [risk / 100.0, float(num_objects), float(center_depth)]
        else:
            y[i, 0] = risk / 100.0
```

### 3) Train/val split
```python
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
Xtr = torch.tensor(X_train, dtype=torch.float32)
ytr = torch.tensor(y_train, dtype=torch.float32)
Xva = torch.tensor(X_val, dtype=torch.float32)
yva = torch.tensor(y_val, dtype=torch.float32)
```

### 4) Define LSTM
```python
class ThreatLSTM(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=3, hidden_size=32, num_layers=2, batch_first=True, dropout=0.1)
        self.fc = nn.Linear(32, 1)
        self.out = nn.Sigmoid()
    def forward(self, x):
        s, _ = self.lstm(x)
        return self.out(self.fc(s[:, -1, :]))

model = ThreatLSTM()
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
loss_fn = nn.MSELoss()
```

### 5) Train
```python
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
torch.save(model.state_dict(), "lstm_threat.pth")
from google.colab import files
files.download("lstm_threat.pth")
```

## Put in project
- `smarthelmet-nav\models\lstm_threat.pth`

## Better-data upgrade
- Log real frame sequences from the running app.
- Build supervised targets from near-future observed risk.
- Fine-tune the same network on real sequences.
