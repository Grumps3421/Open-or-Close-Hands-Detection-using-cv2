from flask import Blueprint, request, jsonify
from checking_answer import check_answer_result
from lib.db_config import students_collection
from datetime import datetime, timezone

open_bp = Blueprint("open_bp", __name__)

@open_bp.route("/open", methods=["POST"])
def hand_status_reverse():
    data = request.json or {}
    choice = data.get("choice")

    if not choice:
        return jsonify({
            "status": "error",
            "message": "❌ Missing required field: choice"
        }), 400

    # Run webcam hand detection
    result = check_answer_result()
    print(f"🖐️ Hand detection result: {result}")

    student_name = result.get("student name")
    bracelet_id = result.get("bracelet_id")
    detect_result = result.get("detect")       # "correct" / "wrong" / "no-gesture"
    hand_status = result.get("hand_status")    # "Open" / "Close"

    # Build question entry (logging choice instead)
    question_entry = {
        "choice": choice,
        "answer": hand_status if detect_result in ["correct", "wrong"] else None
    }

    # Check if student record already exists
    student_doc = students_collection.find_one({
        "student name": student_name,
    })

    if not student_doc:
        # Create new document for student
        new_doc = {
            "student name": student_name,
            "bracelet_id": bracelet_id,
            "questions": [question_entry],
            "created_at": datetime.now(timezone.utc),
            "last_updated": datetime.now(timezone.utc)
        }
        students_collection.insert_one(new_doc)
    else:
        # Update existing document
        students_collection.update_one(
            {"student name": student_name},
            {
                "$set": {"last_updated": datetime.now(timezone.utc)},
                "$push": {"questions": question_entry}
            }
        )

    # Response handling
    if detect_result in ["correct", "wrong"]:
        return jsonify({
            "status": "success",
            "message": f"✅ Detected: {detect_result}",
            "student": student_name,
            "bracelet_id": bracelet_id,
            "choice_logged": question_entry
        }), 200

    return jsonify({
        "status": "no-gesture",
        "message": "⚠️ No valid hand gesture detected.",
        "student": student_name,
        "bracelet_id": bracelet_id,
        "choice_logged": question_entry
    }), 409
