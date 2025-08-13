import os
import cv2
import mediapipe as mp
from ultralytics import YOLO
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["alphabot_db"]
collection = db["registered_students"]

# Build class_name_map from MongoDB (dynamic classname)
class_name_map = {}
students = collection.find({})
for i, student in enumerate(students, start=1):
    class_name_map[student["bracelet_id"]] = f"{student['student_name']} | {student.get('color', 'Unknown')}"

class StudentDetector:
    def __init__(self, model_path, thresh=0.7):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")

        self.model = YOLO(model_path, task='detect')
        self.labels = self.model.names
        self.thresh = thresh

        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils

    def get_hand_status(self, landmarks):
        tip_ids = [8, 12, 16, 20]
        fingers = [1 if landmarks[tip].y < landmarks[tip - 2].y else 0 for tip in tip_ids]

        if fingers == [0, 1, 0, 0]:
            return "Inappropriate Action Detected"
        elif sum(fingers) >= 3:
            return "Open"
        else:
            return "Close"

    def detect(self, use_camera=True, show_window=True):
        cap = cv2.VideoCapture(0 if use_camera else 1)

        with self.mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                hand_results = hands.process(rgb)
                hand_status = None

                if hand_results.multi_hand_landmarks:
                    for hlm in hand_results.multi_hand_landmarks:
                        hand_status = self.get_hand_status(hlm.landmark)

                detections = self.model(frame, verbose=False)[0].boxes
                detected_classes = []

                for det in detections:
                    if det.conf.item() < self.thresh:
                        continue
                    cls_id = int(det.cls.item())
                    cls_name = self.labels[cls_id]
                    detected_classes.append(cls_name)

                if detected_classes and hand_status in ("Close", "Open"):
                    for cls in set(detected_classes):
                        student_name = class_name_map.get(cls, cls)
                        print(f"Detected: {student_name} | Hand: {hand_status}")
                        cap.release()
                        cv2.destroyAllWindows()
                        return

                if hand_status == "Inappropriate Action Detected":
                    print("Stop That!! It is not a good gesture")

                if show_window:
                    cv2.imshow("YOLO detection results", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

        cap.release()
        cv2.destroyAllWindows()
