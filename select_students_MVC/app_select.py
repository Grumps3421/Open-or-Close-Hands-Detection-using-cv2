import tkinter as tk
from controller import AlphaBotController

def main():
    root = tk.Tk()
    app = AlphaBotController(root)
    root.mainloop()

if __name__ == "__main__":
    main()
