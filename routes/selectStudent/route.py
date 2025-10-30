import os
import subprocess
from flask import Blueprint, jsonify
import sys

selectStudent_bp = Blueprint("selectStudent_bp", __name__)

@selectStudent_bp.route("/run-selectStudent", methods=["GET", "POST"])
def run_selectStudent():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # current directory of this file
    register_path = os.path.join(base_dir, "../../select_students_MVC/app_select.py")
    register_path = os.path.normpath(register_path)  # clean up path
    python_executable = sys.executable
    subprocess.Popen([python_executable, register_path])
    return jsonify({"status": "success", "message": "Select Player script started"})
    