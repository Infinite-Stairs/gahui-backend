# compute.py
from __future__ import annotations
from typing import Dict, Tuple
from .geometry import SENSOR_POS

# 1) 좌우 하중 퍼센트 계산
def lr_percent(left_sum_avg: float, right_sum_avg: float) -> Tuple[float, float]:
    total = left_sum_avg + right_sum_avg
    if total <= 1e-9:
        return 0.0, 0.0
    lp = (left_sum_avg / total) * 100.0
    rp = 100.0 - lp
    return lp, rp

# 2) CoP 좌표 계산
def cop_xy(sensor_avgs: Dict[str, float]) -> Tuple[float, float]:
    """
    SENSOR_POS 값이 이미 0~100 스케일(%)이라고 가정.
    그러면 sx/ssum, sy/ssum 결과도 0~100 사이가 되므로
    *100 을 추가로 하지 않는다.
    """
    sx = sy = ssum = 0.0
    for name, s in sensor_avgs.items():
        if s <= 0:
            continue
        x, y = SENSOR_POS[name]      # 예: x,y ∈ [0,100]
        sx += s * x
        sy += s * y
        ssum += s

    if ssum <= 1e-9:
        # 압력이 거의 없으면 중앙으로
        return 50.0, 50.0

    cx = sx / ssum    # 0~100
    cy = sy / ssum    # 0~100
    return cx, cy

# 3) 정상/의심 판정
def cop_ok_from_x(cop_x_pct: float, thr_pct: float = 5.0) -> int:
    return 1 if abs(cop_x_pct - 50.0) < thr_pct else 0

# 4) 전체 계산
def compute_all(
    l1: float, l2: float, l3: float,
    r1: float, r2: float, r3: float,
    left_sum_avg: float, right_sum_avg: float,
    thr_pct: float = 5.0,
) -> Dict[str, float | int]:
    lp, rp = lr_percent(left_sum_avg, right_sum_avg)
    cx, cy = cop_xy({
        "L1": l1, "L2": l2, "L3": l3,
        "R1": r1, "R2": r2, "R3": r3,
    })
    ok = cop_ok_from_x(cx, thr_pct=thr_pct)

    # 안전장치: 혹시 좌표계가 달라져도 DB CHECK 안 깨지게 범위 클램프
    def clamp01_100(v: float) -> float:
        if v != v:   # NaN
            return 50.0
        return max(0.0, min(100.0, v))

    lp = clamp01_100(lp)
    rp = clamp01_100(rp)
    cx = clamp01_100(cx)
    cy = clamp01_100(cy)

    return {
        "left_pct": lp,
        "right_pct": rp,
        "cop_x_pct": cx,
        "cop_y_pct": cy,
        "cop_ok": ok,
    }
