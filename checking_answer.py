import time
import threading
import os
import cv2
from alphabotFunction.YoLo.my_model_final.yolo_detect import (
    detect_student_open_hand,
    detect_student_close_hand,
)

# === Constants ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(
    BASE_DIR, "alphabotFunction", "YoLo", "my_model_final", "bracelet_identification_ncnn_model"
)
THRESHOLD = 0.85
COOLDOWN = 2  # seconds

# === Globals ===
detection_lock = threading.Lock()
last_detection_time = 0
last_student_name = None


# ==========================================
# 🖐️ OPEN HAND DETECTION
# ==========================================
def run_yolo_detection_open():
    """
    Runs YOLO + MediaPipe detection for OPEN hand gesture.
    """
    global last_detection_time, last_student_name

    remaining_cooldown = COOLDOWN - (time.time() - last_detection_time)
    if remaining_cooldown > 0:
        print(f"🕒 Cooldown active ({remaining_cooldown:.1f}s left)... skipping duplicate open-hand detection.")
        return {
            "status": "cooldown",
            "student name": last_student_name,
            "bracelet_id": last_student_name,
            "hand_status": "open",
        }

    if detection_lock.locked():
        print("⚠️ Detection already running (open-hand). Skipping new request.")
        return {"status": "busy", "student name": None, "bracelet_id": None, "hand_status": None}

    with detection_lock:
        print("🎥 Starting YOLO (OPEN HAND) detection safely...")
        time.sleep(1)

        try:
            student_name, hand_status = detect_student_open_hand(MODEL_PATH, THRESHOLD)
        except Exception as e:
            print(f"❌ Error during YOLO open-hand detection: {e}")
            return {"status": "error", "student name": None, "hand_status": None, "error": str(e)}

        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

        result_data = {"student name": student_name, "bracelet_id": student_name, "hand_status": hand_status}

        if not student_name or not hand_status:
            print("⚠️ No detection found (open-hand).")
            result_data["status"] = "failed"
        else:
            print(f"✅ Detected: {student_name} | Hand: {hand_status} (open-hand)")
            result_data["status"] = "success"
            last_student_name = student_name
            last_detection_time = time.time()

            def cooldown_notifier():
                time.sleep(COOLDOWN)
                print("✅ Cooldown finished — ready for next OPEN-hand detection!")

            threading.Thread(target=cooldown_notifier, daemon=True).start()

        print(f"🖐️ Final YOLO OPEN output → {result_data}")
        return result_data


# ==========================================
# ✊ CLOSE HAND DETECTION
# ==========================================
def run_yolo_detection_close():
    """
    Runs YOLO + MediaPipe detection for CLOSE hand gesture.
    """
    global last_detection_time, last_student_name

    remaining_cooldown = COOLDOWN - (time.time() - last_detection_time)
    if remaining_cooldown > 0:
        print(f"🕒 Cooldown active ({remaining_cooldown:.1f}s left)... skipping duplicate close-hand detection.")
        return {
            "status": "cooldown",
            "student name": last_student_name,
            "bracelet_id": last_student_name,
            "hand_status": "close",
        }

    if detection_lock.locked():
        print("⚠️ Detection already running (close-hand). Skipping new request.")
        return {"status": "busy", "student name": None, "bracelet_id": None, "hand_status": None}

    with detection_lock:
        print("🎥 Starting YOLO (CLOSE HAND) detection safely...")
        time.sleep(1)

        try:
            student_name, hand_status = detect_student_close_hand(MODEL_PATH, THRESHOLD)
        except Exception as e:
            print(f"❌ Error during YOLO close-hand detection: {e}")
            return {"status": "error", "student name": None, "hand_status": None, "error": str(e)}

        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

        result_data = {"student name": student_name, "bracelet_id": student_name, "hand_status": hand_status}

        if not student_name or not hand_status:
            print("⚠️ No detection found (close-hand).")
            result_data["status"] = "failed"
        else:
            print(f"✅ Detected: {student_name} | Hand: {hand_status} (close-hand)")
            result_data["status"] = "success"
            last_student_name = student_name
            last_detection_time = time.time()

            def cooldown_notifier():
                time.sleep(COOLDOWN)
                print("✅ Cooldown finished — ready for next CLOSE-hand detection!")

            threading.Thread(target=cooldown_notifier, daemon=True).start()

        print(f"✊ Final YOLO CLOSE output → {result_data}")
        return result_data
