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
    # ✅ Register student (creates a separate DB collection)
    # -----------------------------------------------------
    def register_student(self, student_name, bracelet_id):
        if self.is_bracelet_taken(bracelet_id):
            return False, f"{bracelet_id} is already registered"

        # Insert to main registration list
        self.main_collection.insert_one({
            "studentname": student_name,
            "bracelet_id": bracelet_id,
            "date_registered": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # Create personal DB collection for student (e.g. "Student1_db")
        student_collection = self.db[f"{student_name}_db"]

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

        # Insert student document
        student_collection.insert_one({
            "student_name": student_name,
            "bracelet_id": bracelet_id,
            "questions": questions,
            "total_score": 0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return True, f"✅ Registered {student_name} and created {student_name}_db"

    # -----------------------------------------------------
    # ✅ Update score when YOLO result comes in
    # -----------------------------------------------------
    def update_student_score(self, result_data):
        student_name = result_data.get("student name")
        hand_status = result_data.get("hand_status", "").lower()
        detect_result = result_data.get("detect")  # "correct" or "wrong"

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
                q["score"] = 1 if detect_result == "correct" else 0
                break

        # Recalculate total score
        total_score = sum(q["score"] for q in student_doc["questions"])

        # Update in MongoDB
        student_collection.update_one(
            {"student_name": student_name},
            {
                "$set": {
                    "questions": student_doc["questions"],
                    "total_score": total_score,
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        )

        # If finished answering all
        if all(q["student_answer"] is not None for q in student_doc["questions"]):
            return f"🏁 {student_name} finished quiz! Total score: {total_score}/5"
        else:
            return f"✅ Recorded {detect_result} for {student_name}. Current score: {total_score}"

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
            # Drop student's collection too
            student_name = bracelet_id  # same naming
            self.db.drop_collection(f"{student_name}_db")
            return True
        return False

    def delete_all_students(self):
        self.main_collection.delete_many({})
        # Drop all per-student collections
        for student in self.bracelet_colors.keys():
            self.db.drop_collection(f"{student}_db")
        return True