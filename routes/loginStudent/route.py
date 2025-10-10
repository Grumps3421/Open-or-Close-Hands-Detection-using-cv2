import subprocess
from flask import Blueprint, jsonify
import sys

login_bp = Blueprint("login_bp", __name__)

@login_bp.route("/run-login", methods=["GET", "POST"])
def run_script():
    register_path = r"C:\Thesis\backend\Open-or-Close-Hands-Detection-using-cv2\login_students_MVC\login_gui.py"

    # Use the Python interpreter of the current virtual environment
    python_executable = sys.executable
    subprocess.Popen([python_executable, register_path])
    
    return jsonify({"status": "success", "message": "Login script started"})
