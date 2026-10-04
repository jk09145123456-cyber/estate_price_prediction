# AI Price Prediction API

FastAPI service that loads the XGBoost ensemble model for real estate price prediction.

## Model file

The trained model is located at:

```text
ai/api/models/xgb_price_unit_ensemble_model.joblib
```

This file is tracked in Git and is loaded automatically on startup.
After retraining (e.g., adding baseline_lookup / road_condition_lookup),
replace this file and redeploy.

## Run locally

```bash
cd ai/api
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/predict` | Price prediction |
| GET | `/docs` | Swagger UI |

## Render deployment

| Setting | Value |
|---------|-------|
| Root Directory | `ai/api` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

Environment variables: none required (model path is resolved automatically).

## Request / Response

POST `/predict`

```json
{
  "address": "경기도 용인시 수지구 죽전동 1234",
  "building_type": "단독",
  "total_area": 132.5,
  "land_area": 95.0,
  "build_year": 2004,
  "contract_year": 2026,
  "contract_month": 6,
  "contract_day": 10
}
```

```json
{
  "predicted_price_manwon": 78200,
  "predicted_price_text": "7억 8,200만원"
}
```
