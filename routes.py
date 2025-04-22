import json
import subprocess
import cv2
from flask import Blueprint, render_template, redirect, url_for, Response

bp = Blueprint('main', __name__)
SETTINGS_PATH = "config/settings.json"

# Global reference to the subprocess
tracker_process = None


@bp.route("/")
def home():
    return render_template("home.html")


@bp.route("/modules")
def modules():
    with open(SETTINGS_PATH, "r") as f:
        settings = json.load(f)
    return render_template("modules.html", settings=settings)


@bp.route("/toggle/<module>")
def toggle_module(module):
    with open(SETTINGS_PATH, "r+") as f:
        settings = json.load(f)
        settings[module] = not settings[module]
        f.seek(0)
        json.dump(settings, f, indent=4)
        f.truncate()
    return redirect(url_for("main.modules"))


@bp.route("/servo")
def servo_page():
    return render_template("servo.html")


@bp.route("/servo/<direction>")
def servo_control(direction):
    print(f"[Servo] Moving {direction}")
    # You can add code here to send signal to your servo
    return redirect(url_for("main.servo_page"))


@bp.route("/toggle_auto")
def toggle_auto():
    global tracker_process
    with open(SETTINGS_PATH, "r+") as f:
        settings = json.load(f)
        settings["auto_mode"] = not settings["auto_mode"]

        # Start/stop the eye tracker subprocess
        if settings["auto_mode"]:
            tracker_process = subprocess.Popen(["python", "core/eye_tracker.py"])
        elif tracker_process:
            tracker_process.terminate()
            tracker_process = None

        f.seek(0)
        json.dump(settings, f, indent=4)
        f.truncate()
    return redirect(url_for("main.modules"))

@bp.route("/camera")
def camera():
    return render_template("camera.html")

@bp.route("/camera_feed")
def camera_feed():
    def generate_frames():
        cap = cv2.VideoCapture(0)
        while True:
            success, frame = cap.read()
            if not success:
                break
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        cap.release()

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
