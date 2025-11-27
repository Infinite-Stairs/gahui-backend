import serial
import time

ser = serial.Serial('COM10', 9600, timeout=1)
time.sleep(2)

print("Start reading STEP...")

while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        print("Received:", line)




# postgresql://gahui:UTMyUVGeVjcQ3tTbw3Pd3flix2ce8Hft@dpg-d4i0n32li9vc73eg01eg-a.oregon-postgres.render.com/game_results_tpj5
