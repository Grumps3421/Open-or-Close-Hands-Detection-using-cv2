import cv2
import mediapipe as mp

# Set-Up MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Open webcam source
cap = cv2.VideoCapture(0)

# Use MediaPipe Hands
with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
    while True:
        # Read frame from webcam
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)  # Mirror view
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame to find hands
        result = hands.process(rgb_frame)

        # If hands are detected
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # Draw hand landmarks
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get landmark positions
                landmarks = hand_landmarks.landmark
                h, w, _ = frame.shape

                # Check if fingers are open (excluding thumb)
                fingers = []
                tip_ids = [8, 12, 16, 20]

                for tip in tip_ids:
                    if landmarks[tip].y < landmarks[tip - 2].y:
                        fingers.append(1)  # Finger is open
                    else:
                        fingers.append(0)  # Finger is closed

                # Simple check: if 4 or more fingers open, assume open hand
                
                if fingers == [0, 1, 0, 0]: #Middle Finger
                    hand_status = "Inappropriate Action Detected"
                elif sum(fingers) >= 4:
                    hand_status = "Option A = Open"
                else:
                    hand_status = "Option B = Close"

                # Get wrist position to display text
                x = int(landmarks[0].x * w)
                y = int(landmarks[0].y * h) - 20

                # Show status on the frame
                cv2.putText(frame, hand_status, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Show the video
        cv2.imshow("Open or Close Hands", frame)

        # Press q to exit program
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
