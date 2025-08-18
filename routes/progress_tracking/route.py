from flask import Blueprint, request, jsonify
import threading
from alphabotFunction.progress_tracking import launch_progressTracking_gui

progressTracking_bp = Blueprint("progressTracking_bp", __name__)

@progressTracking_bp.route("/progressTracking", methods=["GET", "POST"])
def progressTracking():
    # Check if thread already running
    if not any(thread.name == "progressTracking_gui" for thread in threading.enumerate()):
        t = threading.Thread(target=launch_progressTracking_gui, name="progressTracking_gui")
        t.daemon = True
        t.start()
        return jsonify({"status": "GUI Launched"})
    else:
        return jsonify({"status": "Already Running"})
