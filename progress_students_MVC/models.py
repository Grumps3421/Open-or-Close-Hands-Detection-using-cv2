from pymongo import MongoClient

class AlphaBotModel:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="alphabot_db"):
        self.uri = uri
        self.db_name = db_name

    def get_db(self):
        client = MongoClient(self.uri)
        return client, client[self.db_name]

    def load_registered_students(self):
        client, db = self.get_db()
        collection = db["bracelet_registrations"]
        registered = {}

        for doc in collection.find({}, {"bracelet_id": 1, "studentname": 1, "_id": 0}):
            bracelet_id = doc.get("bracelet_id")
            if not bracelet_id:
                continue
            registered[bracelet_id] = doc.get("studentname", "Unregistered")

        client.close()
        return registered

    def get_student_progress(self, bracelet_id):
        """Return student's categorized questions by subject and lesson."""
        client, db = self.get_db()
        matched_collection = None
        progress_data = []

        for coll_name in db.list_collection_names():
            collection = db[coll_name]
            match = collection.find_one({"bracelet_id": bracelet_id, "questions": {"$size": 50}})
            if match:
                matched_collection = coll_name
                progress_data = list(collection.find({"bracelet_id": bracelet_id}, {"_id": 0}))
                break

        client.close()

        if not matched_collection:
            return None

        categorized = {}
        for record in progress_data:
            for q in record.get("questions", []):
                subject = q.get("subject", "Uncategorized")
                lesson = q.get("lesson", "Lesson 1")
                categorized.setdefault(subject, {}).setdefault(lesson, []).append(q)

        return categorized

    def get_subjects(self):
        """Return all subjects across collections."""
        client, db = self.get_db()
        subjects = set()

        for coll_name in db.list_collection_names():
            collection = db[coll_name]
            for record in collection.find({"questions": {"$exists": True}}):
                for q in record.get("questions", []):
                    subjects.add(q.get("subject", "Uncategorized"))

        client.close()
        return sorted(subjects)

    def get_leaderboard_data(self, registered, subject):
        """Compute leaderboard scores per subject."""
        client, db = self.get_db()
        leaderboard_data = []

        for bracelet_id, studentname in registered.items():
            total_score = 0
            total_questions = 0
            has_collection = False

            for coll_name in db.list_collection_names():
                collection = db[coll_name]
                record = collection.find_one({"bracelet_id": bracelet_id})
                if record:
                    has_collection = True
                    for q in record.get("questions", []):
                        if q.get("subject") == subject:
                            total_questions += 1
                            student_answer = str(q.get("student_answer", "")).strip()
                            correct_answer = str(q.get("correct_answer", "")).strip()
                            if student_answer and student_answer == correct_answer:
                                total_score += 1

            if has_collection:
                score = (total_score / total_questions * 100) if total_questions > 0 else 0
                leaderboard_data.append({
                    "studentname": studentname,
                    "score": round(score, 1)
                })

        client.close()
        leaderboard_data.sort(key=lambda x: x["score"], reverse=True)
        return leaderboard_data
