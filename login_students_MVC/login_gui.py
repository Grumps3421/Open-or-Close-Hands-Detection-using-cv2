import os
import sys
import argparse
import mediapipe as mp
import time
import cv2
from ultralytics import YOLO
from pymongo import MongoClient
import tkinter as tk
from tkinter import messagebox

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# =========================
# MongoDB connection
# =========================
def load_class_name_map():
    client = MongoClient("mongodb://localhost:27017")
    db = client["alphabot_db"]
    collection = db["bracelet_registrations"]
    data = collection.find()
    class_map = {}
    for doc in data:
        class_map[doc["bracelet_id"]] = doc["studentname"]
    return class_map

class_name_map = load_class_name_map()


# =========================
# YOLO + MediaPipe Detection
# =========================
def start_detection(allowed_bracelet):
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='C:\\Programming\\Thesis\\YoLo\\my_model_final\\bracelet_identification_ncnn_model')
    parser.add_argument('--thresh', type=float, default=0.7)
    args = parser.parse_args()

    if not os.path.exists(args.model):
        print("Model Not Found")
        sys.exit(1)

    model = YOLO(args.model, task='detect')
    labels = model.names

    mp_hands = mp.solutions.hands
    cap = cv2.VideoCapture(0)

    start_time = time.time()
    duration = 10  # seconds

    with mp_hands.Hands(min_detection_confidence=0.7,
                        min_tracking_confidence=0.7,
                        max_num_hands=6) as hands:
        while True:
            elapsed = time.time() - start_time
            remaining = int(duration - elapsed)

            if remaining <= 0:
                print("\n⏹️ 10 seconds elapsed. Stopping program...")
                break

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
                    fingers = [1 if lm[tip].y < lm[tip-2].y else 0 for tip in tip_ids]

                    if fingers == [0, 1, 0, 0]:
                        hand_status = "Inappropriate Action Detected"
                    elif sum(fingers) >= 3:
                        hand_status = "Open"
                    else:
                        hand_status = "Close"

            results = model(frame, verbose=False)
            detections = results[0].boxes

            detected_classes = []
            for det in detections:
                conf = det.conf.item()
                if conf < args.thresh:
                    continue
                cls_id = int(det.cls.item())
                cls_name = labels[cls_id]
                detected_classes.append(cls_name)

            # === Only Detect Logged-In Student ===
            if allowed_bracelet in detected_classes:
                student_name = class_name_map.get(allowed_bracelet, allowed_bracelet)
                if hand_status:
                    print(f"\n👤 {student_name} detected | Hand: {hand_status}")
            else:
                if detected_classes:
                    print(f"\n⚠️ Other bracelets detected, ignoring...")

    cap.release()
    # (No destroyAllWindows for headless environment)


# =========================
# Scan bracelet using YOLO
# =========================
def scan_bracelet(entry_field, result_label):
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='C:\\Programming\\Thesis\\YoLo\\my_model_final\\bracelet_identification_ncnn_model')
    parser.add_argument('--thresh', type=float, default=0.7)
    args = parser.parse_args()

    if not os.path.exists(args.model):
        messagebox.showerror("Error", "YOLO model not found.")
        return

    model = YOLO(args.model, task='detect')
    labels = model.names

    cap = cv2.VideoCapture(0)
    start_time = time.time()
    duration = 8  # seconds to scan bracelet

    detected_bracelet = None
    result_label.config(text="📸 Scanning for bracelet... (show your bracelet to the camera)", fg="black")

    while True:
        elapsed = time.time() - start_time
        remaining = int(duration - elapsed)

        if remaining <= 0 or detected_bracelet:
            break

        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, verbose=False)
        detections = results[0].boxes

        for det in detections:
            conf = det.conf.item()
            if conf < args.thresh:
                continue
            cls_id = int(det.cls.item())
            cls_name = labels[cls_id]
            detected_bracelet = cls_name
            break

    cap.release()

    if detected_bracelet:
        entry_field.delete(0, tk.END)
        entry_field.insert(0, detected_bracelet)

        student_name = class_name_map.get(detected_bracelet, "Not Registered")
        result_label.config(
            text=f"✅ Bracelet Detected: {detected_bracelet}\n👤 Student: {student_name}",
            fg="green"
        )
    else:
        result_label.config(text="⚠️ No bracelet detected.", fg="red")


# =========================
# Tkinter GUI
# =========================
def start_gui():
    def login():
        bracelet_id = bracelet_entry.get().strip()
        student_name = class_name_map.get(bracelet_id)

        if not bracelet_id:
            messagebox.showerror("Error", "Please enter or scan your Bracelet ID")
            return

        if not student_name:
            messagebox.showerror("Not Registered", f"Bracelet ID '{bracelet_id}' not found in database.")
            return

        messagebox.showinfo("Login Successful", f"Welcome, {student_name}!")
        root.destroy()
        start_detection(bracelet_id)

    def scan_action():
        scan_bracelet(bracelet_entry, result_label)

    def exit_app():
        root.destroy()

    root = tk.Tk()
    root.title("Student Bracelet Login")
    root.attributes('-fullscreen', True)
    root.configure(bg="#f0f0f0")

    # Center Frame for content
    frame = tk.Frame(root, bg="#f0f0f0")
    frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(frame, text="🎓 Student Bracelet Login", font=("Arial", 28, "bold"), bg="#f0f0f0").pack(pady=20)
    tk.Label(frame, text="Bracelet ID:", font=("Arial", 16), bg="#f0f0f0").pack(pady=5)
    bracelet_entry = tk.Entry(frame, width=40, font=("Arial", 16))
    bracelet_entry.pack(pady=10)

    tk.Button(frame, text="📸 Scan Bracelet", command=scan_action,
              width=20, height=2, bg="#0078D7", fg="white", font=("Arial", 14, "bold")).pack(pady=10)
    tk.Button(frame, text="✅ Login", command=login,
              width=15, height=2, bg="green", fg="white", font=("Arial", 14, "bold")).pack(pady=10)

    # Result label
    result_label = tk.Label(frame, text="", font=("Arial", 14), wraplength=600, bg="#f0f0f0")
    result_label.pack(pady=20)

    # Exit Button
    tk.Button(frame, text="❌ Exit", command=exit_app,
              width=10, height=1, bg="red", fg="white", font=("Arial", 12, "bold")).pack(pady=10)

    root.mainloop()


# =========================
# Run GUI
# =========================
if __name__ == "__main__":
    start_gui()
