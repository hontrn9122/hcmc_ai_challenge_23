from fastapi import FastAPI
from model.ocrmodel import retrieveOCR
from model.kosmosmodel import retrieveKosmos
from model.clipmodel import cosine_faiss
from model.objmodel import retrieve_obj
from path2idx import frame2idx
from path2utube import frame2url
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os


from pathlib import Path
from pydantic import BaseModel

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    query: str

class Item(BaseModel):
    path: str

class Time(BaseModel):
    frame_idx: int
    second: int
    url: str

class FilterQuery(BaseModel):
    ocr: str
    labels: list[str]
    qtys: list[int]
    colors: list[list[set[str]]]
    
class RetrivalHistory:
    prev_res = []



##### PATH NEED TO PASSSS 
# path need to pass: Keyframes_L01/keyframes/L01_V001/0056

def convert_paths(original_paths):
    converted_paths = []
    for original_path in original_paths:
        # Split the original path into parts using underscores and remove the file extension
        parts = os.path.splitext(original_path)[0].split('_')
        if len(parts) >= 4:
            # Extract relevant components from the original path
            _, level, video, frame = parts[0], parts[1], parts[2], parts[3]
            # Create the new path in the desired format
            new_path = f'Keyframes_{level.zfill(2)}/keyframes/{level}_{(video)}/{frame}'
            converted_paths.append(new_path)
        else:
            # Handle paths that don't match the expected format
            print(f"Invalid path format: {original_path}")
    return converted_paths


@app.post("/clipmodel", response_model=list[Item])
async def create_item(data: Query) -> list[Item]:
    # global prev_res
    query = data.query
    scores, _, infos_query, image_paths = cosine_faiss.text_search(query, k= 500)
    items = [Item(path = a) for a in image_paths]
    RetrivalHistory.prev_res = image_paths
    return items 


    # path need to return: Keyframes_L01/keyframes/L01_V001/0056
@app.post("/kosmosmodel", response_model=list[Item])
async def create_item(data: Query) -> list[Item]:
    # global prev_res
    query = data.query
    listofpaths = retrieveKosmos(query)
    listofpaths = convert_paths(listofpaths)
    items = [Item(path = a) for a in listofpaths]
    RetrivalHistory.prev_res = listofpaths
    return items 

# FIX THIS 
@app.post("/filename", response_model= list[Item])
async def create_item(data: Query) -> list[Item]:
    # global prev_res
    query = data.query.upper()
    query = query.split('/')
    if(len(query) == 2):
        querynew = query[0].split('_')
        RetrivalHistory.prev_res = path = (f'Keyframes_{querynew[0]}/keyframes/{data.query.upper()}')
        items = [Item(path = (f'Keyframes_{querynew[0]}/keyframes/{data.query.upper()}'))]
        return items
    else:
        querynew = query[0].split('_')
        paths = (os.listdir(os.getcwd() + f'\\Data\\images\\Keyframes_{querynew[0]}\\keyframes\\{query[0]}'))
        filename = [Path(a).stem for a in paths]
        items = [Item(path = f'Keyframes_{querynew[0]}/keyframes/{query[0]}/{a}') for a in filename]
        RetrivalHistory.prev_res = items
        return items



@app.post("/filter", response_model=list[Item])
async def retrieve_item(data: FilterQuery) -> list[Item]:
    ocr, labels, qtys, colors = data.ocr, data.labels, data.qtys, data.colors
    #   handle ocr query
    res = RetrivalHistory.prev_res
    
    if ocr != '':
        ocr = ocr.lower()
        listofkeyword = ocr.split(',')
        listofkeyword = [a.strip() for a in listofkeyword]
        print(listofkeyword)
        res = retrieveOCR(listofkeyword,res)
    #   handle object detection
    if len(labels) != 0:
        # print("hhuhu")
        res = retrieve_obj(labels, qtys=qtys, colors=colors, prev_res=res)
    # print(RetrivalHistory.prev_res)
    
    items = [Item(path = a) for a in res]
    return items

# Keyframes_L18/keyframes/L18_V005/109
@app.post("/frameindex", response_model= Time)
async def create_item(data: Query) -> Time:
    frame_idx = frame2idx(data.query)
    second  = (frame_idx/25)//1
    Time.url = frame2url(data.query)
    Time.frame_idx = frame_idx
    Time.second = second
    return Time
    
    
### Clear everything    
@app.get("/clear")
async def clear_item():
    RetrivalHistory.prev_res = []
    
    

@app.get("/images/{folder}/keyframes/{video}/{id}")
async def get_image(folder:str, video: str, id:str):
    return FileResponse(os.getcwd() + (f'/Data/images/{folder}/keyframes/{video}/{id}.jpg'))

