import cv2
import time
from alphabotFunction.student_detector import StudentDetector, load_class_name_map

# ✅ Use raw string (avoid double escaping \\)
model_path = r"C:\Thesis\backend\Open-or-Close-Hands-Detection-using-cv2\alphabotFunction\my_model_final\my_model.pt"
threshold = 0.7


def check_answer():
    """
    Detect if a student's hand is CLOSE → 'correct'
    or OPEN → 'wrong'
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Cannot open webcam.")
        return {"detect": "error", "student_name": None, "bracelet_id": None, "hand_status": None}

    class_name_map = load_class_name_map()
    detector = StudentDetector(model_path=model_path, thresh=threshold)
    detector.class_name_map = class_name_map

    print("⌛ Waiting 2 seconds before detection...")
    time.sleep(2)

    result_data = {
        "detect": "none",
        "student_name": None,
        "bracelet_id": None,
        "hand_status": None,
    }

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error: Could not access webcam.")
            break

        frame, detected_students = detector.detect_frame(frame)

        if detected_students:
            student = detected_students[0]  # ✅ Only the first student
            student_name = student["name"]
            bracelet_id = student.get("bracelet_id", "Unknown")
            hand_status = student["hand_status"]

            has_bracelet = student_name != "No bracelet detected"
            has_hand_status = hand_status in ["Open", "Close"]

            if has_bracelet and has_hand_status:
                # ✅ For check_answer: "Close" = correct
                result = "correct" if hand_status == "Close" else "wrong"

                print(f"✅ Detected bracelet + hand status: {hand_status} → {result}")
                print(f"👤 Student name : {student_name}")
                print(f"🖐️ Hand status  : {hand_status}")

                result_data = {
                    "detect": result,
                    "student_name": student_name,
                    "bracelet_id": bracelet_id,
                    "hand_status": hand_status,
                }
                break

        else:
            print("🔍 No valid detection")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("🛑 Quit manually.")
            break

    cap.release()
    detector.release()
    cv2.destroyAllWindows()
    return result_data


def check_answer_result():
    """
    Detect if a student's hand is OPEN → 'correct'
    or CLOSE → 'wrong'
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Cannot open webcam.")
        return {"detect": "error", "student_name": None, "bracelet_id": None, "hand_status": None}

    class_name_map = load_class_name_map()
    detector = StudentDetector(model_path=model_path, thresh=threshold)
    detector.class_name_map = class_name_map

    print("⌛ Waiting 2 seconds before detection...")
    time.sleep(2)

    result_data = {
        "detect": "none",
        "student_name": None,
        "bracelet_id": None,
        "hand_status": None,
    }

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error: Could not access webcam.")
            break

        frame, detected_students = detector.detect_frame(frame)

        if detected_students:
            student = detected_students[0]
            student_name = student["name"]
            bracelet_id = student.get("bracelet_id", "Unknown")
            hand_status = student["hand_status"]

            has_bracelet = student_name != "No bracelet detected"
            has_hand_status = hand_status in ["Open", "Close"]

            if has_bracelet and has_hand_status:
                # ✅ For check_answer_result: "Open" = correct
                result = "correct" if hand_status == "Open" else "wrong"

                print(f"✅ Detected bracelet + hand status: {hand_status} → {result}")
                print(f"👤 Student name : {student_name}")
                print(f"🖐️ Hand status  : {hand_status}")

                result_data = {
                    "detect": result,
                    "student_name": student_name,
                    "bracelet_id": bracelet_id,
                    "hand_status": hand_status,
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


# ✅ Optional direct test
if __name__ == "__main__":
    print("🔹 Running check_answer()...")
    res1 = check_answer()
    print("📊 Result 1:", res1)

    print("\n🔹 Running check_answer_result()...")
    res2 = check_answer_result()
    print("📊 Result 2:", res2)
