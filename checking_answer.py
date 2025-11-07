import time
import threading
import os
import cv2
from pymongo import MongoClient
from sound_player_MVC.sound_controller import SoundController
from alphabotFunction.YoLo.my_model_final.yolo_detect import (
    detect_student_open_hand,
    detect_student_close_hand,
)

# ==========================================
# 🧭 SOUND CONTROLLER INITIALIZATION
sound_controller = SoundController()

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
# 🧭 HELPER FUNCTION - GET BRACELET ID FROM DB
# ==========================================
def get_bracelet_id_by_student(student_name: str):
    """Fetches the bracelet_id of a student from MongoDB."""
    try:
        client = MongoClient("mongodb://localhost:27017")
        db = client["alphabot_db"]
        collection = db["bracelet_registrations"]
        record = collection.find_one({"studentname": student_name})
        if record:
            return record.get("bracelet_id")
        else:
            print(f"❌ No bracelet record found for student '{student_name}'")
    except Exception as e:
        print(f"❌ Error fetching bracelet_id from MongoDB: {e}")
    return None


# ==========================================
# 🖐️ OPEN HAND DETECTION
# ==========================================
def run_yolo_detection_open():
    global last_detection_time, last_student_name

    remaining_cooldown = COOLDOWN - (time.time() - last_detection_time)
    if remaining_cooldown > 0:
        print(f"🕒 Cooldown active ({remaining_cooldown:.1f}s left)... skipping duplicate open-hand detection.")
        return {
            "status": "cooldown",
            "student name": last_student_name,
            "bracelet_id": get_bracelet_id_by_student(last_student_name) if last_student_name else None,
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

        # 🕒 Timeout / no detection
        if student_name == "No bracelet detected" or hand_status == "No hand detected" or not student_name or not hand_status:
            print("⏰ TIMEOUT: No valid student detected (open-hand)")
            sound_controller.play_student_sound("NoAnswer")
            return {
                "status": "timeout",
                "student name": None,
                "bracelet_id": None,
                "hand_status": None,
                "message": "No one answered"
            }

        # Get bracelet ID
        bracelet_id = get_bracelet_id_by_student(student_name)
        if not bracelet_id:
            print(f"⏰ TIMEOUT: Student '{student_name}' detected but no bracelet registered (open-hand)")
            sound_controller.play_student_sound("NoAnswer")
            return {
                "status": "timeout",
                "student name": None,
                "bracelet_id": None,
                "hand_status": None,
                "message": "No registered student answered"
            }

        result_data = {"student name": student_name, "bracelet_id": bracelet_id, "hand_status": hand_status}
        result_data["status"] = "success"

        print(f"✅ Detected: {student_name} | Hand: {hand_status} (open-hand)")
        last_student_name = student_name
        last_detection_time = time.time()

        threading.Thread(target=lambda: (time.sleep(COOLDOWN), print("✅ Cooldown finished — ready for next OPEN-hand detection!")), daemon=True).start()

        print(f"🖐️ Final YOLO OPEN output → {result_data}")
        sound_controller.play_student_sound(result_data["bracelet_id"])
        return result_data


# ==========================================
# ✊ CLOSE HAND DETECTION
# ==========================================
def run_yolo_detection_close():
    global last_detection_time, last_student_name

    remaining_cooldown = COOLDOWN - (time.time() - last_detection_time)
    if remaining_cooldown > 0:
        print(f"🕒 Cooldown active ({remaining_cooldown:.1f}s left)... skipping duplicate close-hand detection.")
        return {
            "status": "cooldown",
            "student name": last_student_name,
            "bracelet_id": get_bracelet_id_by_student(last_student_name) if last_student_name else None,
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

        # 🕒 Timeout / no detection
        if student_name == "No bracelet detected" or hand_status == "No hand detected" or not student_name or not hand_status:
            print("⏰ TIMEOUT: No valid student detected (close-hand)")
            sound_controller.play_student_sound("NoAnswer")
            return {
                "status": "timeout",
                "student name": None,
                "bracelet_id": None,
                "hand_status": None,
                "message": "No one answered"
            }

        # Get bracelet ID
        bracelet_id = get_bracelet_id_by_student(student_name)
        if not bracelet_id:
            print(f"⏰ TIMEOUT: Student '{student_name}' detected but no bracelet registered (close-hand)")
            sound_controller.play_student_sound("NoAnswer")
            return {
                "status": "timeout",
                "student name": None,
                "bracelet_id": None,
                "hand_status": None,
                "message": "No registered student answered"
            }

        result_data = {"student name": student_name, "bracelet_id": bracelet_id, "hand_status": hand_status}
        result_data["status"] = "success"

        print(f"✅ Detected: {student_name} | Hand: {hand_status} (close-hand)")
        last_student_name = student_name
        last_detection_time = time.time()

        threading.Thread(target=lambda: (time.sleep(COOLDOWN), print("✅ Cooldown finished — ready for next CLOSE-hand detection!")), daemon=True).start()

        # ✅ Play sound for successful detection
        print(f"✊ Final YOLO CLOSE output → {result_data}")
        sound_controller.play_student_sound(result_data["bracelet_id"])

        return result_data
