from flask import Blueprint  , request, jsonify
from checking_answer import check_answer_result
from lib.db_config import students_collection
from datetime import datetime, timezone

open_bp = Blueprint('open_bp' , __name__)

@open_bp.route("/open" , methods=["POST" , "GET"])
def hand_status_reverse():
    data = request.json
    choice = data.get("choice")
    question = data.get("question")
    subject = data.get("subject")
    lesson = data.get("lesson")

    print("📩 Received choice from Next.js:", choice)
    print(question)

    # Check if "choice" was provided
    if not choice:
        return jsonify({
            "status": "error",
            "message": "❌ No choice provided"
        }), 400

    # Run webcam hand detection
    result = check_answer_result()
    print(f"🖐️ Hand detection result: {result}")
    print(f"Question from frontend: {question}")
    print(f"subject from frontend: {subject}")
    print(f"lesson from frontend: {lesson}")

    log_entry = {
        "student name": result["student name"],
        "bracelet_id": result["bracelet_id"],

        "choice": choice,
        "question": question,
        "subject": subject,
        "lesson": lesson,
        "answer": result["detect"],
        "hand Status" : result["hand_status"],
        "timestamp": datetime.now(timezone.utc)
    }
    students_collection.insert_one(log_entry)

    # Return success if gesture is valid
    if result in ["correct", "wrong"]:
        return jsonify({
            "status": "success",
            "message": f"✅ Detected: {result}",
            "detected": result,
            "choice": choice ,
            "question": question,
            "subject": subject,
            "lesson": lesson
        }), 200

    # Otherwise return a "Conflict" (409) for no valid hand gesture
    return jsonify({
        "status": "no-gesture",
        "message": "⚠️ No valid hand gesture detected.",
        "detected": result,
        "choice": choice,
        "question": question,
        "subject": subject,
        "lesson": lesson
    }), 409