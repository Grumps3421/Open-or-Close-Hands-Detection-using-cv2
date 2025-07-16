import cv2
import time
from hand_detector import HandStatusDetector

def check_answer():
    cap = cv2.VideoCapture(0)
    detector = HandStatusDetector()

    print("⌛ Waiting 2 seconds before detection...")
    time.sleep(2)  # Delay before starting detection

    result = "none"

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error: Could not access webcam.")
            break

        frame, status = detector.detector_frame(frame)

        cv2.imshow("Hand Detection", frame)

        if status in ["correct", "wrong"]:
            print(f"✅ Detected hand status: {status}")
            result = status
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("🛑 Quit manually.")
            break

    cap.release()
    detector.release()
    cv2.destroyAllWindows()
    return result

# ✅ Optional: Run directly to test hand detection
if __name__ == "__main__":
    status = check_answer()
    if status == "correct":
        print("🎉 Answer is correct!")
    elif status == "wrong":
        print("❌ Answer is wrong!")
    else:
        print("⚠️ No valid hand gesture detected.")
