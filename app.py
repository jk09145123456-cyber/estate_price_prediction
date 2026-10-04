"""Render 루트 배포용 엔트리포인트.

실제 구현은 ai/api/main.py 에 있으며, 루트에서 `uvicorn app:app` 으로 실행할 수 있도록 재노출한다.
"""
import sys
from pathlib import Path

# ai/api 디렉터리를 모듈 검색 경로에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent / "ai" / "api"))

from main import app  # noqa: E402,F401
