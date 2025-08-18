#checking_answer.py
import cv2
import time
from alphabotFunction.main import main
from alphabotFunction.student_detector import StudentDetector , load_class_name_map

model_path = 'C:\\Thesis\\backend\\Open-or-Close-Hands-Detection-using-cv2\\alphabotFunction\\my_model_final\\my_model.pt'
threshold = 0.7


def check_answer():
    cap = cv2.VideoCapture(0)
    detector = StudentDetector(model_path=model_path, thresh=threshold)
    # 🔹 Load fresh bracelet mappings once for this detection run
    class_name_map = load_class_name_map()
    detector = StudentDetector(model_path=model_path, thresh=threshold)
    detector.class_name_map = class_name_map  # attach para magamit sa detect_frame

    print("⌛ Waiting 2 seconds before detection...")
    time.sleep(2)

    result = "none"

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error: Could not access webcam.")
            break

        frame, student_names, hand_status = detector.detect_frame(frame)

        has_bracelet = student_names and "No bracelet detected" not in student_names
        has_hand_status = hand_status in ["Open", "Close"]

        if has_bracelet and has_hand_status:
            for student in student_names:
                print(f"{student} | hand Status : {hand_status}")

            if hand_status == "Close":
                result = "correct"
            else:
                result = "wrong"

            print(f"✅ Detected bracelet + hand status: {hand_status} → {result}")
            break
        else:
            print(f"No valid detection | Bracelet: {has_bracelet} | Hand status: {hand_status}")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("🛑 Quit manually.")
            break

    cap.release()
    detector.release()
    cv2.destroyAllWindows()
    return result


def check_answer_result():
    cap = cv2.VideoCapture(0)
    detector = StudentDetector(model_path=model_path, thresh=threshold)
    # 🔹 Load fresh bracelet mappings once for this detection run
    class_name_map = load_class_name_map()
    detector = StudentDetector(model_path=model_path, thresh=threshold)
    detector.class_name_map = class_name_map  # attach para magamit sa detect_frame

    print("⌛ Waiting 2 seconds before detection...")
    time.sleep(2)

    result = "none"

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error: Could not access webcam.")
            break

        frame, student_names, hand_status = detector.detect_frame(frame)

        has_bracelet = student_names and "No bracelet detected" not in student_names
        has_hand_status = hand_status in ["Open", "Close"]

        if has_bracelet:
            for student in student_names:
                print(f"{student} | hand Status : {hand_status}")

        cv2.imshow("Hand Detection", frame)

        if has_bracelet and has_hand_status:
            if hand_status == "Open":
                result = "correct"
            else:
                result = "wrong"
            print(f"✅ Detected bracelet + hand status: {hand_status} → {result}")
            break
        else:
            print(f"No valid detection | Bracelet: {has_bracelet} | Hand status: {hand_status}")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("🛑 Quit manually.")
            break

    cap.release()
    detector.release()
    cv2.destroyAllWindows()
    return result


# ✅ Optional: Run directly to test
if __name__ == "__main__":
    status = check_answer()
    print(status)
