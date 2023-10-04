from flask import Flask, Response
import cv2
import urllib.request

app = Flask(__name__)

# Replace with the URL of the internet video file
VIDEO_URL = "https://github.com/jojogamezHub/RobloxScreenShare/raw/main/video.mp4"

def generate_frames():
    cap = cv2.VideoCapture(VIDEO_URL)

    while True:
        success, frame = cap.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        frame_data = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')

@app.route('/')
def index():
    return "OpenCV Web Server"

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
