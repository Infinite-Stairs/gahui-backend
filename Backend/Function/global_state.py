# Func1/global_state.py

class GlobalState:
    def __init__(self):
        self.serial_connection = None  # 아두이노 연결 객체 저장
        self.is_collecting = False     # 데이터 수집 중인지 여부

# 이 변수를 다른 파일들이 import해서 같이 씁니다.
state = GlobalState()


