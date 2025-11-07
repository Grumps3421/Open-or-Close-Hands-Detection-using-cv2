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
        # Initialize video capture with Full HD settings
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        cap.set(cv2.CAP_PROP_FPS, 60)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Enhanced hand detection for better accuracy
        hand_detector = mp.solutions.hands.Hands(
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8,
            max_num_hands=1,
            model_complexity=1
        )
        screen_width, screen_height = pyautogui.size()

        # ----- RESPONSIVE TRACKING PARAMETERS -----
        alpha = 0.7
        prev_x, prev_y = screen_width // 2, screen_height // 2

        # ----- ADAPTIVE CLICK PARAMETERS -----
        click_cooldown = 0.4
        last_click_time = 0

        # Dynamic thresholds with hand size calibration
        base_click_threshold = 28
        base_release_threshold = 35
        click_threshold = base_click_threshold
        min_release_distance = base_release_threshold

        # Enhanced history tracking with outlier rejection
        finger_distance_history = deque(maxlen=8)
        click_trigger_frames = 3
        click_frames_counter = 0
        is_clicking = False
        click_released = True

        # Hand size calibration
        hand_size_history = deque(maxlen=30)
        is_calibrated = False

        # ----- RESPONSIVE MOTION TRACKING -----
        motion_buffer_size = 3
        x_buffer = deque([prev_x] * motion_buffer_size, maxlen=motion_buffer_size)
        y_buffer = deque([prev_y] * motion_buffer_size, maxlen=motion_buffer_size)
        buffer_weights = np.array([0.2, 0.3, 0.5])
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
                        # ----- HAND SIZE CALIBRATION -----
                        wrist = landmarks[0]
                        middle_mcp = landmarks[9]
                        hand_size = np.sqrt(
                            ((middle_mcp.x - wrist.x) * frame_width) ** 2 +
                            ((middle_mcp.y - wrist.y) * frame_height) ** 2
                        )
                        
                        hand_size_history.append(hand_size)
                        
                        if not is_calibrated and len(hand_size_history) >= 30:
                            avg_hand_size = np.median(hand_size_history)
                            scale_factor = avg_hand_size / 150
                            click_threshold = base_click_threshold * scale_factor
                            min_release_distance = base_release_threshold * scale_factor
                            is_calibrated = True
                            print(f"✓ Calibrated - Click: {click_threshold:.1f}px, Release: {min_release_distance:.1f}px")
                        
                        # ----- POINTER WITH THUMB (for tracking cursor) -----
                        thumb_landmark = landmarks[4]
                        thumb_x = int(thumb_landmark.x * frame_width)
                        thumb_y = int(thumb_landmark.y * frame_height)

                        cursor_x = np.interp(thumb_x, [100, frame_width - 100], [0, screen_width])
                        cursor_y = np.interp(thumb_y, [100, frame_height - 100], [0, screen_height])

                        # ----- CLICK WITH INDEX + MIDDLE -----
                        index_tip = landmarks[8]
                        middle_tip = landmarks[12]
                        index_pip = landmarks[6]
                        middle_pip = landmarks[10]
                        index_mcp = landmarks[5]
                        middle_mcp_joint = landmarks[9]
                        
                        index_tip_x = int(index_tip.x * frame_width)
                        index_tip_y = int(index_tip.y * frame_height)
                        middle_x = int(middle_tip.x * frame_width)
                        middle_y = int(middle_tip.y * frame_height)

                        index_pip_y = int(index_pip.y * frame_height)
                        middle_pip_y = int(middle_pip.y * frame_height)
                        index_mcp_y = int(index_mcp.y * frame_height)
                        middle_mcp_y = int(middle_mcp_joint.y * frame_height)

                        finger_distance = np.sqrt((index_tip_x - middle_x) ** 2 + (index_tip_y - middle_y) ** 2)
                        finger_distance_history.append(finger_distance)
                        
                        # Robust averaging with outlier rejection
                        if len(finger_distance_history) >= 5:
                            distances = np.array(finger_distance_history)
                            median_dist = np.median(distances)
                            mad = np.median(np.abs(distances - median_dist))
                            filtered = distances[np.abs(distances - median_dist) < 2 * mad]
                            avg_distance = np.mean(filtered) if len(filtered) > 0 else median_dist
                        else:
                            avg_distance = sum(finger_distance_history) / len(finger_distance_history)

                        # Enhanced finger extension check
                        index_extended = (index_tip_y < index_pip_y - 5) and (index_pip_y < index_mcp_y)
                        middle_extended = (middle_y < middle_pip_y - 5) and (middle_pip_y < middle_mcp_y)
                        fingers_extended = index_extended and middle_extended
                        
                        # Pinch velocity check
                        pinch_velocity = 0
                        if len(finger_distance_history) >= 3:
                            recent = list(finger_distance_history)[-3:]
                            pinch_velocity = abs(recent[-1] - recent[0])

                        if avg_distance < click_threshold and fingers_extended and click_released and pinch_velocity < 12:
                            click_frames_counter += 1

                            if click_frames_counter >= click_trigger_frames and not is_clicking:
                                if time.time() - last_click_time > click_cooldown:
                                    print('✓ Click')
                                    pyautogui.click()
                                    last_click_time = time.time()
                                    is_clicking = True
                                    click_released = False
                        elif avg_distance > min_release_distance:
                            click_frames_counter = max(0, click_frames_counter - 1)
                            is_clicking = False
                            click_released = True
                        else:
                            click_frames_counter = max(0, click_frames_counter - 1)
                            is_clicking = False

                        # ----- CURSOR TRACKING WITH THUMB -----
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
                    click_frames_counter = 0
                    is_clicking = False
                    click_released = True

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