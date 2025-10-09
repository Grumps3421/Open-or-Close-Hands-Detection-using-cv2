from model import BraceletModelRegister

class BraceletController:
    def __init__(self, root):
        self.root = root
        self.model = BraceletModelRegister()  # create model instance

    # --------- Bracelet Data Methods ---------
    def get_bracelet_colors(self):
        return self.model.get_all_bracelets()

    def get_taken_bracelets(self):
        return self.model.get_taken_bracelets()

    # --------- Student Actions ---------
    def register_student(self, student_name, bracelet_id):
        return self.model.register_student(student_name, bracelet_id)

    def unregister_student(self, bracelet_id):
        return self.model.unregister_student(bracelet_id)

    def fetch_registered_students(self):
        return self.model.get_registered_students()

    def remove_student(self, bracelet_id):
        success = self.model.delete_student(bracelet_id)
        if success:
            return True, "Student unregistered successfully!"
        return False, "Failed to unregister student."

    def remove_all_students(self):
        count = self.model.delete_all_students()
        if count > 0:
            return True, f"Deleted {count} students successfully!"
        return False, "No students to delete."
