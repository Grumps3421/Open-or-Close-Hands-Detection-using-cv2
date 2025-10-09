from flask import Blueprint, request, jsonify
from checking_answer import check_answer_result
from lib.db_config import students_collection
from datetime import datetime, timezone

open_bp = Blueprint("open_bp", __name__)

@open_bp.route("/open", methods=["POST"])
def hand_status_reverse():
    try:
        # 📥 Get JSON data from request
        data = request.get_json() or {}
        print("📥 Received request data:", data)

        choice = data.get("choice")
        if not choice:
            return jsonify({
                "status": "error",
                "message": "❌ Missing required field: choice"
            }), 400

        # 🧠 Run webcam hand detection
        result = check_answer_result()
        print("🧩 check_answer_result() returned:", result, type(result))

        # 🛡️ Validate result structure
        if not isinstance(result, dict):
            return jsonify({
                "status": "error",
                "message": "❌ Invalid result from check_answer_result()"
            }), 500

        # 🔍 Extract fields safely (with defaults)
        student_name = result.get("student name", "Unknown Student")
        bracelet_id = result.get("bracelet_id", "Unknown ID")
        detect_result = result.get("detect", "N/A")       # "correct" / "wrong" / "no-gesture"
        hand_status = result.get("hand_status", "N/A")    # "Open" / "Close"

        print(f"🖐️ Hand detection result: {hand_status} ({detect_result})")
        print(f"🎓 Student: {student_name}, 🆔 Bracelet: {bracelet_id}")

        # 🧾 Prepare question entry
        question_entry = {
            "choice": choice,
            "answer": hand_status if detect_result in ["correct", "wrong"] else None
        }

        # 🧠 Check if student record exists in DB
        student_doc = students_collection.find_one({"student name": student_name})
        print("📚 Found existing student:", bool(student_doc))

        if not student_doc:
            # 🆕 Create new document
            new_doc = {
                "student name": student_name,
                "bracelet_id": bracelet_id,
                "questions": [question_entry],
                "created_at": datetime.now(timezone.utc),
                "last_updated": datetime.now(timezone.utc)
            }
            students_collection.insert_one(new_doc)
            print("✅ Inserted new student record.")
        else:
            # 🔁 Update existing document
            students_collection.update_one(
                {"student name": student_name},
                {
                    "$set": {"last_updated": datetime.now(timezone.utc)},
                    "$push": {"questions": question_entry}
                }
            )
            print("🔄 Updated existing student record.")

        # 🟢 Response handling
        if detect_result in ["correct", "wrong"]:
            return jsonify({
                "status": "success",
                "message": f"✅ Detected: {detect_result}",
                "student": student_name,
                "bracelet_id": bracelet_id,
                "choice_logged": question_entry
            }), 200

        # ⚠️ If no valid gesture detected
        return jsonify({
            "status": "no-gesture",
            "message": "⚠️ No valid hand gesture detected.",
            "student": student_name,
            "bracelet_id": bracelet_id,
            "choice_logged": question_entry
        }), 409

    except Exception as e:
        # 💥 Catch unexpected errors
        print("💥 ERROR IN /open ROUTE:", str(e))
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }), 500
