# student_detector.py
import os
import cv2
import mediapipe as mp
from ultralytics import YOLO

from lib.db_config import registered_student_collection
from services.load_class_name_map import load_class_name_map




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

        self.class_name_map = load_class_name_map()

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
        detections = self.model(frame, verbose=False)[0].boxes
        detected_students = []

        # Step 1: YOLO bracelet detections
        for det in detections:
            conf = det.conf.item()
            cls_id = int(det.cls.item())
            cls_name = self.labels[cls_id]
            if conf >= self.thresh:
                student_doc = registered_student_collection.find_one({"bracelet_id": cls_name})
                if student_doc:
                    x1, y1, x2, y2 = map(int, det.xyxy[0].tolist())  # bounding box
                    detected_students.append({
                        "name": student_doc["student_name"],
                        "box": (x1, y1, x2, y2),
                        "hand_status": "None"
                    })

        # Step 2: MediaPipe hand detection
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # get hand bounding box
                h, w, _ = frame.shape
                xs = [lm.x * w for lm in hand_landmarks.landmark]
                ys = [lm.y * h for lm in hand_landmarks.landmark]
                hx1, hy1, hx2, hy2 = int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))

                # Step 3: Find the closest bracelet box
                for student in detected_students:
                    sx1, sy1, sx2, sy2 = student["box"]
                    # check overlap
                    if hx1 < sx2 and hx2 > sx1 and hy1 < sy2 and hy2 > sy1:
                        student["hand_status"] = self.get_hand_status(hand_landmarks.landmark)

                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        return frame, detected_students

    def release(self):
        self.hands.close()

    def detect(self, use_camera=True, show_window=True):
        cap = cv2.VideoCapture(0 if use_camera else 1)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame, detected_students = self.detect_frame(frame)

            # Build output text for each detected student
            if detected_students:
                student = detected_students[0]  # ✅ only first student
                output_text = f"{student['name']} | Hand Status: {student['hand_status']}"
                print(output_text)

                if show_window:
                    x1, y1, x2, y2 = student["box"]
                    cv2.putText(frame, output_text, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            else:
                print("No bracelet detected")
                output_text = "No bracelet detected"
                if show_window:
                    cv2.putText(frame, output_text, (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

            if show_window:
                cv2.imshow("YOLO detection results", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        cap.release()
        cv2.destroyAllWindows()
