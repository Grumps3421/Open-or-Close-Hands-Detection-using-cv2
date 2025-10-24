import os
import sys
import argparse
import mediapipe as mp
import cv2
from ultralytics import YOLO

class_name_map = {
    "Student1": "Andrei Zyrish Manuel | RED", 
    "Student2": "Railey Joseph Pacheco | GRAY", 
    "Student3": "Jomar Aninon | GREEN", 
    "Student4": "John Lorenz Nungay | ORANGE",
    "Student5": "Alfredo Santos III | PINK",
    "Student6": "Ken Mendoza | BLUE",
    "Student7": "Vincent Tan | WHITE",
    "Student8": "Marc Salongcong | TURQUOISE",
    "Student9": "Justin Juanillas | LIGHTPINK",
    "Student10": "Yuki Ascuncion | SKYBLUE",
    "Student11": "Kurt Del Rosario | MAROON",
    "Student12": "John Erick Cabante | PINKGIRL",
}

parser = argparse.ArgumentParser()
parser.add_argument('--model', default='C:\Thesis\backend\Open-or-Close-Hands-Detection-using-cv2\alphabotFunction\YoLo\my_model_final\bracelet_identification_ncnn_model')
parser.add_argument('--thresh', type=float, default=0.7)
args = parser.parse_args()

if not os.path.exists(args.model):
    print("Model Not Found")
    sys.exit(1)

model  = YOLO(args.model, task='detect')
labels = model.names

mp_hands   = mp.solutions.hands
cap        = cv2.VideoCapture(0)

# 🔒 Store the first detected bracelet class
locked_student = None  

with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # --- Hand Tracking ---
        rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hres  = hands.process(rgb)
        hand_status = None                                

        if hres.multi_hand_landmarks:
            for hlm in hres.multi_hand_landmarks:
                lm = hlm.landmark
                tip_ids = [8, 12, 16, 20]
                fingers = [1 if lm[tip].y < lm[tip-2].y else 0 for tip in tip_ids]

                if fingers == [0,1,0,0]:
                    hand_status = "Inappropriate Action Detected"
                elif sum(fingers) >= 3:
                    hand_status = "Open"
                else:
                    hand_status = "Close"

        # --- Run YOLO every frame ---
        results = model(frame, verbose=False)
        detections = results[0].boxes

        current_detected_class = None

        for det in detections:
            conf = det.conf.item()
            if conf < args.thresh:
                continue

            cls_id   = int(det.cls.item())
            cls_name = labels[cls_id]

            # If we haven't locked yet → take the first bracelet
            if locked_student is None:
                locked_student = cls_name
                print(f"🎯 Locked to: {class_name_map.get(locked_student, locked_student)}")

            # Always ignore bracelets that are not the locked one
            if cls_name == locked_student:
                current_detected_class = cls_name
                break   # stop after finding the locked bracelet

        # --- Use only the locked student ---
        if current_detected_class and hand_status in ("Close", "Open"):
            student_name = class_name_map.get(current_detected_class, current_detected_class)
            print(f"Detected: {student_name} | Hand: {hand_status}")
            

        if hand_status == "Inappropriate Action Detected":
            print("Stop That!!, It is not a good gesture")

        #cv2.imshow("Students", frame)
        #if cv2.waitKey(1) & 0xFF == ord("q"):
            #break

cap.release()
cv2.destroyAllWindows()
