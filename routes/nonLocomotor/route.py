from flask import Blueprint, jsonify
from bot_movements.serial_handler import send_command

nonLocomotor_bp = Blueprint("nonLocomotor_bp", __name__)

@nonLocomotor_bp.route("/nonLocomotor", methods=["GET"])
def nonLocomotor():
    try:
        # Command to send to Arduino
        command = "nonlocomotor"

        # Send via serial
        result = send_command(command)

        # Response message
        return jsonify({
            "status": "success",
            "message": f"Command '{command}' sent to Arduino.",
            "result": result
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to send command: {str(e)}"
        })
