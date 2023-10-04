from flask import Flask, jsonify,request
from PIL import Image,ImageGrab
import time
import cv2
import os
from gevent.pywsgi import WSGIServer
from waitress import serve

####Settings####
FPS = 1*8 #//Max FPS is FrameGroups * 8, due to max Roblox HTTP limit/or... we can change the fps to either half of the frame groups or double of the framegroups
XRes = 16*25#//X resolution of your monitor, currently it is 16*N due to my aspect ratio
YRes = 9*25#//Y resolution of your monitor, currently it is 9*N due to my aspect ratio

CompressedColors = False #//Whether to compress colors, by removing their color quality
FrameGroups = 6 #//Amount of Frames sent in Groups

FrameSkip = 0 #How many times it should send a full frame without compression, (artifacts may appear with the compression, so this clears them up at the cost of performance)

FrameStart = 0 #//Starting Frame of the Video
VideoStreaming = True#//Self explanatory,
VideoPath = r"https://github.com/jojogamezHub/RobloxScreenShare/raw/main/video.mp4"
####Settings####

app = Flask(__name__)
app.debug = False

LastFrame = []#Keeps track of the last frame, to apply compressions (doesnt send pixels that didnt change since the last frame)
FrameCount = 1 #Keeps track of the frame count, for refreshing frames with FrameSkip

ServerList = {} #List of the servers its tracking, so that servers can watch their own films without interrupting each other

cap = cv2.VideoCapture(VideoPath)
cap.set(cv2.CAP_PROP_POS_FRAMES,FrameStart)

def RGBToCompHex(rgb):
    return f"{(rgb[0] >> 4):X}{(rgb[1]  >> 4):X}{(rgb[2] >> 4):X}"

def EncodeFrame(FirstTime,ServerID,SkipFrame):     
    global LastFrame,FrameCount

    if VideoStreaming and SkipFrame == "1":
        ServerList[ServerID] += 1
        cap.set(cv2.CAP_PROP_POS_FRAMES,ServerList[ServerID]);
    
    if FirstTime == "1":
        #Refresh the clients screen (doesnt compress it)
        LastFrame = []
    
    
    lastpixel = ""
    lastenumerate,lastDuplicate = 0,0
    number,DuplicateNumber = 1,1
    
    WasDuplicate = False
    WasRepetitive = False

    if not VideoStreaming:
        os.environ["DISPLAY"] = ":0"
        pic = ImageGrab.grab().resize((XRes,YRes),Image.Resampling.BILINEAR)
    else:
        playing, frame = cap.read()
        if not playing:
            #video ended, go back to frame 0 to repeat the video
            cap.set(cv2.CAP_PROP_POS_FRAMES,0)
            ServerList[ServerID] = 0
            _, frame = cap.read()
        
        pic = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize((XRes,YRes),Image.Resampling.BILINEAR)
    
    if CompressedColors:
        CurrentFrame = [RGBToCompHex(pixel) for pixel in pic.getdata()]
    else:
        CurrentFrame = ["%02x%02x%02x" % pixel for pixel in pic.getdata()]


    #removes duplicates
    LastFrame2 = [*CurrentFrame]

    FrameLen = len(LastFrame)
    
    for i,v in enumerate(CurrentFrame):
        #Removes non changed colors
        if FrameLen > i and v == LastFrame[i]:
            if WasDuplicate:
                DuplicateNumber += 1
                CurrentFrame[lastDuplicate] = DuplicateNumber
                CurrentFrame[i] = '' 
            else:
                CurrentFrame[i] = 1
                lastDuplicate = i
                DuplicateNumber = 1
            WasDuplicate = True
            continue
        else:
            WasDuplicate = False
        
        #Removes color repetition
        if lastpixel == v:
            if WasRepetitive:
                number += 1
                CurrentFrame[lastenumerate] = number
                CurrentFrame[i] = ''
            else:
                CurrentFrame[i] = 1.1
                lastenumerate = i
                number = 1.1
            WasRepetitive = True
        else:
            lastpixel = v
            WasRepetitive = False
    
    FrameCount += 1
    if FrameCount < FrameSkip:
        LastFrame = []
    else:
        LastFrame = LastFrame2
    
    return tuple(filter(None, CurrentFrame))

@app.route('/', methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "CONNECT", "TRACE"])

def ReturnFrame():
    Method = request.headers.get("R")
    ServerID = request.headers.get("I")
    SkipFrame = request.headers.get("F")

    if not ServerID in ServerList:
        ServerList[ServerID] = FrameStart

    # Determine the range of frames to send based on FrameGroups
    start_frame = ServerList[ServerID]
    end_frame = start_frame + FrameGroups

    Frames = []
    for _ in range(start_frame, end_frame):
        # makes the frames "flow" smoother, by keeping track of how much time was spent on encoding the frame and then subtracting it from the FPS time sleep
        start = time.time()
        Frames.append(EncodeFrame(Method, ServerID, SkipFrame))
        WaitOffset = time.time() - start
        time.sleep(max(0, 1 / FPS - WaitOffset))

    # Update the frame count for the next request
    ServerList[ServerID] = end_frame

    # Construct the URL for the client receiver
    url = f"https://{os.environ['RENDER_EXTERNAL_HOST']}/"

    # Print the URL to the console
    print("Client Receiver URL:", url)

    return jsonify(Fr=Frames, F=FPS, X=XRes, Y=YRes, G=FrameGroups)
