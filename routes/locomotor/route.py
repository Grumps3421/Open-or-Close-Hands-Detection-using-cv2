from flask import Blueprint, jsonify
from bot_movements.serial_handler import send_command

locomotor_bp = Blueprint("locomotor_bp", __name__)

@locomotor_bp.route("/locomotor", methods=["GET" , "POST"])
def locomotor():
    try:
        # Command to send to Arduino
        command = "locomotor"

        # Send via serial communication
        result = send_command(command)

        # Return success response
        return jsonify({
            "status": "success",
            "message": f"Command '{command}' sent to Arduino.",
            "result": result
        })

    except Exception as e:
        # Return error response
        return jsonify({
            "status": "error",
            "message": f"Failed to send command: {str(e)}"
        })