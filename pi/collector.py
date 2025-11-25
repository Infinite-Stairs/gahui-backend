# pi/collector.py
import json, time, serial, requests
from typing import Tuple
from .config import SERIAL_PORT, SERIAL_BAUD, API_BASE, WINDOW_SEC

def _parse_line(line: str) -> Tuple[float,float,float,float,float,float]:
    line = line.strip()
    if not line:
        raise ValueError("empty")

    # 1) JSON 형태: {"L1":123, "L2":...}
    if line.startswith("{"):
        obj = json.loads(line)
        vals = (obj["L1"], obj["L2"], obj["L3"], obj["R1"], obj["R2"], obj["R3"])
        return tuple(float(x) for x in vals)

    # 2) "v1,v2,v3,v4,v5,v6" 형태
    parts = [p.strip() for p in line.split(",")]
    if len(parts) != 6:
        raise ValueError("not 6 columns")
    return tuple(float(x) for x in parts)


def _should_run() -> bool:
    """
    백엔드 /control 에서 is_collecting 값을 읽어서
    True면 수집, False면 대기.
    """
    try:
        r = requests.get(f"{API_BASE}/control", timeout=3)
        r.raise_for_status()
        data = r.json()
        return bool(data.get("is_collecting", False))
    except Exception as e:
        print("[warn] control 상태 조회 실패:", e)
        # 통신 에러일 땐 안전하게 '수집 안 함'
        return False


def _send_window(payload: dict) -> None:
    """
    10초 요약 payload를 백엔드 /ingest 로 전송
    """
    try:
        r = requests.post(f"{API_BASE}/ingest", json=payload, timeout=5)
        r.raise_for_status()
        print("[info] 업로드 성공:", r.json())
    except Exception as e:
        print("[error] 업로드 실패:", e)


def main():
    # 시리얼 포트 연결
    print(f"[info] open serial: {SERIAL_PORT} @ {SERIAL_BAUD}")
    ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)

    print("[info] collector 데몬 시작")

    while True:
        # 1) 먼저 control 상태 확인
        if not _should_run():
            # 수집 OFF 상태이면 1초 쉬고 다시 확인
            time.sleep(1.0)
            continue

        print("[info] 수집 시작 (새 윈도우)")

        # 여기부터는 start 버튼으로 ON된 상태
        start_ts = time.time()

        l1_vals, l2_vals, l3_vals = [], [], []
        r1_vals, r2_vals, r3_vals = [], [], []

        while time.time() - start_ts < WINDOW_SEC:
            try:
                line = ser.readline().decode(errors="ignore")
                if not line:
                    continue
                L1, L2, L3, R1, R2, R3 = _parse_line(line)

                l1_vals.append(L1)
                l2_vals.append(L2)
                l3_vals.append(L3)
                r1_vals.append(R1)
                r2_vals.append(R2)
                r3_vals.append(R3)
            except ValueError as e:
                # 라인 형식이 안 맞으면 스킵
                print("[warn] parse error:", e)
                continue

        # 한 윈도우(예: 10초) 끝 → 평균 계산
        if not l1_vals:
            print("[warn] 윈도우에 데이터가 없음")
            continue

        def avg(xs): return sum(xs) / len(xs)

        l1_avg = avg(l1_vals)
        l2_avg = avg(l2_vals)
        l3_avg = avg(l3_vals)
        r1_avg = avg(r1_vals)
        r2_avg = avg(r2_vals)
        r3_avg = avg(r3_vals)

        left_sum_avg  = l1_avg + l2_avg + l3_avg
        right_sum_avg = r1_avg + r2_avg + r3_avg
        overall_avg   = (left_sum_avg + right_sum_avg) / 2.0

        # 표준편차 안 쓸 거면 0.0으로
        left_std  = 0.0
        right_std = 0.0

        payload = {
            "l1_avg": l1_avg, "l2_avg": l2_avg, "l3_avg": l3_avg,
            "r1_avg": r1_avg, "r2_avg": r2_avg, "r3_avg": r3_avg,
            "left_sum_avg": left_sum_avg,
            "right_sum_avg": right_sum_avg,
            "overall_avg": overall_avg,
            "left_std": left_std,
            "right_std": right_std,
        }

        print("[info] 윈도우 요약:", payload)
        _send_window(payload)
        # 그 다음 루프에서 다시 /control 확인 → stop 이면 여기서 멈추고 대기


if __name__ == "__main__":
    main()
