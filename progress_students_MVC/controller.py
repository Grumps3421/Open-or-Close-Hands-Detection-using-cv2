import tkinter as tk
from tkinter import ttk
from ui import AlphaBotView
from models import AlphaBotModel
from tkinter import messagebox

class AlphaBotController:
    def __init__(self):
        self.model = AlphaBotModel()
        self.view = AlphaBotView(self)
        self.registered = self.model.load_registered_students()
        self.view.render_main_buttons(self.registered)

    # ==================================================
    # PROGRESS WINDOW
    # ==================================================
    def open_progress(self, bracelet_id):
        studentname = self.registered.get(bracelet_id, "Unregistered")

        if studentname == "Unregistered":
            self.view.show_message("Not Registered", f"{bracelet_id} is not registered yet.")
            return

        categorized = self.model.get_student_progress(bracelet_id)
        if not categorized:
            self.view.show_message("No Progress Found",
                                   f"No collection found for {studentname} ({bracelet_id}) with 50 questions.")
            return

        progress_window = tk.Toplevel(self.view.root)
        progress_window.title(f"{studentname}'s Progress")
        progress_window.attributes('-fullscreen', True)
        progress_window.configure(bg="#FFF8E7")

        tk.Label(progress_window, text=f"🎓 {studentname}'s Learning Progress 🎓",
                 font=("Comic Sans MS", 22, "bold"), fg="#333", bg="#FFF8E7").pack(pady=20)

        content_frame = tk.Frame(progress_window, bg="#FFF8E7")
        content_frame.pack(fill="both", expand=True, padx=30, pady=10)

        pastel_colors = ["#FFD1DC", "#B5EAD7", "#FFDAC1", "#C7CEEA", "#FFF5BA"]

        def show_lesson_questions(subject, lesson, lesson_number):
            for widget in content_frame.winfo_children():
                widget.destroy()

            tk.Label(content_frame, text=f"📘 {subject} - Lesson {lesson_number}",
                     font=("Comic Sans MS", 18, "bold"),
                     bg="#FFF8E7", fg="#333").pack(pady=10)

            questions = categorized[subject][lesson]
            total_q = len(questions)
            correct_q = sum(1 for q in questions if str(q.get("student_answer", "")).strip() ==
                            str(q.get("correct_answer", "")).strip())

            progress_percent = (correct_q / total_q) * 100 if total_q > 0 else 0

            tk.Label(content_frame,
                     text=f"Progress: {correct_q}/{total_q} correct 🌟",
                     font=("Comic Sans MS", 14, "bold"),
                     bg="#FFF8E7").pack(pady=(5, 0))

            progress = ttk.Progressbar(content_frame, orient="horizontal", length=400, mode="determinate")
            progress["value"] = progress_percent
            progress.pack(pady=5)

            style = ttk.Style()
            style.configure("Treeview.Heading", font=("Comic Sans MS", 16, "bold"))
            style.configure("Treeview", font=("Comic Sans MS", 18), rowheight=50)

            tree = ttk.Treeview(content_frame, columns=("Question", "Answer", "Result"), show="headings", height=10)

            # Headings
            tree.heading("Question", text="🧠 Question")
            tree.heading("Answer", text="✏️ Answer")
            tree.heading("Result", text="🌟 Result")

            # Column widths and alignment
            tree.column("Question", width=600, anchor="w")  # Left-aligned
            tree.column("Answer", width=150, anchor="center")  # Centered
            tree.column("Result", width=100, anchor="center")  # Centered

            tree.pack(padx=20, pady=10, fill="both", expand=True)

            # Insert data
            for q in questions:
                student_answer = str(q.get("student_answer", "None"))  # Ensure "None" shows
                correct = "✅" if q.get("score", 0) > 0 else "❌"
                tree.insert("", "end", values=(q.get("question", "N/A"), student_answer, correct))


            tk.Button(content_frame, text="⬅ Back to Lessons",
                      command=lambda: show_lesson_buttons(subject),
                      bg="#A3D8F4", font=("Comic Sans MS", 13, "bold"),
                      relief="raised", width=22, height=2).pack(pady=20)

        def show_lesson_buttons(subject):
            for widget in content_frame.winfo_children():
                widget.destroy()

            tk.Label(content_frame, text=f"📚 {subject} Lessons",
                     font=("Comic Sans MS", 18, "bold"), bg="#FFF8E7").pack(pady=10)

            lessons = list(categorized[subject].keys())
            btn_frame = tk.Frame(content_frame, bg="#FFF8E7")
            btn_frame.pack(pady=30)

            for i, lesson in enumerate(lessons):
                color = pastel_colors[i % len(pastel_colors)]
                tk.Button(btn_frame, text=f"📖 Lesson {i + 1}",
                          command=lambda s=subject, l=lesson, n=i + 1: show_lesson_questions(s, l, n),
                          width=18, height=3, bg=color,
                          font=("Comic Sans MS", 14, "bold")).grid(row=i // 3, column=i % 3, padx=25, pady=20)

            tk.Button(content_frame, text="⬅ Back to Subjects",
                      command=show_subject_buttons,
                      bg="#A3D8F4", font=("Comic Sans MS", 13, "bold"),
                      relief="raised", width=22, height=2).pack(pady=10)

        def show_subject_buttons():
            for widget in content_frame.winfo_children():
                widget.destroy()

            tk.Label(content_frame, text="✨ Choose a Subject ✨",
                     font=("Comic Sans MS", 18, "bold"), bg="#FFF8E7").pack(pady=10)

            subjects = list(categorized.keys())
            btn_frame = tk.Frame(content_frame, bg="#FFF8E7")
            btn_frame.pack(pady=30)

            for i, subject in enumerate(subjects):
                color = pastel_colors[i % len(pastel_colors)]
                tk.Button(btn_frame, text=f"📚 {subject}",
                          command=lambda s=subject: show_lesson_buttons(s),
                          width=18, height=3, bg=color,
                          font=("Comic Sans MS", 14, "bold")).grid(row=i // 3, column=i % 3, padx=25, pady=20)

            tk.Button(content_frame, text="❌ Close Window",
                      command=progress_window.destroy,
                      bg="#F77F00", fg="white",
                      font=("Comic Sans MS", 13, "bold"),
                      relief="raised", width=15, height=2).pack(pady=10)

        show_subject_buttons()

    # ==================================================
    # LEADERBOARD
    # ==================================================
    def open_leaderboard(self):
        subjects = self.model.get_subjects()
        registered = self.registered

        leaderboard_window = tk.Toplevel(self.view.root)
        leaderboard_window.title("🏆 AlphaBot Leaderboard 🏆")
        leaderboard_window.attributes('-fullscreen', True)
        leaderboard_window.config(bg="#E8F3D6")

        content_frame = tk.Frame(leaderboard_window, bg="#E8F3D6")
        content_frame.pack(expand=True)
        pastel_colors = ["#FFD1DC", "#B5EAD7", "#FFDAC1", "#C7CEEA", "#FFF5BA"]

        def show_subject_leaderboard(subject):
            for widget in content_frame.winfo_children():
                widget.destroy()

            tk.Label(content_frame, text=f"🏅 Top Students - {subject} 🏅",
                     font=("Comic Sans MS", 28, "bold"), bg="#E8F3D6").pack(pady=20)

            leaderboard_data = self.model.get_leaderboard_data(registered, subject)

            if not leaderboard_data:
                tk.Label(content_frame, text="No students have data for this subject yet 📊",
                         font=("Comic Sans MS", 16), bg="#E8F3D6").pack(pady=20)
                return

            style = ttk.Style()
            style.configure("Treeview.Heading", font=("Comic Sans MS", 18, "bold"))
            style.configure("Treeview", font=("Comic Sans MS", 20, "bold"), rowheight=40)

            tree = ttk.Treeview(content_frame, columns=("Name", "Score"), show="headings", height=12)
            tree.heading("Name", text="👧 Student Name")
            tree.heading("Score", text="⭐ Score (%)")
            tree.column("Name", width=500)
            tree.column("Score", width=200, anchor="center")
            tree.pack(pady=10, fill="both", expand=True)

            for rank, entry in enumerate(leaderboard_data, start=1):
                medal = ["🥇", "🥈", "🥉"][rank - 1] if rank <= 3 else f" {rank}. "
                display_name = f"{medal} {entry['studentname']}"
                tree.insert("", "end", values=(display_name, f"{entry['score']}%"))

            tk.Button(content_frame, text="⬅ Back to Subjects",
                      command=show_subject_buttons,
                      bg="#A3D8F4", font=("Comic Sans MS", 16, "bold"),
                      relief="raised", width=18, height=2).pack(pady=20)

        def show_subject_buttons():
            for widget in content_frame.winfo_children():
                widget.destroy()

            btn_frame = tk.Frame(content_frame, bg="#E8F3D6")
            btn_frame.pack(pady=40)

            for i, subject in enumerate(subjects):
                color = pastel_colors[i % len(pastel_colors)]
                tk.Button(btn_frame, text=f"📘 {subject}",
                          command=lambda s=subject: show_subject_leaderboard(s),
                          width=20, height=3, bg=color,
                          font=("Comic Sans MS", 16, "bold")).grid(row=i // 3, column=i % 3, padx=25, pady=25)

            tk.Button(content_frame, text="❌ Close Window",
                      command=leaderboard_window.destroy,
                      bg="#F77F00", fg="white",
                      font=("Comic Sans MS", 16, "bold"),
                      relief="raised", width=15, height=2).pack(pady=10)

        show_subject_buttons()
