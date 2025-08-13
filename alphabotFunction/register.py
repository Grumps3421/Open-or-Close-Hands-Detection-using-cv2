# register.py
import tkinter as tk
from tkinter import messagebox, filedialog
from pymongo import MongoClient
import easyocr
import cv2

client = MongoClient("mongodb://localhost:27017/")
db = client["alphabot_db"]
collection = db["registered_students"]

selected_bracelet_id = None
bracelet_buttons = {}
button_refs = {}

bracelet_colors = {
    "Student1": "#FF0000",
    "Student2": "#808080",
    "Student3": "#75FF33",
    "Student4": "#F3FF33",
    "Student5": "#D633FF",
    "Student6": "#FF33A8",
    "Student7": "#33FFD7",
    "Student8": "#FF9E33",
    "Student9": "#C70039",
    "Student10": "#900C3F",
    "Student11": "#581845",
    "Student12": "#1ABC9C",
}

def launch_registration_gui():
    global selected_bracelet_id, bracelet_buttons, button_refs, student_name_var, selected_label

    def save_registration():
        global selected_bracelet_id
        student_name = student_name_var.get().strip()

        if not selected_bracelet_id:
            messagebox.showwarning("Selection Error", "Select a bracelet ID first.")
            return

        if not student_name:
            messagebox.showwarning("Input Error", "Please scan or enter the student name.")
            return

        existing_name = collection.find_one({"student_name": {"$regex": f"^{student_name}$", "$options": "i"}})
        if existing_name:
            messagebox.showerror("Already Exists", f"Student name '{student_name}' is already registered.")
            return

        existing_id = collection.find_one({"bracelet_id": selected_bracelet_id})
        if existing_id:
            messagebox.showerror("Already Exists", f"{selected_bracelet_id} is already registered to {existing_id['student_name']}")
        else:
            collection.insert_one({
                "bracelet_id": selected_bracelet_id,
                "student_name": student_name
            })
            messagebox.showinfo("Success", f"Registered {student_name} to {selected_bracelet_id}")
            student_name_var.set("")
            update_button_status(selected_bracelet_id)
            selected_bracelet_id = None
            update_label()

    def select_bracelet(bracelet_id):
        global selected_bracelet_id
        selected_bracelet_id = bracelet_id
        update_label()

    def update_label():
        if selected_bracelet_id:
            selected_label.config(text=f"Selected: {selected_bracelet_id}")
        else:
            selected_label.config(text="No class selected")

    def scan_name_easyocr():
        file_path = filedialog.askopenfilename(
            title="Select an image of the name tag",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.webp")]
        )
        if not file_path:
            return
        image = cv2.imread(file_path)
        if image is None:
            messagebox.showerror("File Error", "Failed to load image.")
            return

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        reader = easyocr.Reader(['en'])
        results = reader.readtext(gray)
        if results:
            student_name_var.set(results[0][1])
        else:
            messagebox.showwarning("OCR Result", "No text detected in image.")

    def update_button_status(bracelet_id):
        btn = button_refs.get(bracelet_id)
        if btn:
            btn.config(text="Not Available", state=tk.DISABLED)

    root = tk.Tk()
    root.title("Student Bracelet Registration")

    tk.Label(root, text="Select Bracelet Class:").pack(pady=(10, 2))

    btn_frame = tk.Frame(root)
    btn_frame.pack()

    row = 0
    col = 0
    for i, (b_id, color) in enumerate(bracelet_colors.items()):
        existing = collection.find_one({"bracelet_id": b_id})
        is_occupied = existing is not None

        btn = tk.Button(
            btn_frame,
            text="Not Available" if is_occupied else b_id,
            bg=color,
            width=12,
            height=2,
            state=tk.DISABLED if is_occupied else tk.NORMAL,
            command=lambda b=b_id: select_bracelet(b)
        )
        btn.grid(row=row, column=col, padx=5, pady=5)
        button_refs[b_id] = btn
        col += 1
        if col == 4:
            col = 0
            row += 1

    selected_label = tk.Label(root, text="No class selected", font=("Arial", 10, "bold"))
    selected_label.pack(pady=(5, 10))

    tk.Label(root, text="Student Name:").pack()
    student_name_var = tk.StringVar()
    tk.Entry(root, textvariable=student_name_var, width=30).pack(pady=5)
    tk.Button(root, text="Scan Name Tag (Image)", command=scan_name_easyocr, bg="#007ACC", fg="white").pack(pady=5)
    tk.Button(root, text="Register", command=save_registration, bg="green", fg="white").pack(pady=10)

    root.mainloop()
