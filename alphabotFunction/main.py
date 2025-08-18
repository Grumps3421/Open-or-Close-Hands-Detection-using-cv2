from alphabotFunction.student_detector import StudentDetector  # adjust import if needed

def main():
    model_path = 'C:\\Thesis\\backend\\Open-or-Close-Hands-Detection-using-cv2\\alphabotFunction\\my_model_final\\my_model.pt'
    threshold = 0.7

    detector = StudentDetector(model_path=model_path, thresh=threshold)
    return detector  # <-- RETURN the object instead of calling detect here

if __name__ == "__main__":
    detector = main()
    detector.detect()  # call detect here only if running standalone
