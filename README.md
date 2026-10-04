# 용인 전월세 보증금 회수 위험 분석 서비스

> 용인시 주택 실거래 데이터와 XGBoost 앙상블 가격 예측 모델을 활용해 임차인의 보증금 회수 가능성을 분석하는 웹 서비스

![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Spring_Boot-4.0-6DB33F?logo=springboot&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-2.1-EB5B26)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)

## 목차

1. [프로젝트 소개](#1-프로젝트-소개)
2. [주요 기능](#2-주요-기능)
3. [시스템 아키텍처](#3-시스템-아키텍처)
4. [기술 스택](#4-기술-스택)
5. [디렉터리 구조](#5-디렉터리-구조)
6. [AI 가격 예측 모델](#6-ai-가격-예측-모델)
7. [시작하기](#7-시작하기)
8. [API 명세](#8-api-명세)
9. [배포](#9-배포)
10. [모델 재학습 및 교체](#10-모델-재학습-및-교체)
11. [한계 및 향후 과제](#11-한계-및-향후-과제)

---

## 1. 프로젝트 소개

전월세 계약 시 임차인은 집이 경매로 넘어갔을 때 보증금을 얼마나 돌려받을 수 있는지 판단하기 어렵습니다.
이 서비스는 **AI 모델로 해당 주택의 시세를 예측**하고, 이를 바탕으로 **예상 낙찰가 → 선순위 채권(근저당·선순위 임차인) 공제 → 소액임차인 최우선변제**를 순서대로 계산해 보증금 회수 위험도를 보여 줍니다.

- 대상 지역: 경기도 용인시 (수지구 · 기흥구 · 처인구)
- 대상 주택: 단독 · 다가구 주택
- 데이터: 국토교통부 실거래가 공개시스템 단독/다가구 매매 실거래 데이터

## 2. 주요 기능

| 기능 | 설명 |
| --- | --- |
| 보증금 회수 위험 분석 | 주소, 주택 유형, 면적, 보증금, 근저당, 선순위 임차인 정보를 입력받아 회수 가능 금액·위험도 산출 |
| AI 시세 예측 | XGBoost 앙상블 모델로 주택 매매가 예측 후 예상 경매가 산정 |
| 최우선변제 반영 | 소액임차인 기준 및 최우선변제 금액을 반영한 배당 시뮬레이션 |
| 지역 통계 | 용인시 구/동 단위 전월세 거래 통계, 연도별 추이, 면적대별 보증금 분석 |

## 3. 시스템 아키텍처

```text
┌──────────────────┐      ┌──────────────────────┐      ┌───────────────────────┐
│  React Frontend  │ ───▶ │  Spring Boot Backend │ ───▶ │  FastAPI AI API       │
│  (Render)        │ /api │  (Railway)           │/predict  (Render)            │
└──────────────────┘      └──────────┬───────────┘      │  └─ joblib 모델 로드   │
                                     │                  └───────────────────────┘
                                     ▼
                              ┌─────────────┐
                              │   MySQL     │  전월세 거래 데이터
                              └─────────────┘
```

1. 사용자가 프론트엔드에서 주택·계약 정보를 입력
2. Spring Boot가 FastAPI `/predict`를 호출해 예측 시세를 받음
3. Spring Boot가 예측 시세 기반으로 경매가·배당·회수 위험을 계산해 응답
4. 지역 통계 화면은 Spring Boot가 MySQL 거래 데이터를 집계해 제공

## 4. 기술 스택

| 영역 | 기술 |
| --- | --- |
| Frontend | React 18, TypeScript, Vite 6, React Router 7, Recharts, Tailwind CSS 4 |
| Backend | Java 17, Spring Boot 4, Spring JDBC, MySQL |
| AI API | Python, FastAPI, Uvicorn, Pydantic |
| ML | XGBoost 2.1, scikit-learn 1.6, pandas, NumPy, joblib |
| Data | 국토교통부 실거래가, Kakao Local API (지오코딩) |
| Deployment | Render (Frontend, AI API), Railway (Backend) |

## 5. 디렉터리 구조

```text
estate_price_prediction/
├── frontend/                    # React + Vite 프론트엔드
│   └── src/app/
│       ├── pages/               # 랜딩, 분석 입력, 결과, 지역 통계 페이지
│       ├── components/          # 공통 레이아웃
│       └── services/api.ts      # 백엔드 API 클라이언트
├── backend/                     # Spring Boot 백엔드
│   └── src/main/java/com/yongin/backend/
│       ├── controller/          # 분석 / 거래 데이터 API
│       ├── service/             # 거래 데이터 조회, AI API 클라이언트
│       └── dto/                 # 요청·응답 DTO
├── ai/
│   ├── api/                     # FastAPI 예측 서버
│   │   ├── main.py              # FastAPI 앱 (/health, /predict)
│   │   ├── model_service.py     # 모델 로드 + 학습과 동일한 피처 생성 + 앙상블 추론
│   │   ├── schemas.py           # 요청·응답 스키마
│   │   ├── models/              # 배포용 joblib 모델
│   │   └── requirements.txt
│   └── training/                # 모델 학습
│       ├── train_model.py       # 전처리 · 피처 엔지니어링 · 학습 · 평가 · 저장
│       └── requirements.txt
├── app.py                       # 루트 배포용 엔트리 (ai/api/main.py 재노출)
├── requirements.txt             # 루트 배포용 의존성
└── README.md
```

## 6. AI 가격 예측 모델

### 6.1 개요

| 항목 | 내용 |
| --- | --- |
| 문제 유형 | 회귀 (단독·다가구 주택 매매가 예측, 단위: 만원) |
| 알고리즘 | XGBoost Regressor 3종 앙상블 (가격 / 로그 가격 / 단위면적당 가격) |
| 학습 스크립트 | [ai/training/train_model.py](ai/training/train_model.py) |
| 모델 파일 | `ai/api/models/xgb_price_unit_ensemble_model.joblib` |
| 데이터 분할 | 계약일 기준 시계열 분할 (과거 80% 학습 / 최근 20% 테스트) |
| 검증 | `TimeSeriesSplit` 5-fold 교차검증 |

### 6.2 학습 파이프라인

```text
원본 CSV (실거래가)
  │
  ├─ 1. 좌표 부착        Kakao Local API 지오코딩 (주소 → 위경도), CSV 캐시
  ├─ 2. 정제              결측/0 이하 제거, 건물연령 0~150년, 용적률 0~20, 가격 상하위 1% 제거
  ├─ 3. 피처 엔지니어링  면적·연식·시점·좌표·지역 범주·과거 시세 베이스라인
  ├─ 4. 시계열 분할      계약일 정렬 후 앞 80% Train / 뒤 20% Test
  ├─ 5. 앙상블 학습      Raw / Log / Unit XGBoost × TimeSeriesSplit 5-fold
  ├─ 6. 가중치 탐색      OOF 예측으로 3개 모델 블렌딩 가중치 그리드 서치 (RMSE 최소)
  ├─ 7. 최종 학습        전체 Train으로 3개 파이프라인 재학습
  └─ 8. 저장              파이프라인 + 가중치 + 추론용 룩업 테이블을 joblib 번들로 저장
```

### 6.3 데이터 전처리

| 단계 | 처리 내용 |
| --- | --- |
| 날짜 파싱 | `계약년월` → `trade_year`, `trade_month` / `계약일` → `trade_day` |
| 결측·이상치 제거 | 가격·면적·계약일 결측 행 제거, 가격/연면적/대지면적 ≤ 0 제거 |
| 건축년도 | `1900`은 결측 표기로 간주 → `NaN` 처리 후 `build_year_missing` 플래그 생성 |
| 건물연령 | `trade_year - build_year`가 0~150년 범위 밖인 행 제거 |
| 용적률(FAR) | `연면적 / 대지면적`이 0~20 범위 밖인 행 제거 |
| 가격 트리밍 | 거래가 상·하위 1% 제거 (`--trim-price-quantiles`, 기본 활성) |
| 범주 정리 | 빈 값·`-`·`nan` → `기타` 로 통일 |

### 6.4 피처 엔지니어링

총 **32개 입력 피처** (수치 23 + 범주 9) → 파이프라인 내부에서 타깃 인코딩 8개 추가.

| 그룹 | 피처 | 설명 |
| --- | --- | --- |
| 면적 | `total_area`, `land_area`, `log_total_area`, `log_land_area` | 연면적·대지면적 및 로그 변환 |
| 면적 비율 | `far`, `land_to_total_ratio`, `total_to_land_ratio` | 용적률 및 역비율 |
| 연식 | `build_year`, `building_age`, `build_year_missing` | 건축년도, 거래 시점 기준 건물 연령 |
| 시점 | `trade_year`, `trade_month`, `trade_day` | 거래 시점 (시장 추세 반영) |
| 좌표 | `latitude`, `longitude`, `coord_missing`, `lat_lon_interaction`, `lat_sq`, `lon_sq` | 위경도 및 비선형 항 |
| 시세 베이스라인 | `baseline_unit_price`, `baseline_price`, `baseline_count`, `baseline_source_level` | 과거 거래 기반 지역 평균 단가 (아래 6.5) |
| 지역 범주 | `gu`, `dong`, `road_condition`, `house_type` | 구, 동/읍/면, 도로조건, 주택유형 |
| 교차 범주 | `gu_house_type`, `dong_house_type`, `dong_road` | 지역 × 유형 / 도로조건 조합 |
| 좌표 격자 | `coord_grid`, `coord_grid_house_type` | 위경도 0.005° (약 500m) 격자 및 유형 조합 |

### 6.5 핵심 기법

#### (1) 과거 시세 베이스라인 (Target Leakage 방지)

같은 지역의 평균 단가는 가격 예측에 가장 강력한 정보지만, 단순 그룹 평균을 쓰면 **자기 자신과 미래 거래가 포함되어 누수**가 발생합니다.
이를 막기 위해 계약일 순으로 정렬한 뒤 **해당 거래 이전의 거래만** 누적 평균(`cumsum - self`)으로 계산합니다.

표본이 적은 지역은 계층적 fallback 을 적용합니다.

| 레벨 | 그룹 | 사용 조건 |
| :---: | --- | --- |
| 3 | `dong + house_type` | 과거 거래 3건 이상 |
| 2 | `gu + house_type` | 5건 이상 |
| 1 | `house_type` | 10건 이상 |
| 0 | 전체 (global) | 그 외 |

`baseline_source_level`을 피처로 함께 넣어 모델이 베이스라인의 신뢰도를 학습하도록 했습니다.
추론 시에는 학습 데이터로 미리 계산한 **룩업 테이블(`baseline_lookup`)**을 모델 번들에 저장해 같은 fallback 순서로 조회합니다.

#### (2) 스무딩 타깃 인코딩 (`MultiTargetEncoder`)

고유값이 많은 지역 범주(동, 좌표 격자 등) 8개에 대해 **베이지안 스무딩 타깃 평균**을 계산합니다.

```text
encoded = (mean × count + global_mean × m) / (count + m),   m = 20
```

표본이 적은 범주는 전체 평균 쪽으로 수축되어 과적합을 줄입니다. 인코더는 sklearn `Pipeline` 내부에 포함되어 CV fold 마다 학습 데이터로만 fit 됩니다.

#### (3) 전처리 파이프라인

```text
Pipeline
 ├─ target_encoder : MultiTargetEncoder (8개 범주 → *_target_avg)
 ├─ preprocess     : ColumnTransformer
 │                    ├─ num : SimpleImputer(median)
 │                    └─ cat : SimpleImputer(most_frequent) → OneHotEncoder(min_frequency=50, handle_unknown="ignore")
 └─ model          : XGBRegressor(tree_method="hist")
```

전처리와 모델이 하나의 파이프라인으로 저장되므로 **추론 시 피처 순서·인코딩이 학습과 동일하게 보장**됩니다.

#### (4) 3-타깃 앙상블

같은 피처로 서로 다른 타깃을 학습한 3개 모델을 가중 평균합니다.

| 모델 | 학습 타깃 | 역할 | 주요 하이퍼파라미터 |
| --- | --- | --- | --- |
| Raw | `price` | 절대 가격 오차 최소화 | n_estimators=600, max_depth=5, lr=0.025 |
| Log | `log1p(price)` | 저가 구간 상대 오차 안정화 | n_estimators=600, max_depth=4, lr=0.025 |
| Unit | `price / total_area` | 단가 학습 → 면적 곱해 가격 환산 | n_estimators=500, max_depth=4, lr=0.03 |

공통: `subsample 0.85~0.9`, `colsample_bytree 0.85~0.9`, `reg_lambda 2.0`, `random_state 42`

```text
final_price = a × Raw + b × expm1(Log) + c × (Unit × total_area),   a + b + c = 1
```

가중치 `(a, b, c)`는 0.1 단위 66개 조합을 **TimeSeriesSplit OOF 예측의 평균 RMSE**로 비교해 선택합니다.
현재 배포 모델의 최적 가중치는 **`(0.5, 0.0, 0.5)`** — Raw 와 Unit 모델의 균등 블렌딩입니다.

#### (5) 샘플 가중치

- **최신성 가중치**: 거래 연도에 따라 0.65 → 1.0 선형 증가 (최근 시장 반영)
- **고가 주택 가중치**: 20억 원 이상 거래에 ×2.0 (희소한 고가 구간 과소추정 완화)

#### (6) 선택적 후처리 (현재 비활성)

학습 스크립트에는 OOF 기반 선형 보정(`--calibration-strength`), 잔차 보정 모델(`--residual-strength`), OOF 이상치 제거(`--train-outlier-quantile`) 옵션이 구현되어 있으며, 현재 배포 모델은 모두 비활성(0.0 / 1.0) 상태로 학습되었습니다.

### 6.6 모델 성능

시계열 기준 **최근 20% 거래(Test)** 에 대한 평가 결과입니다. (Train 4,309건)

| 지표 | Train | Test | 베이스라인만 사용 (Test) |
| --- | ---: | ---: | ---: |
| R² | 0.915 | **0.787** | 0.417 |
| MAE | 7,830만원 | **1억 6,027만원** | 2억 3,382만원 |
| RMSE | 1억 1,148만원 | **2억 2,789만원** | 3억 7,747만원 |
| Median AE | 5,412만원 | **1억 1,788만원** | 1억 4,794만원 |
| MAPE | 15.2% | **25.8%** | 37.1% |
| 실제 평균가 | 6억 4,222만원 | 7억 7,898만원 | — |
| 예측 평균가 | 6억 4,446만원 | 7억 8,425만원 | 8억 3,974만원 |

- 지역 평균 단가만 쓰는 베이스라인 대비 **R² 0.42 → 0.79**, **MAE 약 31% 감소**
- 예측 평균이 실제 평균과 거의 일치 (Mean Error ≈ +527만원) → 전체적인 편향이 작음
- 20억 원 이상 고가 거래(Test 34건)는 평균 약 4.7억 원 **과소추정** 경향

### 6.7 추론 (서빙)

배포 시에는 **재학습 없이** joblib 번들만 로드합니다. [ai/api/model_service.py](ai/api/model_service.py)가 학습과 동일한 규칙으로 피처를 생성합니다.

| 입력 | 처리 |
| --- | --- |
| `address` | `구`, `동/읍/면/리` 추출 |
| `building_type` | `house_type` |
| `road_condition` | 사용자가 모르는 경우가 많아 번들의 `road_condition_lookup`(동+유형별 최빈값) 사용 |
| `latitude`, `longitude` | 미입력 시 용인시 중심 좌표로 대체 + `coord_missing=1` |
| 베이스라인 4종 | 번들의 `baseline_lookup`에서 계층 fallback 조회 |

joblib 번들 구성:

```text
{
  raw_pipeline, log_pipeline, unit_pipeline,   # 전처리 + XGBoost 파이프라인
  best_weights,                                 # 앙상블 가중치
  baseline_lookup, road_condition_lookup,       # 추론용 룩업 테이블
  calibrator, residual_pipeline, ...            # 선택적 후처리
  metrics, train_metrics, ...                   # 학습 시 평가 결과
}
```

## 7. 시작하기

### 7.1 요구 사항

- Python 3.11+
- Java 17
- Node.js 18+
- MySQL 8

### 7.2 AI API

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

- Swagger UI: http://localhost:8000/docs
- 헬스 체크: `curl http://localhost:8000/health`

> `ai/api` 디렉터리에서 `uvicorn main:app --reload` 로 실행해도 동일합니다.

### 7.3 백엔드 (Spring Boot)

```bash
cd backend
./gradlew bootRun        # Windows: .\gradlew.bat bootRun
```

| 환경변수 | 기본값 | 설명 |
| --- | --- | --- |
| `AI_API_URL` | `http://localhost:8000` | FastAPI 예측 API 주소 |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | 프론트엔드 허용 Origin |
| `DB_URL` | `jdbc:mysql://localhost:3306/yongin_trade_db?...` | MySQL JDBC URL |
| `DB_USERNAME` | `root` | DB 사용자 |
| `DB_PASSWORD` | — | DB 비밀번호 |

### 7.4 프론트엔드

```bash
cd frontend
npm install
npm run dev
```

| 환경변수 | 기본값 | 설명 |
| --- | --- | --- |
| `VITE_API_BASE_URL` | `http://localhost:8080/api` | Spring Boot API base URL |

## 8. API 명세

### 8.1 AI API (FastAPI)

| Method | Path | 설명 |
| --- | --- | --- |
| `GET` | `/health` | 모델 로드 상태 확인 |
| `POST` | `/predict` | 주택 가격 예측 |
| `GET` | `/docs` | Swagger UI |

**`POST /predict`**

Request

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

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | :---: | --- |
| `address` | string | | 주소 (구·동 추출용) |
| `building_type` | string | | 주택유형 (`단독`, `다가구` 등) |
| `total_area` | float | ✅ | 연면적(㎡), > 0 |
| `land_area` | float | ✅ | 대지면적(㎡), > 0 |
| `build_year` | int | ✅ | 건축년도 |
| `contract_year` | int | ✅ | 계약 연도 |
| `contract_month` | int | | 계약 월 (기본 1) |
| `contract_day` | int | | 계약 일 (기본 1) |
| `latitude`, `longitude` | float | | 좌표 (미입력 시 용인시 중심 좌표) |

Response

```json
{
  "predicted_price_manwon": 78200,
  "predicted_price_text": "7억 8,200만원"
}
```

### 8.2 Backend API (Spring Boot)

| Method | Path | 설명 |
| --- | --- | --- |
| `POST` | `/api/analyze` | 보증금 회수 위험 분석 |
| `GET` | `/api/trades` | 거래 데이터 목록 |
| `GET` | `/api/trades/summary` | 구 단위 거래 요약 |
| `GET` | `/api/trades/trend` | 연도별 평균 보증금 추이 |
| `GET` | `/api/trades/regional-analysis` | 동 단위 지역 분석 |

## 9. 배포

| 서비스 | 플랫폼 | Root Directory | Build Command | Start Command |
| --- | --- | --- | --- | --- |
| AI API | Render | `/` (루트) | `pip install -r requirements.txt` | `uvicorn app:app --host 0.0.0.0 --port $PORT` |
| Frontend | Render (Static) | `frontend` | `npm install && npm run build` | Publish: `dist` |
| Backend | Railway | `backend` | `./gradlew bootJar` | `java -jar build/libs/backend-0.0.1-SNAPSHOT.jar` |

배포 환경변수:

```text
# Frontend (Render)
VITE_API_BASE_URL=https://<backend-domain>/api

# Backend (Railway)
AI_API_URL=https://<ai-api-domain>
CORS_ALLOWED_ORIGINS=https://<frontend-domain>
DB_URL=jdbc:mysql://<host>:<port>/<database>?serverTimezone=Asia/Seoul&characterEncoding=UTF-8
DB_USERNAME=<username>
DB_PASSWORD=<password>
```

- 프론트엔드는 SPA 이므로 Render Rewrite 규칙에서 `/*` → `/index.html` 설정이 필요합니다.
- AI API 모델 경로 탐색 순서: `MODEL_PATH` 환경변수 → `ai/api/models/xgb_price_unit_ensemble_model.joblib` → `ai/training/outputs_coord_test/...` (로컬 개발용)

## 10. 모델 재학습 및 교체

```bash
pip install -r ai/training/requirements.txt
python ai/training/train_model.py
```

- 학습 데이터 CSV(`최종_용인_실거래가_통합_결측채움.csv`)는 저장소에 포함되지 않습니다.
- 좌표 캐시가 없으면 `KAKAO_REST_API_KEY` 환경변수로 지오코딩을 수행합니다.
- `train_model.py` 하단에서 `sys.argv`를 고정값으로 덮어씁니다 (Colab 셀 실행용). 옵션을 바꾸려면 해당 블록을 수정하세요.

주요 옵션:

| 옵션 | 현재 값 | 설명 |
| --- | --- | --- |
| `--data` | `최종_용인_실거래가_통합_결측채움.csv` | 학습 CSV |
| `--output-dir` | `ai/training/outputs_coord_test` | 산출물 경로 |
| `--mode` | `full` | `quick`: 빠른 동작 확인용 |
| `--device` | `cpu` | `cuda`: GPU |
| `--model-profile` | `baseline` | `deeper` / `regularized` 하이퍼파라미터 프로필 |
| `--high-price-threshold` | `200000` | 고가 기준 (만원) |
| `--high-price-weight` | `2.0` | 고가 거래 샘플 가중치 |
| `--trim-price-quantiles` | 활성 | 가격 상·하위 1% 제거 |
| `--train-outlier-quantile` | `1.0` | OOF 오차 상위 분위 제거 (1.0 = 비활성) |
| `--calibration-strength` | `0.0` | OOF 선형 보정 강도 |
| `--residual-strength` | `0.0` | 잔차 보정 모델 강도 |
| `--coord-cache` | `ai/training/yongin_coord_cache.csv` | 좌표 캐시 |
| `--coord-grid-size` | `0.005` | 좌표 격자 크기 (도) |

산출물 (`--output-dir`):

| 파일 | 설명 |
| --- | --- |
| `xgb_price_unit_ensemble_model.joblib` | 모델 번들 (배포용) |
| `xgb_price_unit_ensemble_metrics.json` | Train/Test 요약 지표 |
| `experiment_summary.md` | 실험 요약 리포트 |
| `train_price_comparison.csv`, `test_price_comparison.csv` | 행 단위 예측 비교 |
| `test_excluded_top_10pct_errors.csv` | 오차 상위 10% 테스트 행 |
| `train_removed_outliers.csv` | 제거된 학습 이상치 |

새 모델 배포:

```bash
cp ai/training/outputs_coord_test/xgb_price_unit_ensemble_model.joblib ai/api/models/
```

이후 AI API 를 재배포하면 됩니다.

## 11. 한계 및 향후 과제

- **고가 주택 과소추정**: 20억 원 이상 거래는 표본(학습 39건)이 적어 평균 약 20% 과소추정됩니다.
- **시계열 일반화 격차**: Train R² 0.915 ↔ Test R² 0.787 로, 최근 시장 변화에 대한 대응이 제한적입니다.
- **도로조건 추정**: 사용자 입력 대신 지역 최빈값을 사용하므로 개별 필지 특성이 반영되지 않습니다.
- **좌표 미입력**: 좌표가 없으면 격자 피처가 용인시 중심으로 고정되어 정확도가 떨어집니다.
- 향후: 금리·거시지표 피처 추가, 고가 구간 별도 모델, 주기적 재학습 자동화
