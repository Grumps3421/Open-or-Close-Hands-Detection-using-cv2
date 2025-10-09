import subprocess

from flask import Blueprint, Response


progressTracking_bp = Blueprint("progressTracking_bp", __name__)

@progressTracking_bp.route("/run-script2", methods=["GET", "POST"])
def progressTracking():
    register_path = "C:\\Programming\\Thesis\\progress_students_MVC\\app_progress.py"
    subprocess.Popen(["python", register_path])
    return Response(status=204)