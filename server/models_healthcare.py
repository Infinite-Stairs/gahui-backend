# models_healthcare.py
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional


class IngestRequest(BaseModel):
    """
    아두이노/라즈베리에서 10초 윈도우 평균을 보내줄 때 사용하는 입력 모델.
    """
    l1_avg: float = Field(ge=0)
    l2_avg: float = Field(ge=0)
    l3_avg: float = Field(ge=0)
    r1_avg: float = Field(ge=0)
    r2_avg: float = Field(ge=0)
    r3_avg: float = Field(ge=0)

    left_sum_avg: float = Field(ge=0)
    right_sum_avg: float = Field(ge=0)
    overall_avg: float = Field(ge=0)

    # 선택: 라즈베리에서 표준편차까지 계산해서 보낼 경우 사용
    left_std: Optional[float] = None
    right_std: Optional[float] = None


class IngestResponse(BaseModel):
    """
    프론트/라즈베리에 돌려주는 응답 모델.
    DB에 저장된 레코드의 id, created_at + 주요 지표만 노출.
    """
    id: str
    created_at: str  # ISO8601 형식 문자열

    left_pct: float
    right_pct: float
    cop_x_pct: float
    cop_y_pct: float
    cop_ok: int

    left_std: Optional[float] = None
    right_std: Optional[float] = None
