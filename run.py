from hand_detector import HandStatusDetector
import cv2

def main():
    detector = HandStatusDetector()
    cap = cv2.VideoCapture(0)

    while True:
        ret,frame = cap.read()
        if not ret:
            break
        frame = detector.detector_frame(frame) 
        cv2.imshow("Hand Status Detection: ", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    detector.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
