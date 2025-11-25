import json, time, serial, requests
from statistics import fmean
from typing import Tuple
from .config import SERIAL_PORT, SERIAL_BAUD, API_BASE, WINDOW_SEC

def _post(payload: dict) -> dict:
    r = requests.post(f"{API_BASE}/ingest", json=payload, timeout=5)
    r.raise_for_status()
    return r.json()

def main():
    ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
    print(f"[serial] open {SERIAL_PORT} @{SERIAL_BAUD}")

    while True:
        raw = ser.readline().decode(errors="ignore").strip()
        if not raw:
            continue

        # 아두이노 measureMode()의 DATA 라인 처리
        if raw.startswith("DATA"):
            parts = raw.split(",")

            #  ["DATA", l1,l2,l3,r1,r2,r3,leftSum,rightSum,overall]
            if len(parts) != 10:
                print("[skip] malformed:", raw)
                continue

            try:
                l1 = float(parts[1]); l2 = float(parts[2]); l3 = float(parts[3])
                r1 = float(parts[4]); r2 = float(parts[5]); r3 = float(parts[6])
                left_sum = float(parts[7])
                right_sum = float(parts[8])
                overall = float(parts[9])
            except:
                print("[skip] parse error:", raw)
                continue

            payload = {
                "l1_avg": l1,
                "l2_avg": l2,
                "l3_avg": l3,
                "r1_avg": r1,
                "r2_avg": r2,
                "r3_avg": r3,
                "left_sum_avg": left_sum,
                "right_sum_avg": right_sum,
                "overall_avg": overall,
                "left_std": None,
                "right_std": None
            }

            print("[POST] payload:", payload)

            try:
                resp = _post(payload)
                print(
                    f"[ok] L={resp['left_pct']:.1f}% "
                    f"R={resp['right_pct']:.1f}% "
                    f"COP.x={resp['cop_x_pct']:.1f}% ok={resp['cop_ok']}"
                )
            except Exception as e:
                print("[err] POST failed:", e)
