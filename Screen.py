from flask import Flask, jsonify, request
import cv2
import os

app = Flask(__name__)

# Settings
VideoPath = r"video.mp4"
FrameStart = 0

cap = cv2.VideoCapture(VideoPath)
cap.set(cv2.CAP_PROP_POS_FRAMES, FrameStart)

@app.route('/get_frame', methods=["GET"])
def get_frame():
    success, frame = cap.read()
    if not success:
        cap.set(cv2.CAP_PROP_POS_FRAMES, FrameStart)
        success, frame = cap.read()
    
    # Encode the frame to base64 or any other suitable format
    # You can use libraries like base64 or Pillow for this
    
    # Example:
    # import base64
    # frame_encoded = base64.b64encode(frame).decode('utf-8')

    # Send the encoded frame in the response
    response_data = {
        "frame": frame_encoded
    }
    
    return jsonify(response_data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1241)
