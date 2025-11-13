import os, json

#defalut 값 수정 필요
_DEFAULT = {
    "L1": (0.25, 0.20),
    "L2": (0.25, 0.50),
    "L3": (0.25, 0.80),
    "R1": (0.75, 0.20),
    "R2": (0.75, 0.50),
    "R3": (0.75, 0.80),
}

def load_sensor_pos():
    val = os.getenv("SENSOR_POS_JSON", "").strip()
    if not val:
        return _DEFAULT
    try:
        d = json.loads(val)
        return {k: (float(v[0]), float(v[1])) for k, v in d.items()}
    except Exception as e:
        print("[warn] SENSOR_POS_JSON parse error:", e)
        return _DEFAULT

SENSOR_POS = load_sensor_pos()
