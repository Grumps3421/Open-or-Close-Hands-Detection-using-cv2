import tkinter as tk
from tkinter import messagebox


class AlphaBotView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("🎓 AlphaBot - Select Players")
        self.root.attributes('-fullscreen', True)
        self.root.attributes("-topmost", True)
        self.root.after(1000, lambda: self.root.attributes("-topmost", False))
        self.root.config(bg="#FFF8DC")

        self.selected_bracelets = []

        self.create_title()
        self.create_student_buttons()
        self.create_action_buttons()

    def create_title(self):
        tk.Label(
            self.root,
            text="Select Players",
            font=("Comic Sans MS", 20, "bold"),
            bg="#FFF8DC",
            fg="#483D8B"
        ).pack(pady=10)

    def create_student_buttons(self):
        self.frame = tk.Frame(self.root, bg="#FFF8DC")
        self.frame.pack(pady=20)

        students = self.controller.get_students()
        self.registered_dict = {bracelet_id: name for name, bracelet_id in students}

        BUTTON_COLORS = [
            "#FF4D4D", "#808080", "#7CFC00", "#FFA500",
            "#DA70D6", "#00BFFF", "#FFFFFF", "#40E0D0",
            "#FFB6C1", "#FF69B4", "#FF00FF", "#FFB6C1"
        ]

        for i in range(12):
            color = BUTTON_COLORS[i % len(BUTTON_COLORS)]
            bracelet_id = f"Student{i+1}"

            if bracelet_id in self.registered_dict:
                name = self.registered_dict[bracelet_id]
                btn_text = f"{name}\n({bracelet_id})"
                state = "normal"
                bg_color = color
            else:
                btn_text = f"{bracelet_id}\nEmpty Slot"
                state = "disabled"
                bg_color = "#D3D3D3"

            btn = tk.Button(
                self.frame,
                text=btn_text,
                bg=bg_color,
                fg="black",
                font=("Comic Sans MS", 12, "bold"),
                width=18,
                height=2,
                relief="raised",
                state=state
            )
            btn.original_color = color

            if state == "normal":
                btn.config(command=lambda b=bracelet_id, bt=btn: self.toggle_student(bt, b))

            btn.grid(row=i // 4, column=i % 4, padx=15, pady=15)

    def toggle_student(self, btn, bracelet_id):
        if bracelet_id in self.selected_bracelets:
            self.selected_bracelets.remove(bracelet_id)
            btn.config(bg=btn.original_color, relief="raised", fg="black")
        else:
            self.selected_bracelets.append(bracelet_id)
            btn.config(bg="#4CAF50", relief="sunken", fg="black")

    def create_action_buttons(self):
        button_frame = tk.Frame(self.root, bg="#FFF8DC")
        button_frame.pack(pady=30)

        start_btn = tk.Button(
            button_frame,
            text="✅ Confirm Selection",
            bg="#32CD32",
            fg="black",
            font=("Comic Sans MS", 14, "bold"),
            width=20,
            height=2,
            command=self.controller.on_confirm_selection
        )
        start_btn.grid(row=0, column=0, padx=10)

        exit_btn = tk.Button(
            button_frame,
            text="📕 Exit",
            bg="#FF6347",
            fg="black",
            font=("Comic Sans MS", 14, "bold"),
            width=20,
            height=2,
            command=self.root.destroy
        )
        exit_btn.grid(row=0, column=1, padx=10)

    def show_message(self, title, message, warning=False):
        if warning:
            messagebox.showwarning(title, message)
        else:
            messagebox.showinfo(title, message)
