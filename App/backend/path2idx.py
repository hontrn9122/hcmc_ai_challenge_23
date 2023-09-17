import json
import os 

current_path =  os.getcwd()
img2fridx_path = f"{current_path}/clip_path.json" 
with open(img2fridx_path, "r") as json_file:
    img2fridx = json.load(json_file)

def frame2idx(frame_path, img2fridx = img2fridx ):
    for element in img2fridx.items():
        frame_path2frame_idx = element[1]
        frame_idx = 0
        if(frame_path2frame_idx['frame_path'] == frame_path):
            frame_idx = frame_path2frame_idx['frame_idx']
            return frame_idx
    return 0
