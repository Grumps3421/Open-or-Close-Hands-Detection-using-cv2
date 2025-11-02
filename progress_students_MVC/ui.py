import tkinter as tk
from tkinter import ttk, messagebox

class AlphaBotView:
    def __init__(self, controller):
        self.controller = controller

        # --- Main Window ---
        self.root = tk.Tk()
        self.root.title("AlphaBot Report Tracker 🧸")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="#FFF5CC")

        tk.Label(self.root, text="🤖 AlphaBot Report Tracker 🤖",
                 font=("Comic Sans MS", 36, "bold"),
                 bg="#FFF5CC", fg="#333").pack(pady=30)

        self.button_frame = tk.Frame(self.root, bg="#FFF5CC")
        self.button_frame.pack(pady=10)

        self.control_frame = tk.Frame(self.root, bg="#FFF5CC")
        self.control_frame.pack(pady=30)

    # --- Render student buttons ---
    def render_main_buttons(self, registered):
        student_colors = [
            "#FF0000", "#808080", "#75FF33", "#FFA500",
            "#D633FF", "#00BFFF", "#FFFFFF", "#40E0D0",
            "#FFB6C1", "#87CEEB", "#FF13F0", "#FC8EAC"
        ]

        for i in range(12):
            bracelet_id = f"Student{i+1}"
            studentname = registered.get(bracelet_id, "Unregistered")
            color = student_colors[i % len(student_colors)]

            if studentname == "Unregistered":
                color = "#D3D3D3"
                state = "disabled"
            else:
                state = "normal"

            btn = tk.Button(self.button_frame,
                            text=f"🎓 {bracelet_id}\n{studentname}",
                            width=18, height=4,
                            bg=color, fg="black",
                            font=("Comic Sans MS", 14, "bold"),
                            relief="raised", bd=4,
                            state=state,
                            command=lambda b=bracelet_id: self.controller.open_progress(b))
            btn.grid(row=i // 4, column=i % 4, padx=20, pady=20)

        # --- Control Buttons ---
        tk.Button(self.control_frame, text="🚪 Exit",
                  command=self.root.destroy,
                  bg="#FF6B6B", fg="white",
                  font=("Comic Sans MS", 14, "bold"),
                  relief="raised", width=12, height=2).grid(row=0, column=0, padx=40)

        tk.Button(self.control_frame, text="🏅 Leaderboard",
                  command=self.controller.open_leaderboard,
                  bg="#90EE90", fg="black",
                  font=("Comic Sans MS", 14, "bold"),
                  relief="raised", width=16, height=2).grid(row=0, column=1, padx=40)

    # --- Warning message ---
    def show_message(self, title, text):
        messagebox.showwarning(title, text)

    # --- Start Tkinter mainloop ---
    def start_mainloop(self):
        self.root.mainloop()

    # --- Generic function to create a new window ---
    def create_window(self, title, bg="#FFF8E7"):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.attributes('-fullscreen', True)
        window.configure(bg=bg)
        return window

    # --- Generic content frame inside a window ---
    def create_content_frame(self, parent):
        frame = tk.Frame(parent, bg="#FFF8E7")
        frame.pack(fill="both", expand=True, padx=30, pady=10)
        return frame

    # --- Create Treeview for questions/leaderboard ---
    def create_treeview(self, parent, columns, headings, rowheight=40, height=10):
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Comic Sans MS", 16, "bold"))
        style.configure("Treeview", font=("Comic Sans MS", 20), rowheight=rowheight)

        tree = ttk.Treeview(parent, columns=columns, show="headings", height=height)
        for col, head in zip(columns, headings):
            tree.heading(col, text=head)
            # Preserve original widths
            if col == "Question":
                tree.column(col, width=400, anchor="w")
            elif col == "Answer":
                tree.column(col, width=200, anchor="center")
            else:
                tree.column(col, width=100, anchor="center")
        tree.pack(padx=20, pady=10, fill="both", expand=True)
        return tree

    # --- Create a label exactly as in procedural code ---
    def create_label(self, parent, text, font=("Comic Sans MS", 18, "bold"), fg="#333", bg="#FFF8E7", pady=10):
        label = tk.Label(parent, text=text, font=font, fg=fg, bg=bg)
        label.pack(pady=pady)
        return label

    # --- Create a button exactly as in procedural code ---
    def create_button(self, parent, text, command, width=18, height=3,
                      bg="#A3D8F4", fg="#333", font=("Comic Sans MS", 14, "bold")):
        btn = tk.Button(parent, text=text, command=command,
                        width=width, height=height,
                        bg=bg, fg=fg, font=font,
                        relief="raised", bd=4)
        btn.pack(padx=10, pady=10)
        return btn
