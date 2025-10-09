import os
import sys
import argparse
import mediapipe as mp
import cv2
from ultralytics import YOLO
from pymongo import MongoClient


def load_class_name_map():
    client = MongoClient("mongodb://localhost:27017")
    db = client["alphabot_db"]
    collection = db["bracelet_registrations"]
    data = collection.find()
    print("=== REGISTERED BRACELETS ===")
    class_map = {}
    for doc in data:
        print(f"{doc['bracelet_id']} => {doc['studentname']}")
        class_map[doc["bracelet_id"]] = doc["studentname"]
    print("===========================")
    return class_map


def detect_student_and_hand(model_path, threshold=0.7):
    class_name_map = load_class_name_map()

    if not os.path.exists(model_path):
        print("Model Not Found")
        return None, None

    model = YOLO(model_path, task='detect')
    labels = model.names

    mp_hands = mp.solutions.hands
    cap = cv2.VideoCapture(0)

    result_data = None  # Store (student_name_or_bracelet_id, hand_status)

    with mp_hands.Hands(min_detection_confidence=0.7,
                        min_tracking_confidence=0.7) as hands:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

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

            # YOLO detection
            results = model(frame, verbose=False)
            detections = results[0].boxes

            detected_classes = []
            for det in detections:
                conf = det.conf.item()
                if conf < threshold:
                    continue
                cls_id = int(det.cls.item())
                cls_name = labels[cls_id]
                detected_classes.append(cls_name)

            if detected_classes and hand_status in ("Close", "Open"):
                for cls in set(detected_classes):
                    student_name = class_name_map.get(cls, cls)
                    result_data = (student_name, hand_status)
                    print(f"Detected: {student_name} | Hand: {hand_status}")
                    cap.release()
                    return result_data  # ✅ Return result immediately

            if hand_status == "Inappropriate Action Detected":
                print("Stop That!! It is not a good gesture")

    cap.release()
    return None, None  # If nothing detected


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='C:\\Programming\\Thesis\\YoLo\\my_model_final\\bracelet_identification_ncnn_model')
    parser.add_argument('--thresh', type=float, default=0.7)
    args = parser.parse_args()

    student, hand = detect_student_and_hand(args.model, args.thresh)
    print("RESULT:", student, hand)
