# checking_answer.py
import cv2
import time
from alphabotFunction.student_detector import StudentDetector, load_class_name_map

model_path = 'C:\\Thesis\\backend\\Open-or-Close-Hands-Detection-using-cv2\\alphabotFunction\\my_model_final\\my_model.pt'
threshold = 0.7


def check_answer():
    cap = cv2.VideoCapture(0)
    class_name_map = load_class_name_map()
    detector = StudentDetector(model_path=model_path, thresh=threshold)
    detector.class_name_map = class_name_map

    print("⌛ Waiting 2 seconds before detection...")
    time.sleep(2)

    result = "none"

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error: Could not access webcam.")
            break

        frame, detected_students = detector.detect_frame(frame)

        if detected_students:
            student = detected_students[0]  # ✅ only index 0
            student_name = student["name"]
            bracelet_id = student.get("bracelet_id", "Unknown")
            hand_status = student["hand_status"]

            # JSON FILE
            result_data = {
                "detected": "none",
                "student name": None,
                "bracelet_id": None,
                "hand_status": None,
            }

            has_bracelet = student_name != "No bracelet detected"
            has_hand_status = hand_status in ["Open", "Close"]

            if has_bracelet and has_hand_status:
                if hand_status == "Close":
                    result = "correct"
                else:
                    result = "wrong"

                print(f"✅ Detected bracelet + hand status: {hand_status} → {result}")
                print(f"student name : {student_name}")
                print(f"hand status  : {hand_status}")
                result_data = {
                    "detect": result,
                    "student name": student_name,
                    "bracelet_id": bracelet_id,
                    "hand_status": hand_status
                }
                break

        else:
            print("No valid detection")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("🛑 Quit manually.")
            break

    cap.release()
    detector.release()
    cv2.destroyAllWindows()
    return result_data


def check_answer_result():

    cap = cv2.VideoCapture(0)
    class_name_map = load_class_name_map()
    detector = StudentDetector(model_path=model_path, thresh=threshold)
    detector.class_name_map = class_name_map

    print("⌛ Waiting 2 seconds before detection...")
    time.sleep(2)

    result = "none"

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error: Could not access webcam.")
            break

        frame, detected_students = detector.detect_frame(frame)

        if detected_students:
            student = detected_students[0]  # ✅ only index 0
            student_name = student["name"]
            bracelet_id = student.get("bracelet_id", "Unknown")
            hand_status = student["hand_status"]

            #JSON file return
            result_data = {
                "detected": "none",
                "student name": None,
                "bracelet_id": None,
                "hand_status": None,
            }

            has_bracelet = student_name != "No bracelet detected"
            has_hand_status = hand_status in ["Open", "Close"]

            if has_bracelet and has_hand_status:
                if hand_status == "Close":
                    result = "wrong"
                else:
                    result = "correct"

                print(f"✅ Detected bracelet + hand status: {hand_status} → {result}")
                print(f"student name : {student_name}")
                print(f"hand status  : {hand_status}")

                result_data = {
                    "detect" : result ,
                    "student name": student_name,
                    "bracelet_id": bracelet_id,
                    "hand_status": hand_status
                }
                break


        cv2.imshow("Hand Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("🛑 Quit manually.")
            break

    cap.release()
    detector.release()
    cv2.destroyAllWindows()
    return result_data


# ✅ Optional: Run directly to test
if __name__ == "__main__":
    check_answer = check_answer()
    check_answer_result = check_answer_result()
    print("Final result of check answer:", check_answer)
    print("Final result of Checking_answer_result: " , check_answer_result)
