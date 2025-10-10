from flask import Blueprint, request, jsonify
from checking_answer import check_answer
from lib.db_config import students_collection
from datetime import datetime, timezone

close_bp = Blueprint("close_bp", __name__)

@close_bp.route("/close", methods=["POST"])
def detect_hand_status():
    data = request.json or {}
    choice = data.get("choice")

    if not choice:
        return jsonify({
            "status": "error",
            "message": "❌ Missing required field: choice"
        }), 400

    # Run webcam hand detection
    result = check_answer()
    print(f"🖐️ Hand detection result: {result}")

    student_name = result.get("student name")
    bracelet_id = result.get("bracelet_id")
    hand_status = result.get("hand_status")
    detect_result = result.get("detect")

    # Build question entry (just logging the choice)
    question_entry = {
        "choice": choice,
        "answer": hand_status if detect_result in ["correct", "wrong"] else None
    }

    # Check if student record already exists
    student_doc = students_collection.find_one({
        "student name": student_name,
    })

    if not student_doc:
        # If no record yet → create one with this first question
        new_doc = {
            "student name": student_name,
            "bracelet_id": bracelet_id,
            "questions": [question_entry],
            "created_at": datetime.now(timezone.utc),
            "last_updated": datetime.now(timezone.utc)
        }
        students_collection.insert_one(new_doc)
    else:
        # If record exists → just update + push new question
        students_collection.update_one(
            {"student name": student_name},
            {
                "$set": {"last_updated": datetime.now(timezone.utc)},
                "$push": {"questions": question_entry}
            }
        )

    return jsonify({
        "status": "success",
        "message": f"✅ Logged choice for {student_name}",
        "student": student_name,
        "bracelet_id": bracelet_id,
        "choice_logged": question_entry
    }), 200
