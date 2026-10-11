"""AI server settings."""
import os
from pathlib import Path

AI_DIR = Path(__file__).resolve().parents[2]
MODEL_FILENAME = "xgb_price_unit_ensemble_model.joblib"

# Model path resolution: MODEL_PATH env var → ai/models → ai/training outputs (local dev)
_candidates = [
    Path(os.environ["MODEL_PATH"]) if os.getenv("MODEL_PATH") else None,
    AI_DIR / "models" / MODEL_FILENAME,
    AI_DIR / "training" / "outputs_coord_test" / MODEL_FILENAME,
]
MODEL_PATH = next((p for p in _candidates if p and p.exists()), _candidates[1])

# Coordinate grid size used in training / default coordinate when omitted (Yongin center)
COORD_GRID_SIZE = 0.005
YONGIN_CENTER_LAT = 37.2411
YONGIN_CENTER_LON = 127.1776
