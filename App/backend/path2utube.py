import pandas as pd
import os


current_path = os.getcwd()
watch_urls = f'{current_path}/watch_urls.csv'
urls = pd.read_csv(watch_urls)
urls.set_index("json_file_name", inplace = True)
# frame =  Keyframes_L18/keyframes/L18_V005/109
def frame2url(frame, urls = urls ):
    video = frame.split('/')[2]
    result = urls.loc[f"{video}.json"]
    result = result.tolist()[0]
    return result 



# print(frame2url("Keyframes_L18/keyframes/L18_V005/109"))