from flask import Blueprint, jsonify, request
from checking_answer import run_yolo_detection
from register_students_MVC.model import BraceletModelRegister

# Blueprint setup
close_bp = Blueprint("close_bp", __name__)
bracelet_model = BraceletModelRegister()


@close_bp.route("/close", methods=["POST"])
def detect_close():
    """Handles hand-close detection and updates student score."""

    # ✅ Get JSON data from frontend
    data = request.get_json(force=True)
    choice = data.get("choice", "").lower() if data else ""

    # -------------------------------
    # 🕒 Wait until 'ready' signal
    # -------------------------------
    if choice != "ready":
        print("⏸️ Detection not started — waiting for 'ready' signal.")
        return jsonify({
            "status": "waiting",
            "message": "Detection not started yet. Send {'choice': 'ready'} to begin."
        }), 200

    # -------------------------------
    # 🎥 Run YOLO detection
    # -------------------------------
    print("🎥 Running YOLO detection for /close ...")
    result = run_yolo_detection()
    print(f"🖐️ Detection result: {result}")

    # -------------------------------
    # ❌ Handle failed detection
    # -------------------------------
    if result.get("status") != "success":
        return jsonify({
            "status": "error",
            "message": "❌ No hand or student detected.",
            "details": result
        }), 400

    # -------------------------------
    # ✅ Record student score & subject
    # -------------------------------
    subject = data.get("subject", "").strip()
    result["subject"] = subject  # attach subject to result dict
    update_message = bracelet_model.update_student_score(result)

    print(f"📊 Update message: {update_message}")

    # -------------------------------
    # 🧾 Send response back to frontend
    # -------------------------------
    return jsonify({
        "status": "success",
        "student": result.get("student name"),
        "bracelet_id": result.get("bracelet_id"),
        "hand_status": result.get("hand_status"),
        "subject": subject,
        "update_message": update_message
    }), 200
