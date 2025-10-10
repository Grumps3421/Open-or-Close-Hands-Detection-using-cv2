from flask import Blueprint, request, jsonify
from checking_answer import check_answer
from register_students_MVC.model import BraceletModelRegister
from datetime import datetime, timezone

close_bp = Blueprint("close_bp", __name__)
bracelet_model = BraceletModelRegister()  # Initialize model

@close_bp.route("/close", methods=["POST"])
def detect_hand_status():
    data = request.json or {}
    choice = data.get("choice")
    allowed_student = data.get("allowedStudent")  # Optional
    target_bracelet_id = data.get("braceletId")  # Optional filter

    if not choice:
        return jsonify({
            "status": "error",
            "message": "❌ Missing required field: choice"
        }), 400

    # ✅ If allowed_student exists, skip detection
    if allowed_student:
        student_name = allowed_student
        bracelet_id = target_bracelet_id
        hand_status = "close"
        detect_result = "ready"
        result = {}
    else:
        # Run YOLO + MediaPipe detection
        result = check_answer()
        print(f"🖐️ Hand detection result: {result}")
        student_name = result.get("student name")
        bracelet_id = result.get("bracelet_id")
        hand_status = result.get("hand_status").lower()  # lowercase for model
        detect_result = result.get("detect")

        # 🔒 FILTER: If target_bracelet_id is provided, only accept matching bracelets
        if target_bracelet_id:
            if not bracelet_id:
                return jsonify({
                    "status": "no-bracelet",
                    "message": "⚠️ No bracelet detected.",
                    "expected_bracelet": target_bracelet_id
                }), 409
            if str(bracelet_id).strip() != str(target_bracelet_id).strip():
                return jsonify({
                    "status": "unauthorized",
                    "message": f"⚠️ Wrong bracelet detected. Please use your registered bracelet.",
                    "detected_bracelet": bracelet_id,
                    "expected_bracelet": target_bracelet_id
                }), 403

    if not student_name:
        return jsonify({
            "status": "error",
            "message": "❌ No student detected. Try again.",
            "details": result
        }), 400

    # Update score using BraceletModelRegister
    update_message = bracelet_model.update_student_score(result)
    print(f"📊 Update message: {update_message}")

    return jsonify({
        "status": "success",
        "message": f"✅ Logged choice for {student_name}",
        "student": student_name,
        "bracelet_id": bracelet_id,
        "hand_status": hand_status,
        "update_message": update_message
    }), 200
