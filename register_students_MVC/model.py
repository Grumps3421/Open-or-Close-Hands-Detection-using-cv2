from pymongo import MongoClient
from datetime import datetime

class BraceletModelRegister:
    def __init__(self, db_url="mongodb://localhost:27017/", db_name="alphabot_db"):
        self.client = MongoClient(db_url)
        self.db = self.client[db_name]
        self.collection = self.db["bracelet_registrations"]
        self.fixed_subjects = ["Makabansa"]

        self.fixed_questions = {
            "Makabansa": {
                "Lesson 1: Philippine Flag": [
                    {"question": "1. What color is on the top of the flag during peace?", "answer": "closed"},
                    {"question": "2. What does the red color mean?", "answer": "closed"},
                    {"question": "3. What shape is in the middle of the flag?", "answer": "open"},
                    {"question": "4. What do the three stars stand for?", "answer": "open"},
                    {"question": "5. What does the white triangle represent?", "answer": "open"}
                ]
            }
        }

        self.bracelet_colors = {
            "Student1": "#FF0000", "Student2": "#808080", "Student3": "#75FF33",
            "Student4": "#FFA500", "Student5": "#D633FF", "Student6": "#00BFFF",
            "Student7": "#FFFFFF", "Student8": "#40E0D0", "Student9": "#FFB6C1",
            "Student10": "#87CEEB", "Student11": "#FF13F0", "Student12": "#FC8EAC",
        }

    def get_all_bracelets(self):
        return self.bracelet_colors

    def is_bracelet_taken(self, bracelet_id):
        return self.collection.find_one({"bracelet_id": bracelet_id}) is not None

    def get_taken_bracelets(self):
        return [doc["bracelet_id"] for doc in self.collection.find({}, {"bracelet_id": 1, "_id": 0})]

    def register_student(self, student_name, bracelet_id):
        if self.is_bracelet_taken(bracelet_id):
            return False, f"{bracelet_id} is already registered"

        total_subjects = []
        for subject, lessons in self.fixed_questions.items():
            subject_lessons = []
            for lesson_title, questions in lessons.items():
                subject_lessons.append({
                    "lesson_title": lesson_title,
                    "questions": questions,
                    "score": None,
                    "date": None,
                    "status": "Not taken",
                })
            total_subjects.append({
                "subject_name": subject,
                "lessons": subject_lessons
            })

        self.collection.insert_one({
            "studentname": student_name,
            "bracelet_id": bracelet_id,
            "total_subjects": total_subjects,
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        })

        return True, f"Registered {student_name} to {bracelet_id}"

    def get_registered_students(self):
        return list(self.collection.find({}, {"studentname": 1, "bracelet_id": 1, "_id": 0}))

    def delete_student(self, bracelet_id):
        result = self.collection.delete_one({"bracelet_id": bracelet_id})
        return result.deleted_count > 0

    def delete_all_students(self):
        result = self.collection.delete_many({})
        return result.deleted_count 
