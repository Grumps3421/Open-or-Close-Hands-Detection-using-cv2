from flask import Blueprint, request, jsonify
from checking_answer import check_answer
from lib.db_config import students_collection
from datetime import datetime, timezone

close_bp = Blueprint("close_bp", __name__)

@close_bp.route("/close", methods=["POST"])
def detect_hand_status():
    try:
        # 📥 Get request data
        data = request.get_json() or {}
        print("📥 Received request data:", data)

        choice = data.get("choice")
        if not choice:
            return jsonify({
                "status": "error",
                "message": "❌ Missing required field: choice"
            }), 400

        # 🧠 Run webcam hand detection
        result = check_answer()
        print("🧩 check_answer() returned:", result, type(result))

        # 🛡️ Validate result
        if not isinstance(result, dict):
            return jsonify({
                "status": "error",
                "message": "❌ Invalid result from check_answer()"
            }), 500

        # 🔍 Extract data safely
        student_name = result.get("student name", "Unknown Student")
        bracelet_id = result.get("bracelet_id", "Unknown ID")
        hand_status = result.get("hand_status", "N/A")
        detect_result = result.get("detect", "N/A")

        print(f"🖐️ Hand detection result: {hand_status} ({detect_result})")
        print(f"🎓 Student: {student_name}, 🆔 Bracelet: {bracelet_id}")

        # 🧾 Prepare question entry
        question_entry = {
            "choice": choice,
            "answer": hand_status if detect_result in ["correct", "wrong"] else None
        }

        # 🧠 Check if student exists in DB
        student_doc = students_collection.find_one({"student name": student_name})
        print("📚 Found existing student:", bool(student_doc))

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
            print("✅ Inserted new student record.")
        else:
            # 🔁 Update existing record
            students_collection.update_one(
                {"student name": student_name},
                {
                    "$set": {"last_updated": datetime.now(timezone.utc)},
                    "$push": {"questions": question_entry}
                }
            )
            print("🔄 Updated existing student record.")

        # 🟢 Success response
        return jsonify({
            "status": "success",
            "message": f"✅ Logged choice for {student_name}",
            "student": student_name,
            "bracelet_id": bracelet_id,
            "choice_logged": question_entry
        }), 200

    except Exception as e:
        # 💥 Error handler — prevent 500 crash without explanation
        print("💥 ERROR IN /close ROUTE:", str(e))
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }), 500
