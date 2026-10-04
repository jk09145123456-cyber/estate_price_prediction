# AI Training

Colab에서 실행할 수 있는 학습 스크립트입니다.

## Colab 실행 순서

코드셀에 `train_model.py` 내용을 통째로 붙여넣고 실행하는 경우에는 기본값으로 아래 설정이 사용됩니다.

- data: `최종_용인_실거래가_통합_결측채움.csv`
- mode: `full`
- device: `cuda`
- output-dir: `ai/training/outputs`

빠른 문법/동작 확인만 하려면 코드 하단의 `parser.add_argument("--mode"... default="full")`를 `default="quick"`으로 바꿉니다.

```bash
pip install -r ai/training/requirements.txt
python ai/training/train_model.py \
  --data "최종_용인_실거래가_통합_결측채움.csv" \
  --mode full \
  --device cpu \
  --output-dir ai/training/outputs
```

Colab 런타임을 GPU로 바꾼 경우:

```bash
python ai/training/train_model.py \
  --data "최종_용인_실거래가_통합_결측채움.csv" \
  --mode full \
  --device cuda \
  --output-dir ai/training/outputs
```

생성 파일:

- `ai/training/outputs/xgb_price_unit_ensemble_model.joblib`
- `ai/training/outputs/xgb_price_unit_ensemble_metrics.json`
- `ai/training/outputs/experiment_summary.md`

FastAPI에 붙일 때는 생성된 `.joblib` 파일을 아래 위치에 두면 됩니다.

```text
ai/api/models/xgb_price_unit_ensemble_model.joblib
```
