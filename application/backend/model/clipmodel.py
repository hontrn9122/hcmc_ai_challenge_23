import numpy as np
import faiss
import glob
import json
import matplotlib.pyplot as plt
import os
import math
import clip
import torch
import pandas as pd
import re
from langdetect import detect
import time
from googletrans import Translator
    
         
             
class MyFaiss:
  def __init__(self,  bin_file: str, json_path: str):
    self.index = self.load_bin_file(bin_file)
    self.id2img_fps = self.load_json_file(json_path)

    self.translater = Translator()

    self.__device = "cuda" if torch.cuda.is_available() else "cpu"
    self.model, preprocess = clip.load("ViT-B/32", device=self.__device)

  def load_json_file(self, json_path: str):
      with open(json_path, 'r') as f:
        js = json.loads(f.read())
        
    #   print(js.items())    
      return {int(k):v for k,v in js.items()}

  def load_bin_file(self, bin_file: str):
    return faiss.read_index(bin_file)

  def show_images(self, image_paths):
    fig = plt.figure(figsize=(15, 10))
    columns = int(math.sqrt(len(image_paths)))
    rows = int(np.ceil(len(image_paths)/columns))

    for i in range(1, columns*rows +1):
      img = plt.imread(image_paths[i - 1])
      ax = fig.add_subplot(rows, columns, i)
      ax.set_title('/'.join(image_paths[i - 1].split('/')[-3:]))

      plt.imshow(img)
      plt.axis("off")

    plt.show()

  def image_search(self, id_query, k):
    query_feats = self.index.reconstruct(id_query).reshape(1,-1)

    scores, idx_image = self.index.search(query_feats, k=k)
    idx_image = idx_image.flatten()

    infos_query = list(map(self.id2img_fps.get, list(idx_image)))
    image_paths = [info['frame_path'] for info in infos_query]

    # print(f"scores: {scores}")
    # print(f"idx: {idx_image}")
    # print(f"paths: {image_paths}")

    return scores, idx_image, infos_query, image_paths

  def text_search(self, text, k):
    # Make text lower 
    text = text.lower()
    start = time.time()
    if detect(text) == 'vi':
      print(text)
      text = self.translater.translate(text ,src = 'vi', dest = 'en').text
      # translator.translate('Xin chào', src = 'vi', dest = 'en')
    print(text)
    end = time.time()
    print('Translation: ', end - start )
    ###### TEXT FEATURES EXACTING ######
    text = clip.tokenize([text]).to(self.__device)
    text_features = self.model.encode_text(text).cpu().detach().numpy().astype(np.float32)

    ###### SEARCHING #####
    scores, idx_image = self.index.search(text_features, k=k)
    idx_image = idx_image.flatten()

    ###### GET INFOS KEYFRAMES_ID ######
    infos_query = list(map(self.id2img_fps.get, list(idx_image)))
    image_paths = [info['frame_path'] for info in infos_query]
    return scores, idx_image, infos_query, image_paths

  def write_csv(self, infos_query, des_path):
    check_files = []

    ### GET INFOS SUBMIT ###
    for info in infos_query:
      video_name = info['frame_path'].split('/')[-2]
      lst_frames = info['frame_idx']

      # for id_frame in lst_frames:
      check_files.append(os.path.join(video_name, str(lst_frames)))
    ###########################

    check_files = set(check_files)

    if os.path.exists(des_path):
        df_exist = pd.read_csv(des_path, header=None)
        lst_check_exist = df_exist.values.tolist()
        check_exist = [info[0].replace('.mp4','/') + f"{info[1]:0>6d}" for info in lst_check_exist]

        ##### FILTER EXIST LINES FROM SUBMIT.CSV FILE #####
        check_files = [info for info in check_files if info not in check_exist]
    else:
      check_exist = []

    video_names = [i.split('/')[0] + '.mp4' for i in check_files]
    frame_ids = [i.split('/')[-1] for i in check_files]

    dct = {'video_names': video_names, 'frame_ids': frame_ids}
    df = pd.DataFrame(dct)

    if len(check_files) + len(check_exist) < 99:
      df.to_csv(des_path, mode='a', header=False, index=False)
      print(f"Save submit file to {des_path}")
    else:
      print('Exceed the allowed number of lines')
      
      

current_path =  os.getcwd()
bin_file=f'{current_path}/Data/clip/faiss_index_b2.bin'
json_path = f'{current_path}/Data/clip/updated_merged_results.json'
cosine_faiss = MyFaiss(bin_file, json_path)    



## TESTING UNIT
# text = 'Vườn hoa của bác nông dân'



# start = time.time()
# scores, _, infos_query, image_paths = cosine_faiss.text_search(text, k=50)
# # end = time.time()
# # print(end-start)
# # # print(infos_query)
# print(image_paths)