import os, json

#defalut 값 수정 완료
_DEFAULT = {
    "L1": (375, 360),
    "L2": (330, 330),
    "L3": (380, 215),
    "R1": (660, 350),
    "R2": (700, 330),
    "R3": (650, 220),
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
