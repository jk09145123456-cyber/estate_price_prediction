from fastapi import APIRouter, HTTPException

from ..schemas.prediction import PricePredictionRequest, PricePredictionResponse
from ..services.predictor import PriceModelService

router = APIRouter()
model_service = PriceModelService()


@router.get("/health")
def health():
    return {
        "status": "ok" if model_service.is_loaded() else "model_not_loaded",
        "model_loaded": model_service.is_loaded(),
        "detail": model_service.load_error,
    }


@router.post("/predict", response_model=PricePredictionResponse)
def predict(request: PricePredictionRequest):
    try:
        return model_service.predict(request)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
