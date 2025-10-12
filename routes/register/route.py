import os
import subprocess
from flask import Blueprint, jsonify
import sys

register_bp = Blueprint("register_bp", __name__)

@register_bp.route("/run-script", methods=["GET", "POST"])
def run_script():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # current directory of this file
    register_path = os.path.join(base_dir, "../../register_students_MVC/app_register.py")
    register_path = os.path.normpath(register_path)  # clean up path
    
    python_executable = sys.executable
    subprocess.Popen([python_executable, register_path])
    
    return jsonify({"status": "success", "message": "Register script started"})
