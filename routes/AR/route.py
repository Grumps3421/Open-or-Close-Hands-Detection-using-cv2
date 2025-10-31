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
            return {"status": "already_running"}
        
        self.running = True
        self.thread = threading.Thread(target=self._run_tracking, daemon=True)
        self.thread.start()
        return {"status": "started"}
    
    def stop(self):
        if not self.running:
            return {"status": "not_running"}
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        return {"status": "stopped"}
    
    def _run_tracking(self):
        # Initialize video capture and hand detection
        cap = cv2.VideoCapture(0)
        hand_detector = mp.solutions.hands.Hands(
            min_detection_confidence=0.7, 
            min_tracking_confidence=0.7, 
            max_num_hands=1
        )
        screen_width, screen_height = pyautogui.size()

        # ----- RESPONSIVE TRACKING PARAMETERS -----
        alpha = 0.7
        prev_x, prev_y = screen_width // 2, screen_height // 2

        # ----- IMPROVED CLICK PARAMETERS -----
        click_cooldown = 0.4
        last_click_time = 0
        click_threshold = 30
        finger_distance_history = deque(maxlen=5)
        click_trigger_frames = 1
        click_frames_counter = 0
        is_clicking = False
        click_released = True
        min_release_distance = 30

        # ----- RESPONSIVE MOTION TRACKING -----
        motion_buffer_size = 3
        x_buffer = deque([prev_x] * motion_buffer_size, maxlen=motion_buffer_size)
        y_buffer = deque([prev_y] * motion_buffer_size, maxlen=motion_buffer_size)
        buffer_weights = np.array([0.2, 0.3, 0.5])
        buffer_weights = buffer_weights / np.sum(buffer_weights)

        # Disable PyAutoGUI delay
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
                        # ----- POINTER WITH THUMB -----
                        thumb_landmark = landmarks[4]
                        x = int(thumb_landmark.x * frame_width)
                        y = int(thumb_landmark.y * frame_height)

                        index_x = np.interp(x, [100, frame_width - 100], [0, screen_width])
                        index_y = np.interp(y, [100, frame_height - 100], [0, screen_height])

                        # ----- CLICK WITH INDEX + MIDDLE -----
                        index_tip = landmarks[8]
                        middle_tip = landmarks[12]
                        index_tip_x = int(index_tip.x * frame_width)
                        index_tip_y = int(index_tip.y * frame_height)
                        middle_x = int(middle_tip.x * frame_width)
                        middle_y = int(middle_tip.y * frame_height)

                        index_pip_y = int(landmarks[6].y * frame_height)
                        middle_pip_y = int(landmarks[10].y * frame_height)

                        finger_distance = np.sqrt((index_tip_x - middle_x) ** 2 + (index_tip_y - middle_y) ** 2)
                        finger_distance_history.append(finger_distance)
                        avg_distance = sum(finger_distance_history) / len(finger_distance_history)

                        fingers_extended = (index_tip_y < index_pip_y) and (middle_y < middle_pip_y)

                        if avg_distance < click_threshold and fingers_extended and click_released:
                            click_frames_counter += 1

                            if click_frames_counter >= click_trigger_frames and not is_clicking:
                                if time.time() - last_click_time > click_cooldown:
                                    print('Clicked')
                                    pyautogui.click()
                                    last_click_time = time.time()
                                    is_clicking = True
                                    click_released = False
                        elif avg_distance > min_release_distance:
                            click_frames_counter = 0
                            is_clicking = False
                            click_released = True
                        else:
                            click_frames_counter = 0
                            is_clicking = False

                        # ----- CURSOR TRACKING -----
                        if index_x is not None and index_y is not None:
                            x_buffer.append(index_x)
                            y_buffer.append(index_y)

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

        finally:
            cap.release()
            hand_detector.close()

# Global controller instance
ar_controller = ARMouseController()

@AR_bp.route("/", methods=["GET", "POST"])
def run_AR():
    print("Hello AR Route")
    
    # Start the AR tracking automatically when this route is called
    result = ar_controller.start()
    
    return jsonify({
        "message": "Running the AR",
        "status": result["status"],
        "running": ar_controller.running
    }), 200