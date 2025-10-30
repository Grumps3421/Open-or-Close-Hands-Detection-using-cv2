import os
import cv2
import time
import mediapipe as mp
from ultralytics import YOLO
from pymongo import MongoClient


# ============================================================
# 🔧 Load bracelet mappings from MongoDB
# ============================================================
def load_class_name_map():
    """Loads registered bracelets and their student names from MongoDB."""
    client = MongoClient("mongodb://localhost:27017")
    db = client["alphabot_db"]
    collection = db["Present_db"]
    data = collection.find()

    class_map = {}
    print("\n=== REGISTERED BRACELETS ===")
    for doc in data:
        student_name = doc.get("student_name") or doc.get("studentname")
        bracelet_id = doc.get("bracelet_id")
        if bracelet_id and student_name:
            class_map[bracelet_id] = student_name
            print(f"{bracelet_id} => {student_name}")
    print("===========================\n")

    return class_map


# ============================================================
# 🖐️ YOLO + MediaPipe (Open Hand Detection)
# ============================================================
def detect_student_open_hand(model_path, threshold=0.7, timeout=20):
    if not os.path.exists(model_path):
        print(f"❌ Model not found at: {model_path}")
        return "No bracelet detected", "No hand detected"

    print("🧠 Loading YOLO model for bracelet detection...")
    model = YOLO(model_path, task='detect')
    labels = model.names

    class_name_map = load_class_name_map()
    registered_bracelets = set(class_name_map.keys())

    mp_hands = mp.solutions.hands
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("❌ Cannot open camera.")
        return "No bracelet detected", "No hand detected"

    print("🎥 Detecting OPEN hand gestures...")
    start_time = time.time()
    student_detected = None
    hand_status = None
    open_frames = 0  # count how many consecutive frames show open hand

    with mp_hands.Hands(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
        max_num_hands=1
    ) as hands:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("⚠️ Frame capture failed.")
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            hand_res = hands.process(rgb)

            hand_status = "not_open"

            if hand_res.multi_hand_landmarks:
                for hlm in hand_res.multi_hand_landmarks:
                    lm = hlm.landmark
                    tip_ids = [8, 12, 16, 20]
                    fingers = [1 if lm[tip].y < lm[tip - 2].y else 0 for tip in tip_ids]

                    # ✅ Strict OPEN condition: at least 3 fingers up
                    if sum(fingers) >= 3:
                        hand_status = "open"
                        open_frames += 1
                    else:
                        open_frames = 0
            else:
                open_frames = 0

            # YOLO detection
            results = model(frame, verbose=False)
            detections = results[0].boxes
            detected_classes = []

            for det in detections:
                conf = det.conf.item()
                if conf < threshold:
                    continue
                cls_name = labels[int(det.cls.item())]
                if cls_name in registered_bracelets:
                    detected_classes.append(cls_name)

            # ✅ Confirm only if stable for 5 frames
            if detected_classes and hand_status == "open" and open_frames >= 5:
                bracelet_id = detected_classes[0]
                student_detected = class_name_map.get(bracelet_id)
                print(f"✅ Detected: {student_detected} | Hand: OPEN (stable)")
                break

            if time.time() - start_time > timeout:
                print("⏰ Timeout: No stable OPEN hand detected.")
                break

    cap.release()
    cv2.destroyAllWindows()

    if not student_detected and hand_status != "open":
        return "No bracelet detected", "No hand detected"
    elif not student_detected:
        return "No bracelet detected", hand_status or "No hand detected"
    elif hand_status != "open":
        return student_detected, "No hand detected"

    return student_detected, hand_status


# ============================================================
# ✊ YOLO + MediaPipe (Close Hand Detection)
# ============================================================
def detect_student_close_hand(model_path, threshold=0.7, timeout=20):
    if not os.path.exists(model_path):
        print(f"❌ Model not found at: {model_path}")
        return "No bracelet detected", "No hand detected"

    print("🧠 Loading YOLO model for bracelet detection...")
    model = YOLO(model_path, task='detect')
    labels = model.names

    class_name_map = load_class_name_map()
    registered_bracelets = set(class_name_map.keys())

    mp_hands = mp.solutions.hands
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("❌ Cannot open camera.")
        return "No bracelet detected", "No hand detected"

    print("🎥 Detecting CLOSED hand gestures...")
    start_time = time.time()
    student_detected = None
    hand_status = None
    close_frames = 0  # count consecutive closed hand frames

    with mp_hands.Hands(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
        max_num_hands=1
    ) as hands:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("⚠️ Frame capture failed.")
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            hand_res = hands.process(rgb)

            hand_status = "not_close"

            if hand_res.multi_hand_landmarks:
                for hlm in hand_res.multi_hand_landmarks:
                    lm = hlm.landmark
                    tip_ids = [8, 12, 16, 20]
                    fingers = [1 if lm[tip].y < lm[tip - 2].y else 0 for tip in tip_ids]

                    # ✅ Strict CLOSE condition: all fingers down
                    if sum(fingers) == 0:
                        hand_status = "close"
                        close_frames += 1
                    else:
                        close_frames = 0
            else:
                close_frames = 0

            # YOLO detection
            results = model(frame, verbose=False)
            detections = results[0].boxes
            detected_classes = []

            for det in detections:
                conf = det.conf.item()
                if conf < threshold:
                    continue
                cls_name = labels[int(det.cls.item())]
                if cls_name in registered_bracelets:
                    detected_classes.append(cls_name)

            # ✅ Confirm only if stable for 5 frames
            if detected_classes and hand_status == "close" and close_frames >= 5:
                bracelet_id = detected_classes[0]
                student_detected = class_name_map.get(bracelet_id)
                print(f"✅ Detected: {student_detected} | Hand: CLOSE (stable)")
                break

            if time.time() - start_time > timeout:
                print("⏰ Timeout: No stable CLOSED hand detected.")
                break

    cap.release()
    cv2.destroyAllWindows()

    if not student_detected and hand_status != "close":
        return "No bracelet detected", "No hand detected"
    elif not student_detected:
        return "No bracelet detected", hand_status or "No hand detected"
    elif hand_status != "close":
        return student_detected, "No hand detected"

    return student_detected, hand_status


# ============================================================
# 🧪 Local Testing
# ============================================================
if __name__ == "__main__":
    MODEL_PATH = (
        r"C:\Users\Jomar\Desktop\andito mga code ko\Open-or-Close-Hands-Detection-using-cv2"
        r"\alphabotFunction\YoLo\my_model_final\bracelet_identification_ncnn_model"
    )

    print("\n--- TESTING OPEN HAND DETECTION ---")
    student_open, hand_open = detect_student_open_hand(MODEL_PATH)
    print(f"📋 Result → Student: {student_open} | Hand: {hand_open}")

    print("\n--- TESTING CLOSE HAND DETECTION ---")
    student_close, hand_close = detect_student_close_hand(MODEL_PATH)
    print(f"📋 Result → Student: {student_close} | Hand: {hand_close}")
