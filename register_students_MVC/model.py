from pymongo import MongoClient
from datetime import datetime

class BraceletModelRegister:
    def __init__(self, db_url="mongodb://localhost:27017/", db_name="alphabot_db"):
        self.client = MongoClient(db_url)
        self.db = self.client[db_name]
        self.main_collection = self.db["bracelet_registrations"]

        # Fixed data
        self.fixed_subjects = ["Makabansa"]
        self.fixed_questions = {
            "Makabansa": {
                "Lesson 1: Philippine Flag": [
                    {"question": "1. What color is on the top of the flag during peace?", "answer": "Close"},
                    {"question": "2. What does the red color mean?", "answer": "Close"},
                    {"question": "3. What shape is in the middle of the flag?", "answer": "Open"},
                    {"question": "4. What do the three stars stand for?", "answer": "Open"},
                    {"question": "5. What does the white triangle represent?", "answer": "Open"}
                ]
            }
        }

        self.bracelet_colors = {
            "Student1": "#FF0000", "Student2": "#808080", "Student3": "#75FF33",
            "Student4": "#FFA500", "Student5": "#D633FF", "Student6": "#00BFFF",
            "Student7": "#FFFFFF", "Student8": "#40E0D0", "Student9": "#FFB6C1",
            "Student10": "#87CEEB", "Student11": "#FF13F0", "Student12": "#FC8EAC",
        }

    # -----------------------------------------------------
    # ✅ Helper functions
    # -----------------------------------------------------
    def get_all_bracelets(self):
        return self.bracelet_colors

    def is_bracelet_taken(self, bracelet_id):
        return self.main_collection.find_one({"bracelet_id": bracelet_id}) is not None

    def get_taken_bracelets(self):
        return [doc["bracelet_id"] for doc in self.main_collection.find({}, {"bracelet_id": 1, "_id": 0})]

    # -----------------------------------------------------
    # ✅ Register student (creates or resets student DB)
    # -----------------------------------------------------
    def register_student(self, student_name, bracelet_id):
        """Registers a student and ensures their personal collection exists."""
        if not student_name or not bracelet_id:
            return False, "❌ Missing student name or bracelet ID."

        # Insert to main registration list if not already registered
        if not self.is_bracelet_taken(bracelet_id):
            self.main_collection.insert_one({
                "studentname": student_name,
                "bracelet_id": bracelet_id,
                "date_registered": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        # Create or reset student DB collection
        student_collection = self.db[f"{student_name}_db"]

        # Remove old data (if retaking)
        student_collection.delete_many({})

        # Prepare default question set
        questions = []
        for subject, lessons in self.fixed_questions.items():
            for lesson_title, qlist in lessons.items():
                for q in qlist:
                    questions.append({
                        "question": q["question"],
                        "correct_answer": q["answer"],
                        "student_answer": None,
                        "score": 0
                    })

        # Insert fresh quiz record
        student_collection.insert_one({
            "student_name": student_name,
            "bracelet_id": bracelet_id,
            "questions": questions,
            "total_score": 0,
            "attempt_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return True, f"✅ Registered {student_name} (reset quiz if retake)."

    # -----------------------------------------------------
    # ✅ Update score per answer and auto-update total
    # -----------------------------------------------------
    def update_student_score(self, result_data):
        student_name = result_data.get("student name")
        hand_status = result_data.get("hand_status", "").capitalize()

        if not student_name:
            return "❌ No student detected."

        student_collection = self.db[f"{student_name}_db"]
        student_doc = student_collection.find_one({"student_name": student_name})

        if not student_doc:
            return f"❌ No record found for {student_name}."

        # Find next unanswered question
        for q in student_doc["questions"]:
            if q["student_answer"] is None:
                q["student_answer"] = hand_status
                q["score"] = 1 if q["student_answer"] == q["correct_answer"] else 0
                break

        # Recalculate total score
        total_score = sum(q["score"] for q in student_doc["questions"])

        # Update DB immediately after each answer
        student_collection.update_one(
            {"student_name": student_name},
            {
                "$set": {
                    "questions": student_doc["questions"],
                    "total_score": total_score,
                    "attempt_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        )

        # Check if finished all questions
        if all(q["student_answer"] is not None for q in student_doc["questions"]):
            return f"🏁 {student_name} finished quiz! Final score: {total_score}/5 (updated record)"
        else:
            return f"✅ Updated answer for {student_name}. Current score: {total_score}"

    # -----------------------------------------------------
    # ✅ Utility: show registered students
    # -----------------------------------------------------
    def get_registered_students(self):
        return list(self.main_collection.find({}, {"studentname": 1, "bracelet_id": 1, "_id": 0}))

    # -----------------------------------------------------
    # ✅ Delete single or all students
    # -----------------------------------------------------
    def delete_student(self, bracelet_id):
        result = self.main_collection.delete_one({"bracelet_id": bracelet_id})
        if result.deleted_count > 0:
            # Drop student's personal DB
            for name in self.db.list_collection_names():
                if name.endswith("_db"):
                    self.db.drop_collection(name)
            return True
        return False

    def delete_all_students(self):
        self.main_collection.delete_many({})
        # Drop all per-student collections
        for name in self.db.list_collection_names():
            if name.endswith("_db"):
                self.db.drop_collection(name)
        return True
