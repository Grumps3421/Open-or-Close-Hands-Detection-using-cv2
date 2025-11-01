from flask import Blueprint, jsonify, request
from checking_answer import run_yolo_detection_close  # ✅ close hand function
from register_students_MVC.model import BraceletModelRegister
from routes.AR.route import ar_controller
import threading
import time

# Blueprint setup
close_bp = Blueprint("close_bp", __name__)
bracelet_model = BraceletModelRegister()

# 🧠 Global flag + lock
detection_running = False
lock = threading.Lock()


@close_bp.route("/close", methods=["POST"])
def detect_close():
    global detection_running

    with lock:
        if detection_running:
            print("⚠️ Detection already running — rejecting new request.")
            return jsonify({
                "status": "error",
                "message": "⚠️ Detection already in progress. Please wait..."
            }), 429  # Too Many Requests
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
        time.sleep(1)  # give time to release the camera properly

        # ✅ Run YOLO detection (CLOSE)
        print("🎥 Running YOLO detection for /close ...")
        result = run_yolo_detection_close()

        # OPEN AR AFTER DETECTION
        print("🔁 Restarting AR after YOLO detection...")
        start_result = ar_controller.start()
        print(f"✅ AR start result: {start_result['status']}")

        # ✅ Handle failed detection
        if result.get("status") != "success":
            return jsonify({
                "status": "error",
                "message": "❌ No hand or student detected (close).",
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
        # ⏳ Cooldown bago payagan ulit
        time.sleep(3)
        detection_running = False
        print("✅ Detection finished — system unlocked.")
