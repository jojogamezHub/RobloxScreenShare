
# Screen Sharing in Roblox

This project is a simple way of doing screen sharing in Roblox, while trying to keep the quality while being performant.


It uses 2 main forms of compression:
- Removing repetition of color data:
  
 (255,255,255), (255,255,255), (255,255,255) -> (255,255,255), 2

 - Removes colors that we're not changed compared to the last frame:

Last Frame:
  (255,255,255), (255,255,255), (255,255,255), (255,255,255)

New Frame: 
(255,255,255), (0,0,0), (255,255,255), (255,255,255)

Output: 
1.1, (250,255,250), 2.1

Hex is used to store the color, but to display how the compression works I used RGB values

## How To Use
Setting this up may require some knowledge, but I will try making it as simple as possible:
 1. If you don't already have Python installed, then install it: https://www.python.org/downloads/
  
  2. Install the required packages (Instructions at the Installation section)
  
  3. Open Screen.py and modify the settings to your liking

  4. Open a CMD line in the directory of the python file, in there type:
  ```bash
  py Screen.py
  ```
  This will run the python file, this part will send the Roblox server your screen

  5. Open up Screen.rbxl, and modify the IP:Port if you changed it in the settings, go play test it and it should hopefully work.

  6. Bit of a heads up: if you are using this in a Roblox server, you will need to port forward or use a service such as PlayIt.gg and then change the HTTPAdress variable in the     .rbxl file
  

## Installation

It's quite simple to install this, you only need a way to port forward (I recommend using PlayIt.gg, if you cannot do it yourself)

You will also need to install the Python packages: 
```bash
pip install -r requirements.txt
```
(run the command in the path of the requirements.txt file)



## Notes
- There are 2 versions of the server code, one that works on your local PC (if you do not want to publish the game to the public) and another that is compatible with webservers (Which allow you to access the data on any server, anywhere).

- However the Webserver-compatible code is tailored specifically for replit, meaning you will have to modify the code to be able to work on any other webserver service.

- So far, the code is able to handle the provided video with somewhat smooth playback (There are still times where the playback will stop shortly (for like half a second), this is due to the http request taking longer than usual.

 - A little advice for you dear reader, This might sound too technical for u, but either way if you plan on using this github project, that would be a bit redundant. However, the more efficient your video codec is at decoding and encoding, the faster and lighter the overall process that the webserver (or local server) has to go through to send data to your roblox server. I do not whole-heartedly recommend you to use HEVC for your videos due to limited support (As you will risk having problems with whatever server your using). Any video codec that is more efficient than the standard H.264 will definetly lead to a performance increase no matter what.
## License

[MIT](https://choosealicense.com/licenses/mit/)
