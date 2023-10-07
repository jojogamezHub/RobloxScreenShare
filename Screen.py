from flask import Flask, jsonify, request
from PIL import Image, ImageGrab
import random
import string
import time
import cv2
from gevent.pywsgi import WSGIServer
from collections import deque

# Constants
FPS = 1 * 8
XRes = 80
YRes = 60
CompressedColors = True
FrameGroups = 14
FrameSkip = 0
FrameStart = 1
VideoStreaming = True
VideoPath = r"video.mp4"

app = Flask(__name__)

# Initialize variables
ServerList = {}

# Create a buffer with a maximum size of FrameGroups
frame_buffer = deque(maxlen=FrameGroups)

# Cache for frames
video_frames = []

# Number of frames to accumulate before sending a batch
batch_size = 6

# Precompute constant values
if CompressedColors:
    pixel_conversion = lambda pixel: f"{(pixel[0] >> 4):X}{(pixel[1] >> 4):X}{(pixel[2] >> 4):X}"
else:
    pixel_conversion = lambda pixel: "%02x%02x%02x" % pixel

cap = cv2.VideoCapture(VideoPath)
cap.set(cv2.CAP_PROP_POS_FRAMES, FrameStart)

# Load and cache video frames in memory
if VideoStreaming:
    while True:
        playing, frame = cap.read()
        if not playing:
            break

        pic = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize(
            (XRes, YRes), Image.Resampling.BILINEAR)

        current_frame = [pixel_conversion(pixel) for pixel in pic.getdata()]
        video_frames.append(current_frame)

# Function to calculate the time to wait for consistent frame rate
def calculate_wait_time():
    frame_time = 1 / FPS  # Desired frame time in seconds
    elapsed_time = time.time() - start_time
    wait_time = max(0, frame_time - elapsed_time)
    return wait_time

# Function to skip frames as needed
def skip_frames(method, server_id, skip_frame):
    for _ in range(FrameSkip):
        if not frame_buffer:
            frame_buffer.append(encode_frame(method, server_id, skip_frame))
        frame_buffer.popleft()

def encode_frame(first_time, server_id, skip_frame):
    global frame_buffer

    if VideoStreaming and skip_frame == "1":
        ServerList[server_id] += 1
        cap.set(cv2.CAP_PROP_POS_FRAMES, ServerList[server_id])

    if first_time == "1":
        frame_buffer.clear()

    if not VideoStreaming:
        pic = ImageGrab.grab().resize((XRes, YRes), Image.Resampling.BILINEAR)
    else:
        playing, frame = cap.read()
        if not playing:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ServerList[server_id] = 0
            _, frame = cap.read()

        pic = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize(
            (XRes, YRes), Image.Resampling.BILINEAR)

    current_frame = [pixel_conversion(pixel) for pixel in pic.getdata()]

    if not frame_buffer:
        frame_buffer.append(current_frame)

    return tuple(filter(None, current_frame))

@app.route('/',
           methods=[
               "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS",
               "CONNECT", "TRACE"
           ])
def return_frame():
    method = request.headers.get("R")
    server_id = request.headers.get("I")
    skip_frame = request.headers.get("F")

    if server_id not in ServerList:
        ServerList[server_id] = FrameStart

    start_frame = ServerList[server_id]
    end_frame = start_frame + FrameGroups

    frames = []

    # Use cached video frames instead of capturing from video stream
    for _ in range(start_frame, end_frame):
        global start_time
        start_time = time.time()

        # Calculate the time to wait for consistent frame rate
        wait_time = calculate_wait_time()
        time.sleep(wait_time)

        # Skip frames as needed
        skip_frames(method, server_id, skip_frame)

        if not frame_buffer:
            # Use cached video frames
            if len(video_frames) > 0:
                frames.append(video_frames.pop(0))
            else:
                # If we've reached the end of the cached frames, stop streaming
                break
        else:
            frame_buffer.append(encode_frame(method, server_id, skip_frame))
            frames.append(frame_buffer.popleft())

    ServerList[server_id] = end_frame

    return jsonify(Fr=frames, F=FPS, X=XRes, Y=YRes, G=FrameGroups)

def start_api(port):
    print(
        str(XRes) + "x" + str(YRes) + "    FPS: " + str(FPS) + "    Port: " +
        str(port))
    server = WSGIServer(('0.0.0.0', port), app)
    server.serve_forever()

start_api(random.randint(1, 65535))
