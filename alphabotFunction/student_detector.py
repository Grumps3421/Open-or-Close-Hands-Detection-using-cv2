# student_detector.py
import os
import cv2
import mediapipe as mp
from ultralytics import YOLO
from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["alphabot_db"]
collection = db["registered_students"]

def load_class_name_map():
    """Fetch all students with bracelets from MongoDB."""
    class_name_map = {}
    students = collection.find({})  # lahat ng may bracelet_id
    for student in students:
        bracelet_id = student["bracelet_id"].strip().lower().replace(" ", "")
        student_name = student["student_name"]
        color = student.get("color", "Unknown")
        class_name_map[bracelet_id] = f"{student_name} | {color}"
    print(f"DEBUG: Loaded {len(class_name_map)} bracelet mappings from DB")
    return class_name_map


class StudentDetector:
    def __init__(self, model_path, thresh=0.5):  # lowered threshold for testing
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")

        self.model = YOLO(model_path, task='detect')
        self.labels = self.model.names  # YOLO class names
        print(f"DEBUG: YOLO labels: {self.labels}")  # debug
        self.thresh = thresh

        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

    def get_hand_status(self, landmarks):
        tip_ids = [8, 12, 16, 20]
        fingers = [1 if landmarks[tip].y < landmarks[tip - 2].y else 0 for tip in tip_ids]

        if fingers == [0, 1, 0, 0]:
            return "Inappropriate Action Detected"
        elif sum(fingers) >= 3:
            return "Open"
        else:
            return "Close"

    def detect_frame(self, frame):
        # YOLO detection
        detections = self.model(frame, verbose=False)[0].boxes
        detected_classes = []

        for det in detections:
            conf = det.conf.item()
            cls_id = int(det.cls.item())
            cls_name = self.labels[cls_id]
            if conf >= self.thresh:
                detected_classes.append(cls_name)
                print(f"DEBUG: YOLO detected class={cls_name} conf={conf:.2f}")

        # MediaPipe hand detection
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        hand_status = None
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                hand_status = self.get_hand_status(hand_landmarks.landmark)
                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        # Map detected YOLO classes to student names via MongoDB bracelet_id lookup
        student_names = []
        for cls in detected_classes:
            # Hanapin kung may bracelet_id match sa DB
            student_doc = collection.find_one({"bracelet_id": cls})
            if student_doc:
                student_names.append(student_doc["student_name"])

        if student_names:
            student_names = list(set(student_names))  # remove duplicates
        else:
            student_names = ["No bracelet detected"]

        if not hand_status:
            hand_status = "None"

        return frame, student_names, hand_status

    def release(self):
        self.hands.close()

    def detect(self, use_camera=True, show_window=True):
        cap = cv2.VideoCapture(0 if use_camera else 1)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame, student_names, hand_status = self.detect_frame(frame)
            output_text = f"{', '.join(student_names)} | hand status: {hand_status}"
            print(output_text)
            
            if student_names and student_names[0] != "No Bracelet detected":
                print("Bracelet Detected , Stopping YOLO!!")
                break

            if show_window:
                cv2.putText(frame, output_text, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.imshow("YOLO detection results", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        cap.release()
        cv2.destroyAllWindows()