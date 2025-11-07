# serial_handler.py
import serial
import time

try:
    arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)
    time.sleep(2)
    print("[INFO] Connected to Arduino on COM3")
except Exception as e:
    print("[ERROR] Cannot configure port, something went wrong.", e)
    arduino = None

def send_command(command):
    if arduino and arduino.is_open:
        try:
            arduino.write((command + '\n').encode())
            print(f"[SERIAL] Sent: {command}")
            return command
        except Exception as e:
            print("[ERROR] Failed to send command:", e)
            return "Error sending"
    else:
        print("[ERROR] Arduino not connected or port is closed.")
        return "Arduino not connected"