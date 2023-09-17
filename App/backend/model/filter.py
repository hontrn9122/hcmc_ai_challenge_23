import json
from clipmodel import cosine_faiss

##infos_query 
item_paths = "C:/Users/admin/Projects/AI challenge/backend/Data/filter object/filter_object.json"

with open(item_paths, "r") as json_file:
    items = json.load(json_file)
info = []
# print(items.items())
for item in items.items():
    info.append(item[1])

def filterKW(listofframes, listofkeywords, info = info):
    # infos_query = items.items()[1]
    # for frame in listofframes:
    # print(info)
    infos_query = list(filter(lambda x: any(item in x['frame_path'] for item in listofframes), info))
    filtered_data = list(filter(lambda x: all(item in x['object'] for item in listofkeywords.split(',')), infos_query))
    frame_paths = [x['frame_path'] for x in filtered_data]
    return frame_paths
    
 
 
### TESTING UNIT    
listofkeywords = "Person", 
queryCLIP = 'Khung cảnh 2 thanh niên chạy xe dừng trước nhà một lúc. 2 con chó trong nhà sủa về phía hai người thanh niên. Ngôi nhà có trồng cây cảnh ở phía bên trái.'
scores, _, infos_query, image_paths = cosine_faiss.text_search(queryCLIP, k= 10000)
# print(image_paths)

print(len(filterKW(image_paths, listofkeywords)))
