import os
import sys
import argparse
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
# Scan bracelet using YOLO
# =========================
def scan_bracelet(entry_field, result_label):
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='C:\\Thesis\\backend\\Open-or-Close-Hands-Detection-using-cv2\\alphabotFunction\\YoLo\\my_model_final\\bracelet_identification_ncnn_model')
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
    allowed_student = {"student_name": None}
