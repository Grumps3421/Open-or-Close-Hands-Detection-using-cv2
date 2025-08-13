from student_detector import StudentDetector

def main():
    model_path = 'C:\\Thesis\\backend\\Open-or-Close-Hands-Detection-using-cv2\\alphabotFunction\\my_model_final\\my_model.pt'
    threshold = 0.7

    detector = StudentDetector(model_path=model_path, thresh=threshold)
    detector.detect()

if __name__ == "__main__":
    main()
