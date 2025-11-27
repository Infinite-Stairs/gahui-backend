import uvicorn
import threading
import sys
import os
import time

# ---------------------------------------------------------
# 1. 환경 변수 설정 (Render 원격 DB 주소)
# ---------------------------------------------------------
# 서버(Func1)가 실행될 때 이 주소를 사용하여 DB에 접속합니다.
os.environ["DATABASE_URL"] = "postgresql://plantar_min_db_user:HFRT1QPoIxlpErmhrfRTKOwS4XVjOS9P@dpg-d4i358ggjchc73dk5de0-a.oregon-postgres.render.com/plantar_min_db?sslmode=require"

# ---------------------------------------------------------
# 2. 시스템 경로 설정
# ---------------------------------------------------------
# Func1, Func2 폴더를 파이썬이 찾을 수 있게 경로를 추가합니다.
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, "Func1"))

# ---------------------------------------------------------
# 3. 모듈 불러오기
# ---------------------------------------------------------
try:
    # 로컬 게임 서버 (Func1/main_server.py)
    from Func1.test_main_server import app as fastapi_app


    # 센서 수집기 (Func2/pi/collector.py)
    from Func2.pi.collector_1 import run_collector

except ImportError as e:
    print("==================================================")
    print(f"[Critical Error] 필수 모듈을 불러올 수 없습니다.")
    print(f"에러 내용: {e}")
    print("Func1, Func2 폴더가 main.py와 같은 위치에 있는지 확인해주세요.")
    print("==================================================")
    sys.exit(1)

# ---------------------------------------------------------
# 4. 실행 로직
# ---------------------------------------------------------
def start_collector_thread():
    """
    서버가 켜지는 동안 잠시 기다렸다가(5초)
    백그라운드에서 센서 수집기를 실행합니다.
    """
    print("[System] 서버 부팅 대기 중... (5초)")
    time.sleep(5)
    print("[System] 센서 수집기(Collector) 활성화 완료! 아두이노 버튼 대기중.")

    # collector.py 내부의 무한 루프 실행 (아두이노 연결 대기)
    run_collector()

def main():
    print("==============================================")
    print("   Infinite Stairs : Game & Sensor Server     ")
    print("==============================================")

    t_collector = threading.Thread(target=start_collector_thread)
    t_collector.daemon = True
    t_collector.start()

    print("[System] FastAPI 서버 시작 (Port: 8000)")
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    main()
'''
import serial
import time
import json
import requests
from typing import Tuple, List, Dict, Any, Optional


# =========================
# [1] 설정값 (Configuration)
# =========================
# 라즈베리파이 실제 포트
SERIAL_PORT = "/dev/ttyACM0"
SERIAL_BAUD = 9600

# 백엔드 API 주소
API_BASE = "https://infinite-stairs-backend.onrender.com"

# SEC 라인 몇 개를 모을지 (10초 윈도우)
WINDOW_SEC = 10  # 10개 SEC = 10초

# 노트북 테스트 시 쓸 수 있는 예시
# SERIAL_PORT = "COM4"


# =========================
# [2] 유틸 함수
# =========================

def avg(xs: List[float]) -> float:
    """리스트 평균 계산 (비어 있으면 0.0 반환)."""
    return sum(xs) / len(xs) if xs else 0.0


def parse_sec_line(line: str) -> Optional[Tuple[float, float, float, float, float, float]]:
    """
    'SEC, ...' 형식의 라인을 파싱해서 (L1, L2, L3, R1, R2, R3)를 반환.
    포맷 예시: SEC,123,456,789,100,200,300
    """
    line = line.strip()
    if not line.startswith("SEC,"):
        return None

    parts = [p.strip() for p in line.split(",")]

    # parts[0] = 'SEC', parts[1]~[6] = L1~R3 여야 함
    if len(parts) < 7:
        print(f"[warn] SEC 라인 항목 개수 부족: {line}")
        return None

    try:
        L1 = float(parts[1])
        L2 = float(parts[2])
        L3 = float(parts[3])
        R1 = float(parts[4])
        R2 = float(parts[5])
        R3 = float(parts[6])
        return (L1, L2, L3, R1, R2, R3)
    except ValueError:
        print(f"[warn] SEC 라인 숫자 변환 실패: {line}")
        return None


def handle_data_line(line: str) -> None:
    """
    'DATA,...' 형식 디버깅 출력.
    포맷 예시: DATA,l1,l2,l3,r1,r2,r3,left_sum,right_sum,overall
    """
    parts = [p.strip() for p in line.split(",")]
    if len(parts) < 10:
        print(f"[warn] DATA 라인 항목 개수 부족: {line}")
        return

    try:
        l1 = float(parts[1])
        l2 = float(parts[2])
        l3 = float(parts[3])
        r1 = float(parts[4])
        r2 = float(parts[5])
        r3 = float(parts[6])

        left_sum = float(parts[7])
        right_sum = float(parts[8])
        overall = float(parts[9])

        print("센서값:", l1, l2, l3, r1, r2, r3)
        print("왼발:", left_sum, "오른발:", right_sum, "전체:", overall)
    except ValueError:
        print(f"[warn] DATA 라인 숫자 변환 실패: {line}")


def send_window(payload: Dict[str, Any]) -> None:
    """
    10초 요약 페이로드를 백엔드 /ingest로 전송.
    """
    url = f"{API_BASE}/ingest"
    print("[info] 10초 요약 데이터 전송:", url)
    print("[info] payload:", json.dumps(payload, indent=2, ensure_ascii=False))

    try:
        # 실제 전송
        r = requests.post(url, json=payload, timeout=5)
        r.raise_for_status()
        print(f"[info] 업로드 성공 (status={r.status_code})")
    except Exception as e:
        print(f"[error] 업로드 실패: {e}")


# =========================
# [3] 메인 루프
# =========================

def main():
    print(f"[info] 시리얼 포트 오픈 시도: {SERIAL_PORT} @ {SERIAL_BAUD}")

    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
    except serial.SerialException as e:
        print(f"[error] 시리얼 포트를 열 수 없습니다: {e}")
        return

    print("[info] collector 데몬 시작")

    # SEC 윈도우용 리스트
    l1_vals: List[float] = []
    l2_vals: List[float] = []
    l3_vals: List[float] = []
    r1_vals: List[float] = []
    r2_vals: List[float] = []
    r3_vals: List[float] = []

    while True:
        try:
            raw = ser.readline()
            if not raw:
                # timeout일 때
                continue

            line = raw.decode(errors="ignore").strip()
            if not line:
                continue

            # --- 1) DATA 라인: 디버깅 ---
            if line.startswith("DATA"):
                handle_data_line(line)
                continue

            # --- 2) SEC 라인: 1초 요약 → WINDOW_SEC개 모이면 전송 ---
            if line.startswith("SEC,"):
                parsed = parse_sec_line(line)
                if parsed is None:
                    continue

                L1, L2, L3, R1, R2, R3 = parsed

                l1_vals.append(L1)
                l2_vals.append(L2)
                l3_vals.append(L3)
                r1_vals.append(R1)
                r2_vals.append(R2)
                r3_vals.append(R3)

                print(f"[info] SEC 수신 ({len(l1_vals)}/{WINDOW_SEC}) "
                      f"L1={L1:.1f}, L2={L2:.1f}, L3={L3:.1f}, "
                      f"R1={R1:.1f}, R2={R2:.1f}, R3={R3:.1f}")

                # WINDOW_SEC개 모이면 윈도우 완성
                if len(l1_vals) >= WINDOW_SEC:
                    # 평균 계산
                    l1_avg = avg(l1_vals)
                    l2_avg = avg(l2_vals)
                    l3_avg = avg(l3_vals)
                    r1_avg = avg(r1_vals)
                    r2_avg = avg(r2_vals)
                    r3_avg = avg(r3_vals)

                    left_sum_avg = l1_avg + l2_avg + l3_avg
                    right_sum_avg = r1_avg + r2_avg + r3_avg
                    overall_avg = (left_sum_avg + right_sum_avg) / 2.0

                    # 표준편차는 일단 0.0 (나중에 필요하면 Welford 넣자)
                    left_std = 0.0
                    right_std = 0.0

                    payload = {
                        "l1_avg": l1_avg,
                        "l2_avg": l2_avg,
                        "l3_avg": l3_avg,
                        "r1_avg": r1_avg,
                        "r2_avg": r2_avg,
                        "r3_avg": r3_avg,
                        "left_sum_avg": left_sum_avg,
                        "right_sum_avg": right_sum_avg,
                        "overall_avg": overall_avg,
                        "left_std": left_std,
                        "right_std": right_std,
                    }

                    print("[info] === 10초 윈도우 완료, 서버 전송 ===")
                    send_window(payload)

                    # 다음 윈도우를 위해 리스트 초기화
                    l1_vals.clear()
                    l2_vals.clear()
                    l3_vals.clear()
                    r1_vals.clear()
                    r2_vals.clear()
                    r3_vals.clear()

                continue

            # --- 3) 그 외 라인들은 그냥 로그만 ---
            print(f"[debug] 기타 라인: {line}")

        except serial.SerialException as e:
            print(f"[error] 시리얼 통신 오류: {e}")
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n[info] 수동 종료 (Ctrl+C)")
            break
        except Exception as e:
            print(f"[error] 알 수 없는 오류: {e}")
            time.sleep(0.1)

if __name__ == "__main__":
    main()
    '''