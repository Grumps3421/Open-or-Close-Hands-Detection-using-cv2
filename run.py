from flask import Flask, request, jsonify
from flask_cors import CORS
from checking_answer import check_answer , check_answer_result # Your hand detection logic
import threading

app = Flask(__name__)
CORS(app)

@app.route("/close", methods=["POST"])
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


@app.route("/", methods=["POST"])
def receive_choice():
    data = request.json
    print("📩 Received choice payload:", data)
    return jsonify({
        "status": "received",
        "received_choice": data
    })



@app.route("/open" , methods=["GET" , "POST"])
def hand_status_reverse():
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
    result = check_answer_result()
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

@app.route("/register" , methods=["POST" , "GET"])
def GUIRegister():
    from alphabotFunction.register import launch_registration_gui
    # I-check muna kung may bukas nang GUI
    if not any(thread.name == "registration_gui" for thread in threading.enumerate()):
        t = threading.Thread(target=launch_registration_gui, name="registration_gui")
        t.daemon = True
        t.start()
        return jsonify({"status": "GUI Launched"})
    else:
        return jsonify({"status": "Already Running"})
    return jsonify({"status" : "GUI Launched"})


if __name__ == "__main__":
    app.run(debug=True)




