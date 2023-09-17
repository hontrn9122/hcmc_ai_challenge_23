import torch
from scipy.spatial.distance import cosine
from transformers import AutoModel, AutoTokenizer
import faiss
import numpy as np
import time
import pickle
from langdetect import detect
from googletrans import Translator
import os

current_path =  os.getcwd()
# Load the model and tokenizer once
tokenizer = AutoTokenizer.from_pretrained("princeton-nlp/sup-simcse-roberta-base")
model = AutoModel.from_pretrained("princeton-nlp/sup-simcse-roberta-base")


index = faiss.read_index(f"{current_path}/Data/kosmos/large.index")
with open(f"{current_path}/Data/kosmos/test", "rb") as fp:   # Unpickling
    frame_paths = pickle.load(fp)
translator = Translator() 

def embeddingQuery(query: str, tokenizer = tokenizer, model = model):
    if detect(query) == 'vi':
      print(query)
      query = translator.translate(query ,src = 'vi', dest = 'en').text
    print(query)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    inputs = tokenizer(query, padding=True, truncation=True, return_tensors="pt")
    inputs = inputs.to(device)
    model = model.to(device)

    with torch.no_grad():
        query_embedding = model(**inputs, output_hidden_states=True, return_dict=True).pooler_output
    return query_embedding.to('cpu')

def retrieveKosmos(query_embedding: str, index = index, frame_paths = frame_paths):
    start = time.time()
    k = 500
    query_embedding = embeddingQuery(query_embedding)
    xq = np.array(query_embedding.to('cpu'))
    faiss.normalize_L2(xq)
    D, I = index.search(xq, k)
    keys = [frame_paths[a] for a in I[0]]    
    return keys

####TESTING 
# query_embedding = embeddingQuery("Two men are arrested at the police station, there are two police officers standing with them.")
# Now you can call retrieve(query_embedding) as many times as needed
# sentence = 'Bé gái được các chú cứu hộ giải cứu thành công'
# sentence = "police drive car"
# print(retrieveKosmos(sentence))



