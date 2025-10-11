from urllib import request
from flask import Blueprint, jsonify
from checking_answer import run_yolo_detection
from register_students_MVC.model import BraceletModelRegister

open_bp = Blueprint("open_bp", __name__)
bracelet_model = BraceletModelRegister()


@open_bp.route("/open", methods=["GET"])
def detect_open():
    print("🎥 Running YOLO detection for /open ...")
    result = run_yolo_detection()
    print(f"🖐️ Detection result: {result}")
    data = request.json or {}
    choice = data.get("choice")

    if result.get("status") != "success":
        return jsonify({
            "status": "error",
            "message": "❌ No hand or student detected.",
            "details": result
        }), 400

    update_message = bracelet_model.update_student_score(result)
    print(f"📊 Update message: {update_message}")

    return jsonify({
        "status": "success",
        "student": result.get("student name"),
        "bracelet_id": result.get("bracelet_id"),
        "hand_status": result.get("hand_status"),
        "update_message": update_message
    }), 200
