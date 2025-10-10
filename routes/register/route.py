import subprocess
from flask import Blueprint, jsonify
import sys  # add this

register_bp = Blueprint("register_bp", __name__)

@register_bp.route("/run-script", methods=["GET", "POST"])
def run_script():
    register_path = r"C:\Thesis\backend\Open-or-Close-Hands-Detection-using-cv2\register_students_MVC\app_register.py"
    
    # Use the current Python interpreter (from .venv)
    python_executable = sys.executable
    
    subprocess.Popen([python_executable, register_path])
    
    return jsonify({"status": "success", "message": "Register script started"})
