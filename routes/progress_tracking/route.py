import subprocess

from flask import Blueprint, jsonify


progressTracking_bp = Blueprint("progressTracking_bp", __name__)

@progressTracking_bp.route("/run-script2", methods=["GET", "POST"])
def progressTracking():
    register_path = "C:\\Thesis\\backend\\Open-or-Close-Hands-Detection-using-cv2\\progress_students_MVC\\app_progress.py"
    subprocess.Popen(["python", register_path])
    return jsonify({"status": "success", "message": "Register script started"})
