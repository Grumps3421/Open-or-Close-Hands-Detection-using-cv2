from flask import Blueprint  , request, jsonify

main_bp = Blueprint('main' , __name__)

@main_bp.route("/", methods=["POST"])
def receive_choice():
    data = request.json
    print("📩 Received choice payload:", data)
    return jsonify({
        "status": "received",
        "received_choice": data
    })