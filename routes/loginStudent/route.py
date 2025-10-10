import subprocess
from flask import Blueprint, jsonify
import sys
import os
import threading

login_bp = Blueprint("login_bp", __name__)

@login_bp.route("/run-login", methods=["GET", "POST"])
def run_script():
    register_path = r"C:\Thesis\backend\Open-or-Close-Hands-Detection-using-cv2\login_students_MVC\login_gui.py"

    # Verify file exists
    if not os.path.exists(register_path):
        return jsonify({
            "status": "error", 
            "message": f"Script not found at: {register_path}"
        }), 404

    def run_gui():
        """Run GUI in separate thread"""
        try:
            # Import and run the GUI's start function
            sys.path.insert(0, os.path.dirname(register_path))
            import login_gui
            login_gui.start_gui()  # Make sure your login_gui.py has this function
        except Exception as e:
            print(f"❌ Error running GUI: {e}")
    
    # Start GUI in separate thread so Flask doesn't block
    thread = threading.Thread(target=run_gui, daemon=True)
    thread.start()
    
    return jsonify({
        "status": "success", 
        "message": "Login GUI started in background thread"
    })