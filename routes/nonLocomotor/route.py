
from flask import Blueprint, jsonify


nonLocomotor_bp = Blueprint("nonLocomotor_bp", __name__)

@nonLocomotor_bp.route("/nonLocomotor", methods=["GET", "POST"])
def nonLocomotor():
    return jsonify({"status": "success", "message": "Non Locomotor here!"})
