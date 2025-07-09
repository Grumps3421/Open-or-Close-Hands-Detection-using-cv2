
import cv2
import mediapipe as mp

class HandStatusDetector:
    def __init__(this, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7):
        this.mp_hands = mp.solutions.hands
        this.mp_drawing = mp.solutions.drawing_utils
        this.hands = this.mp_hands.Hands(
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def detector_frame(this, frame):
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = this.hands.process(rgb_frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                this.mp_drawing.draw_landmarks(frame, hand_landmarks, this.mp_hands.HAND_CONNECTIONS)

                landmarks = hand_landmarks.landmark
                h, w, _ = frame.shape

                fingers = []
                tip_ids = [8, 12, 16, 20]

                for tip in tip_ids:
                    if landmarks[tip].y < landmarks[tip - 2].y:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                if fingers == [0, 1, 0, 0]:
                    hand_status = "Inappropriate Action"
                elif sum(fingers) >= 4:
                    hand_status = "Open"
                else:
                    hand_status = "Close"

                x = int(landmarks[0].x * w)
                y = int(landmarks[0].y * h) - 20

                cv2.putText(frame, hand_status, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return frame

    def release(self):
        self.hands.close()
