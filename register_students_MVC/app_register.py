import tkinter as tk
from controller import BraceletController
from ui import BraceletView


def main():
    root = tk.Tk()
    controller = BraceletController(root)
    view = BraceletView(root, controller)
    
    bracelet_colors = controller.get_bracelet_colors()
    taken_bracelets = controller.get_taken_bracelets()
    view.load_bracelet_buttons(bracelet_colors, taken_bracelets)

    root.mainloop()

if __name__ == "__main__":
    main()
