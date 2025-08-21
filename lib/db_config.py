from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "alphabot_db"
MONGO_COLLECTION = "registered_students"
MONGO_COLLECTION_2 =  "makabansa"

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
registered_student_collection = db[MONGO_COLLECTION]
students_collection = db[MONGO_COLLECTION_2]
