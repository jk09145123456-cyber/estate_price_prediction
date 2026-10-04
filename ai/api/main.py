from fastapi import FastAPI, HTTPException

from model_service import PriceModelService
from schemas import PricePredictionRequest, PricePredictionResponse


app = FastAPI(title="Housing Price Prediction API")
model_service = PriceModelService()


@app.get("/health")
def health():
    return {
        "status": "ok" if model_service.is_loaded() else "model_not_loaded",
        "model_loaded": model_service.is_loaded(),
        "detail": model_service.load_error,
    }


@app.post("/predict", response_model=PricePredictionResponse)
def predict(request: PricePredictionRequest):
    try:
        return model_service.predict(request)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
