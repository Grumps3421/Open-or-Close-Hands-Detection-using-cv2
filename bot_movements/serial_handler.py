import serial
import time

try:
    print("[INFO] Attempting to open COM3...")
    arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)
    time.sleep(2)
    print(f"[INFO] Connected to Arduino on {arduino.port}")
    print(f"[INFO] Port open? {arduino.is_open}")
except Exception as e:
    print("[ERROR] Cannot configure port, something went wrong.", e)
    arduino = None

def send_command(command):
    global arduino
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
        if arduino: print(f" - is_open = {arduino.is_open}")
        else: print(" - arduino = None")
        return "Arduino not connected"
