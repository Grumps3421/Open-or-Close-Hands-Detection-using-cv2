from flask import Blueprint  , request, jsonify
import threading
from alphabotFunction.register import launch_registration_gui

register_bp = Blueprint('register_bp' , __name__)

@register_bp.route("/register" , methods=["POST" , "GET"])
def GUIRegister():
    # I-check muna kung may bukas nang GUI
    if not any(thread.name == "registration_gui" for thread in threading.enumerate()):
        t = threading.Thread(target=launch_registration_gui, name="registration_gui")
        t.daemon = True
        t.start()
        return jsonify({"status": "GUI Launched"})
    else:
        return jsonify({"status": "Already Running"})
    return jsonify({"status" : "GUI Launched"})