import os
import cv2
import mediapipe as mp
import time
from ultralytics import YOLO
from pymongo import MongoClient

# Suppress TensorFlow logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# ============================================================
# 🔧 Load bracelet mappings from MongoDB
# ============================================================
def load_class_name_map():
    """Loads registered bracelets and their student names from MongoDB."""
    client = MongoClient("mongodb://localhost:27017")
    db = client["alphabot_db"]
    collection = db["bracelet_registrations"]
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
# 🧠 Detection Function — runs YOLO + MediaPipe
# ============================================================
def detect_student_and_hand(model_path, threshold=0.7):
    """
    Detects bracelet (via YOLO) and hand gesture (via MediaPipe).
    Returns:
        (student_name, hand_status)
    """
    if not os.path.exists(model_path):
        print(f"❌ Model not found at: {model_path}")
        return None, None

    print("🧠 Loading YOLO model for bracelet detection...")
    model = YOLO(model_path, task='detect')
    labels = model.names

    # Load registered bracelets
    class_name_map = load_class_name_map()
    registered_bracelets = set(class_name_map.keys())

    mp_hands = mp.solutions.hands
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Cannot open camera.")
        return None, None

    print("🎥 Starting detection...")
    student_detected = None
    hand_status = None
    start_time = time.time()
    timeout = 20  # seconds (max detection duration)

    with mp_hands.Hands(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
        max_num_hands=6
    ) as hands:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("⚠️ Frame capture failed.")
                break

            # Flip frame horizontally for natural camera view
            frame = cv2.flip(frame, 1)

            # MediaPipe hand detection
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            hand_res = hands.process(rgb)

            if hand_res.multi_hand_landmarks:
                for hlm in hand_res.multi_hand_landmarks:
                    lm = hlm.landmark
                    tip_ids = [8, 12, 16, 20]
                    fingers = [1 if lm[tip].y < lm[tip - 2].y else 0 for tip in tip_ids]

                    # Determine hand status
                    if fingers == [0, 1, 0, 0]:
                        hand_status = "Inappropriate Action Detected"
                    elif sum(fingers) >= 3:
                        hand_status = "open"
                    else:
                        hand_status = "close"

            # YOLO bracelet detection
            results = model(frame, verbose=False)
            detections = results[0].boxes

            detected_classes = []
            for det in detections:
                conf = det.conf.item()
                if conf < threshold:
                    continue
                cls_id = int(det.cls.item())
                cls_name = labels[cls_id]

                # Only use registered bracelets
                if cls_name in registered_bracelets:
                    detected_classes.append(cls_name)
                else:
                    print(f"⚠️ Ignored unregistered bracelet: {cls_name}")

            if detected_classes:
                bracelet_id = detected_classes[0]
                student_detected = class_name_map.get(bracelet_id)

            # Show the live video feed (optional, press 'q' to exit early)
            cv2.imshow("Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("🛑 Detection manually stopped.")
                break

            # Stop when both student and hand status detected
            if student_detected and hand_status:
                print(f"✅ Detected: {student_detected} | Hand: {hand_status}")
                break

            # Timeout handling
            if time.time() - start_time > timeout:
                print("⏰ Timeout: No detection after 20s.")
                break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

    return student_detected, hand_status


# ============================================================
# 🧪 Local Testing
# ============================================================
if __name__ == "__main__":
    MODEL_PATH = (
        r"C:\Thesis\backend\Open-or-Close-Hands-Detection-using-cv2"
        r"\alphabotFunction\YoLo\my_model_final\bracelet_identification_ncnn_model"
    )

    student, hand = detect_student_and_hand(MODEL_PATH)
    print(f"\n📋 Final Detection Result → Student: {student} | Hand: {hand}")
