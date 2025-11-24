import json, time, serial, requests
from statistics import fmean
from typing import Tuple
from .config import SERIAL_PORT, SERIAL_BAUD, API_BASE, WINDOW_SEC
from .welford import Welford

def _parse_line(line: str) -> Tuple[float,float,float,float,float,float]:
    line = line.strip()
    if not line:
        raise ValueError("empty")
    if line.startswith("{"):
        obj = json.loads(line)
        vals = (obj["L1"], obj["L2"], obj["L3"], obj["R1"], obj["R2"], obj["R3"])
        return tuple(float(x) for x in vals)
    parts = [p.strip() for p in line.split(",")]
    if len(parts) != 6:
        raise ValueError("not 6 columns")
    return tuple(float(x) for x in parts)

def _post(payload: dict) -> dict:
    r = requests.post(f"{API_BASE}/ingest", json=payload, timeout=5)
    r.raise_for_status()
    return r.json()

def main():
    ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
    print(f"[serial] open {SERIAL_PORT} @{SERIAL_BAUD}")

    while True:
        L1s,L2s,L3s,R1s,R2s,R3s = [],[],[],[],[],[]
        left_w, right_w = Welford(), Welford()
        n_ok = 0
        t0 = time.time()

        while time.time() - t0 < WINDOW_SEC:
            raw = ser.readline().decode(errors="ignore")
            if not raw:
                continue
            try:
                L1,L2,L3,R1,R2,R3 = _parse_line(raw)
                L1s.append(L1); L2s.append(L2); L3s.append(L3)
                R1s.append(R1); R2s.append(R2); R3s.append(R3)
                left_w.add(L1 + L2 + L3)
                right_w.add(R1 + R2 + R3)
                n_ok += 1
            except Exception as e:
                print("[skip]", raw.strip(), "->", e)

        if n_ok == 0:
            print("[warn] no samples in window; continue")
            continue

        l1 = fmean(L1s); l2 = fmean(L2s); l3 = fmean(L3s)
        r1 = fmean(R1s); r2 = fmean(R2s); r3 = fmean(R3s)

        left_sum  = l1 + l2 + l3
        right_sum = r1 + r2 + r3
        overall   = (left_sum + right_sum) / 6.0

        payload = {
            "l1_avg": l1, "l2_avg": l2, "l3_avg": l3,
            "r1_avg": r1, "r2_avg": r2, "r3_avg": r3,
            "left_sum_avg": left_sum, "right_sum_avg": right_sum,
            "overall_avg": overall,
            "left_std": left_w.stdev, "right_std": right_w.stdev,
        }

        try:
            resp = _post(payload)
            print(
                f"[ok] n={n_ok} L={resp['left_pct']:.2f}% R={resp['right_pct']:.2f}% "
                f"CoP.x={resp['cop_x_pct']:.1f}% ok={resp['cop_ok']}"
            )
        except Exception as e:
            print("[err] POST failed:", e)

if __name__ == "__main__":
    main()