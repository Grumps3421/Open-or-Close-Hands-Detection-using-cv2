from pymongo import MongoClient
from datetime import datetime


class AlphaBotModel:
    def __init__(self, uri="mongodb://localhost:27017", db_name="alphabot_db"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.registrations = self.db["bracelet_registrations"]
        self.present = self.db["Present_db"]

    def load_registered_students(self):
        data = list(self.registrations.find())
        return [(doc["studentname"], doc["bracelet_id"]) for doc in data]

    def add_present_students(self, students):
        for name, bracelet_id in students:
            entry = {
                "studentname": name,
                "bracelet_id": bracelet_id,
                "datetime_played": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
            }
            self.present.insert_one(entry)
        return len(students)
