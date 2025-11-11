import os
import time
import webbrowser
import subprocess
import socket
from threading import Thread
from flask import Flask
from flask_cors import CORS

app = Flask(__name__) 
CORS(app)

# --- Import all routes ---
from routes.default import main_bp
from routes.register import register_bp
from routes.close import close_bp
from routes.open import open_bp
from routes.progress_tracking import progressTracking_bp
from routes.loginStudent import login_bp
from routes.selectStudent import selectStudent_bp
from routes.AR import AR_bp
from routes.locomotor import locomotor_bp
from routes.nonLocomotor import nonLocomotor_bp

# --- Register blueprints ---
app.register_blueprint(main_bp)
app.register_blueprint(register_bp)
app.register_blueprint(close_bp)
app.register_blueprint(open_bp)
app.register_blueprint(progressTracking_bp)
app.register_blueprint(login_bp)
app.register_blueprint(selectStudent_bp)
app.register_blueprint(AR_bp)
app.register_blueprint(locomotor_bp)
app.register_blueprint(nonLocomotor_bp)


# --- Function to start Docker MongoDB container ---
def start_mongo():
    print("[INFO] Starting MongoDB Docker container...")
    mongo_dir = r"/home/pi/mongodb-setup"
    try:
        subprocess.call("docker start alphabot-mongo", shell=True, cwd=mongo_dir)
        print("[INFO] MongoDB container started successfully.")
    except Exception as e:
        print("[ERROR] Failed to start MongoDB container:", e)


# --- Function to free a port if in use ---
def free_port(port=3000):
    try:
        result = subprocess.check_output(f"lsof -ti:{port}", shell=True)
        for pid in result.splitlines():
            subprocess.call(f"kill -9 {pid.decode()}", shell=True)
            print(f"[INFO] Killed process {pid.decode()} on port {port}")
    except subprocess.CalledProcessError:
        # No process using port
        pass


# --- Function to open Chromium safely ---
def open_chromium(url="http://localhost:3000"):
    chromium_path = "/usr/bin/chromium-browser"  # default path on Raspberry Pi
    if os.path.exists(chromium_path):
        try:
            webbrowser.register('chromium', None, webbrowser.BackgroundBrowser(chromium_path))
            webbrowser.get('chromium').open(url)
            print(f"[INFO] Chromium opened {url}")
        except Exception as e:
            print("[WARNING] Failed to open Chromium:", e)
    else:
        print("[WARNING] Chromium not found, opening default browser instead")
        webbrowser.open(url)


# --- Function to start Next.js frontend ---
def run_frontend():
    print("[INFO] Building and starting Next.js frontend...")
    frontend_dir = r"/home/pi/Downloads/Thesis-mk3.0-main"  # adjust if different path in your Pi 

    # Free port 3000 before starting frontend
    free_port(3000)

    # Build frontend (blocking)
    #subprocess.call("npm run build", shell=True, cwd=frontend_dir)

    # Start frontend in background
    subprocess.Popen("npm run start", shell=True, cwd=frontend_dir)


# --- Function to wait until Next.js is live ---
def wait_for_port(host, port, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except OSError:
            time.sleep(1)
    return False


if __name__ == "__main__": 
    # Step 1: Start MongoDB container
    start_mongo()

    # Step 2: Start frontend
    frontend_thread = Thread(target=run_frontend)
    frontend_thread.start()

    # Step 3: Wait until frontend is live (localhost:3000)
    if wait_for_port("localhost", 3000):
        print("[INFO] Frontend is live! Opening in Chromium...")
        open_chromium("http://localhost:3000")
    else:
        print("[WARNING] Frontend didn't start in time.")

    # Step 4: Start Flask backend
    print("[INFO] Starting Flask backend...")
    app.run(debug=False, host="0.0.0.0", port=5000)
