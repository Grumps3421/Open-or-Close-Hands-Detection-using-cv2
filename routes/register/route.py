import subprocess
from flask import Blueprint, jsonify

register_bp = Blueprint("register_bp", __name__)

@register_bp.route("/run-script", methods=["GET", "POST"])
def run_script():
    register_path = r"C:\Thesis\backend\Open-or-Close-Hands-Detection-using-cv2\register_students_MVC\app_register.py"
    subprocess.Popen(["python", register_path])
    return jsonify({"status": "success", "message": "Register script started"})
