from flask import Blueprint, jsonify
import cv2
import mediapipe as mp
import pyautogui
import time
import numpy as np
from collections import deque
import threading

AR_bp = Blueprint("AR_bp", __name__)

class ARMouseController:
    def __init__(self):
        self.running = False
        self.thread = None
        
    def start(self):
        if self.running:
            print("⚠️ AR is already running.")
            return {"status": "already_running"}
        
        print("🎬 Starting AR tracking...")
        self.running = True
        self.thread = threading.Thread(target=self._run_tracking, daemon=True)
        self.thread.start()
        return {"status": "started"}
    
    def stop(self):
        if not self.running:
            print("⚠️ AR is not running, no need to stop.")
            return {"status": "not_running"}
        
        print("🛑 Stopping AR tracking...")
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        
        print("✅ AR stopped successfully.")
        return {"status": "stopped"}
    
    def _run_tracking(self):
        # Initialize video capture and hand detection
        cap = cv2.VideoCapture(0)  # Use index 0 for primary/built-in camera
        hand_detector = mp.solutions.hands.Hands(
            min_detection_confidence=0.7, 
            min_tracking_confidence=0.7, 
            max_num_hands=1
        )
        screen_width, screen_height = pyautogui.size()

        # ----- CURSOR SMOOTHING -----
        alpha = 0.8  # Increased for more responsiveness
        prev_x, prev_y = screen_width // 2, screen_height // 2

        # ----- IMPROVED CLICK DETECTION -----
        click_cooldown = 0.5  # Increased cooldown
        last_click_time = 0
        click_threshold = 35  # Stricter threshold
        release_threshold = 50  # Clear separation for release
        
        # State machine for clicks
        IDLE = 0
        PINCHING = 1
        CLICKED = 2
        click_state = IDLE
        
        # History tracking
        finger_distance_history = deque(maxlen=7)
        stable_pinch_frames = 0
        required_stable_frames = 3  # Need consistent pinch before click
        
        # ----- CURSOR MOTION TRACKING -----
        motion_buffer_size = 2  # Reduced buffer for faster response
        x_buffer = deque([prev_x] * motion_buffer_size, maxlen=motion_buffer_size)
        y_buffer = deque([prev_y] * motion_buffer_size, maxlen=motion_buffer_size)
        buffer_weights = np.array([0.3, 0.7])  # Weight recent positions more
        buffer_weights = buffer_weights / np.sum(buffer_weights)

        # PyAutoGUI settings
        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = False

        # Frame rate control
        frame_time = 0
        fps_cap = 120

        try:
            while self.running:
                current_time = time.time()
                if current_time - frame_time < 1.0 / fps_cap:
                    continue
                frame_time = current_time

                ret, frame = cap.read()
                if not ret or frame is None:
                    continue

                frame = cv2.flip(frame, 1)
                frame_height, frame_width, _ = frame.shape
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                output = hand_detector.process(rgb_frame)
                hands = output.multi_hand_landmarks

                if hands:
                    hand = hands[0]
                    landmarks = hand.landmark

                    if len(landmarks) >= 21:
                        # ----- CURSOR CONTROL: THUMB TIP -----
                        thumb_tip = landmarks[4]
                        x = int(thumb_tip.x * frame_width)
                        y = int(thumb_tip.y * frame_height)

                        cursor_x = np.interp(x, [50, frame_width - 50], [0, screen_width])
                        cursor_y = np.interp(y, [50, frame_height - 50], [0, screen_height])

                        # ----- CLICK DETECTION: INDEX + MIDDLE PINCH -----
                        index_tip = landmarks[8]
                        middle_tip = landmarks[12]
                        index_pip = landmarks[6]
                        middle_pip = landmarks[10]
                        
                        index_tip_x = int(index_tip.x * frame_width)
                        index_tip_y = int(index_tip.y * frame_height)
                        middle_x = int(middle_tip.x * frame_width)
                        middle_y = int(middle_tip.y * frame_height)
                        
                        index_pip_y = int(index_pip.y * frame_height)
                        middle_pip_y = int(middle_pip.y * frame_height)

                        # Calculate distance between index and middle fingertips
                        finger_distance = np.sqrt(
                            (index_tip_x - middle_x) ** 2 + 
                            (index_tip_y - middle_y) ** 2
                        )
                        
                        finger_distance_history.append(finger_distance)
                        avg_distance = sum(finger_distance_history) / len(finger_distance_history)

                        # Check if fingers are extended (not folded down)
                        fingers_extended = (index_tip_y < index_pip_y) and (middle_y < middle_pip_y)

                        # ----- STATE MACHINE FOR RELIABLE CLICKS -----
                        if click_state == IDLE:
                            # Looking for a pinch gesture
                            if avg_distance < click_threshold and fingers_extended:
                                stable_pinch_frames += 1
                                if stable_pinch_frames >= required_stable_frames:
                                    click_state = PINCHING
                            else:
                                stable_pinch_frames = 0
                                
                        elif click_state == PINCHING:
                            # Confirm pinch is stable, then click
                            if avg_distance < click_threshold and fingers_extended:
                                if time.time() - last_click_time > click_cooldown:
                                    print('✓ Click')
                                    pyautogui.click()
                                    last_click_time = time.time()
                                    click_state = CLICKED
                                    stable_pinch_frames = 0
                            else:
                                # False alarm, reset
                                click_state = IDLE
                                stable_pinch_frames = 0
                                
                        elif click_state == CLICKED:
                            # Wait for fingers to separate before allowing next click
                            if avg_distance > release_threshold:
                                click_state = IDLE
                                stable_pinch_frames = 0

                        # ----- SMOOTH CURSOR MOVEMENT -----
                        if cursor_x is not None and cursor_y is not None:
                            x_buffer.append(cursor_x)
                            y_buffer.append(cursor_y)

                            x_arr = np.array(x_buffer)
                            y_arr = np.array(y_buffer)

                            weighted_x = np.sum(x_arr * buffer_weights)
                            weighted_y = np.sum(y_arr * buffer_weights)

                            smoothed_x = alpha * weighted_x + (1 - alpha) * prev_x
                            smoothed_y = alpha * weighted_y + (1 - alpha) * prev_y

                            try:
                                smoothed_x = max(0, min(screen_width - 1, smoothed_x))
                                smoothed_y = max(0, min(screen_height - 1, smoothed_y))

                                pyautogui.moveTo(int(smoothed_x), int(smoothed_y), duration=0)
                                prev_x, prev_y = smoothed_x, smoothed_y
                            except:
                                pass
                else:
                    # No hand detected, reset click state
                    click_state = IDLE
                    stable_pinch_frames = 0

        finally:
            cap.release()
            hand_detector.close()

# Global controller instance
ar_controller = ARMouseController()

@AR_bp.route("/", methods=["GET", "POST"])
def run_AR():
    print("Hello AR Route")
    result = ar_controller.start()
    
    return jsonify({
        "message": "Running the AR",
        "status": result["status"],
        "running": ar_controller.running
    }), 200