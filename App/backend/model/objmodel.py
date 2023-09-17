import json
import copy
from typing import List, Set
import os 


current_path =  os.getcwd()
JSON_PATH = f'{current_path}/Data/object/obj_data.json'


with open(JSON_PATH, 'r') as of:
    obj_data = json.load(of)

def find_min_match_color(color_list, color_dict_list):
    min_match = min_id = None
    for i, cdict in enumerate(color_dict_list):
        if set(color_list).issubset(set(cdict.keys())) \
        and (min_match == None or min_match>len(cdict)):
            min_match = len(cdict)
            min_id = i
    return min_id

def convert_path(path):
    return path + '.jpg'

def retrieve_obj(labels: List[str], qtys: List[int], colors: List[List[Set[str]]], prev_res: list = []):
    res = []
    if len(prev_res) == 0:
        prev_res = list(obj_data.keys())
    else:
        prev_res = map(convert_path, prev_res)
    for path in prev_res:
        img_labels = set(obj_data[path].keys())
        if not set(labels).issubset(img_labels):
            continue
        is_matched=True
        for i, label in enumerate(labels):
            if obj_data[path][label]['quantity'] < qtys[i]:
                is_matched = False
                break
            tmp_colors = copy.copy(list(obj_data[path][label]['color']))
            for color in colors[i]:
                if len(color) == 0:
                    continue
                pop_id = find_min_match_color(color, tmp_colors)
                if pop_id == None:
                    is_matched = False
                    break
                tmp_colors.pop(pop_id)
        if is_matched == True:
            res.append(path[:-4])
    return res