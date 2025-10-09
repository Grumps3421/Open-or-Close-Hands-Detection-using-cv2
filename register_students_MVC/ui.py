import tkinter as tk
from tkinter import messagebox

class BraceletView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        self.selected_bracelet_id = None
        self.student_name_var = tk.StringVar()

        self.root.title("🎈 Student Bracelet Registration 🎈")
        self.root.attributes('-fullscreen', True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#FFF8DC")
        self.root.after(1000, lambda: root.attributes("-topmost", False))


        # Title
        tk.Label(
            self.root, text="🎉 Welcome to Bracelet Registration 🎉",
            font=("Comic Sans MS", 28, "bold"), bg="#FFF8DC", fg="#FF5733"
        ).pack(pady=20)

        # Bracelet selection
        tk.Label(
            self.root, text="Select Bracelet Number:",
            font=("Comic Sans MS", 18, "bold"), bg="#FFF8DC", fg="#2E86C1"
        ).pack(pady=(10, 2))

        self.btn_frame = tk.Frame(self.root, bg="#FFF8DC")
        self.btn_frame.pack()

        self.selected_label = tk.Label(
            self.root, text="No bracelet selected 🙃",
            font=("Comic Sans MS", 16, "bold"), bg="#FFF8DC", fg="#8E44AD"
        )
        self.selected_label.pack(pady=(10, 15))

        tk.Label(
            self.root, text="Student Name:",
            font=("Comic Sans MS", 16, "bold"), bg="#FFF8DC", fg="#117A65"
        ).pack()
        tk.Entry(
            self.root, textvariable=self.student_name_var,
            font=("Comic Sans MS", 14), width=30, relief="solid"
        ).pack(pady=8)

        tk.Button(
            self.root, text="📷 Scan Name Tag (Camera For Registration)", command=self.scan_name_easyocr,
            bg="#007ACC", fg="white", font=("Comic Sans MS", 14, "bold"), width=38
        ).pack(pady=8)

        tk.Button(
            self.root, text="🧹Clear Text", command=self.clear_text_field,
            bg="orange", fg="white", font=("Comic Sans MS", 14, "bold"), width=20
        ).pack(pady=8)

        tk.Button(
            self.root, text="✅ Register", command=self.register_student,
            bg="green", fg="white", font=("Comic Sans MS", 14, "bold"), width=20
        ).pack(pady=8)

        tk.Button(
            self.root, text="❌ Unregister", command=self.show_unregister_window,
            bg="red", fg="white", font=("Comic Sans MS", 14, "bold"), width=20
        ).pack(pady=8)


        tk.Button(
            self.root, text="🚪 Exit", command=self.root.destroy,
            bg="#E74C3C", fg="white", font=("Comic Sans MS", 14, "bold"), width=15
        ).pack(pady=15)

    def load_bracelet_buttons(self, bracelet_colors, taken_bracelets):
        row = 0
        col = 0
        for b_id, color in bracelet_colors.items():
            is_occupied = b_id in taken_bracelets
            btn = tk.Button(
                self.btn_frame,
                text="❌ Taken" if is_occupied else b_id,
                bg=color, fg="white", font=("Comic Sans MS", 14, "bold"),
                width=12, height=2,
                state=tk.DISABLED if is_occupied else tk.NORMAL,
                command=lambda b=b_id: self.select_bracelet(b)
            )
            btn.grid(row=row, column=col, padx=8, pady=8)
            col += 1
            if col == 4:
                col = 0
                row += 1

    def select_bracelet(self, bracelet_id):
        self.selected_bracelet_id = bracelet_id
        self.selected_label.config(text=f"🎯 Selected: {bracelet_id}")

    def register_student(self):
        name = self.student_name_var.get().strip()
        if not self.selected_bracelet_id:
            messagebox.showwarning("Oops! 😅", "Please select a bracelet ID first!")
            return
        if not name:
            messagebox.showwarning("Hmm 🤔", "Please enter the student name.")
            return

        success, message = self.controller.register_student(name, self.selected_bracelet_id)
        if success:
            messagebox.showinfo("Yay! 🎉", message)
            self.selected_bracelet_id = None
            self.selected_label.config(text="No bracelet selected 🙃")
            self.student_name_var.set("")
            self.refresh_bracelets()
        else:
            messagebox.showerror("Oh no! 🚫", message)


    def refresh_bracelets(self):
        for widget in self.btn_frame.winfo_children():
            widget.destroy()
        bracelet_colors = self.controller.get_bracelet_colors()
        taken_bracelets = self.controller.get_taken_bracelets()
        self.load_bracelet_buttons(bracelet_colors, taken_bracelets)


    def scan_name_easyocr(self):
        import cv2
        import easyocr
        from PIL import Image, ImageTk
        import threading

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Camera Error", "Unable to access the camera.")
            return

        preview = tk.Toplevel(self.root)
        preview.title("Scan Name Tag in the Camera to Read Text")
        preview.geometry("400x228")
        preview.configure(bg="white")

        preview_label = tk.Label(preview)
        preview_label.pack()

        countdown_label = tk.Label(preview, text="Auto-capturing in 5...", font=("Comic Sans MS", 16, "bold"), bg="white", fg="red")
        countdown_label.pack(pady=10)

        countdown = [10]

        def update_frame():
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = cv2.resize(frame_rgb, (640, 480))
                img = ImageTk.PhotoImage(Image.fromarray(img))
                preview_label.img = img
                preview_label.config(image=img)
            preview.after(10, update_frame)

        def process_ocr(frame):
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            reader = easyocr.Reader(['en'])
            results = reader.readtext(gray)
            if results:
                self.student_name_var.set(results[0][1])
            else:
                messagebox.showwarning("No Text", "No text detected in the image.")

        def auto_capture():
            if countdown[0] > 0:
                countdown_label.config(text=f"Auto-capturing in {countdown[0]}...")
                countdown[0] -= 1
                preview.after(1000, auto_capture)
            else:
                ret, frame = cap.read()
                if ret:
                    cap.release()
                    preview.destroy()
                    threading.Thread(target=process_ocr, args=(frame,), daemon=True).start()

        def cancel():
            cap.release()
            preview.destroy()

        tk.Button(preview, text="❌ Cancel", command=cancel, bg="red", fg="white",
                font=("Comic Sans MS", 12, "bold"), width=10).pack(pady=5)

        update_frame()
        auto_capture()

    
    def show_unregister_window(self):
        unregister_win = tk.Toplevel(self.root)
        unregister_win.title("🗑️ Unregister Student")
        unregister_win.attributes('-fullscreen', True)
        unregister_win.configure(bg="white")

        tk.Label(unregister_win, text="Select Student to Unregister", 
                font=("Comic Sans MS", 16, "bold"), bg="white", fg="red").pack(pady=10)

        student_listbox = tk.Listbox(unregister_win, font=("Comic Sans MS", 20), width=40, height=15)
        student_listbox.pack(pady=10)

        def load_students():
            student_listbox.delete(0, tk.END)
            students = self.controller.fetch_registered_students()
            for student in students:
                student_listbox.insert(tk.END, f"{student['studentname']} ({student['bracelet_id']})")

        load_students()

        def delete_selected():
            selected = student_listbox.curselection()
            if not selected:
                messagebox.showwarning("Oops!", "Please select a student first.")
                return

            student_text = student_listbox.get(selected[0])
            name, bracelet_id = student_text.rsplit(" (", 1)
            bracelet_id = bracelet_id[:-1] 

            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to unregister {name}?")
            if confirm:
                success, msg = self.controller.remove_student(bracelet_id)
                if success:
                    messagebox.showinfo("Deleted", msg)
                    self.refresh_bracelets()
                    load_students()
                else:
                    messagebox.showerror("Error", msg)

        tk.Button(unregister_win, text="🗑️ Delete Selected", command=delete_selected,
                bg="red", fg="white", font=("Comic Sans MS", 14, "bold"), width=20).pack(pady=10)
        
        tk.Button(unregister_win, text="🗑️ Delete All", command=self.delete_all_students,
                bg="red", fg="white", font=("Comic Sans MS", 14, "bold"), width=20).pack(pady=10)

        tk.Button(unregister_win, text="Close", command=unregister_win.destroy,
                bg="gray", fg="white", font=("Comic Sans MS", 12, "bold"), width=15).pack(pady=5)
    
    def clear_text_field(self):
        self.student_name_var.set("")


    def delete_all_students(self):
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete ALL students?")
        if confirm:
            success, message = self.controller.remove_all_students()
            if success:
                messagebox.showinfo("Deleted", message)
                self.refresh_bracelets()
            else:
                messagebox.showwarning("Info", message)



