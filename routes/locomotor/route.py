
from flask import Blueprint, jsonify


locomotor_bp = Blueprint("locomotor_bp", __name__)

@locomotor_bp.route("/locomotor", methods=["GET", "POST"])
def locomotor():
    return jsonify({"status": "success", "message": "Locomotor here!"})
