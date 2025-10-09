from pymongo import MongoClient

class AlphaBotModel:
    def __init__(self):
        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client["alphabot_db"]
        self.collection = db["bracelet_registrations"]

    # ---------------- Student Data ----------------
    def get_student(self, bracelet_id):
        """Fetch a single student's data by bracelet ID"""
        return self.collection.find_one({"bracelet_id": bracelet_id})

    def get_all_students(self):
        """Fetch all students"""
        return self.collection.find()

    # ---------------- Subject/Attempts Data ----------------
    def get_student_subjects(self, bracelet_id):
        """Get all subjects for a student"""
        student = self.get_student(bracelet_id)
        return student.get("total_subjects", []) if student else []

    def get_lesson_attempts(self, lesson):
        """Return attempts for a lesson"""
        return lesson.get("attempts", [])

    def get_latest_attempt(self, lesson):
        """Get the latest attempt for a lesson"""
        attempts = self.get_lesson_attempts(lesson)
        return attempts[-1] if attempts else None
