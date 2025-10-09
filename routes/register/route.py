import subprocess
import threading
from flask import Blueprint, Response

register_bp = Blueprint('register_bp' , __name__)

@register_bp.route("/run-script" , methods=["POST" , "GET"])
def GUIRegister():
    register_path = "C:\\Programming\\Thesis\\register_students_MVC\\app_register.py"
    subprocess.Popen(["python", register_path])
    return Response(status=204) 