from flask import Blueprint, request, jsonify
from checking_answer import check_answer_result
from lib.db_config import students_collection
from datetime import datetime, timezone

open_bp = Blueprint("open_bp", __name__)

@open_bp.route("/open", methods=["POST"])
def detect_open_hand_status():
    data = request.json or {}
    choice = data.get("choice")

    if not choice:
        return jsonify({
            "status": "error",
            "message": "❌ Missing required field: choice"
        }), 400

    # 🖐️ Run YOLO + MediaPipe hand detection (Open = correct)
    result = check_answer_result()
    print(f"🖐️ Hand detection result: {result}")

    # Extract detection data
    student_name = result.get("student name")
    bracelet_id = result.get("bracelet_id")
    hand_status = result.get("hand_status")     # “Open” or “Close”
    detect_result = result.get("detect")        # “correct”, “wrong”, “none”

    # Build question log entry
    question_entry = {
        "choice": choice,
        "answer": hand_status if detect_result in ["correct", "wrong"] else None
    }

    # 🧠 If no student detected (e.g., camera failed)
    if not student_name:
        return jsonify({
            "status": "no-student",
            "message": "⚠️ No student detected.",
            "choice_logged": question_entry
        }), 409

    # 🔍 Check if this student already exists
    student_doc = students_collection.find_one({"student name": student_name})

    if not student_doc:
        # 🆕 Create new record
        new_doc = {
            "student name": student_name,
            "bracelet_id": bracelet_id,
            "questions": [question_entry],
            "created_at": datetime.now(timezone.utc),
            "last_updated": datetime.now(timezone.utc)
        }
        students_collection.insert_one(new_doc)
    else:
        # 🔁 Update existing record
        students_collection.update_one(
            {"student name": student_name},
            {
                "$set": {"last_updated": datetime.now(timezone.utc)},
                "$push": {"questions": question_entry}
            }
        )

    # 🧾 Response handling
    if detect_result in ["correct", "wrong"]:
        return jsonify({
            "status": "success",
            "message": f"✅ Detected: {detect_result}",
            "student": student_name,
            "bracelet_id": bracelet_id,
            "hand_status": hand_status,
            "choice_logged": question_entry
        }), 200

    # ⚠️ No valid hand gesture detected
    return jsonify({
        "status": "no-gesture",
        "message": "⚠️ No valid hand gesture detected.",
        "student": student_name,
        "bracelet_id": bracelet_id,
        "choice_logged": question_entry
    }), 409
