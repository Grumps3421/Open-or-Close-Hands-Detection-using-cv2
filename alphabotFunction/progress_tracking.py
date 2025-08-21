import tkinter as tk
from tkinter import messagebox, ttk, Toplevel
from pymongo import MongoClient
from PIL import Image, ImageTk
import os

# MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["alphabot_db"]
collection = db["makabansa"]

current_student = None

def show_subject_detail(subject):
    detail_window = Toplevel()
    detail_window.title(subject['subject_name'])
    detail_window.attributes('-fullscreen', True)
    detail_window.configure(bg="#FFF9E3")

    back_button = tk.Button(detail_window, text="🔙 Back", command=detail_window.destroy,
                            font=("Comic Sans MS", 14), bg="#FFCCCB", fg="black")
    back_button.pack(anchor="ne", padx=10, pady=10)

    subject_label = tk.Label(detail_window, text=f"📘 {subject['subject_name']}", font=("Comic Sans MS", 22, "bold"), bg="#FFF9E3")
    subject_label.pack(pady=10)

    completed = sum(1 for l in subject['lessons'] if l['score'] is not None)
    total = len(subject['lessons'])
    percent = (completed / total) * 100 if total > 0 else 0

    progress = ttk.Progressbar(detail_window, orient="horizontal", length=600, mode="determinate")
    progress.pack(pady=5)
    progress["value"] = percent

    progress_label = tk.Label(detail_window, text=f"{percent:.0f}% Complete", font=("Comic Sans MS", 16, "bold"), fg="blue", bg="#FFF9E3")
    progress_label.pack(pady=(0, 10))

    for lesson in subject['lessons']:
        text = f"📗 {lesson['lesson_title']}\n"
        if lesson['score'] is not None:
            text += f"   ⭐ Score: {lesson['score']} / {len(lesson['questions'])}\n"
            text += f"   📅 Date: {lesson['date']}\n"
            text += f"   🏅 Status: {lesson.get('status', 'Doing great!')}\n"
            if lesson['wrong_questions']:
                text += "   ❌ Incorrect Answers:\n"
                for wq in lesson['wrong_questions']:
                    text += f"      - {wq}\n"
            else:
                text += "   🎉 All answers correct!\n"
        else:
            text += "   🛌 Lesson not yet taken.\n"

        lesson_label = tk.Label(detail_window, text=text, font=("Courier", 13), bg="#FFF9E3", justify="left", anchor="w")
        lesson_label.pack(anchor="w", padx=20, pady=5)

def show_student_profile(bracelet):
    global current_student
    BRACELET_KEY = "bracelet_id"
    student = collection.find_one({BRACELET_KEY: bracelet})
    print(student)
    if not student:
        messagebox.showerror("Uh-oh!", f"Bracelet {bracelet} is not registered!")
        return

    profile_window = Toplevel()
    profile_window.title(f"{student['studentname']}'s Profile")
    profile_window.attributes('-fullscreen', True)
    profile_window.configure(bg="#FFF9E3")

    back_button = tk.Button(profile_window, text="🔙 Back", command=profile_window.destroy,
                             font=("Comic Sans MS", 14), bg="#FFCCCB", fg="black")
    back_button.pack(anchor="ne", padx=10, pady=10)

    # Scrollable frame
    canvas = tk.Canvas(profile_window, bg="#FFF9E3")
    scrollbar = ttk.Scrollbar(profile_window, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#FFF9E3")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Avatar
    avatar_path = student.get("avatar", "default_avatar.png")
    if os.path.exists(avatar_path):
        img = Image.open(avatar_path).resize((100, 100))
    else:
        img = Image.new('RGB', (100, 100), color='gray')
    photo = ImageTk.PhotoImage(img)
    avatar_label = tk.Label(scrollable_frame, image=photo, bg="#FFF9E3")
    avatar_label.image = photo
    avatar_label.grid(row=0, column=0, rowspan=3, padx=20, pady=10)

    name_label = tk.Label(scrollable_frame, text=f"👦 Name: {student['studentname']}", font=("Comic Sans MS", 18, "bold"), bg="#FFF9E3")
    bracelet_label = tk.Label(scrollable_frame,
                              text=f"🎟️ Bracelet #: {student['bracelet_id']}",
                              font=("Comic Sans MS", 16), bg="#FFF9E3")

    subjects_label = tk.Label(scrollable_frame, text=f"📚 Subjects Enrolled: {len(student['total_subjects'])}", font=("Comic Sans MS", 16), bg="#FFF9E3")

    name_label.grid(row=0, column=1, sticky="w")
    bracelet_label.grid(row=1, column=1, sticky="w")
    subjects_label.grid(row=2, column=1, sticky="w")

    completed = 0
    total = 0
    for subject in student['total_subjects']:
        total += len(subject['lessons'])
        completed += sum(1 for l in subject['lessons'] if l['score'] is not None)

    percent = (completed / total) * 100 if total > 0 else 0
    progress_bar = ttk.Progressbar(scrollable_frame, orient="horizontal", length=600, mode="determinate")
    progress_bar.grid(row=3, column=0, columnspan=2, pady=(10, 0))
    progress_bar["value"] = percent

    progress_label = tk.Label(scrollable_frame, text=f"{percent:.0f}% Complete", font=("Comic Sans MS", 14, "bold"), fg="green", bg="#FFF9E3")
    progress_label.grid(row=4, column=0, columnspan=2, pady=(0, 10))

    row = 5
    for subject in student['total_subjects']:
        subject_label = tk.Label(scrollable_frame, text=f"📘 {subject['subject_name']}", font=("Comic Sans MS", 16, "bold"), bg="#FFF9E3")
        subject_label.grid(row=row, column=0, sticky="w", pady=(10, 0))

        view_button = tk.Button(scrollable_frame, text="View", font=("Comic Sans MS", 12), bg="#ADD8E6",
                                command=lambda s=subject: show_subject_detail(s))
        view_button.grid(row=row, column=1, sticky="e")
        row += 1

        subject_total = len(subject['lessons'])
        subject_completed = sum(1 for l in subject['lessons'] if l['score'] is not None)
        subject_percent = (subject_completed / subject_total) * 100 if subject_total > 0 else 0

        subject_progress = ttk.Progressbar(scrollable_frame, orient="horizontal", length=500, mode="determinate")
        subject_progress.grid(row=row, column=0, columnspan=2, pady=(0, 5))
        subject_progress["value"] = subject_percent

        subject_progress_label = tk.Label(scrollable_frame, text=f"{subject_percent:.0f}% Complete", font=("Comic Sans MS", 12), bg="#FFF9E3", fg="blue")
        subject_progress_label.grid(row=row+1, column=0, columnspan=2, sticky="w")

        row += 2

# ✅ Eto yung function na tatawagin sa Flask route
def launch_progressTracking_gui():
    window = tk.Tk()
    window.title("AlphaBot - Student Profile Viewer")
    window.attributes('-fullscreen', True)
    window.configure(bg="#FFF9E3")

    tk.Label(window, text="📚 AlphaBot - Student Profile Progress Viewer", font=("Comic Sans MS", 26, "bold"),
            bg="#FFF9E3", fg="#FF7F50").pack(pady=20)

    button_frame = tk.Frame(window, bg="#FFF9E3")
    button_frame.pack(pady=10)

    colors = ["#FFB6C1", "#ADD8E6", "#90EE90", "#FFD700", "#FFA07A", "#DDA0DD",
            "#F08080", "#87CEFA", "#FF69B4", "#00FA9A", "#FFA500", "#B0E0E6"]

    def on_enter(e):
        e.widget.config(bg="#ffffff", fg="black")

    def on_leave(e, color):
        e.widget.config(bg=color, fg="black")

    for i in range(1, 13):
        color = colors[i - 1]
        bracelet_id = f"Student{i}" # format for db
        btn = tk.Button(
            button_frame,
            text=f"Student {i}",
            width=12,
            height=3,
            font=("Comic Sans MS", 12, "bold"),
            bg=color,
            fg="black",
            command=lambda b=bracelet_id: show_student_profile(b)  # ito na ang ipapasa
        )
        btn.grid(row=(i - 1) // 4, column=(i - 1) % 4, padx=15, pady=15)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", lambda e, c=color: on_leave(e, c))

    exit_button = tk.Button(
        window,
        text="❌ Exit",
        font=("Comic Sans MS", 16, "bold"),
        bg="#FF6666",
        fg="white",
        padx=20,
        pady=10,
        command=window.destroy
    )
    exit_button.pack(pady=30)

    window.mainloop()
