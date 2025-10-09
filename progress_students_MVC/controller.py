from models import AlphaBotModel
from ui import AlphaBotView
import tkinter as tk
from tkinter import ttk, Toplevel

class AlphaBotController:
    def __init__(self, root):
        self.model = AlphaBotModel()
        self.view = AlphaBotView(root, self)

    # ---------------- Event Handlers ----------------
    def show_student_profile(self, bracelet):
        student = self.model.get_student(bracelet)
        if not student:
            self.view.show_error("Uh-oh!", f"Bracelet {bracelet} is not registered!")
        else:
            self.view.show_student_profile_window(student)

    def show_leaderboard(self):
        students = self.model.get_all_students()
        subjects = {}
        for student in students:
            for subject in student.get("total_subjects", []):
                subject_name = subject["subject_name"]
                scores = []
                for l in subject["lessons"]:
                    if l.get("attempts"):
                        latest = l["attempts"][-1]
                        if len(l["questions"]) > 0:
                            scores.append(latest["score"] / len(l["questions"]) * 100)
                if scores:
                    avg_score = sum(scores) / len(scores)
                    if subject_name not in subjects:
                        subjects[subject_name] = []
                    subjects[subject_name].append((student["studentname"], avg_score))
        self.view.show_leaderboard_window(subjects)

    # ---------------- UI Windows ----------------
    def _show_attempts_ui(self, lesson):
        attempts_window = Toplevel()
        attempts_window.title(f"Attempts - {lesson['lesson_title']}")
        attempts_window.attributes('-fullscreen', True)
        attempts_window.configure(bg="#FFF9E3")

        # Back button
        back_button = tk.Button(attempts_window, text="🔙 Back",
                                command=attempts_window.destroy,
                                font=("Comic Sans MS", 16, "bold"),
                                bg="#FFB6B6", fg="black", padx=20, pady=10)
        back_button.pack(anchor="ne", padx=15, pady=15)

        tk.Label(attempts_window, text=f"📖 All Attempts for {lesson['lesson_title']}",
                 font=("Comic Sans MS", 28, "bold"), bg="#FFF9E3").pack(pady=10)

        # Scrollable frame
        canvas = tk.Canvas(attempts_window, bg="#FFF9E3", highlightthickness=0)
        scrollbar = ttk.Scrollbar(attempts_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#FFF9E3")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Grid of attempts
        for idx, attempt in enumerate(lesson.get("attempts", []), start=1):
            row = (idx - 1) // 3
            col = (idx - 1) % 3
            frame = tk.Frame(scrollable_frame, bg="#FAF3DD", bd=2, relief="ridge", padx=10, pady=10)
            frame.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

            tk.Label(frame, text=f"Attempt {idx} - 📅 {attempt['date']}",
                     font=("Comic Sans MS", 16, "bold"), bg="#FAF3DD").pack(anchor="w")
            tk.Label(frame, text=f"⭐ Score: {attempt['score']} / {len(lesson['questions'])}",
                     font=("Comic Sans MS", 14), bg="#FAF3DD").pack(anchor="w")
            tk.Label(frame, text=f"🏅 Status: {attempt.get('status','Doing great!')}",
                     font=("Comic Sans MS", 14), bg="#FAF3DD").pack(anchor="w")

            if attempt.get("wrong_questions"):
                tk.Label(frame, text="❌ Wrong:", font=("Comic Sans MS", 12, "bold"),
                         bg="#FAF3DD", fg="red").pack(anchor="w")
                for q in attempt["wrong_questions"]:
                    tk.Label(frame, text=f"   - {q}", font=("Comic Sans MS", 12),
                             bg="#FAF3DD", fg="red").pack(anchor="w")

            if attempt.get("correct_questions"):
                tk.Label(frame, text="✅ Correct:", font=("Comic Sans MS", 12, "bold"),
                         bg="#FAF3DD", fg="green").pack(anchor="w")
                for q in attempt["correct_questions"]:
                    tk.Label(frame, text=f"   - {q}", font=("Comic Sans MS", 12),
                             bg="#FAF3DD", fg="green").pack(anchor="w")

    def _show_subject_detail_ui(self, subject):
        detail_window = Toplevel()
        detail_window.title(subject['subject_name'])
        detail_window.attributes('-fullscreen', True)
        detail_window.configure(bg="#FFF9E3")

        back_button = tk.Button(detail_window, text="🔙 Back",
                                command=detail_window.destroy,
                                font=("Comic Sans MS", 16, "bold"),
                                bg="#FFB6B6", fg="black", padx=20, pady=10)
        back_button.pack(anchor="ne", padx=15, pady=15)

        tk.Label(detail_window, text=f"📘 {subject['subject_name']}",
                 font=("Comic Sans MS", 28, "bold"), bg="#FFF9E3").pack(pady=10)

        completed = sum(1 for l in subject['lessons'] if l.get("attempts"))
        total = len(subject['lessons'])
        percent = (completed / total) * 100 if total > 0 else 0

        progress = ttk.Progressbar(detail_window, orient="horizontal", length=700, mode="determinate")
        progress["value"] = percent
        progress.pack(pady=2)

        tk.Label(detail_window, text=f"{percent:.0f}% Complete",
                 font=("Comic Sans MS", 18, "bold"), fg="blue", bg="#FFF9E3").pack(pady=(0, 10))

        # Scroll horizontally
        canvas = tk.Canvas(detail_window, bg="#FFF9E3", highlightthickness=0, height=500)
        scrollbar = ttk.Scrollbar(detail_window, orient="horizontal", command=canvas.xview)
        scrollable_frame = tk.Frame(canvas, bg="#FFF9E3")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)

        canvas.pack(fill="both", expand=True)
        scrollbar.pack(fill="x")

        # Lessons
        for idx, lesson in enumerate(subject['lessons']):
            frame = tk.Frame(scrollable_frame, bg="#FAF3DD", bd=2, relief="ridge", width=300, height=420)
            frame.grid(row=0, column=idx, padx=20, pady=10)
            frame.grid_propagate(False)

            tk.Label(frame, text=f"📗 {lesson['lesson_title']}",
                     font=("Comic Sans MS", 16, "bold"), bg="#FAF3DD").pack(anchor="w", padx=10)

            if lesson.get("attempts"):
                latest = lesson["attempts"][-1]
                total_q = len(lesson['questions'])
                score_percent = (latest['score'] / total_q) * 100 if total_q > 0 else 0

                score_bar = ttk.Progressbar(frame, orient="horizontal", length=250, mode="determinate")
                score_bar["value"] = score_percent
                score_bar.pack(padx=10)

                tk.Label(frame, text=f"{score_percent:.0f}% Correct",
                         font=("Comic Sans MS", 12, "bold"), fg="blue", bg="#FAF3DD").pack()
                tk.Label(frame, text=f"⭐ {latest['score']} / {total_q}",
                         font=("Comic Sans MS", 14, "bold"), fg="green", bg="#FAF3DD").pack(anchor="w", padx=10)
                tk.Label(frame, text=f"📅 Date: {latest['date']}",
                         font=("Comic Sans MS", 12), bg="#FAF3DD").pack(anchor="w", padx=10)
                tk.Label(frame, text=f"🏅 Status: {latest.get('status','Doing great!')}",
                         font=("Comic Sans MS", 12), bg="#FAF3DD").pack(anchor="w", padx=10)

                tk.Button(frame, text="📖 View Attempts", bg="#ADD8E6",
                          font=("Comic Sans MS", 12, "bold"),
                          command=lambda l=lesson: self._show_attempts_ui(l)).pack(pady=5)
            else:
                tk.Label(frame, text="🛌 Lesson not yet taken.",
                         font=("Comic Sans MS", 12, "italic"), bg="#FAF3DD").pack(anchor="w", padx=10)

    def _show_student_profile_ui(self, student):
        profile_window = Toplevel()
        profile_window.title(f"{student['studentname']}'s Profile")
        profile_window.attributes('-fullscreen', True)
        profile_window.configure(bg="#FFF9E3")

        tk.Button(profile_window, text="🔙 Back", command=profile_window.destroy,
                  font=("Comic Sans MS", 16, "bold"),
                  bg="#FFB6B6", fg="black", padx=20, pady=10).pack(anchor="ne", padx=15, pady=15)

        canvas = tk.Canvas(profile_window, bg="#FFF9E3", highlightthickness=0)
        scrollbar = ttk.Scrollbar(profile_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#FFF9E3")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(scrollable_frame, text="🧒", font=("Arial", 60), bg="#FFF9E3").grid(row=0, column=0, rowspan=3, padx=20, pady=10)
        tk.Label(scrollable_frame, text=f"👦 Name: {student['studentname']}",
                 font=("Comic Sans MS", 20, "bold"), bg="#FFF9E3").grid(row=0, column=1, sticky="w")
        tk.Label(scrollable_frame, text=f"🎟️ Bracelet #: {student['bracelet_id']}",
                 font=("Comic Sans MS", 18), bg="#FFF9E3").grid(row=1, column=1, sticky="w")
        tk.Label(scrollable_frame, text=f"📚 Subjects Enrolled: {len(student['total_subjects'])}",
                 font=("Comic Sans MS", 18), bg="#FFF9E3").grid(row=2, column=1, sticky="w")

        completed = sum(1 for s in student['total_subjects'] for l in s['lessons'] if l.get("attempts"))
        total = sum(len(s['lessons']) for s in student['total_subjects'])
        percent = (completed / total) * 100 if total > 0 else 0

        progress_bar = ttk.Progressbar(scrollable_frame, orient="horizontal", length=700, mode="determinate")
        progress_bar["value"] = percent
        progress_bar.grid(row=3, column=0, columnspan=2, pady=(5, 0))
        tk.Label(scrollable_frame, text=f"{percent:.0f}% Taken",
                 font=("Comic Sans MS", 16, "bold"), fg="green", bg="#FFF9E3").grid(row=4, column=0, columnspan=2)

        row = 5
        for subject in student['total_subjects']:
            frame = tk.Frame(scrollable_frame, bg="#E0F7FA", bd=2, relief="ridge")
            frame.grid(row=row, column=0, columnspan=2, padx=20, pady=2, sticky="w")

            tk.Label(frame, text=f"📘 {subject['subject_name']}",
                     font=("Comic Sans MS", 16, "bold"), bg="#E0F7FA").grid(row=0, column=0, sticky="w", padx=10)
            tk.Button(frame, text="View", font=("Comic Sans MS", 12),
                      bg="#ADD8E6", command=lambda s=subject: self._show_subject_detail_ui(s)).grid(row=0, column=1, sticky="e", padx=5)

            subject_total = len(subject['lessons'])
            subject_completed = sum(1 for l in subject['lessons'] if l.get("attempts"))
            subject_percent = (subject_completed / subject_total) * 100 if subject_total > 0 else 0

            progress = ttk.Progressbar(frame, orient="horizontal", length=500, mode="determinate")
            progress["value"] = subject_percent
            progress.grid(row=1, column=0, columnspan=2, padx=10, sticky="w")
            tk.Label(frame, text=f"{subject_percent:.0f}% Complete",
                     font=("Comic Sans MS", 12, "bold"), bg="#E0F7FA", fg="blue").grid(row=2, column=0, columnspan=2, sticky="w")
            row += 1

    def _show_leaderboard_ui(self, subjects):
        leaderboard_window = Toplevel()
        leaderboard_window.title("🏆 Leaderboards")
        leaderboard_window.attributes('-fullscreen', True)
        leaderboard_window.configure(bg="#FFF9E3")

        tk.Button(leaderboard_window, text="🔙 Back", command=leaderboard_window.destroy,
                  font=("Comic Sans MS", 16, "bold"), bg="#FFB6B6", fg="black", padx=20, pady=10).pack(anchor="ne", padx=15, pady=15)

        tk.Label(leaderboard_window, text="📊 Subject Leaderboards",
                 font=("Comic Sans MS", 28, "bold"), bg="#FFF9E3").pack(pady=20)

        canvas = tk.Canvas(leaderboard_window, bg="#FFF9E3", highlightthickness=0)
        scrollbar = ttk.Scrollbar(leaderboard_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#FFF9E3")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        max_cols = 4
        row_index, col_index = 0, 0

        for subject_name, data in subjects.items():
            data.sort(key=lambda x: x[1], reverse=True)

            subject_frame = tk.Frame(scrollable_frame, bg="#FFF9E3", bd=2, relief="groove", padx=10, pady=10)
            subject_frame.grid(row=row_index, column=col_index, padx=15, pady=15, sticky="n")

            tk.Label(subject_frame, text=f"🏅 {subject_name} Leaderboard",
                     font=("Comic Sans MS", 16, "bold"), bg="#FFF9E3", fg="#006FB9").pack(pady=5)

            previous_score = None
            for rank, (student, score) in enumerate(data, start=1):
                label_text = f"{rank}. {student} - {score:.1f}%" if previous_score != score else f"{rank}. {student} - {score:.1f}% (Tied)"

                entry_frame = tk.Frame(subject_frame, bg="#FFF9E3")
                entry_frame.pack(anchor="w", pady=2)

                tk.Label(entry_frame, text=label_text, font=("Comic Sans MS", 12), bg="#FFF9E3").pack(anchor="w")

                score_bar = ttk.Progressbar(entry_frame, orient="horizontal", length=200, mode="determinate")
                score_bar["value"] = score
                score_bar.pack(anchor="w", pady=(0, 2))

                previous_score = score

            col_index += 1
            if col_index >= max_cols:
                col_index = 0
                row_index += 1
