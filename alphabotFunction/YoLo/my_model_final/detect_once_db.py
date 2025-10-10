import os
import sys
import argparse
import mediapipe as mp
import cv2
from ultralytics import YOLO
from pymongo import MongoClient


def detect_student_and_hand(model_path, threshold=0.7):
    """
    Detect bracelet and hand gesture.
    Returns:
        (student_name_or_bracelet_id, hand_status)
    """

    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["alphabot_db"]
    collection = db["bracelet_registrations"]

    # Load bracelet -> student name map
    class_name_map = {
        doc["bracelet_id"]: doc["studentname"]
        for doc in collection.find()
    }

    if not class_name_map:
        print("⚠️ No bracelet registrations found in MongoDB!")
        return None, None

    # Check model path
    if not os.path.exists(model_path):
        print("❌ Model Not Found:", model_path)
        return None, None

    # Load YOLO model
    model = YOLO(model_path, task="detect")
    labels = model.names

    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    cap = cv2.VideoCapture(0)

    locked_student = None

    with mp_hands.Hands(
        min_detection_confidence=0.7, min_tracking_confidence=0.7
    ) as hands:

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Detect hand landmarks
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            hres = hands.process(rgb)
            hand_status = None

            if hres.multi_hand_landmarks:
                for hlm in hres.multi_hand_landmarks:
                    lm = hlm.landmark
                    tip_ids = [8, 12, 16, 20]
                    fingers = [1 if lm[tip].y < lm[tip - 2].y else 0 for tip in tip_ids]

                    if fingers == [0, 1, 0, 0]:
                        hand_status = "Inappropriate Action Detected"
                    elif sum(fingers) >= 3:
                        hand_status = "Open"
                    else:
                        hand_status = "Close"

            # Run YOLO detection
            results = model(frame, verbose=False)
            detections = results[0].boxes

            current_detected_class = None

            for det in detections:
                conf = det.conf.item()
                if conf < threshold:
                    continue

                cls_id = int(det.cls.item())
                cls_name = labels[cls_id]

                if locked_student is None:
                    locked_student = cls_name
                    print(f"🎯 Locked to: {class_name_map.get(locked_student, locked_student)}")

                if cls_name == locked_student:
                    current_detected_class = cls_name
                    break

            # ✅ If valid detection and hand status found
            if current_detected_class and hand_status in ("Close", "Open"):
                student_name = class_name_map.get(current_detected_class, current_detected_class)
                print(f"✅ Detected: {student_name} | Hand: {hand_status}")
                cap.release()
                try:
                    cv2.destroyAllWindows()
                except cv2.error:
                    pass
                return student_name, hand_status

            if hand_status == "Inappropriate Action Detected":
                print("🚫 Stop That!! It is not a good gesture")

    cap.release()
    try:
        cv2.destroyAllWindows()
    except cv2.error:
        pass
    return None, None


# ✅ For standalone test
if _name_ == "_main_":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        default="C:\Thesis\backend\Open-or-Close-Hands-Detection-using-cv2\alphabotFunction\YoLo\my_model_final\bracelet_identification_ncnn_model",
    )
    parser.add_argument("--thresh", type=float, default=0.7)
    args = parser.parse_args()

    student, hand = detect_student_and_hand(args.model, args.thresh)
    print("\nRESULT:", student, "|", hand)