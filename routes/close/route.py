from flask import Blueprint  , request, jsonify
from checking_answer import check_answer

close_bp = Blueprint("close_bp" , __name__)

@close_bp.route("/close", methods=["POST" , "GET"])
def detect_hand_status():
    data = request.json
    choice = data.get("choice")

    print("📩 Received choice from Next.js:", choice)

    # Check if "choice" was provided
    if not choice:
        return jsonify({
            "status": "error",
            "message": "❌ No choice provided"
        }), 400

    # Run webcam hand detection
    result = check_answer()
    print(f"🖐️ Hand detection result: {result}")

    # Return success if gesture is valid
    if result in ["correct", "wrong"]:
        return jsonify({
            "status": "success",
            "message": f"✅ Detected: {result}",
            "detected": result,
            "choice": choice
        }), 200

    # Otherwise return a "Conflict" (409) for no valid hand gesture
    return jsonify({
        "status": "no-gesture",
        "message": "⚠️ No valid hand gesture detected.",
        "detected": result,
        "choice": choice
    }), 409