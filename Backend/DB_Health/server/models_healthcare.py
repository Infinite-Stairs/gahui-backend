from pydantic import BaseModel, Field
from typing import Optional

class IngestRequest(BaseModel):
    l1_avg: float = Field(ge=0)
    l2_avg: float = Field(ge=0)
    l3_avg: float = Field(ge=0)
    r1_avg: float = Field(ge=0)
    r2_avg: float = Field(ge=0)
    r3_avg: float = Field(ge=0)

    left_sum_avg: float = Field(ge=0)
    right_sum_avg: float = Field(ge=0)
    overall_avg: float = Field(ge=0)

    left_std: Optional[float] = None
    right_std: Optional[float] = None


class IngestResponse(BaseModel):
    id: str
    created_at: str
    left_pct: float
    right_pct: float
    cop_x_pct: float
    cop_y_pct: float
    cop_ok: int
    left_std: Optional[float] = None
    right_std: Optional[float] = None
