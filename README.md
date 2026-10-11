# Yongin Rental Deposit Risk Analysis

> A web service that estimates how much of a tenant's rental deposit is recoverable, using real-estate transaction data from Yongin, Korea and an XGBoost ensemble price prediction model.

![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Spring_Boot-4.0-6DB33F?logo=springboot&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-2.1-EB5B26)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)

## Table of Contents

1. [Overview](#1-overview)
2. [Features](#2-features)
3. [Architecture](#3-architecture)
4. [Tech Stack](#4-tech-stack)
5. [Project Structure](#5-project-structure)
6. [AI Price Prediction Model](#6-ai-price-prediction-model)
7. [Getting Started](#7-getting-started)
8. [API Reference](#8-api-reference)
9. [Deployment](#9-deployment)
10. [Retraining the Model](#10-retraining-the-model)
11. [Limitations and Future Work](#11-limitations-and-future-work)

---

## 1. Overview

When a rented house goes to auction, tenants often cannot tell how much of their deposit they will get back.
This service **predicts the market price of the house with an AI model**, then calculates
**expected auction price → senior claims (mortgage, prior tenants) → small-tenant priority repayment**
in order, and reports the recoverable amount and a risk level.

- **Region**: Yongin-si, Gyeonggi-do (Suji-gu, Giheung-gu, Cheoin-gu)
- **Housing type**: Detached and multi-household houses (단독 / 다가구)
- **Data**: MOLIT (Ministry of Land, Infrastructure and Transport) real transaction price records

## 2. Features

| Feature | Description |
| --- | --- |
| Deposit risk analysis | Takes address, housing type, area, deposit, mortgage and prior-tenant info and returns the recoverable amount and risk level |
| AI price prediction | Predicts the sale price with an XGBoost ensemble and derives the expected auction price |
| Priority repayment | Simulates distribution with small-tenant thresholds and priority repayment amounts |
| Regional statistics | Rental transaction stats, yearly trends and deposit by area band for each district/neighborhood |

## 3. Architecture

```text
┌──────────────────┐      ┌──────────────────────┐          ┌───────────────────────┐
│  React Frontend  │ ───▶ │  Spring Boot Backend │ ───────▶ │  FastAPI AI Server    │
│  (Render)        │ /api │  (Railway)           │ /predict │  (Render)             │
└──────────────────┘      └──────────┬───────────┘          │  └─ joblib model      │
                                     │                      └───────────────────────┘
                                     ▼
                              ┌─────────────┐
                              │   MySQL     │  rental transaction data
                              └─────────────┘
```

1. The user enters house and contract information in the frontend.
2. The backend calls the AI server's `/predict` endpoint to get the predicted price.
3. The backend computes auction price, distribution and recovery risk, and returns the result.
4. Regional statistics are aggregated by the backend from MySQL.

## 4. Tech Stack

| Layer | Technologies |
| --- | --- |
| Frontend | React 18, TypeScript, Vite 6, React Router 7, Recharts, Tailwind CSS 4 |
| Backend | Java 17, Spring Boot 4, Spring JDBC, MySQL |
| AI Server | Python, FastAPI, Uvicorn, Pydantic |
| Machine Learning | XGBoost 2.1, scikit-learn 1.6, pandas, NumPy, joblib |
| Data | MOLIT real transaction data, Kakao Local API (geocoding) |
| Deployment | Render (frontend, AI server), Railway (backend) |

## 5. Project Structure

```text
estate_price_prediction/
├── frontend/                              # React + Vite SPA
│   ├── src/
│   │   ├── main.tsx                       # entry point
│   │   ├── App.tsx                        # root component
│   │   ├── router.tsx                     # route definitions
│   │   ├── pages/                         # Landing, AnalysisInput, Results, RegionalData
│   │   ├── components/layout/             # shared layout (navigation)
│   │   ├── services/api.ts                # backend API client
│   │   ├── styles/                        # Tailwind and theme
│   │   └── vite-env.d.ts                  # env variable types
│   ├── .env.example
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── backend/                               # Spring Boot REST API
│   ├── src/main/java/com/yongin/backend/
│   │   ├── BackendApplication.java
│   │   ├── config/                        # CORS configuration
│   │   ├── controller/                    # REST controllers
│   │   ├── service/                       # business logic (risk analysis, trade stats)
│   │   ├── client/                        # AI server HTTP client
│   │   └── dto/
│   │       ├── analysis/                  # risk analysis request / response
│   │       ├── prediction/                # AI prediction request / response
│   │       └── trade/                     # trade statistics
│   ├── src/main/resources/application.properties
│   ├── src/test/java/...
│   ├── build.gradle
│   └── Dockerfile
│
├── ai/                                    # AI server and model training
│   ├── app/                               # FastAPI application
│   │   ├── main.py                        # app factory
│   │   ├── api/routes.py                  # /health, /predict
│   │   ├── core/config.py                 # model path and constants
│   │   ├── schemas/prediction.py          # request / response schemas
│   │   └── services/
│   │       ├── features.py                # feature engineering (same rules as training)
│   │       └── predictor.py               # model loading and ensemble inference
│   ├── models/                            # trained model artifact (.joblib)
│   ├── training/
│   │   ├── train_model.py                 # preprocessing, training, evaluation, export
│   │   └── requirements.txt
│   └── requirements.txt                   # AI server dependencies
│
├── app.py                                 # Render entrypoint (re-exports ai.app.main:app)
├── requirements.txt                       # Render entrypoint dependencies (-r ai/requirements.txt)
└── README.md
```

## 6. AI Price Prediction Model

### 6.1 Summary

| Item | Value |
| --- | --- |
| Task | Regression — sale price of detached / multi-household houses (unit: 10,000 KRW) |
| Algorithm | Ensemble of three XGBoost regressors (price / log price / price per area) |
| Training script | [ai/training/train_model.py](ai/training/train_model.py) |
| Model artifact | `ai/models/xgb_price_unit_ensemble_model.joblib` |
| Data split | Time-based split by contract date (oldest 80% train / latest 20% test) |
| Validation | `TimeSeriesSplit` 5-fold cross-validation |

### 6.2 Training Pipeline

```text
Raw CSV (real transactions)
  │
  ├─ 1. Geocoding           Kakao Local API (address → lat/lon), cached in CSV
  ├─ 2. Cleaning            drop missing / non-positive values, building age 0–150,
  │                         floor area ratio 0–20, trim top/bottom 1% prices
  ├─ 3. Feature engineering area, age, time, coordinates, region categories,
  │                         historical price baseline
  ├─ 4. Time-based split    sort by contract date → first 80% train / last 20% test
  ├─ 5. Ensemble training   Raw / Log / Unit XGBoost × TimeSeriesSplit 5-fold
  ├─ 6. Weight search       grid search of blend weights on OOF predictions (min RMSE)
  ├─ 7. Final fit           refit the three pipelines on the full training set
  └─ 8. Export              pipelines + weights + inference lookup tables → joblib bundle
```

### 6.3 Data Preprocessing

| Step | Details |
| --- | --- |
| Date parsing | `계약년월` → `trade_year`, `trade_month`; `계약일` → `trade_day` |
| Missing / invalid rows | Drop rows with missing price, area or date, and rows where price / floor area / land area ≤ 0 |
| Build year | `1900` is treated as a missing marker → `NaN` plus a `build_year_missing` flag |
| Building age | Drop rows where `trade_year - build_year` is outside 0–150 |
| Floor area ratio | Drop rows where `floor area / land area` is outside 0–20 |
| Price trimming | Remove the top and bottom 1% of prices (`--trim-price-quantiles`, on by default) |
| Category cleanup | Empty, `-` and `nan` values are unified to `기타` (other) |

### 6.4 Feature Engineering

**32 input features** (23 numeric + 9 categorical); the pipeline adds 8 target-encoded features internally.

| Group | Features | Description |
| --- | --- | --- |
| Area | `total_area`, `land_area`, `log_total_area`, `log_land_area` | Floor / land area and log transforms |
| Area ratios | `far`, `land_to_total_ratio`, `total_to_land_ratio` | Floor area ratio and inverses |
| Age | `build_year`, `building_age`, `build_year_missing` | Build year and age at trade time |
| Time | `trade_year`, `trade_month`, `trade_day` | Trade date (captures market trend) |
| Coordinates | `latitude`, `longitude`, `coord_missing`, `lat_lon_interaction`, `lat_sq`, `lon_sq` | Location and non-linear terms |
| Price baseline | `baseline_unit_price`, `baseline_price`, `baseline_count`, `baseline_source_level` | Historical regional unit price (see 6.5) |
| Region | `gu`, `dong`, `road_condition`, `house_type` | District, neighborhood, road condition, housing type |
| Cross categories | `gu_house_type`, `dong_house_type`, `dong_road` | Region × type / road combinations |
| Coordinate grid | `coord_grid`, `coord_grid_house_type` | 0.005° (~500 m) grid cell and grid × type |

### 6.5 Key Techniques

#### (1) Historical price baseline (leakage-free)

The average unit price of the same area is the strongest price signal, but a plain group mean leaks
**the row's own price and future trades**. To prevent this, rows are sorted by contract date and the
baseline is computed from **prior trades only** using a cumulative mean (`cumsum - self`).

Sparse groups fall back hierarchically:

| Level | Group | Used when |
| :---: | --- | --- |
| 3 | `dong + house_type` | ≥ 3 prior trades |
| 2 | `gu + house_type` | ≥ 5 prior trades |
| 1 | `house_type` | ≥ 10 prior trades |
| 0 | global | otherwise |

`baseline_source_level` is also fed to the model so it can learn how reliable the baseline is.
At inference time, a precomputed **lookup table (`baseline_lookup`)** stored in the model bundle is queried with the same fallback order.

#### (2) Smoothed target encoding (`MultiTargetEncoder`)

For 8 high-cardinality region categories (neighborhood, coordinate grid, etc.), a **Bayesian-smoothed target mean** is computed:

```text
encoded = (mean × count + global_mean × m) / (count + m),   m = 20
```

Rare categories shrink toward the global mean, reducing overfitting. The encoder lives inside the sklearn
`Pipeline`, so it is fitted only on training data in every CV fold.

#### (3) Preprocessing pipeline

```text
Pipeline
 ├─ target_encoder : MultiTargetEncoder (8 categories → *_target_avg)
 ├─ preprocess     : ColumnTransformer
 │                    ├─ num : SimpleImputer(median)
 │                    └─ cat : SimpleImputer(most_frequent) → OneHotEncoder(min_frequency=50, handle_unknown="ignore")
 └─ model          : XGBRegressor(tree_method="hist")
```

Because preprocessing and model are saved as one pipeline, **feature order and encoding at inference are guaranteed to match training**.

#### (4) Three-target ensemble

Three models are trained on the same features with different targets and blended:

| Model | Target | Role | Key hyperparameters |
| --- | --- | --- | --- |
| Raw | `price` | Minimize absolute price error | n_estimators=600, max_depth=5, lr=0.025 |
| Log | `log1p(price)` | Stabilize relative error on low prices | n_estimators=600, max_depth=4, lr=0.025 |
| Unit | `price / total_area` | Learn unit price, then multiply by area | n_estimators=500, max_depth=4, lr=0.03 |

Shared: `subsample 0.85–0.9`, `colsample_bytree 0.85–0.9`, `reg_lambda 2.0`, `random_state 42`

```text
final_price = a × Raw + b × expm1(Log) + c × (Unit × total_area),   a + b + c = 1
```

The weights `(a, b, c)` are chosen from 66 combinations (step 0.1) by **mean RMSE of TimeSeriesSplit OOF predictions**.
The deployed model uses **`(0.5, 0.0, 0.5)`** — an equal blend of the Raw and Unit models.

#### (5) Sample weighting

- **Recency weight**: increases linearly from 0.65 to 1.0 by trade year (emphasizes the recent market)
- **High-price weight**: ×2.0 for trades ≥ 2B KRW (reduces under-prediction in the sparse high-price range)

#### (6) Optional post-processing (disabled)

The training script also implements OOF linear calibration (`--calibration-strength`), a residual correction model
(`--residual-strength`) and OOF outlier removal (`--train-outlier-quantile`). All are disabled (0.0 / 1.0) in the deployed model.

### 6.6 Performance

Evaluated on the **latest 20% of trades (test set)** in time order. Training set: 4,309 trades.

| Metric | Train | Test | Baseline only (Test) |
| --- | ---: | ---: | ---: |
| R² | 0.915 | **0.787** | 0.417 |
| MAE | 78.3M KRW | **160.3M KRW** | 233.8M KRW |
| RMSE | 111.5M KRW | **227.9M KRW** | 377.5M KRW |
| Median AE | 54.1M KRW | **117.9M KRW** | 147.9M KRW |
| MAPE | 15.2% | **25.8%** | 37.1% |
| Mean actual price | 642.2M KRW | 779.0M KRW | — |
| Mean predicted price | 644.5M KRW | 784.3M KRW | 839.7M KRW |

- Compared to the regional-baseline-only predictor: **R² 0.42 → 0.79**, **MAE −31%**
- Mean prediction closely matches the mean actual price (mean error ≈ +5.3M KRW), indicating low overall bias
- Trades ≥ 2B KRW (34 in test) are **under-predicted** by about 472M KRW on average

### 6.7 Inference

The server loads the joblib bundle **without retraining**. [ai/app/services/features.py](ai/app/services/features.py)
builds features with the same rules as training.

| Input | Handling |
| --- | --- |
| `address` | Extracts district (`구`) and neighborhood (`동/읍/면/리`) |
| `building_type` | Mapped to `house_type` |
| `road_condition` | Users rarely know it, so the most frequent value per neighborhood + type (`road_condition_lookup`) is used |
| `latitude`, `longitude` | If omitted, Yongin's center coordinate is used and `coord_missing=1` |
| Baseline features | Looked up from `baseline_lookup` with hierarchical fallback |

Bundle contents:

```text
{
  raw_pipeline, log_pipeline, unit_pipeline,   # preprocessing + XGBoost pipelines
  best_weights,                                 # ensemble weights
  baseline_lookup, road_condition_lookup,       # inference lookup tables
  calibrator, residual_pipeline, ...            # optional post-processing
  metrics, train_metrics, ...                   # evaluation results at training time
}
```

## 7. Getting Started

### 7.1 Prerequisites

- Python 3.11+
- Java 17
- Node.js 18+
- MySQL 8

### 7.2 AI Server

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

- Swagger UI: http://localhost:8000/docs
- Health check: `curl http://localhost:8000/health`

### 7.3 Backend

```bash
cd backend
./gradlew bootRun        # Windows: .\gradlew.bat bootRun
```

| Variable | Default | Description |
| --- | --- | --- |
| `AI_API_URL` | `http://localhost:8000` | AI server URL |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Allowed frontend origin(s), comma-separated |
| `DB_URL` | `jdbc:mysql://localhost:3306/yongin_trade_db?...` | MySQL JDBC URL |
| `DB_USERNAME` | `root` | Database user |
| `DB_PASSWORD` | — | Database password |

### 7.4 Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

| Variable | Default | Description |
| --- | --- | --- |
| `VITE_API_BASE_URL` | `http://localhost:8080/api` | Backend API base URL |

## 8. API Reference

### 8.1 AI Server (FastAPI)

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Model load status |
| `POST` | `/predict` | Predict house price |
| `GET` | `/docs` | Swagger UI |

**`POST /predict`**

Request:

```json
{
  "address": "경기도 용인시 수지구 죽전동 1234",
  "building_type": "단독",
  "total_area": 132.5,
  "land_area": 95.0,
  "build_year": 2004,
  "contract_year": 2026,
  "contract_month": 6,
  "contract_day": 10,
  "latitude": 37.3245,
  "longitude": 127.1078
}
```

| Field | Type | Required | Description |
| --- | --- | :---: | --- |
| `address` | string | | Address (used to extract district / neighborhood) |
| `building_type` | string | | Housing type (`단독`, `다가구`, ...) |
| `total_area` | float | ✅ | Floor area (㎡), > 0 |
| `land_area` | float | ✅ | Land area (㎡), > 0 |
| `build_year` | int | ✅ | Year built |
| `contract_year` | int | ✅ | Contract year |
| `contract_month` | int | | Contract month (default 1) |
| `contract_day` | int | | Contract day (default 1) |
| `latitude`, `longitude` | float | | Coordinates (default: Yongin center) |

Response:

```json
{
  "predicted_price_manwon": 78200,
  "predicted_price_text": "7억 8,200만원"
}
```

`predicted_price_manwon` is in units of 10,000 KRW (만원).

### 8.2 Backend (Spring Boot)

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/analyze` | Deposit recovery risk analysis |
| `GET` | `/api/trades` | List of trades |
| `GET` | `/api/trades/summary` | Summary by district |
| `GET` | `/api/trades/trend` | Yearly average deposit trend |
| `GET` | `/api/trades/regional-analysis` | Analysis by neighborhood |

## 9. Deployment

| Service | Platform | Root Directory | Build Command | Start Command |
| --- | --- | --- | --- | --- |
| AI Server | Render | `/` | `pip install -r requirements.txt` | `uvicorn app:app --host 0.0.0.0 --port $PORT` |
| Frontend | Render (Static Site) | `frontend` | `npm install && npm run build` | Publish directory: `dist` |
| Backend | Railway | `backend` | `./gradlew bootJar` | `java -jar build/libs/backend-0.0.1-SNAPSHOT.jar` |

Environment variables:

```text
# Frontend (Render)
VITE_API_BASE_URL=https://<backend-domain>/api

# Backend (Railway)
AI_API_URL=https://<ai-server-domain>
CORS_ALLOWED_ORIGINS=https://<frontend-domain>
DB_URL=jdbc:mysql://<host>:<port>/<database>?serverTimezone=Asia/Seoul&characterEncoding=UTF-8
DB_USERNAME=<username>
DB_PASSWORD=<password>
```

- The frontend is an SPA: add a Render rewrite rule `/*` → `/index.html`.
- Model path resolution order: `MODEL_PATH` env var → `ai/models/xgb_price_unit_ensemble_model.joblib` → `ai/training/outputs_coord_test/...` (local development).

## 10. Retraining the Model

```bash
pip install -r ai/training/requirements.txt
python ai/training/train_model.py
```

- The training CSV (`최종_용인_실거래가_통합_결측채움.csv`) is not included in the repository.
- If no coordinate cache exists, geocoding runs with the `KAKAO_REST_API_KEY` environment variable.
- `train_model.py` overrides `sys.argv` with fixed values at the bottom (for running in a Colab cell). Edit that block to change options.

Main options:

| Option | Current value | Description |
| --- | --- | --- |
| `--data` | `최종_용인_실거래가_통합_결측채움.csv` | Training CSV |
| `--output-dir` | `ai/training/outputs_coord_test` | Output directory |
| `--mode` | `full` | `quick` for a fast smoke run |
| `--device` | `cpu` | `cuda` for GPU |
| `--model-profile` | `baseline` | `deeper` / `regularized` hyperparameter profiles |
| `--high-price-threshold` | `200000` | High-price threshold (10,000 KRW) |
| `--high-price-weight` | `2.0` | Sample weight for high-price trades |
| `--trim-price-quantiles` | enabled | Remove top/bottom 1% prices |
| `--train-outlier-quantile` | `1.0` | Remove OOF errors above this quantile (1.0 = off) |
| `--calibration-strength` | `0.0` | OOF linear calibration strength |
| `--residual-strength` | `0.0` | Residual correction strength |
| `--coord-cache` | `ai/training/yongin_coord_cache.csv` | Coordinate cache |
| `--coord-grid-size` | `0.005` | Coordinate grid size (degrees) |

Outputs (in `--output-dir`):

| File | Description |
| --- | --- |
| `xgb_price_unit_ensemble_model.joblib` | Model bundle (for deployment) |
| `xgb_price_unit_ensemble_metrics.json` | Train / test summary metrics |
| `experiment_summary.md` | Experiment report |
| `train_price_comparison.csv`, `test_price_comparison.csv` | Row-level prediction comparison |
| `test_excluded_top_10pct_errors.csv` | Test rows with the top 10% errors |
| `train_removed_outliers.csv` | Removed training outliers |

To deploy a new model:

```bash
cp ai/training/outputs_coord_test/xgb_price_unit_ensemble_model.joblib ai/models/
```

Then redeploy the AI server.

## 11. Limitations and Future Work

- **High-price under-prediction**: trades ≥ 2B KRW are rare (39 in training) and are under-predicted by about 20% on average.
- **Temporal generalization gap**: train R² 0.915 vs. test R² 0.787 — limited adaptation to recent market shifts.
- **Estimated road condition**: the most frequent regional value is used instead of user input, so parcel-specific traits are not reflected.
- **Missing coordinates**: without coordinates, grid features fall back to Yongin's center and accuracy drops.
- **Future work**: interest-rate / macro features, a separate high-price model, automated periodic retraining.
