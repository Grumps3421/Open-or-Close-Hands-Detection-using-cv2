import tkinter as tk
from model import AlphaBotModel
from view import AlphaBotView


class AlphaBotController:
    def __init__(self, root):
        self.model = AlphaBotModel()
        self.view = AlphaBotView(root, self)

    def get_students(self):
        return self.model.load_registered_students()

    def on_confirm_selection(self):
        selected_bracelets = self.view.selected_bracelets
        students = self.get_students()
        registered_dict = {bracelet_id: name for name, bracelet_id in students}

        if not selected_bracelets:
            self.view.show_message("No Selection", "Please select at least one student.", warning=True)
            return

        selected_students = [
            (registered_dict[b], b)
            for b in selected_bracelets if b in registered_dict
        ]

        inserted_count = self.model.add_present_students(selected_students)
        self.view.show_message(
            "Recorded Successfully",
            f"{inserted_count} student(s) are now eligible to play."
        )
        self.view.root.destroy()

