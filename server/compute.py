# compute.py
from __future__ import annotations
from typing import Dict, Tuple
from .geometry import SENSOR_POS


def lr_percent(left_sum_avg: float, right_sum_avg: float) -> Tuple[float, float]:
    """
    왼발 / 오른발 하중 퍼센트 계산.
    """
    total = left_sum_avg + right_sum_avg
    if total <= 1e-9:
        return 0.0, 0.0
    lp = (left_sum_avg / total) * 100.0
    rp = 100.0 - lp
    return lp, rp


def cop_xy(sensor_avgs: Dict[str, float]) -> Tuple[float, float]:
    """
    센서 평균값으로 CoP(무게중심) x,y 좌표 계산 (0~100% 스케일).
    sensor_avgs 키: "L1","L2","L3","R1","R2","R3"
    SENSOR_POS[key] = (x_norm, y_norm)  # 0~1 범위라고 가정
    """
    sx = sy = ssum = 0.0
    for name, s in sensor_avgs.items():
        if s <= 0:
            continue
        x, y = SENSOR_POS[name]
        sx += s * x
        sy += s * y
        ssum += s

    if ssum <= 1e-9:
        # 압력이 거의 없으면 중앙(50,50)으로 처리
        return 50.0, 50.0

    return (sx / ssum) * 100.0, (sy / ssum) * 100.0


def cop_ok_from_x(cop_x_pct: float, thr_pct: float = 5.0) -> int:
    """
    CoP X가 중앙(50%)에서 thr_pct 이내면 정상(1), 아니면 의심(0).
    """
    return 1 if abs(cop_x_pct - 50.0) < thr_pct else 0


def compute_all(
    l1: float, l2: float, l3: float,
    r1: float, r2: float, r3: float,
    left_sum_avg: float, right_sum_avg: float,
    thr_pct: float = 5.0,
) -> Dict[str, float | int]:
    """
    좌우 퍼센트, CoP 좌표, 정상/의심 플래그까지 한 번에 계산해서 dict로 반환.
    """
    # 좌우 하중 퍼센트
    lp, rp = lr_percent(left_sum_avg, right_sum_avg)

    # CoP 좌표
    cx, cy = cop_xy({
        "L1": l1, "L2": l2, "L3": l3,
        "R1": r1, "R2": r2, "R3": r3,
    })

    # 정상/의심 판정
    ok = cop_ok_from_x(cx, thr_pct=thr_pct)

    return {
        "left_pct": lp,
        "right_pct": rp,
        "cop_x_pct": cx,
        "cop_y_pct": cy,
        "cop_ok": ok,
    }
