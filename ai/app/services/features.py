"""학습(ai/training/train_model.py)과 동일한 규칙으로 추론용 피처를 생성한다."""
from __future__ import annotations

import re
import sys
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from ..core.config import COORD_GRID_SIZE, YONGIN_CENTER_LAT, YONGIN_CENTER_LON
from ..schemas.prediction import PricePredictionRequest


class MultiTargetEncoder(BaseEstimator, TransformerMixin):
    def __init__(self, columns, smoothing=20):
        self.columns = columns
        self.smoothing = smoothing

    def fit(self, X, y, sample_weight=None):
        self.global_mean_ = float(np.mean(y))
        self.mappings_ = {}
        x_temp = X.copy()
        x_temp["_target"] = np.asarray(y)
        for col in self.columns:
            stats = x_temp.groupby(col)["_target"].agg(["mean", "count"])
            mapping = (
                (stats["mean"] * stats["count"] + self.global_mean_ * self.smoothing)
                / (stats["count"] + self.smoothing)
            )
            self.mappings_[col] = mapping.to_dict()
        return self

    def transform(self, X):
        x_out = X.copy()
        for col in self.columns:
            mapping = self.mappings_.get(col, {})
            x_out[f"{col}_target_avg"] = x_out[col].map(mapping).fillna(self.global_mean_)
        return x_out


# joblib이 __main__.MultiTargetEncoder로 pickle 된 경우 역직렬화를 위해 등록
setattr(sys.modules["__main__"], "MultiTargetEncoder", MultiTargetEncoder)


def _clean_category(value) -> str:
    text = str(value).strip()
    if text in {"", "-", "nan", "None"}:
        return "기타"
    return text


def _extract_gu(address: str) -> str:
    for gu in ["수지구", "기흥구", "처인구"]:
        if gu in address:
            return gu
    return "기타"


def _extract_dong(address: str) -> str:
    tokens = str(address).split()
    # 뒤에서부터 동/읍/면/리로 끝나는 토큰을 찾는다 (괄호 제거 후 검사)
    for token in reversed(tokens):
        clean = re.sub(r"[()（）]", "", token)
        if re.search(r"[동읍면리]$", clean):
            return _clean_category(clean)
    # 찾지 못하면 마지막 토큰 fallback
    return _clean_category(tokens[-1]) if tokens else "기타"


def _lookup_baseline(
    bundle: dict, dong: str, gu: str, house_type: str, total_area: float
):
    """모델 번들에 저장된 통계로 baseline 피처 4개를 반환.
    dong+house_type → gu+house_type → house_type → global 순서로 fallback.
    번들에 룩업 테이블이 없으면 NaN 반환 (SimpleImputer가 대신 채움).
    """
    lk = bundle.get("baseline_lookup") if bundle else None
    if not lk:
        return np.nan, np.nan, np.nan, np.nan

    entry = (
        lk.get("dong_house_type", {}).get((dong, house_type))
        or lk.get("gu_house_type", {}).get((gu, house_type))
        or lk.get("house_type", {}).get(house_type)
        or lk.get("global")
    )
    if entry is None:
        return np.nan, np.nan, np.nan, np.nan

    unit_price = entry["unit_price"]
    return (
        unit_price,
        unit_price * total_area,
        float(entry["count"]),
        entry["source_level"],
    )


def _lookup_road_condition(bundle: dict, dong: str, house_type: str) -> str:
    """모델 번들에 저장된 dong+house_type별 최빈 도로조건 반환.
    번들에 테이블이 없거나 해당 조합이 없으면 '기타' 반환.
    """
    lk = bundle.get("road_condition_lookup") if bundle else None
    if not lk:
        return "기타"
    return lk.get((dong, house_type), "기타")


def build_features(request: PricePredictionRequest, bundle: Optional[dict] = None) -> pd.DataFrame:
    total_area = float(request.total_area)
    land_area = float(request.land_area)
    build_year_raw = int(request.build_year)
    build_year_missing = int(build_year_raw == 1900)
    build_year = np.nan if build_year_missing else float(build_year_raw)
    trade_year = int(request.contract_year)
    trade_month = int(request.contract_month)
    trade_day = int(request.contract_day)
    building_age = np.nan if build_year_missing else float(max(0, trade_year - build_year_raw))

    gu = _extract_gu(request.address)
    dong = _extract_dong(request.address)
    house_type = _clean_category(request.building_type)

    # 사용자가 도로조건을 모르므로 번들에서 dong+house_type 최빈값 조회 후 fallback
    road_condition = _lookup_road_condition(bundle, dong, house_type)

    # 번들 룩업 테이블에서 베이스라인 피처 계산
    baseline_unit_price, baseline_price, baseline_count, baseline_source_level = \
        _lookup_baseline(bundle, dong, gu, house_type, total_area)

    lat = float(request.latitude) if request.latitude is not None else np.nan
    lon = float(request.longitude) if request.longitude is not None else np.nan
    coord_missing = int(np.isnan(lat) or np.isnan(lon))

    lat_val = lat if not np.isnan(lat) else YONGIN_CENTER_LAT
    lon_val = lon if not np.isnan(lon) else YONGIN_CENTER_LON
    lat_bin = round(np.floor(lat_val / COORD_GRID_SIZE) * COORD_GRID_SIZE, 4)
    lon_bin = round(np.floor(lon_val / COORD_GRID_SIZE) * COORD_GRID_SIZE, 4)
    coord_grid = f"{lat_bin}_{lon_bin}"

    return pd.DataFrame([{
        "total_area": total_area,
        "land_area": land_area,
        "log_total_area": float(np.log1p(total_area)),
        "log_land_area": float(np.log1p(land_area)),
        "far": total_area / land_area,
        "land_to_total_ratio": land_area / total_area,
        "total_to_land_ratio": total_area / land_area,
        "building_age": building_age,
        "build_year": build_year,
        "build_year_missing": float(build_year_missing),
        "trade_year": float(trade_year),
        "trade_month": float(trade_month),
        "trade_day": float(trade_day),
        "latitude": lat if not np.isnan(lat) else np.nan,
        "longitude": lon if not np.isnan(lon) else np.nan,
        "coord_missing": float(coord_missing),
        "lat_lon_interaction": lat_val * lon_val,
        "lat_sq": lat_val ** 2,
        "lon_sq": lon_val ** 2,
        "baseline_unit_price": baseline_unit_price,
        "baseline_price": baseline_price,
        "baseline_count": baseline_count,
        "baseline_source_level": baseline_source_level,
        "gu": gu,
        "dong": dong,
        "road_condition": road_condition,
        "house_type": house_type,
        "gu_house_type": f"{gu}_{house_type}",
        "dong_house_type": f"{dong}_{house_type}",
        "dong_road": f"{dong}_{road_condition}",
        "coord_grid": coord_grid,
        "coord_grid_house_type": f"{coord_grid}_{house_type}",
    }])
