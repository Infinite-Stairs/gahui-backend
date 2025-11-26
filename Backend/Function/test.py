import serial
import time

def send_one_to_arduino():
    # 1. 아두이노 연결 설정
    # 라즈베리 파이에서 아두이노는 보통 '/dev/ttyACM0' 또는 '/dev/ttyUSB0'로 잡힙니다.
    # 터미널에서 'ls /dev/tty*' 명령어로 확인 가능합니다.
    port = '/dev/ttyACM0'  
    baud_rate = 9600       # 아두이노 코드의 Serial.begin(9600)과 맞춰야 합니다.

    try:
        # 시리얼 포트 열기
        ser = serial.Serial(port, baud_rate, timeout=1)
        
        # 중요: 시리얼 포트를 열면 아두이노가 재부팅됩니다. 
        # 부팅이 완료될 때까지 잠시 기다려야 데이터가 유실되지 않습니다.
        print("아두이노 접속 중...")
        time.sleep(2) 
        
        # 2. 데이터 전송
        # write() 함수는 바이트(bytes) 단위로 보내야 하므로 b'1' 또는 '1'.encode()를 사용합니다.
        ser.write(b'1')
        print("신호 전송 완료: 1")

        # (선택) 아두이노가 잘 받았는지 응답을 확인하고 싶다면:
        # if ser.in_waiting > 0:
        #     line = ser.readline().decode('utf-8').rstrip()
        #     print(f"아두이노 응답: {line}")

        # 3. 연결 종료
        ser.close()

    except serial.SerialException as e:
        print(f"시리얼 통신 에러 발생: {e}")
        print("아두이노가 연결된 포트(/dev/ttyACM0 등)가 맞는지 확인해주세요.")
    except Exception as e:
        print(f"기타 에러: {e}")

# 함수 실행
if __name__ == "__main__":
    send_one_to_arduino()








    