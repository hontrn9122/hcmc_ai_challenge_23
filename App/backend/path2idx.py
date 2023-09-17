import json
import os 

current_path =  os.getcwd()
img2fridx_path = f"{current_path}/clip_path.json" 
with open(img2fridx_path, "r") as json_file:
    img2fridx = json.load(json_file)

# test_kf = "Keyframes_L04/keyframes/L04_V008/0107"
# 
# "Keyframes_L18/keyframes/L18_V005/109"

def frame2idx(frame_path, img2fridx = img2fridx ):
    for element in img2fridx.items():
        # print(i) Tuple of ('74957', {'frame_idx': 616, 'frame_path': 'Keyframes_L09/keyframes/L09_V019/0008'})
        frame_path2frame_idx = element[1]
        frame_idx = 0
        if(frame_path2frame_idx['frame_path'] == frame_path):
            # print(element[0])
            # print(frame_idx)
            frame_idx = frame_path2frame_idx['frame_idx']
            return frame_idx
    return 0


# frame_idx = frame2idx(test_kf)