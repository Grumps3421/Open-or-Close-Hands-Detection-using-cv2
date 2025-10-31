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
                    {"question": "1. Which one is the mother?", "answer": "Close"},
                    {"question": "2. Which one is the father?", "answer": "Close"},
                    {"question": "3. Which one is the child?", "answer": "Open"},
                    {"question": "4. Which picture shows a family?", "answer": "Close"},
                    {"question": "5. Which one is a sibling?", "answer": "Open"}
                ],
                "Lesson 2: Respecting Elders": [
                    {"question": "1. Is saying thank you to your parents respectful?", "answer": "Close"},
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
    # ✅ NEW: Update score for ALL students (winner gets 1, others get 0)
    # -----------------------------------------------------
    def update_student_score(self, result_data):
        """
        Update scores for ALL registered students:
        - The student who answered correctly gets score = 1
        - All other students get score = 0 for that question
        """
        # ✅ Get data from YOLO detection
        bracelet_id = result_data.get("bracelet_id", "").strip()
        student_name = result_data.get("student name", "").strip()
        hand_status = result_data.get("hand_status", "").capitalize()
        subject = result_data.get("subject", "").strip()

        print(f"\n🔍 DEBUG - Received data:")
        print(f"   Student Name: {student_name}")
        print(f"   Bracelet ID: {bracelet_id}")
        print(f"   Hand Status: {hand_status}")
        print(f"   Subject: {subject}")

        if not student_name:
            return "❌ No student detected."
        if not bracelet_id:
            return "❌ No bracelet ID found."
        if not subject:
            return "❌ No subject provided."

        # ✅ Verify the student is registered with this bracelet
        registration = self.main_collection.find_one({"bracelet_id": bracelet_id})
        
        if not registration:
            print(f"❌ Bracelet '{bracelet_id}' not found in bracelet_registrations")
            return f"❌ Bracelet {bracelet_id} is not registered."
        
        registered_student_name = registration["studentname"]
        
        # ✅ Verify the detected student matches the registered bracelet
        if student_name.lower() != registered_student_name.lower():
            print(f"⚠️ WARNING: Detected '{student_name}' but bracelet {bracelet_id} is registered to '{registered_student_name}'")
            return f"❌ Mismatch: Detected {student_name} but bracelet belongs to {registered_student_name}"
        
        print(f"✅ Verified: {student_name} with bracelet {bracelet_id}")

        # ✅ Get ALL registered students
        all_registrations = list(self.main_collection.find({}))
        if not all_registrations:
            return "❌ No students registered in the system."

        print(f"\n📋 Found {len(all_registrations)} registered students")

        # ✅ Find the question index to update (first unanswered question in subject)
        winner_collection = self.db[f"{student_name}_db"]
        winner_doc = winner_collection.find_one({"student_name": student_name})

        if not winner_doc:
            print(f"❌ Collection {student_name}_db not found or empty")
            return f"❌ No record found for {student_name}."

        # Find the question to update
        question_index = None
        question_text = None
        correct_answer = None

        for i, q in enumerate(winner_doc["questions"]):
            if q["subject"].lower() == subject.lower() and q["student_answer"] is None:
                question_index = i
                question_text = q["question"]
                correct_answer = q["correct_answer"]
                print(f"📝 Target Question #{i+1}: {question_text[:50]}...")
                print(f"   Correct Answer: {correct_answer}")
                break

        if question_index is None:
            print(f"⚠️ No unanswered questions found for subject: {subject}")
            return f"⚠️ All questions answered for {subject} or no questions found"

        # ✅ Check if the winner answered correctly
        is_correct = hand_status == correct_answer
        winner_score = 1 if is_correct else 0

        print(f"\n🎯 Winner Analysis:")
        print(f"   Student: {student_name}")
        print(f"   Answer: {hand_status}")
        print(f"   Correct: {is_correct}")
        print(f"   Score: {winner_score}")

        # ✅ UPDATE ALL STUDENTS
        print(f"\n🔄 Updating all {len(all_registrations)} students...")
        
        for reg in all_registrations:
            current_student = reg["studentname"]
            current_collection = self.db[f"{current_student}_db"]
            current_doc = current_collection.find_one({"student_name": current_student})

            if not current_doc:
                print(f"⚠️ Skipping {current_student} - no data found")
                continue

            # Check if this question exists for this student
            if question_index >= len(current_doc["questions"]):
                print(f"⚠️ Skipping {current_student} - question index out of range")
                continue

            # Get the question at the same index
            question = current_doc["questions"][question_index]

            # Skip if already answered
            if question["student_answer"] is not None:
                print(f"⏭️ Skipping {current_student} - already answered this question")
                continue

            # Determine score: only the winner who answered correctly gets 1, everyone else gets 0
            if current_student == student_name:
                # This is the student who answered
                question["student_answer"] = hand_status
                question["score"] = winner_score
                print(f"✅ {current_student} (WINNER): Answer={hand_status}, Score={winner_score}")
            else:
                # This is another student who didn't answer
                question["student_answer"] = "No answer"
                question["score"] = 0
                print(f"❌ {current_student}: No answer, Score=0")

            # Calculate new total score
            new_total_score = sum(q["score"] for q in current_doc["questions"])

            # Update the database
            current_collection.update_one(
                {"student_name": current_student},
                {
                    "$set": {
                        "questions": current_doc["questions"],
                        "total_score": new_total_score,
                        "attempt_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                }
            )

            print(f"💾 {current_student} - New Total Score: {new_total_score}")

        # ✅ Check progress for the subject
        subject_questions = [q for q in winner_doc["questions"] if q["subject"].lower() == subject.lower()]
        answered_count = sum(1 for q in subject_questions if q["student_answer"] is not None) + 1  # +1 for current answer
        total_count = len(subject_questions)
        
        subject_done = answered_count == total_count

        print(f"\n✅ Update completed for all students!")
        
        if subject_done:
            return f"🏁 Question answered! {student_name} scored {winner_score} point. Subject {subject} progress: {answered_count}/{total_count} completed."
        else:
            return f"✅ Question answered! {student_name} scored {winner_score} point. Subject {subject} progress: {answered_count}/{total_count}."

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
    
    # -----------------------------------------------------
    # ✅ DEBUGGING HELPER
    # -----------------------------------------------------
    def debug_show_all_students(self):
        """Show all registered students with their bracelet IDs"""
        print("\n" + "="*60)
        print("📊 REGISTERED STUDENTS IN DATABASE")
        print("="*60)
        
        registrations = list(self.main_collection.find({}))
        if not registrations:
            print("❌ No students registered")
            return
        
        for reg in registrations:
            student_name = reg.get("studentname")
            bracelet_id = reg.get("bracelet_id")
            date_reg = reg.get("date_registered")
            
            print(f"\n👤 Student: {student_name}")
            print(f"   🔗 Bracelet: {bracelet_id}")
            print(f"   📅 Registered: {date_reg}")
            
            # Check if their collection exists
            collection_name = f"{student_name}_db"
            if collection_name in self.db.list_collection_names():
                student_doc = self.db[collection_name].find_one({"student_name": student_name})
                if student_doc:
                    total_q = len(student_doc.get("questions", []))
                    answered = sum(1 for q in student_doc["questions"] if q["student_answer"] is not None)
                    score = student_doc.get("total_score", 0)
                    print(f"   ✅ Progress: {answered}/{total_q} questions answered")
                    print(f"   🏆 Score: {score}")
                else:
                    print(f"   ⚠️ Collection exists but no data found")
            else:
                print(f"   ❌ Collection {collection_name} not found")
        
        print("\n" + "="*60 + "\n")