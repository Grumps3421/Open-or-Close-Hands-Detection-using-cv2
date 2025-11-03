from flask import Blueprint, jsonify, request
from checking_answer import run_yolo_detection_open
from register_students_MVC.model import BraceletModelRegister
from routes.AR.route import ar_controller
import threading
import time

# Blueprint setup
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
            }), 429
        detection_running = True

    try:
        data = request.get_json(force=True)
        subject = data.get("choice", "").strip().lower()
        lesson = data.get("lesson", "").strip().lower()

        print("📦 Raw frontend data:", data)
        print(f"🎯 Subject: {subject} | 📖 Lesson: {lesson}")

        # ✅ Validation
        if not subject or not lesson:
            print("⚠️ Missing subject or lesson — detection aborted.")
            return jsonify({
                "status": "error",
                "message": "❌ Both 'choice' (subject) and 'lesson' are required to start detection."
            }), 400
        
        # 📴 STOP AR before YOLO detection
        print("🧠 Stopping AR before YOLO detection...")
        stop_result = ar_controller.stop()
        print(f"🛑 AR stop result: {stop_result['status']}")
        time.sleep(1)

        # ✅ Run YOLO detection (OPEN)
        print("🎥 Running YOLO detection for /open ...")
        result = run_yolo_detection_open()

        # OPEN AR AFTER DETECTION
        print("🔁 Restarting AR after YOLO detection...")
        start_result = ar_controller.start()
        print(f"✅ AR start result: {start_result['status']}")

        # ✅ Handle TIMEOUT - no one answered
        if result.get("status") == "timeout":
            print(f"⏰ TIMEOUT DETECTED - Marking all PRESENT students with 'No answer' and score 0")
            update_message = bracelet_model.mark_no_answer(subject)
            
            return jsonify({
                "status": "timeout",
                "message": update_message,
                "subject": subject,
                "lesson": lesson,
                "allow_next": True
            }), 200

        # ✅ Handle failed detection (not timeout, just failed)
        if result.get("status") != "success":
            return jsonify({
                "status": "error",
                "message": "❌ No hand or student detected (open).",
                "details": result,
                "allow_next": False
            }), 400

        # ✅ Update DB - someone answered
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
            "update_message": update_message,
            "allow_next": True
        }), 200

    finally:
        time.sleep(3)
        detection_running = False
        print("✅ Detection finished — system unlocked.")