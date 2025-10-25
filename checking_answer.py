import time
import threading
from alphabotFunction.YoLo.my_model_final.yolo_detect import detect_student_and_hand
import os

# Constants
# Dynamically locate model relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "alphabotFunction", "YoLo", "my_model_final", "bracelet_identification_ncnn_model")
THRESHOLD = 0.85
COOLDOWN = 2  # seconds

# Global locks and trackers
detection_lock = threading.Lock()
last_detection_time = 0
last_student_name = None


def run_yolo_detection():
    """
    Runs YOLO + MediaPipe detection once.
    Prevents overlapping calls and filters random false detections.
    """
    global last_detection_time, last_student_name

    # 🕒 Prevent repeated detections too fast
    remaining_cooldown = COOLDOWN - (time.time() - last_detection_time)
    if remaining_cooldown > 0:
        print(f"🕒 Cooldown active ({remaining_cooldown:.1f}s left)... skipping duplicate detection.")
        return {
            "status": "cooldown",
            "student name": last_student_name,
            "bracelet_id": last_student_name,
            "hand_status": None
        }

    # 🧠 Check if another detection is already running
    if detection_lock.locked():
        print("⚠️ Detection already running, skipping new request.")
        return {
            "status": "busy",
            "student name": None,
            "bracelet_id": None,
            "hand_status": None
        }

    with detection_lock:
        print("🎥 Starting YOLO detection safely...")
        time.sleep(1)  # optional delay

        try:
            student_name, hand_status = detect_student_and_hand(MODEL_PATH, THRESHOLD)
        except Exception as e:
            print(f"❌ Error during YOLO detection: {e}")
            return {
                "status": "error",
                "student name": None,
                "bracelet_id": None,
                "hand_status": None,
                "error": str(e)
            }

        # 🧹 Cleanup
        try:
            import cv2
            cv2.destroyAllWindows()
        except Exception:
            pass

        # 📊 Prepare result
        result_data = {
            "student name": student_name,
            "bracelet_id": student_name,
            "hand_status": hand_status
        }

        if not student_name or not hand_status:
            print("⚠️ No detection found.")
            result_data["status"] = "failed"
        else:
            # ✅ Valid detection
            print(f"✅ Detected: {student_name} | Hand: {hand_status}")
            result_data["status"] = "success"

            # 🔒 Track last detection for next runs
            last_student_name = student_name
            last_detection_time = time.time()

            # 🔔 Print when it's ready again
            def cooldown_notifier():
                time.sleep(COOLDOWN)
                print("✅ Cooldown finished — ready for next detection request!")

            threading.Thread(target=cooldown_notifier, daemon=True).start()

        print(f"🖐️ Final YOLO output → {result_data}")
        return result_data
