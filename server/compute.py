from __future__ import annotations
from typing import Dict, Tuple
from .geometry import SENSOR_POS

# 1. 좌우 하중 퍼센트
def lr_percent(left_sum_avg: float, right_sum_avg: float) -> Tuple[float, float]:
    total = left_sum_avg + right_sum_avg
    if total <= 1e-9:
        return 0.0, 0.0
    lp = (left_sum_avg / total) * 100.0
    rp = 100.0 - lp
    return lp, rp



# 2. 센서 좌표계 범위 (min/max) 계산
_XS = [pos[0] for pos in SENSOR_POS.values()]
_YS = [pos[1] for pos in SENSOR_POS.values()]
MIN_X, MAX_X = min(_XS), max(_XS)
MIN_Y, MAX_Y = min(_YS), max(_YS)
RANGE_X = MAX_X - MIN_X if MAX_X > MIN_X else 1.0
RANGE_Y = MAX_Y - MIN_Y if MAX_Y > MIN_Y else 1.0



# 3. CoP 계산 (raw, 좌표계 단위)
def cop_raw(sensor_avgs: Dict[str, float]) -> Tuple[float, float]:
    sx = sy = ssum = 0.0
    for name, s in sensor_avgs.items():
        if s <= 0:
            continue
        x, y = SENSOR_POS[name]
        sx += s * x
        sy += s * y
        ssum += s

    if ssum <= 1e-9:
        # 압력이 거의 없으면 좌표계 중앙으로
        cx0 = (MIN_X + MAX_X) * 0.5
        cy0 = (MIN_Y + MAX_Y) * 0.5
        return cx0, cy0

    cx = sx / ssum
    cy = sy / ssum
    return cx, cy



# 4. raw CoP → 0~100%로 정규화
def cop_xy_pct(sensor_avgs: Dict[str, float]) -> Tuple[float, float]:
    cx_raw, cy_raw = cop_raw(sensor_avgs)

    # 0~100 비율로 정규화
    cx_pct = (cx_raw - MIN_X) / RANGE_X * 100.0
    cy_pct = (cy_raw - MIN_Y) / RANGE_Y * 100.0

    # 안전하게 0~100으로 클램프
    def clamp_0_100(v: float) -> float:
        if v != v:  # NaN 보호
            return 50.0
        return max(0.0, min(100.0, v))

    return clamp_0_100(cx_pct), clamp_0_100(cy_pct)

# 5. 정상/의심 판정
#    (좌우 기준: x = 50%가 정중앙)
def cop_ok_from_x(cop_x_pct: float, thr_pct: float = 5.0) -> int:
    return 1 if abs(cop_x_pct - 50.0) < thr_pct else 0



# 6. 전체 계산
def compute_all(
    l1: float, l2: float, l3: float,
    r1: float, r2: float, r3: float,
    left_sum_avg: float, right_sum_avg: float,
    thr_pct: float = 5.0,
) -> Dict[str, float | int]:
    # 좌우 하중
    lp, rp = lr_percent(left_sum_avg, right_sum_avg)

    # CoP (0~100% 스케일)
    cx_pct, cy_pct = cop_xy_pct({
        "L1": l1, "L2": l2, "L3": l3,
        "R1": r1, "R2": r2, "R3": r3,
    })

    # 정상/의심 판정
    ok = cop_ok_from_x(cx_pct, thr_pct=thr_pct)

    return {
        "left_pct": lp,
        "right_pct": rp,
        "cop_x_pct": cx_pct,
        "cop_y_pct": cy_pct,
        "cop_ok": ok,
    }
