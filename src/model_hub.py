from __future__ import annotations

import os
from pathlib import Path

try:
    from huggingface_hub import hf_hub_download
except ModuleNotFoundError:
    hf_hub_download = None

from src.model_paths import MODELS_DIR


def ensure_model_file(filename: str) -> Path:
    target = MODELS_DIR / filename
    if target.exists():
        return target

    repo_id = os.getenv("SMARTHELMET_MODELS_REPO", "").strip()
    if not repo_id or hf_hub_download is None:
        return target

    try:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        downloaded = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=str(MODELS_DIR),
            local_dir_use_symlinks=False,
        )
        return Path(downloaded)
    except Exception:
        return target
