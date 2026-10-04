from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor


RANDOM_STATE = 42
TEST_SIZE = 0.2
MIN_CATEGORY_COUNT = 50
SMOOTHING = 20
TARGET_MODE = "direct_price_with_historical_baseline_features"
HIGH_ERROR_DONGS = {
    "죽전동",
    "성복동",
    "동천동",
    "풍덕천동",
    "신봉동",
    "고기동",
    "삼가동",
    "유방동",
    "남동",
    "묵리",
    "마북동",
    "영덕동",
    "언남동",
}

COL_SIGUNGU = "시군구"
COL_AREA = "연면적(㎡)"
COL_LAND = "대지면적(㎡)"
COL_TYPE = "주택유형"
COL_YEAR = "건축년도"
COL_PRICE = "거래금액(만원)"
COL_TRADE_YM = "계약년월"
COL_TRADE_D = "계약일"
COL_ROAD_COND = "도로조건"
COL_ROAD_NAME = "도로명"
COL_LOT = "번지"
COL_LAT = "latitude"
COL_LON = "longitude"
YONGIN_CENTER_LAT = 37.2411
YONGIN_CENTER_LON = 127.1776

TARGET_ENCODE_COLS = [
    "gu",
    "dong",
    "house_type",
    "gu_house_type",
    "dong_house_type",
    "dong_road",
    "coord_grid",
    "coord_grid_house_type",
]

NUM_FEATURES = [
    "total_area",
    "land_area",
    "log_total_area",
    "log_land_area",
    "far",
    "land_to_total_ratio",
    "total_to_land_ratio",
    "building_age",
    "build_year",
    "build_year_missing",
    "trade_year",
    "trade_month",
    "trade_day",
    "latitude",
    "longitude",
    "coord_missing",
    "lat_lon_interaction",
    "lat_sq",
    "lon_sq",
    "baseline_unit_price",
    "baseline_price",
    "baseline_count",
    "baseline_source_level",
    "gu_target_avg",
    "dong_target_avg",
    "house_type_target_avg",
    "gu_house_type_target_avg",
    "dong_house_type_target_avg",
    "dong_road_target_avg",
    "coord_grid_target_avg",
    "coord_grid_house_type_target_avg",
]

CAT_FEATURES = [
    "gu",
    "dong",
    "road_condition",
    "house_type",
    "gu_house_type",
    "dong_house_type",
    "dong_road",
    "coord_grid",
    "coord_grid_house_type",
]

BASE_FEATURES = [
    "total_area",
    "land_area",
    "log_total_area",
    "log_land_area",
    "far",
    "land_to_total_ratio",
    "total_to_land_ratio",
    "building_age",
    "build_year",
    "build_year_missing",
    "trade_year",
    "trade_month",
    "trade_day",
    "latitude",
    "longitude",
    "coord_missing",
    "lat_lon_interaction",
    "lat_sq",
    "lon_sq",
    "baseline_unit_price",
    "baseline_price",
    "baseline_count",
    "baseline_source_level",
] + CAT_FEATURES


def normalize_money(value):
    text = str(value).replace(",", "").strip()
    return pd.to_numeric(text, errors="coerce")


def clean_category(value):
    text = str(value).strip()
    if text in {"", "-", "nan", "None"}:
        return "기타"
    return text


def extract_gu(addr):
    text = str(addr)
    for gu in ["수지구", "기흥구", "처인구"]:
        if gu in text:
            return gu
    return "기타"


def extract_eup_myeon_dong(addr):
    parts = str(addr).split()
    if not parts:
        return "기타"
    return clean_category(parts[-1])


def historical_group_mean(df, group_cols, value_col):
    grouped = df.groupby(group_cols, sort=False)[value_col]
    cumulative_sum = grouped.cumsum() - df[value_col]
    cumulative_count = grouped.cumcount()
    return cumulative_sum / cumulative_count.replace(0, np.nan)


def historical_group_count(df, group_cols):
    return df.groupby(group_cols, sort=False).cumcount()


def add_historical_baseline_features(df):
    out = df.copy()

    out["baseline_unit_specific"] = historical_group_mean(
        out, ["dong", "house_type"], "price_per_total_area"
    )
    out["baseline_count_specific"] = historical_group_count(out, ["dong", "house_type"])
    out["baseline_unit_medium"] = historical_group_mean(
        out, ["gu", "house_type"], "price_per_total_area"
    )
    out["baseline_count_medium"] = historical_group_count(out, ["gu", "house_type"])
    out["baseline_unit_broad"] = historical_group_mean(out, ["house_type"], "price_per_total_area")
    out["baseline_count_broad"] = historical_group_count(out, ["house_type"])
    out["baseline_unit_global"] = out["price_per_total_area"].expanding().mean().shift(1)
    out["baseline_count_global"] = np.arange(len(out), dtype=float)

    out["baseline_unit_price"] = out["baseline_unit_specific"]
    out["baseline_count"] = out["baseline_count_specific"].astype(float)
    out["baseline_source_level"] = 3.0

    medium_mask = out["baseline_unit_price"].isna() | (out["baseline_count"] < 3)
    out.loc[medium_mask, "baseline_unit_price"] = out.loc[medium_mask, "baseline_unit_medium"]
    out.loc[medium_mask, "baseline_count"] = out.loc[medium_mask, "baseline_count_medium"]
    out.loc[medium_mask, "baseline_source_level"] = 2.0

    broad_mask = out["baseline_unit_price"].isna() | (out["baseline_count"] < 5)
    out.loc[broad_mask, "baseline_unit_price"] = out.loc[broad_mask, "baseline_unit_broad"]
    out.loc[broad_mask, "baseline_count"] = out.loc[broad_mask, "baseline_count_broad"]
    out.loc[broad_mask, "baseline_source_level"] = 1.0

    global_mask = out["baseline_unit_price"].isna() | (out["baseline_count"] < 10)
    out.loc[global_mask, "baseline_unit_price"] = out.loc[global_mask, "baseline_unit_global"]
    out.loc[global_mask, "baseline_count"] = out.loc[global_mask, "baseline_count_global"]
    out.loc[global_mask, "baseline_source_level"] = 0.0

    fallback_unit = out["price_per_total_area"].median()
    out["baseline_unit_price"] = out["baseline_unit_price"].fillna(fallback_unit)
    out["baseline_count"] = out["baseline_count"].fillna(0).astype(float)
    out["baseline_price"] = out["baseline_unit_price"] * out["total_area"]

    return out.drop(
        columns=[
            "baseline_unit_specific",
            "baseline_count_specific",
            "baseline_unit_medium",
            "baseline_count_medium",
            "baseline_unit_broad",
            "baseline_count_broad",
            "baseline_unit_global",
            "baseline_count_global",
        ]
    )



def is_masked_lot(value):
    text = str(value).strip()
    return (not text) or text.lower() in {"nan", "none", "-"} or "*" in text


def make_geocode_query(row):
    sigungu = str(row.get(COL_SIGUNGU, "")).strip()
    road_name = str(row.get(COL_ROAD_NAME, "")).strip()
    lot = str(row.get(COL_LOT, "")).strip()

    if road_name and road_name.lower() not in {"nan", "none", "-"}:
        return f"{sigungu} {road_name}".strip()
    if not is_masked_lot(lot):
        return f"{sigungu} {lot}".strip()
    return sigungu


def load_coordinate_cache(path):
    if not path:
        return {}
    cache_path = Path(path)
    if not cache_path.exists():
        return {}
    cache_df = pd.read_csv(cache_path)
    required = {"address_key", "latitude", "longitude"}
    if not required.issubset(cache_df.columns):
        raise ValueError(f"Coordinate cache must contain columns: {sorted(required)}")
    cache = {}
    for _, row in cache_df.iterrows():
        lat = pd.to_numeric(row["latitude"], errors="coerce")
        lon = pd.to_numeric(row["longitude"], errors="coerce")
        if pd.notna(lat) and pd.notna(lon):
            cache[str(row["address_key"])] = (float(lat), float(lon))
    return cache


def save_coordinate_cache(path, cache):
    if not path:
        return
    cache_path = Path(path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {"address_key": key, "latitude": value[0], "longitude": value[1]}
        for key, value in sorted(cache.items())
    ]
    pd.DataFrame(rows).to_csv(cache_path, index=False, encoding="utf-8-sig")


def kakao_geocode(query, kakao_api_key):
    if requests is None:
        raise ImportError("requests is required for Kakao geocoding. Install requests or use a coordinate cache.")
    headers = {"Authorization": f"KakaoAK {kakao_api_key}"}

    # 1차: 주소 검색. 정확한 지번/도로명주소가 있으면 가장 안정적이다.
    address_url = "https://dapi.kakao.com/v2/local/search/address.json"
    response = requests.get(address_url, headers=headers, params={"query": query}, timeout=10)
    response.raise_for_status()
    docs = response.json().get("documents", [])
    if docs:
        first = docs[0]
        return float(first["y"]), float(first["x"])

    # 2차: 현재 CSV처럼 번지가 마스킹되었거나 도로명만 있는 경우 keyword 검색으로 보완한다.
    keyword_url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    response = requests.get(keyword_url, headers=headers, params={"query": query}, timeout=10)
    response.raise_for_status()
    docs = response.json().get("documents", [])
    if docs:
        first = docs[0]
        return float(first["y"]), float(first["x"])

    return None


def attach_coordinates(raw_df, coord_cache_path=None, kakao_api_key=None, geocode_sleep=0.08):
    out = raw_df.copy()
    existing_lat_cols = ["latitude", "lat", "위도"]
    existing_lon_cols = ["longitude", "lon", "lng", "경도"]
    lat_col = next((c for c in existing_lat_cols if c in out.columns), None)
    lon_col = next((c for c in existing_lon_cols if c in out.columns), None)

    if lat_col and lon_col:
        out[COL_LAT] = pd.to_numeric(out[lat_col], errors="coerce")
        out[COL_LON] = pd.to_numeric(out[lon_col], errors="coerce")
        return out

    out["address_key"] = out.apply(make_geocode_query, axis=1)
    cache = load_coordinate_cache(coord_cache_path)
    kakao_api_key = kakao_api_key or os.getenv("KAKAO_REST_API_KEY")

    missing_keys = sorted(set(out["address_key"]) - set(cache))
    if kakao_api_key:
        for i, key in enumerate(missing_keys, start=1):
            try:
                result = kakao_geocode(key, kakao_api_key)
                if result is not None:
                    cache[key] = result
            except Exception as exc:
                print(f"geocode failed: {key} / {exc}")
            if i % 50 == 0:
                save_coordinate_cache(coord_cache_path, cache)
                print(f"geocoded {i}/{len(missing_keys)} unique addresses")
            time.sleep(geocode_sleep)
        save_coordinate_cache(coord_cache_path, cache)
    elif coord_cache_path:
        print("No Kakao API key found. Existing coordinate cache will be used only.")

    out[COL_LAT] = out["address_key"].map(lambda key: cache.get(key, (np.nan, np.nan))[0])
    out[COL_LON] = out["address_key"].map(lambda key: cache.get(key, (np.nan, np.nan))[1])
    return out


def add_coordinate_features(out, coord_grid_size):
    out[COL_LAT] = pd.to_numeric(out.get(COL_LAT, np.nan), errors="coerce")
    out[COL_LON] = pd.to_numeric(out.get(COL_LON, np.nan), errors="coerce")
    out["coord_missing"] = (out[COL_LAT].isna() | out[COL_LON].isna()).astype(int)

    lat_fill = out[COL_LAT].median()
    lon_fill = out[COL_LON].median()
    if pd.isna(lat_fill):
        lat_fill = YONGIN_CENTER_LAT
    if pd.isna(lon_fill):
        lon_fill = YONGIN_CENTER_LON

    out[COL_LAT] = out[COL_LAT].fillna(lat_fill)
    out[COL_LON] = out[COL_LON].fillna(lon_fill)
    out["lat_lon_interaction"] = out[COL_LAT] * out[COL_LON]
    out["lat_sq"] = out[COL_LAT] ** 2
    out["lon_sq"] = out[COL_LON] ** 2

    lat_bin = np.floor(out[COL_LAT] / coord_grid_size) * coord_grid_size
    lon_bin = np.floor(out[COL_LON] / coord_grid_size) * coord_grid_size
    out["coord_grid"] = lat_bin.round(4).astype(str) + "_" + lon_bin.round(4).astype(str)
    out["coord_grid_house_type"] = out["coord_grid"] + "_" + out["house_type"]
    return out

def prepare_dataframe(df, trim_price_quantiles, drop_suspected_duplicates, coord_grid_size=0.005):
    out = df.copy()

    out["contract_ym"] = pd.to_numeric(out[COL_TRADE_YM], errors="coerce")
    out["trade_year"] = (out["contract_ym"] // 100).astype("Int64")
    out["trade_month"] = (out["contract_ym"] % 100).astype("Int64")
    out["trade_day"] = pd.to_numeric(out[COL_TRADE_D], errors="coerce")

    out["price"] = out[COL_PRICE].apply(normalize_money)
    out["total_area"] = pd.to_numeric(out[COL_AREA], errors="coerce")
    out["land_area"] = pd.to_numeric(out[COL_LAND], errors="coerce")
    out["build_year"] = pd.to_numeric(out[COL_YEAR], errors="coerce")
    out["build_year_missing"] = (
        out["build_year"].isna() | (out["build_year"] == 1900)
    ).astype(int)
    out.loc[out["build_year"] == 1900, "build_year"] = np.nan

    out = out.dropna(
        subset=[
            "price",
            "total_area",
            "land_area",
            "trade_year",
            "trade_month",
            "trade_day",
        ]
    )
    out = out[(out["price"] > 0) & (out["total_area"] > 0) & (out["land_area"] > 0)]

    out["trade_year"] = out["trade_year"].astype(int)
    out["trade_month"] = out["trade_month"].astype(int)
    out["trade_day"] = out["trade_day"].astype(int)

    out["building_age"] = out["trade_year"] - out["build_year"]
    valid_age_mask = out["building_age"].isna() | (
        (out["building_age"] >= 0) & (out["building_age"] <= 150)
    )
    out = out[valid_age_mask]

    out["far"] = out["total_area"] / out["land_area"]
    out = out.replace([np.inf, -np.inf], np.nan).dropna(subset=["far"])
    out = out[(out["far"] > 0) & (out["far"] < 20)]

    out["log_total_area"] = np.log1p(out["total_area"])
    out["log_land_area"] = np.log1p(out["land_area"])
    out["land_to_total_ratio"] = out["land_area"] / out["total_area"]
    out["total_to_land_ratio"] = out["total_area"] / out["land_area"]

    out["house_type"] = out[COL_TYPE].map(clean_category)
    out["gu"] = out[COL_SIGUNGU].apply(extract_gu)
    out["dong"] = out[COL_SIGUNGU].apply(extract_eup_myeon_dong)
    out["road_condition"] = out[COL_ROAD_COND].map(clean_category)

    out["gu_house_type"] = out["gu"] + "_" + out["house_type"]
    out["dong_house_type"] = out["dong"] + "_" + out["house_type"]
    out["dong_road"] = out["dong"] + "_" + out["road_condition"]
    out = add_coordinate_features(out, coord_grid_size=coord_grid_size)

    out["contract_date_order"] = (
        out["trade_year"] * 10000 + out["trade_month"] * 100 + out["trade_day"]
    )
    if trim_price_quantiles:
        price_lower = out["price"].quantile(0.01)
        price_upper = out["price"].quantile(0.99)
        out = out[(out["price"] >= price_lower) & (out["price"] <= price_upper)]
    out = out.sort_values("contract_date_order").reset_index(drop=True)
    if drop_suspected_duplicates:
        out = out.drop_duplicates(
            subset=[
                "contract_date_order",
                "gu",
                "dong",
                "house_type",
                "road_condition",
                "total_area",
                "land_area",
                "build_year",
                "price",
            ],
            keep="first",
        ).reset_index(drop=True)
    out["price_per_total_area"] = out["price"] / out["total_area"]

    return add_historical_baseline_features(out)


def time_based_split(df, test_size=0.2):
    split_idx = int(len(df) * (1 - test_size))
    split_idx = min(max(split_idx, 1), len(df) - 1)
    return df.iloc[:split_idx].copy(), df.iloc[split_idx:].copy()


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


def build_pipeline(params, device):
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), NUM_FEATURES),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        (
                            "onehot",
                            OneHotEncoder(
                                handle_unknown="ignore",
                                min_frequency=MIN_CATEGORY_COUNT,
                                sparse_output=False,
                            ),
                        ),
                    ]
                ),
                CAT_FEATURES,
            ),
        ]
    )

    model = XGBRegressor(
        objective="reg:squarederror",
        random_state=RANDOM_STATE,
        n_jobs=-1,
        tree_method="hist",
        device=device,
        eval_metric="rmse",
        **params,
    )

    return Pipeline(
        steps=[
            ("target_encoder", MultiTargetEncoder(TARGET_ENCODE_COLS, smoothing=SMOOTHING)),
            ("preprocess", preprocessor),
            ("model", model),
        ]
    )


def pipeline_predict(pipeline, x):
    transformed = pipeline[:-1].transform(x)
    return pipeline.named_steps["model"].predict(transformed)


def evaluate(y_true, pred, reference_price=None):
    mae = mean_absolute_error(y_true, pred)
    mse = mean_squared_error(y_true, pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, pred)
    y_true_array = np.asarray(y_true, dtype=float)
    pred_array = np.asarray(pred, dtype=float)
    error = pred_array - y_true_array
    abs_error = np.abs(error)
    actual_mean = float(np.mean(y_true_array))
    actual_median = float(np.median(y_true_array))
    pred_mean = float(np.mean(pred_array))
    nonzero_mask = y_true_array != 0
    mape = (
        np.mean(
            np.abs(
                (y_true_array[nonzero_mask] - pred_array[nonzero_mask])
                / y_true_array[nonzero_mask]
            )
        )
        * 100
        if nonzero_mask.any()
        else np.nan
    )
    wmape = (
        np.sum(np.abs(y_true_array - pred_array)) / np.sum(np.abs(y_true_array)) * 100
        if np.sum(np.abs(y_true_array)) != 0
        else np.nan
    )
    metrics = {
        "MAE_만원": float(mae),
        "MSE_만원2": float(mse),
        "RMSE_만원": float(rmse),
        "MedianAE_만원": float(np.median(abs_error)),
        "MeanError_만원": float(np.mean(error)),
        "MaxAE_만원": float(np.max(abs_error)),
        "R2": float(r2),
        "MAPE_%": float(mape),
        "WMAPE_%": float(wmape),
        "Actual_mean_price_만원": actual_mean,
        "Actual_median_price_만원": actual_median,
        "Pred_mean_price_만원": pred_mean,
        "MAE_vs_actual_mean_%": float(mae / actual_mean * 100) if actual_mean != 0 else np.nan,
        "RMSE_vs_actual_mean_%": float(rmse / actual_mean * 100) if actual_mean != 0 else np.nan,
    }
    if reference_price is not None:
        reference_array = np.asarray(reference_price, dtype=float)
        metrics.update(
            {
                "Reference_mean_price_만원": float(np.mean(reference_array)),
                "Reference_median_price_만원": float(np.median(reference_array)),
            }
        )
    return metrics


def summarize_rmse_impact(y_true, pred, high_price_threshold):
    actual = np.asarray(y_true, dtype=float)
    predicted = np.asarray(pred, dtype=float)
    squared_error = np.square(predicted - actual)
    high_mask = actual >= high_price_threshold
    regular_mask = ~high_mask
    top_count = max(1, int(np.ceil(len(actual) * 0.10)))
    top_indices = np.argsort(squared_error)[-top_count:]
    keep_mask = np.ones(len(actual), dtype=bool)
    keep_mask[top_indices] = False

    def group_summary(mask):
        group_actual = actual[mask]
        group_error = squared_error[mask]
        return {
            "rows": int(mask.sum()),
            "actual_avg": format_manwon(np.mean(group_actual)),
            "RMSE": format_manwon(np.sqrt(np.mean(group_error))),
        }

    return {
        "regular_price_test": group_summary(regular_mask),
        "high_price_test": group_summary(high_mask),
        "top_10pct_error_rows": top_count,
        "top_10pct_squared_error_share_%": float(
            squared_error[top_indices].sum() / squared_error.sum() * 100
        ),
        "filtered_test_excluding_top_10pct": {
            "excluded_condition": "Test squared error top 10%",
            "rows": int(keep_mask.sum()),
            "removed_rows": top_count,
            "actual_avg": format_manwon(np.mean(actual[keep_mask])),
            "predicted_avg": format_manwon(np.mean(predicted[keep_mask])),
            "R2": float(r2_score(actual[keep_mask], predicted[keep_mask])),
            "RMSE": format_manwon(np.sqrt(np.mean(squared_error[keep_mask]))),
        },
    }


def summarize_price_level(y_true, pred, baseline):
    y_true_array = np.asarray(y_true, dtype=float)
    pred_array = np.asarray(pred, dtype=float)
    baseline_array = np.asarray(baseline, dtype=float)
    abs_error = np.abs(pred_array - y_true_array)
    baseline_abs_error = np.abs(baseline_array - y_true_array)

    return {
        "actual_avg_만원": float(np.mean(y_true_array)),
        "predicted_avg_만원": float(np.mean(pred_array)),
        "baseline_avg_만원": float(np.mean(baseline_array)),
        "model_avg_abs_error_만원": float(np.mean(abs_error)),
        "baseline_avg_abs_error_만원": float(np.mean(baseline_abs_error)),
        "model_median_abs_error_만원": float(np.median(abs_error)),
        "baseline_median_abs_error_만원": float(np.median(baseline_abs_error)),
    }


def make_evaluation_table(df, pred):
    actual = np.asarray(df["price"], dtype=float)
    predicted = np.asarray(pred, dtype=float)
    error = predicted - actual

    columns = [
        "contract_ym",
        "gu",
        "dong",
        "house_type",
        "total_area",
        "land_area",
        "building_age",
    ]
    table = df[columns].copy()
    table["actual_price_만원"] = actual
    table["predicted_price_만원"] = predicted
    table["error_만원"] = error
    table["abs_error_만원"] = np.abs(error)
    table["abs_error_%"] = table["abs_error_만원"] / table["actual_price_만원"] * 100
    table["actual_price"] = table["actual_price_만원"].map(format_manwon)
    table["predicted_price"] = table["predicted_price_만원"].map(format_manwon)
    table["price_difference"] = table["error_만원"].map(format_manwon)
    table["absolute_difference"] = table["abs_error_만원"].map(format_manwon)
    return table


def get_param_sets(mode, model_profile="baseline"):
    if mode == "quick":
        return {
            "raw": {"n_estimators": 250, "max_depth": 5, "learning_rate": 0.04, "subsample": 0.9, "colsample_bytree": 0.9, "reg_lambda": 2.0},
            "log": {"n_estimators": 250, "max_depth": 4, "learning_rate": 0.04, "subsample": 0.85, "colsample_bytree": 0.85, "reg_lambda": 2.0},
            "unit": {"n_estimators": 220, "max_depth": 4, "learning_rate": 0.045, "subsample": 0.85, "colsample_bytree": 0.85, "reg_lambda": 2.0},
        }

    params = {
        "raw": {"n_estimators": 600, "max_depth": 5, "learning_rate": 0.025, "subsample": 0.9, "colsample_bytree": 0.9, "reg_lambda": 2.0},
        "log": {"n_estimators": 600, "max_depth": 4, "learning_rate": 0.025, "subsample": 0.85, "colsample_bytree": 0.85, "reg_lambda": 2.0},
        "unit": {"n_estimators": 500, "max_depth": 4, "learning_rate": 0.03, "subsample": 0.85, "colsample_bytree": 0.85, "reg_lambda": 2.0},
    }
    if model_profile == "deeper":
        params["raw"].update(max_depth=7, min_child_weight=3, reg_lambda=3.0)
        params["log"].update(max_depth=6, min_child_weight=3, reg_lambda=3.0)
        params["unit"].update(max_depth=6, min_child_weight=3, reg_lambda=3.0)
    elif model_profile == "regularized":
        params["raw"].update(
            n_estimators=800,
            max_depth=3,
            min_child_weight=5,
            reg_lambda=5.0,
            reg_alpha=1.0,
        )
        params["log"].update(
            n_estimators=800,
            max_depth=3,
            min_child_weight=5,
            reg_lambda=5.0,
            reg_alpha=1.0,
        )
        params["unit"].update(
            n_estimators=700,
            max_depth=3,
            min_child_weight=5,
            reg_lambda=5.0,
            reg_alpha=1.0,
        )
    return params


def predict_bundle(bundle, x):
    raw_pred = np.maximum(pipeline_predict(bundle["raw_pipeline"], x), 0)
    log_pred = np.maximum(np.expm1(pipeline_predict(bundle["log_pipeline"], x)), 0)
    unit_pred = pipeline_predict(bundle["unit_pipeline"], x)
    unit_price_pred = np.maximum(unit_pred * x["total_area"].values, 0)
    a, b, c = bundle["best_weights"]
    price_pred = np.maximum(a * raw_pred + b * log_pred + c * unit_price_pred, 0)
    if bundle.get("calibrator") is not None:
        calibrated_pred = bundle["calibrator"].predict(price_pred.reshape(-1, 1))
        strength = bundle.get("calibration_strength", 0.0)
        price_pred = (1 - strength) * price_pred + strength * calibrated_pred
    if bundle.get("residual_pipeline") is not None:
        residual_pred = pipeline_predict(bundle["residual_pipeline"], x)
        if bundle.get("positive_residual_only", False):
            residual_pred = np.maximum(residual_pred, 0)
        residual_gate = bundle.get("residual_gate_만원", 0.0)
        residual_pred = np.where(price_pred >= residual_gate, residual_pred, 0)
        price_pred = price_pred + bundle.get("residual_strength", 0.0) * residual_pred
    return np.maximum(price_pred, 0)


def train_type_bundle(
    train_df,
    mode,
    device,
    high_price_threshold,
    high_price_weight,
    scale_high_price_weight,
    risk_segment_weight,
    train_outlier_quantile,
    calibration_strength,
    residual_strength,
    residual_gate,
    positive_residual_only,
    model_profile,
):
    x_train = train_df[BASE_FEATURES]
    y_train_raw = train_df["price"]
    y_train_log = np.log1p(train_df["price"])
    y_train_unit = train_df["price_per_total_area"]
    weight_base_year = train_df["trade_year"].min()
    sample_weight = 0.65 + 0.35 * (
        (train_df["trade_year"] - weight_base_year)
        / max(1, train_df["trade_year"].max() - weight_base_year)
    )
    high_price_mask = train_df["price"] >= high_price_threshold
    if scale_high_price_weight:
        high_price_multiplier = np.where(
            high_price_mask,
            np.minimum(
                high_price_weight * train_df["price"] / high_price_threshold,
                high_price_weight * 2,
            ),
            1.0,
        )
    else:
        high_price_multiplier = np.where(high_price_mask, high_price_weight, 1.0)
    sample_weight = sample_weight * high_price_multiplier
    risk_segment_mask = (
        train_df["dong"].isin(HIGH_ERROR_DONGS)
        & train_df["house_type"].isin(["단독", "다가구"])
        & (train_df["price"] >= 100_000)
    )
    sample_weight = sample_weight * np.where(risk_segment_mask, risk_segment_weight, 1.0)
    params = get_param_sets(mode, model_profile=model_profile)
    weight_candidates = [
        (raw_weight / 10, log_weight / 10, unit_weight / 10)
        for raw_weight in range(11)
        for log_weight in range(11 - raw_weight)
        for unit_weight in [10 - raw_weight - log_weight]
    ]

    cv = TimeSeriesSplit(n_splits=3 if mode == "quick" else 5)
    weight_scores = {w: [] for w in weight_candidates}
    fold_predictions = []

    for fold, (train_idx, valid_idx) in enumerate(cv.split(x_train), start=1):
        x_cv_train = x_train.iloc[train_idx]
        x_cv_valid = x_train.iloc[valid_idx]
        w_cv_train = sample_weight.iloc[train_idx]

        raw_pipeline = build_pipeline(params["raw"], device)
        log_pipeline = build_pipeline(params["log"], device)
        unit_pipeline = build_pipeline(params["unit"], device)

        raw_pipeline.fit(
            x_cv_train,
            y_train_raw.iloc[train_idx],
            target_encoder__sample_weight=w_cv_train,
            model__sample_weight=w_cv_train,
        )
        log_pipeline.fit(
            x_cv_train,
            y_train_log.iloc[train_idx],
            target_encoder__sample_weight=w_cv_train,
            model__sample_weight=w_cv_train,
        )
        unit_pipeline.fit(
            x_cv_train,
            y_train_unit.iloc[train_idx],
            target_encoder__sample_weight=w_cv_train,
            model__sample_weight=w_cv_train,
        )

        raw_pred = np.maximum(pipeline_predict(raw_pipeline, x_cv_valid), 0)
        log_pred = np.maximum(np.expm1(pipeline_predict(log_pipeline, x_cv_valid)), 0)
        unit_pred = pipeline_predict(unit_pipeline, x_cv_valid)
        unit_price_pred = np.maximum(unit_pred * x_cv_valid["total_area"].values, 0)
        fold_predictions.append((valid_idx, raw_pred, log_pred, unit_price_pred))

        for weights in weight_candidates:
            a, b, c = weights
            price_pred = np.maximum(a * raw_pred + b * log_pred + c * unit_price_pred, 0)
            actual_price = train_df["price"].iloc[valid_idx]
            weight_scores[weights].append(
                np.sqrt(mean_squared_error(actual_price, price_pred))
            )

        print(f"fold {fold} done")

    best_weights = min(weight_scores, key=lambda w: np.mean(weight_scores[w]))
    a, b, c = best_weights
    oof_pred = np.full(len(train_df), np.nan, dtype=float)
    for valid_idx, raw_pred, log_pred, unit_price_pred in fold_predictions:
        oof_pred[valid_idx] = np.maximum(
            a * raw_pred + b * log_pred + c * unit_price_pred,
            0,
        )

    oof_abs_error = np.abs(oof_pred - y_train_raw.to_numpy())
    oof_valid_mask = np.isfinite(oof_abs_error)
    outlier_threshold = float(
        np.quantile(oof_abs_error[oof_valid_mask], train_outlier_quantile)
    )
    outlier_mask = oof_valid_mask & (oof_abs_error > outlier_threshold)
    fit_mask = ~outlier_mask
    x_fit = x_train.loc[fit_mask]
    y_fit_raw = y_train_raw.loc[fit_mask]
    y_fit_log = y_train_log.loc[fit_mask]
    y_fit_unit = y_train_unit.loc[fit_mask]
    fit_weight = sample_weight.loc[fit_mask]
    calibrator = LinearRegression()
    calibrator.fit(
        oof_pred[oof_valid_mask].reshape(-1, 1),
        y_train_raw.to_numpy()[oof_valid_mask],
    )
    residual_pipeline = build_pipeline(params["log"], device)
    residual_target = (
        y_train_raw.to_numpy()[oof_valid_mask] - oof_pred[oof_valid_mask]
    )
    residual_pipeline.fit(
        x_train.loc[oof_valid_mask],
        residual_target,
        target_encoder__sample_weight=sample_weight.loc[oof_valid_mask],
        model__sample_weight=sample_weight.loc[oof_valid_mask],
    )

    final_raw_pipeline = build_pipeline(params["raw"], device)
    final_log_pipeline = build_pipeline(params["log"], device)
    final_unit_pipeline = build_pipeline(params["unit"], device)

    final_raw_pipeline.fit(
        x_fit,
        y_fit_raw,
        target_encoder__sample_weight=fit_weight,
        model__sample_weight=fit_weight,
    )
    final_log_pipeline.fit(
        x_fit,
        y_fit_log,
        target_encoder__sample_weight=fit_weight,
        model__sample_weight=fit_weight,
    )
    final_unit_pipeline.fit(
        x_fit,
        y_fit_unit,
        target_encoder__sample_weight=fit_weight,
        model__sample_weight=fit_weight,
    )

    return {
        "raw_pipeline": final_raw_pipeline,
        "log_pipeline": final_log_pipeline,
        "unit_pipeline": final_unit_pipeline,
        "best_weights": best_weights,
        "calibrator": calibrator,
        "calibrator_intercept": float(calibrator.intercept_),
        "calibrator_slope": float(calibrator.coef_[0]),
        "calibration_strength": float(calibration_strength),
        "residual_pipeline": residual_pipeline,
        "residual_strength": float(residual_strength),
        "residual_gate_만원": float(residual_gate),
        "positive_residual_only": bool(positive_residual_only),
        "weight_result": {str(k): float(np.mean(v)) for k, v in weight_scores.items()},
        "train_rows": int(len(train_df)),
        "fit_train_rows": int(fit_mask.sum()),
        "train_outlier_quantile": float(train_outlier_quantile),
        "train_outlier_threshold_만원": outlier_threshold,
        "removed_train_indices": train_df.index[outlier_mask].tolist(),
        "removed_train_oof_predictions": oof_pred[outlier_mask].tolist(),
        "removed_train_oof_abs_errors": oof_abs_error[outlier_mask].tolist(),
        "high_price_train_rows": int(high_price_mask.sum()),
        "risk_segment_train_rows": int(risk_segment_mask.sum()),
    }


def compute_baseline_lookup(df):
    """훈련 데이터에서 추론용 베이스라인 통계 테이블 생성.

    dong+house_type → gu+house_type → house_type → global 순서의 4단계 fallback 구조.
    """
    lookup = {}

    grp = df.groupby(["dong", "house_type"])["baseline_unit_price"].agg(["median", "count"])
    lookup["dong_house_type"] = {
        (idx[0], idx[1]): {"unit_price": float(row["median"]), "count": int(row["count"]), "source_level": 3.0}
        for idx, row in grp.iterrows()
        if not np.isnan(row["median"])
    }

    grp = df.groupby(["gu", "house_type"])["baseline_unit_price"].agg(["median", "count"])
    lookup["gu_house_type"] = {
        (idx[0], idx[1]): {"unit_price": float(row["median"]), "count": int(row["count"]), "source_level": 2.0}
        for idx, row in grp.iterrows()
        if not np.isnan(row["median"])
    }

    grp = df.groupby("house_type")["baseline_unit_price"].agg(["median", "count"])
    lookup["house_type"] = {
        idx: {"unit_price": float(row["median"]), "count": int(row["count"]), "source_level": 1.0}
        for idx, row in grp.iterrows()
        if not np.isnan(row["median"])
    }

    global_median = df["baseline_unit_price"].median()
    lookup["global"] = {
        "unit_price": float(global_median) if not np.isnan(global_median) else 0.0,
        "count": int(len(df)),
        "source_level": 0.0,
    }

    return lookup


def compute_road_condition_lookup(df):
    """dong+house_type별 최빈 도로조건 저장."""
    result = {}
    for (dong, house_type), group in df.groupby(["dong", "house_type"]):
        vc = group["road_condition"].value_counts()
        if len(vc) > 0:
            result[(dong, house_type)] = vc.index[0]
    return result


def train_ensemble(
    data,
    mode,
    device,
    high_price_threshold,
    high_price_weight,
    scale_high_price_weight,
    risk_segment_weight,
    train_outlier_quantile,
    calibration_strength,
    residual_strength,
    residual_gate,
    positive_residual_only,
    model_profile,
):
    train_df, test_df = time_based_split(data, test_size=TEST_SIZE)
    baseline_lookup = compute_baseline_lookup(train_df)
    road_condition_lookup = compute_road_condition_lookup(train_df)
    params = get_param_sets(mode, model_profile=model_profile)
    x_train = train_df[BASE_FEATURES]
    x_test = test_df[BASE_FEATURES]
    y_test = test_df["price"]
    bundle = train_type_bundle(
        train_df,
        mode,
        device,
        high_price_threshold,
        high_price_weight,
        scale_high_price_weight,
        risk_segment_weight,
        train_outlier_quantile,
        calibration_strength,
        residual_strength,
        residual_gate,
        positive_residual_only,
        model_profile,
    )
    train_pred = predict_bundle(bundle, x_train)
    test_pred = predict_bundle(bundle, x_test)

    train_metrics = evaluate(train_df["price"], train_pred, train_df["baseline_price"].values)
    test_metrics = evaluate(y_test, test_pred, x_test["baseline_price"].values)
    rmse_impact = summarize_rmse_impact(y_test, test_pred, high_price_threshold)
    high_price_test_mask = test_df["price"] >= high_price_threshold
    high_price_test_metrics = (
        {
            **evaluate(
                test_df.loc[high_price_test_mask, "price"],
                test_pred[high_price_test_mask.to_numpy()],
            ),
            "rows": int(high_price_test_mask.sum()),
        }
        if high_price_test_mask.any()
        else None
    )
    train_baseline_only_metrics = evaluate(
        train_df["price"],
        x_train["baseline_price"].values,
        x_train["baseline_price"].values,
    )
    baseline_only_metrics = evaluate(y_test, x_test["baseline_price"].values, x_test["baseline_price"].values)
    train_price_summary = summarize_price_level(
        train_df["price"],
        train_pred,
        x_train["baseline_price"].values,
    )
    test_price_summary = summarize_price_level(
        y_test,
        test_pred,
        x_test["baseline_price"].values,
    )
    evaluation_tables = {
        "train": make_evaluation_table(train_df, train_pred),
        "test": make_evaluation_table(test_df, test_pred),
    }
    removed_outliers = train_df.loc[bundle["removed_train_indices"]].copy()
    removed_outliers["oof_predicted_price_만원"] = bundle["removed_train_oof_predictions"]
    removed_outliers["oof_abs_error_만원"] = bundle["removed_train_oof_abs_errors"]
    removed_outliers["actual_price"] = removed_outliers["price"].map(format_manwon)
    removed_outliers["oof_predicted_price"] = removed_outliers[
        "oof_predicted_price_만원"
    ].map(format_manwon)
    removed_outliers["oof_absolute_difference"] = removed_outliers[
        "oof_abs_error_만원"
    ].map(format_manwon)
    evaluation_tables["removed_train_outliers"] = removed_outliers.sort_values(
        "oof_abs_error_만원",
        ascending=False,
    )

    artifact = {
        **bundle,
        "smoothing": SMOOTHING,
        "target_mode": TARGET_MODE,
        "target_encode_cols": TARGET_ENCODE_COLS,
        "num_features": NUM_FEATURES,
        "cat_features": CAT_FEATURES,
        "base_features": BASE_FEATURES,
        "baseline_lookup": baseline_lookup,
        "road_condition_lookup": road_condition_lookup,
        "high_price_threshold_만원": float(high_price_threshold),
        "high_price_weight": float(high_price_weight),
        "risk_segment_weight": float(risk_segment_weight),
        "high_price_weight_mode": (
            "price_scaled_capped" if scale_high_price_weight else "fixed"
        ),
        "train_outlier_quantile": float(train_outlier_quantile),
        "removed_train_rows": len(bundle["removed_train_indices"]),
        "train_outlier_threshold_만원": bundle["train_outlier_threshold_만원"],
        "metrics": test_metrics,
        "high_price_test_metrics": high_price_test_metrics,
        "rmse_impact": rmse_impact,
        "train_metrics": train_metrics,
        "train_baseline_only_metrics": train_baseline_only_metrics,
        "baseline_only_metrics": baseline_only_metrics,
        "train_price_summary": train_price_summary,
        "test_price_summary": test_price_summary,
    }

    result = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "mode": mode,
        "device": device,
        "rows_total": int(len(data)),
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "test_period": [int(test_df["contract_ym"].min()), int(test_df["contract_ym"].max())],
        "model_type": "direct_price_xgb_with_historical_baseline_features",
        "target_mode": TARGET_MODE,
        "params": params,
        "model_profile": model_profile,
        "weight_selection_metric": "RMSE_만원",
        "high_price_threshold_만원": float(high_price_threshold),
        "high_price_weight": float(high_price_weight),
        "risk_segment_weight": float(risk_segment_weight),
        "high_price_weight_mode": (
            "price_scaled_capped" if scale_high_price_weight else "fixed"
        ),
        "high_price_train_rows": bundle["high_price_train_rows"],
        "risk_segment_train_rows": bundle["risk_segment_train_rows"],
        "train_outlier_quantile": float(train_outlier_quantile),
        "removed_train_rows": len(bundle["removed_train_indices"]),
        "train_outlier_threshold_만원": bundle["train_outlier_threshold_만원"],
        "best_weights": list(bundle["best_weights"]),
        "weight_result": bundle["weight_result"],
        "metrics": test_metrics,
        "high_price_test_metrics": high_price_test_metrics,
        "rmse_impact": rmse_impact,
        "train_metrics": train_metrics,
        "train_baseline_only_metrics": train_baseline_only_metrics,
        "baseline_only_metrics": baseline_only_metrics,
        "train_price_summary": train_price_summary,
        "test_price_summary": test_price_summary,
        "r2_gap": float(train_metrics["R2"] - test_metrics["R2"]),
        "target_encode_cols": TARGET_ENCODE_COLS,
        "num_features": NUM_FEATURES,
        "cat_features": CAT_FEATURES,
        "base_features": BASE_FEATURES,
    }

    return artifact, result, evaluation_tables


def format_manwon(value):
    rounded_value = int(round(value))
    sign = "-" if rounded_value < 0 else ""
    amount = abs(rounded_value)
    eok, remainder = divmod(amount, 10_000)
    cheon, man = divmod(remainder, 1_000)

    parts = []
    if eok:
        parts.append(f"{eok:,}억")
    if cheon:
        parts.append(f"{cheon}천")
    if man or not parts:
        parts.append(f"{man:,}만원")

    return sign + " ".join(parts)


def make_console_summary(result):
    train_metrics = result["train_metrics"]
    test_metrics = result["metrics"]

    return {
        "Train": {
            "R2": round(train_metrics["R2"], 6),
            "MAE": format_manwon(train_metrics["MAE_만원"]),
            "actual_avg": format_manwon(train_metrics["Actual_mean_price_만원"]),
            "predicted_avg": format_manwon(train_metrics["Pred_mean_price_만원"]),
        },
        "Test": {
            "R2": round(test_metrics["R2"], 6),
            "MAE": format_manwon(test_metrics["MAE_만원"]),
            "actual_avg": format_manwon(test_metrics["Actual_mean_price_만원"]),
            "predicted_avg": format_manwon(test_metrics["Pred_mean_price_만원"]),
        },
    }

def write_summary(path, result):
    metrics = result["metrics"]
    train_metrics = result["train_metrics"]
    impact = result["rmse_impact"]
    filtered = impact["filtered_test_excluding_top_10pct"]
    content = f"""# Experiment Summary

## Latest Run

- Mode: `{result["mode"]}`
- Device: `{result["device"]}`
- Model: `{result["model_type"]}`
- Target mode: `{result["target_mode"]}`
- Rows: `{result["rows_total"]:,}` total / `{result["train_rows"]:,}` train / `{result["test_rows"]:,}` test
- Test period: `{result["test_period"][0]}` ~ `{result["test_period"][1]}`
- Best weights: `{result["best_weights"]}`
- High-price threshold: `{format_manwon(result["high_price_threshold_만원"])}`
- High-price weight: `{result["high_price_weight"]:.2f}`
- High-price train rows: `{result["high_price_train_rows"]:,}`
- Trim price quantiles: `{result["trim_price_quantiles"]}`
- Train outlier quantile: `{result["train_outlier_quantile"]:.4f}`
- Removed Train rows: `{result["removed_train_rows"]:,}`
- Train outlier threshold: `{format_manwon(result["train_outlier_threshold_만원"])}`

## Evaluation Metrics

| Split | R2 | 실제 평가 금액 평균 | 예측 금액 평균 | RMSE |
| --- | ---: | ---: | ---: | ---: |
| Train | `{train_metrics["R2"]:.6f}` | `{format_manwon(train_metrics["Actual_mean_price_만원"])}` | `{format_manwon(train_metrics["Pred_mean_price_만원"])}` | `{format_manwon(train_metrics["RMSE_만원"])}` |
| Test | `{metrics["R2"]:.6f}` | `{format_manwon(metrics["Actual_mean_price_만원"])}` | `{format_manwon(metrics["Pred_mean_price_만원"])}` | `{format_manwon(metrics["RMSE_만원"])}` |

- R2 gap: `{result["r2_gap"]:.6f}`

## RMSE Impact

| Group | Rows | Actual average | RMSE |
| --- | ---: | ---: | ---: |
| Below high-price threshold | `{impact["regular_price_test"]["rows"]:,}` | `{impact["regular_price_test"]["actual_avg"]}` | `{impact["regular_price_test"]["RMSE"]}` |
| High-price group | `{impact["high_price_test"]["rows"]:,}` | `{impact["high_price_test"]["actual_avg"]}` | `{impact["high_price_test"]["RMSE"]}` |

- Top 10% error rows: `{impact["top_10pct_error_rows"]:,}`
- Top 10% squared-error share: `{impact["top_10pct_squared_error_share_%"]:.2f}%`

## Filtered Test Metrics

| Condition | Rows used | Rows removed | R2 | Actual average | Predicted average | RMSE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Excluding top 10% error rows | `{filtered["rows"]:,}` | `{filtered["removed_rows"]:,}` | `{filtered["R2"]:.6f}` | `{filtered["actual_avg"]}` | `{filtered["predicted_avg"]}` | `{filtered["RMSE"]}` |

## Changes In This Script

- Predicts direct absolute price.
- Uses historical local baseline price as helper features.
- Historical baseline uses only prior transactions to reduce target leakage.
- Baseline hierarchy: `dong+house_type` -> `gu+house_type` -> `house_type` -> global prior mean.
"""
    path.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        default="최종_용인_실거래가_통합_결측채움.csv",
        help="Training CSV path",
    )
    parser.add_argument("--output-dir", default="ai/training/outputs")
    parser.add_argument("--mode", choices=["quick", "full"], default="full")
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument(
        "--model-profile",
        choices=["baseline", "deeper", "regularized"],
        default="baseline",
    )
    parser.add_argument(
        "--high-price-threshold",
        type=float,
        default=200_000,
        help="High-price threshold in 만원. Default: 200000 (20억원).",
    )
    parser.add_argument(
        "--high-price-weight",
        type=float,
        default=2.0,
        help="Training weight multiplier for high-price rows. Default: 2.0.",
    )
    parser.add_argument(
        "--risk-segment-weight",
        type=float,
        default=1.0,
        help="Additional weight for known high-error dong/type rows above 10억원. Default: 1.0.",
    )
    parser.add_argument(
        "--train-outlier-quantile",
        type=float,
        default=1.0,
        help="Remove Train OOF residuals above this quantile. Default: 1.0 (disabled).",
    )
    parser.add_argument(
        "--scale-high-price-weight",
        action="store_true",
        help="Scale high-price weights by price, capped at twice the configured weight.",
    )
    parser.add_argument(
        "--trim-price-quantiles",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Remove the bottom/top 1%% price rows before training. Default: enabled.",
    )
    parser.add_argument(
        "--drop-suspected-duplicates",
        action="store_true",
        help="Drop rows with identical date, location, type, area, build year, and price.",
    )
    parser.add_argument(
        "--coord-cache",
        default="ai/training/yongin_coord_cache.csv",
        help="CSV cache with address_key, latitude, longitude. Created/updated when Kakao API key is available.",
    )
    parser.add_argument(
        "--kakao-api-key",
        default=None,
        help="Kakao REST API key. If omitted, KAKAO_REST_API_KEY environment variable is used.",
    )
    parser.add_argument(
        "--geocode-sleep",
        type=float,
        default=0.08,
        help="Sleep seconds between Kakao geocoding requests.",
    )
    parser.add_argument(
        "--coord-grid-size",
        type=float,
        default=0.005,
        help="Latitude/longitude grid size for coordinate group features. Default 0.005 degrees.",
    )
    parser.add_argument(
        "--calibration-strength",
        type=float,
        default=0.0,
        help="Blend strength for OOF linear calibration. Default: 0.0.",
    )
    parser.add_argument(
        "--residual-strength",
        type=float,
        default=0.0,
        help="Strength for the Train OOF residual correction model. Default: 0.0.",
    )
    parser.add_argument(
        "--residual-gate",
        type=float,
        default=100_000,
        help="Apply residual correction only above this predicted price in 만원.",
    )
    parser.add_argument(
        "--positive-residual-only",
        action="store_true",
        help="Apply only positive residual corrections.",
    )
    parser.add_argument(
        "--show-eval-samples",
        action="store_true",
        help="Print train/test row-level evaluation samples.",
    )
    args, _unknown = parser.parse_known_args()
    if args.high_price_threshold <= 0:
        parser.error("--high-price-threshold must be greater than 0.")
    if args.high_price_weight <= 0:
        parser.error("--high-price-weight must be greater than 0.")
    if args.risk_segment_weight <= 0:
        parser.error("--risk-segment-weight must be greater than 0.")
    if not 0.9 <= args.train_outlier_quantile <= 1.0:
        parser.error("--train-outlier-quantile must be between 0.9 and 1.0.")
    if not 0.0 <= args.calibration_strength <= 1.0:
        parser.error("--calibration-strength must be between 0.0 and 1.0.")
    if not 0.0 <= args.residual_strength <= 1.0:
        parser.error("--residual-strength must be between 0.0 and 1.0.")
    if args.residual_gate < 0:
        parser.error("--residual-gate must be 0 or greater.")
    if args.coord_grid_size <= 0:
        parser.error("--coord-grid-size must be greater than 0.")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.data)
    df = attach_coordinates(
        df,
        coord_cache_path=args.coord_cache,
        kakao_api_key=args.kakao_api_key,
        geocode_sleep=args.geocode_sleep,
    )
    data = prepare_dataframe(
        df,
        trim_price_quantiles=args.trim_price_quantiles,
        drop_suspected_duplicates=args.drop_suspected_duplicates,
        coord_grid_size=args.coord_grid_size,
    )
    artifact, result, evaluation_tables = train_ensemble(
        data,
        mode=args.mode,
        device=args.device,
        high_price_threshold=args.high_price_threshold,
        high_price_weight=args.high_price_weight,
        scale_high_price_weight=args.scale_high_price_weight,
        risk_segment_weight=args.risk_segment_weight,
        train_outlier_quantile=args.train_outlier_quantile,
        calibration_strength=args.calibration_strength,
        residual_strength=args.residual_strength,
        residual_gate=args.residual_gate,
        positive_residual_only=args.positive_residual_only,
        model_profile=args.model_profile,
    )
    result["trim_price_quantiles"] = args.trim_price_quantiles
    result["drop_suspected_duplicates"] = args.drop_suspected_duplicates
    result["calibration_strength"] = args.calibration_strength
    result["residual_strength"] = args.residual_strength
    result["residual_gate_만원"] = args.residual_gate
    result["positive_residual_only"] = args.positive_residual_only
    result["coord_cache"] = args.coord_cache
    result["coord_grid_size"] = args.coord_grid_size
    result["coordinate_missing_rows"] = int(data["coord_missing"].sum())
    artifact["trim_price_quantiles"] = args.trim_price_quantiles
    artifact["coord_grid_size"] = args.coord_grid_size

    model_path = output_dir / "xgb_price_unit_ensemble_model.joblib"
    metrics_path = output_dir / "xgb_price_unit_ensemble_metrics.json"
    summary_path = output_dir / "experiment_summary.md"
    train_comparison_path = output_dir / "train_price_comparison.csv"
    test_comparison_path = output_dir / "test_price_comparison.csv"
    excluded_test_path = output_dir / "test_excluded_top_10pct_errors.csv"
    removed_outliers_path = output_dir / "train_removed_outliers.csv"

    joblib.dump(artifact, model_path)
    metrics_path.write_text(
        json.dumps(make_console_summary(result), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_summary(summary_path, result)
    evaluation_tables["train"].sort_values("abs_error_만원", ascending=False).to_csv(
        train_comparison_path,
        index=False,
        encoding="utf-8-sig",
    )
    evaluation_tables["test"].sort_values("abs_error_만원", ascending=False).to_csv(
        test_comparison_path,
        index=False,
        encoding="utf-8-sig",
    )
    evaluation_tables["test"].sort_values("abs_error_만원", ascending=False).head(
        result["rmse_impact"]["filtered_test_excluding_top_10pct"]["removed_rows"]
    ).to_csv(
        excluded_test_path,
        index=False,
        encoding="utf-8-sig",
    )
    evaluation_tables["removed_train_outliers"].to_csv(
        removed_outliers_path,
        index=False,
        encoding="utf-8-sig",
    )

    print("===== Evaluation Summary =====")
    print(json.dumps(make_console_summary(result), ensure_ascii=False, indent=2))
    if args.show_eval_samples:
        print("===== Train Evaluation Sample =====")
        print(evaluation_tables["train"].head(20).to_string(index=False))
        print("===== Test Evaluation Sample =====")
        print(evaluation_tables["test"].head(20).to_string(index=False))
    print(f"model saved: {model_path}")
    print(f"metrics saved: {metrics_path}")
    print(f"summary saved: {summary_path}")
    print(f"train comparison saved: {train_comparison_path}")
    print(f"test comparison saved: {test_comparison_path}")
    print(f"excluded test errors saved: {excluded_test_path}")
    print(f"removed train outliers saved: {removed_outliers_path}")

import sys

sys.argv = [
    "colab_run.py",
    "--data", "최종_용인_실거래가_통합_결측채움.csv",
    "--output-dir", "ai/training/outputs_coord_test",
    "--mode", "full",
    "--device", "cpu",
    "--train-outlier-quantile", "1.0",
    "--risk-segment-weight", "1.0",
    "--calibration-strength", "0.0",
    "--residual-strength", "0.0",
    "--coord-cache", "ai/training/yongin_coord_cache.csv",
    "--coord-grid-size", "0.005"
]

if __name__ == "__main__":
    main()
