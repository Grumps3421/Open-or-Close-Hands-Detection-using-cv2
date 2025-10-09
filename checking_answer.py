import time
from alphabotFunction.YoLo.my_model_final.yolo_detect import detect_student_and_hand

# ✅ Model configuration
MODEL_PATH = r"C:\THESIS\backend\Open-or-Close-Hands-Detection-using-cv2\alphabotFunction\YoLo\my_model_final\bracelet_identification_ncnn_model"
THRESHOLD = 0.7


# ===========================================================
# FUNCTION USED BY /close ROUTE
# ===========================================================
def check_answer():
    """
    Logic for /close route:
    - 'Close' hand = correct
    - 'Open' hand = wrong
    """
    print("⌛ Waiting 2 seconds before detection...")
    time.sleep(2)

    # Run YOLO + MediaPipe detection
    student_name, hand_status = detect_student_and_hand(MODEL_PATH, THRESHOLD)

    # Default JSON
    result_data = {
        "detect": "none",
        "student name": None,
        "bracelet_id": None,
        "hand_status": None,
    }

    # If detection failed
    if not student_name or not hand_status:
        print("❌ No detection found.")
        return result_data

    # ✅ Normal logic (for close)
    if hand_status.lower() == "close":
        result = "correct"
    elif hand_status.lower() == "open":
        result = "wrong"
    else:
        result = "none"

    result_data = {
        "detect": result,
        "student name": student_name,
        "bracelet_id": student_name,  # same as name if not mapped yet
        "hand_status": hand_status,
    }

    print(f"✅ [CLOSE] Detected: {student_name} | Hand: {hand_status} → {result}")
    return result_data


# ===========================================================
# FUNCTION USED BY /open ROUTE
# ===========================================================
def check_answer_result():
    """
    Logic for /open route:
    - 'Open' hand = correct
    - 'Close' hand = wrong
    """
    print("⌛ Waiting 2 seconds before detection...")
    time.sleep(2)

    # Run YOLO + MediaPipe detection
    student_name, hand_status = detect_student_and_hand(MODEL_PATH, THRESHOLD)

    # Default JSON
    result_data = {
        "detect": "none",
        "student name": None,
        "bracelet_id": None,
        "hand_status": None,
    }

    # If detection failed
    if not student_name or not hand_status:
        print("❌ No detection found.")
        return result_data

    # ✅ Reversed logic (for open)
    if hand_status.lower() == "open":
        result = "correct"
    elif hand_status.lower() == "close":
        result = "wrong"
    else:
        result = "none"

    result_data = {
        "detect": result,
        "student name": student_name,
        "bracelet_id": student_name,
        "hand_status": hand_status,
    }

    print(f"✅ [OPEN] Detected: {student_name} | Hand: {hand_status} → {result}")
    return result_data


# ===========================================================
# OPTIONAL TESTING
# ===========================================================
if __name__ == "__main__":
    print("Testing both functions...\n")

    close_result = check_answer()
    print("\nFinal result of check_answer (/close):", close_result)

    open_result = check_answer_result()
    print("\nFinal result of check_answer_result (/open):", open_result)
