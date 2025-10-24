from flask import Blueprint, jsonify, request
from checking_answer import run_yolo_detection
from register_students_MVC.model import BraceletModelRegister
import threading
import time

open_bp = Blueprint("open_bp", __name__)
bracelet_model = BraceletModelRegister()

# 🧠 Global flag + lock
detection_running = False
lock = threading.Lock()

@open_bp.route("/open", methods=["POST"])
def detect_open():
    global detection_running

    with lock:
        if detection_running:
            print("⚠️ Detection already running — rejecting new request.")
            return jsonify({
                "status": "error",
                "message": "⚠️ Detection already in progress. Please wait..."
            }), 429  # 429 = Too Many Requests
        detection_running = True

    try:
        data = request.get_json(force=True)
        subject = data.get("choice", "").strip().lower()
        lesson = data.get("lesson", "").strip().lower()
        
        print("📦 Raw frontend data:", data)
        print(f"🎯 Subject: {subject} | 📖 Lesson: {lesson}")

        # ✅ Validation: kailangan may subject at lesson pareho
        if not subject or not lesson:
            print("⚠️ Missing subject or lesson — detection aborted.")
            return jsonify({
                "status": "error",
                "message": "❌ Both 'choice' (subject) and 'lesson' are required to start detection."
            }), 400

        # ✅ Run YOLO detection
        print("🎥 Running YOLO detection for /open ...")
        result = run_yolo_detection()

        if result.get("status") != "success":
            return jsonify({
                "status": "error",
                "message": "❌ No hand or student detected.",
                "details": result
            }), 400

        # ✅ Update DB
        result["subject"] = subject
        result["lesson"] = lesson
        update_message = bracelet_model.update_student_score(result)

        print(f"📊 Update message: {update_message}")

        return jsonify({
            "status": "success",
            "student": result.get("student name"),
            "bracelet_id": result.get("bracelet_id"),
            "hand_status": result.get("hand_status"),
            "subject": subject,
            "lesson": lesson,
            "update_message": update_message
        }), 200

    finally:
        # ⏳ Small cooldown para di mag-spam
        time.sleep(3)
        detection_running = False
        print("✅ Detection finished — system unlocked.")
