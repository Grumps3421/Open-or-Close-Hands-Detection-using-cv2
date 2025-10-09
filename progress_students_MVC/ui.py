import tkinter as tk
from tkinter import messagebox, ttk, Toplevel

class AlphaBotView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("AlphaBot - Student Profile Viewer")
        self.root.attributes('-fullscreen', True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#FFF9E3")
        self.root.after(1000, lambda: root.attributes("-topmost", False))

        # Title
        tk.Label(self.root, text="📚 AlphaBot - Student Profile Progress Viewer",
                 font=("Comic Sans MS", 28, "bold"),
                 bg="#FFF9E3", fg="#FF7F50").pack(pady=30)

        # Student buttons frame
        self.button_frame = tk.Frame(self.root, bg="#FFF9E3")
        self.button_frame.pack(pady=20)

        self.colors = ["#FF0000", "#808080", "#75FF33", "#FFA500",
                       "#D633FF", "#00BFFF", "#FFFFFF", "#40E0D0",
                       "#FFB6C1", "#87CEEB", "#FF13F0", "#FC8EAC"]

        # Create main UI buttons
        self.create_student_buttons()
        self.create_leaderboard_button()
        self.create_exit_button()

    # ---------------- Main Window Buttons ----------------
    def create_student_buttons(self):
        for i in range(1, 13):
            color = self.colors[i - 1]
            btn = tk.Button(self.button_frame, text=f"Student {i}", width=15, height=3,
                            font=("Comic Sans MS", 14, "bold"), bg=color, fg="black",
                            command=lambda b=f"Student{i}": self.controller.show_student_profile(b))
            btn.grid(row=(i - 1) // 4, column=(i - 1) % 4, padx=20, pady=20)
            btn.bind("<Enter>", lambda e: e.widget.config(bg="#ffffff", fg="black"))
            btn.bind("<Leave>", lambda e, c=color: e.widget.config(bg=c, fg="black"))

    def create_leaderboard_button(self):
        leaderboard_button = tk.Button(self.root, text="🏆 View Leaderboards",
                                       font=("Comic Sans MS", 18, "bold"),
                                       bg="#FFD700", fg="black", padx=20, pady=10,
                                       command=self.controller.show_leaderboard)
        leaderboard_button.pack(pady=20)

    def create_exit_button(self):
        exit_button = tk.Button(self.root, text="❌ Exit",
                                command=self.root.quit,
                                font=("Comic Sans MS", 16, "bold"),
                                bg="#FFB6B6", fg="black", padx=20, pady=10)
        exit_button.pack(pady=10)

    # ---------------- Windows ----------------
    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def show_student_profile_window(self, student):
        self.controller._show_student_profile_ui(student)

    def show_subject_detail_window(self, subject):
        self.controller._show_subject_detail_ui(subject)

    def show_attempts_window(self, lesson):
        self.controller._show_attempts_ui(lesson)

    def show_leaderboard_window(self, subjects):
        self.controller._show_leaderboard_ui(subjects)
