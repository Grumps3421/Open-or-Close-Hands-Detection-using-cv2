from hand_detector import HandStatusDetector
import cv2
from flask import Flask, Response, render_template_string , request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

from hand_detector import HandStatusDetector
import cv2
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allows request from Next.js (localhost:3000)


@app.route("/nungay", methods=["POST"])
def main():
    data = request.json
    choice = data.get("choice")

    print("Received choice from Next.js:", choice)

    detector = HandStatusDetector()
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = detector.detector_frame(frame)
        cv2.imshow("Hand Status Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    detector.release()
    cv2.destroyAllWindows()

    return (
        jsonify({
            "status": "success",
            "message": f"Started hand detection for choice: {choice}"
        }), 200
    ) if choice else (
        jsonify({
            "status": "error",
            "message": "No choice provided"
        }), 400
    )


@app.route("/soco")
def soco():
    return "Hello Soco!!!"

@app.route("/", methods=["POST"])
def receive_choice():
    data = request.json
    print("Received choice from Next.js:", data)
    return jsonify({"status": "received", "received_choice": data})


if __name__ == "__main__":
    app.run(debug=True)
