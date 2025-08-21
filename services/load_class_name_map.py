from lib.db_config import registered_student_collection

def load_class_name_map():
    class_name_map = {}
    students = registered_student_collection.find({})
    for student in students:
        bracelet_id = student["bracelet_id"].strip().lower().replace(" ", "")
        student_name = student["student_name"]
        color = student.get("color", "Unknown")
        class_name_map[bracelet_id] = f"{student_name} | {color}"
    return class_name_map