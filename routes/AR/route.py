from flask import Blueprint, jsonify


AR_bp = Blueprint("AR_bp", __name__)

@AR_bp.route("/", methods=["GET", "POST"])
def run_AR():
    print("Hello AR Route")
    return jsonify({"message":"Running the AR"}) , 200