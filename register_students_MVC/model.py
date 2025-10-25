from pymongo import MongoClient
from datetime import datetime

class BraceletModelRegister:
    def __init__(self, db_url="mongodb://localhost:27017/", db_name="alphabot_db"):
        self.client = MongoClient(db_url)
        self.db = self.client[db_name]
        self.main_collection = self.db["bracelet_registrations"]

        # ✅ Fixed subjects and question sets
        self.fixed_questions = {
            "makabansa": {
                "Lesson 1: Philippine Flag": [
                    {"question": "1. What color is on the top of the flag during peace?", "answer": "Close"},
                    {"question": "2. What does the red color mean?", "answer": "Close"},
                    {"question": "3. What shape is in the middle of the flag?", "answer": "Open"},
                    {"question": "4. What do the three stars stand for?", "answer": "Open"},
                    {"question": "5. What does the white triangle represent?", "answer": "Open"}
                ]
            },
            "gmrc": {
                "Lesson 1: Good Manners": [
                    {"question": "1. Which one is the mother?", "answer": "Open"},
                    {"question": "2. Which one is the father?", "answer": "Close"},
                    {"question": "3. Which one is the child?", "answer": "Open"},
                    {"question": "4. Which picture shows a family?", "answer": "Close"},
                    {"question": "5. Which one is a sibling?", "answer": "Open"}
                ],
                "Lesson 2: Respecting Elders": [
                    {"question": "1. Is saying thank you to your parents respectful?", "answer": "Open"},
                    {"question": "2. Is keeping yourself clean and brushing your teeth a way of respecting yourself?", "answer": "Open"},
                    {"question": "3. Is shouting at your family members a respectful attitude?", "answer": "Close"},
                    {"question": "4. Is Helping your parents with simple chorse a respectful act?", "answer": "Open"},
                    {"question": "5. Is calling your brother or sister bad names respectful?", "answer": "Open"}
                ],
                "Lesson 3: I have Rights Too!":[
                    {"question": "1. Do children have the right to play?", "answer": "Close"},
                    {"question": "2. Do children have the right to go to school and learn?", "answer": "Open"},
                    {"question": "3. Is it okay for children to be hurt or bullied?", "answer": "Close"},
                    {"question": "4. Should children be given food, love, and care?", "answer": "Open"},
                    {"question": "5. Is it wrong for children to say how they feel?", "answer": "Close"}
                ]
            },
            "language": {
                "Lesson 1: Me, My Family, and My Home": [
                    {"question": "1. Which one is a mother?", "answer": "Open"},
                    {"question": "2. Which one is a chair?", "answer": "Close"},
                    {"question": "3. Which one is a car?", "answer": "Open"},
                    {"question": "4. Which one is a pencil?", "answer": "Open"},
                    {"question": "5. Which one is a plate?", "answer": "Close"}
                ],
                "Lesson 2: Lower Case": [
                    {"question": "1. Which one is the lowercase of letter A?", "answer": "Open"},
                    {"question": "2. Which one is the lowercase of letter B?", "answer": "Close"},
                    {"question": "3. Which one is the lowercase of letter R?", "answer": "Close"},
                    {"question": "4. Which one is the lowercase of letter Q?", "answer": "Open"},
                    {"question": "5. Which one is the lowercase of letter H?", "answer": "Close"}
                ],
                "Lesson 2: Upper Case": [
                    {"question": "1. Which one is the uppercase of letter e?", "answer": "Open"},
                    {"question": "2. Which one is the uppercase of letter i?", "answer": "Open"},
                    {"question": "3. Which one is the uppercase of letter n?", "answer": "Close"},
                    {"question": "4. Which one is the uppercase of letter l?", "answer": "Close"},
                    {"question": "5. Which one is the uppercase of letter z?", "answer": "Close"}
                ]
            },
            "mathematics": {
                "Lesson 1: Count and Match": [
                    {"question": "1. Count the blocks?", "answer": "Close"},
                    {"question": "2. Count the apples?", "answer": "Open"},
                    {"question": "3. Count the toy cars?", "answer": "Close"},
                    {"question": "4. Count the stars?", "answer": "Open"},
                    {"question": "5. Count the pencils?", "answer": "Open"}
                ]
            },
            "science": {
                "Lesson 1: What Can Our Body Do?": [
                    {"question": "1. What do we use to see?", "answer": "Open"},
                    {"question": "2. What do we use to walk?", "answer": "Close"},
                    {"question": "3. What do we use to hear?", "answer": "Open"},
                    {"question": "4. What do we use to eat?", "answer": "Open"},
                    {"question": "5. What do we use to pick things up?", "answer": "Open"}
                ],
                "Lesson 3: Let's Look touch, and Tell!": [
                    {"question": "1. Which one is the square?", "answer": "Open"},
                    {"question": "2. Which one is the circle?", "answer": "Close"},
                    {"question": "3. Which one is the rectangle?", "answer": "Open"},
                    {"question": "4. Which one is the star?", "answer": "Close"},
                    {"question": "5. Which one is the oblong?", "answer": "Open"}
                ]
            },
            
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
    # ✅ Register student
    # -----------------------------------------------------
    def register_student(self, student_name, bracelet_id):
        """Registers a student and creates/reset their question sets."""
        if not student_name or not bracelet_id:
            return False, "❌ Missing student name or bracelet ID."

        if not self.is_bracelet_taken(bracelet_id):
            self.main_collection.insert_one({
                "studentname": student_name,
                "bracelet_id": bracelet_id,
                "date_registered": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        student_collection = self.db[f"{student_name}_db"]
        student_collection.delete_many({})  # Reset if retaking

        questions = []
        for subject, lessons in self.fixed_questions.items():
            for lesson_title, qlist in lessons.items():
                for q in qlist:
                    questions.append({
                        "subject": subject,
                        "lesson": lesson_title,
                        "question": q["question"],
                        "correct_answer": q["answer"],
                        "student_answer": None,
                        "score": 0
                    })

        student_collection.insert_one({
            "student_name": student_name,
            "bracelet_id": bracelet_id,
            "questions": questions,
            "total_score": 0,
            "attempt_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return True, f"✅ Registered {student_name} (reset quiz if retake)."

    # -----------------------------------------------------
    # ✅ Update score per answer & per subject
    # -----------------------------------------------------
    def update_student_score(self, result_data):
        student_name = result_data.get("student name")
        hand_status = result_data.get("hand_status", "").capitalize()
        subject = result_data.get("subject", "").strip()

        if not student_name:
            return "❌ No student detected."
        if not subject:
            return "❌ No subject provided."

        student_collection = self.db[f"{student_name}_db"]
        student_doc = student_collection.find_one({"student_name": student_name})

        if not student_doc:
            return f"❌ No record found for {student_name}."

        # Only update unanswered question from the same subject
        for q in student_doc["questions"]:
            if q["subject"].lower() == subject.lower() and q["student_answer"] is None:
                q["student_answer"] = hand_status
                q["score"] = 1 if q["student_answer"] == q["correct_answer"] else 0
                break

        total_score = sum(q["score"] for q in student_doc["questions"])

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

        # Check if finished that subject only
        subject_done = all(
            q["student_answer"] is not None
            for q in student_doc["questions"]
            if q["subject"].lower() == subject.lower()
        )

        if subject_done:
            return f"🏁 {student_name} finished {subject}! Current total: {total_score}"
        else:
            return f"✅ Updated answer for {student_name} ({subject}). Score: {total_score}"

    # -----------------------------------------------------
    # ✅ Utilities
    # -----------------------------------------------------
    def get_registered_students(self):
        return list(self.main_collection.find({}, {"studentname": 1, "bracelet_id": 1, "_id": 0}))

    def delete_student(self, bracelet_id):
        result = self.main_collection.delete_one({"bracelet_id": bracelet_id})
        if result.deleted_count > 0:
            for name in self.db.list_collection_names():
                if name.endswith("_db"):
                    self.db.drop_collection(name)
            return True
        return False

    def delete_all_students(self):
        self.main_collection.delete_many({})
        for name in self.db.list_collection_names():
            if name.endswith("_db"):
                self.db.drop_collection(name)
        return True
