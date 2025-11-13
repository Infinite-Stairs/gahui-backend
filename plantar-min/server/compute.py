from typing import Dict, Tuple
from .geometry import SENSOR_POS

#오른발,왼발 하중 퍼센트 계산 함수
def lr_percent(left_sum_avg: float, right_sum_avg: float) -> Tuple[float, float]:
    total = left_sum_avg + right_sum_avg
    if total <= 1e-9:
        return 0.0, 0.0
    lp = (left_sum_avg / total) * 100.0
    rp = 100.0 - lp
    return lp, rp

#CoP 중심 좌표 계산 함수
def cop_xy(sensor_avgs: Dict[str, float]) -> Tuple[float, float]:
    sx = sy = ssum = 0.0
    for name, s in sensor_avgs.items():
        if s <= 0:
            continue
        x, y = SENSOR_POS[name]
        sx += s * x
        sy += s * y
        ssum += s
    if ssum <= 1e-9:
        return 50.0, 50.0
    return (sx / ssum) * 100.0, (sy / ssum) * 100.0

#정상군 의심군 구별 함수
def cop_ok_from_x(cop_x_pct: float, thr_pct: float = 5.0) -> int:
    return 1 if abs(cop_x_pct - 50.0) < thr_pct else 0

#위의 3 계산 수행 후 dict로 반환
def compute_all(
    l1: float, l2: float, l3: float,
    r1: float, r2: float, r3: float,
    left_sum_avg: float, right_sum_avg: float,
    thr_pct: float = 5.0,
) -> Dict[str, float | int]:
    lp, rp = lr_percent(left_sum_avg, right_sum_avg)
    cx, cy = cop_xy({"L1": l1, "L2": l2, "L3": l3, "R1": r1, "R2": r2, "R3": r3})
    ok = cop_ok_from_x(cx, thr_pct=thr_pct)
    return {
        "left_pct": lp,
        "right_pct": rp,
        "cop_x_pct": cx,
        "cop_y_pct": cy,
        "cop_ok": ok
    }
