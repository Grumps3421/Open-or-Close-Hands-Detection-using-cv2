import cv2
import mediapipe as mp
import math


class HandStatusDetector:
    def __init__(self, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def distance(self, a, b):
        return math.hypot(b.x - a.x, b.y - a.y)

    def detector_frame(self, frame):
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb_frame)

        hand_status = "none"  # Default if nothing detected

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                landmarks = hand_landmarks.landmark
                h, w, _ = frame.shape

                palm_base = landmarks[0]
                fingers = []

                # Thumb
                if landmarks[4].x > landmarks[3].x:
                    fingers.append(1)
                else:
                    fingers.append(0)

                # Other fingers
                for tip_id in [8, 12, 16, 20]:
                    mcp_id = tip_id - 3
                    tip_dist = self.distance(landmarks[tip_id], palm_base)
                    mcp_dist = self.distance(landmarks[mcp_id], palm_base)
                    if tip_dist > mcp_dist:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                # Hand gesture logic
                if fingers == [0, 1, 0, 0]:
                    display_text = "Inappropriate Action"
                elif sum(fingers) >= 4:
                    hand_status = "wrong"
                    display_text = "Close"
                else:
                    hand_status = "correct"
                    display_text = "Open"

                # Draw text
                x = int(landmarks[0].x * w)
                y = int(landmarks[0].y * h) - 20
                cv2.putText(frame, display_text, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 0), 2)

        return frame, hand_status  # ✅ Now returns both

    def release(self):
        self.hands.close()
