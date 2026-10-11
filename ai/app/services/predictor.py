"""저장된 joblib 앙상블 번들을 로드해 가격을 예측한다."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import pandas as pd

from ..core.config import MODEL_PATH
from .features import build_features
from ..schemas.prediction import PricePredictionRequest, PricePredictionResponse

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _pipeline_predict(pipeline, x: pd.DataFrame) -> np.ndarray:
    transformed = pipeline[:-1].transform(x)
    return pipeline.named_steps["model"].predict(transformed)


def format_manwon(value: float) -> str:
    rounded = int(round(value))
    sign = "-" if rounded < 0 else ""
    amount = abs(rounded)
    eok, man = divmod(amount, 10_000)
    if eok and man:
        return f"{sign}{eok:,}억 {man:,}만원"
    if eok:
        return f"{sign}{eok:,}억원"
    return f"{sign}{man:,}만원"


class PriceModelService:
    def __init__(self, model_path: Path = MODEL_PATH):
        self.model_path = model_path
        self.bundle = None
        self.load_error: Optional[str] = None
        self._load()

    def _load(self) -> None:
        if not self.model_path.exists():
            self.load_error = f"Model file not found: {self.model_path}"
            return
        try:
            self.bundle = joblib.load(self.model_path)
            self.load_error = None
        except Exception as exc:
            self.load_error = str(exc)
            self.bundle = None

    def is_loaded(self) -> bool:
        return self.bundle is not None

    def predict(self, request: PricePredictionRequest) -> PricePredictionResponse:
        if self.bundle is None:
            raise RuntimeError(self.load_error or "Model is not loaded")

        x = build_features(request, self.bundle)

        debug_cols = [
            "total_area", "land_area", "far", "land_to_total_ratio", "total_to_land_ratio",
            "building_age", "build_year", "build_year_missing",
            "gu", "dong", "road_condition", "house_type",
            "gu_house_type", "dong_house_type", "dong_road",
            "baseline_unit_price", "baseline_price", "baseline_count", "baseline_source_level",
        ]
        logger.info("[predict] feature row:\n%s", x[[c for c in debug_cols if c in x.columns]].to_string())

        b = self.bundle

        raw_pred = np.maximum(_pipeline_predict(b["raw_pipeline"], x), 0)
        log_pred = np.maximum(np.expm1(_pipeline_predict(b["log_pipeline"], x)), 0)
        unit_pred = _pipeline_predict(b["unit_pipeline"], x)
        unit_price_pred = np.maximum(unit_pred * x["total_area"].values, 0)

        a, w, c = b["best_weights"]
        price_pred = np.maximum(a * raw_pred + w * log_pred + c * unit_price_pred, 0)

        if b.get("calibrator") is not None:
            cal = b["calibrator"].predict(price_pred.reshape(-1, 1))
            strength = b.get("calibration_strength", 0.0)
            price_pred = (1 - strength) * price_pred + strength * cal

        if b.get("residual_pipeline") is not None:
            residual = _pipeline_predict(b["residual_pipeline"], x)
            if b.get("positive_residual_only", False):
                residual = np.maximum(residual, 0)
            gate = b.get("residual_gate_만원", 0.0)
            residual = np.where(price_pred >= gate, residual, 0)
            price_pred = price_pred + b.get("residual_strength", 0.0) * residual

        predicted_manwon = float(np.maximum(price_pred, 0)[0])

        return PricePredictionResponse(
            predicted_price_manwon=round(predicted_manwon),
            predicted_price_text=format_manwon(predicted_manwon),
        )
