import torch
from scipy.spatial.distance import cosine
from transformers import AutoModel, AutoTokenizer
import faiss
import numpy as np
import time
import pickle
from langdetect import detect
from googletrans import Translator

# Load the model and tokenizer once
tokenizer = AutoTokenizer.from_pretrained("princeton-nlp/sup-simcse-roberta-base")
model = AutoModel.from_pretrained("princeton-nlp/sup-simcse-roberta-base")
# index = faiss.read_index("C:/Users/admin/Projects/AI challenge/backend/Data/kosmos/kosmos.index")
index = faiss.read_index("C:/Users/admin/Projects/AI challenge/backend/Data/kosmos/large.index")
with open("C:/Users/admin/Projects/AI challenge/backend/Data/kosmos/test", "rb") as fp:   # Unpickling
    frame_paths = pickle.load(fp)
translator = Translator() 
# with open("C:/Users/admin/Projects/AI challenge/backend/Data/kosmos/listofquery", 'rb') as fp:   # Unpickling
#     listofquery = pickle.load(fp)


def embeddingQuery(query: str, tokenizer = tokenizer, model = model):
    if detect(query) == 'vi':
      print(query)
      query = translator.translate(query ,src = 'vi', dest = 'en').text
    print(query)
    # query = query.lower()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # print(device)

    inputs = tokenizer(query, padding=True, truncation=True, return_tensors="pt")
    inputs = inputs.to(device)
    model = model.to(device)

    with torch.no_grad():
        query_embedding = model(**inputs, output_hidden_states=True, return_dict=True).pooler_output
    return query_embedding.to('cpu')


# Function to calculate a match score for substring presence
def calculate_substring_score(list_of_querys, text):
    # my_str = 'apple, egg, kiwi'
    # list_of_strings = ['apple', 'egg', 'kiwi']
    # print(list_of_querys)
    if all(substring in text for substring in list_of_querys):
        return 1
    return 0

# def retrieveKosmos(query_embedding: str, index = index, listofquery = listofquery):
def retrieveKosmos(query_embedding: str, index = index, frame_paths = frame_paths):
    start = time.time()
    k = 500
    query_embedding = embeddingQuery(query_embedding)
    xq = np.array(query_embedding.to('cpu'))
    faiss.normalize_L2(xq)
    D, I = index.search(xq, k)
    # print(I)
    # print(D)
    keys = [frame_paths[a] for a in I[0]]
    
    return keys
    # listofkeyword = query_embedding.split(',')
    # listofkeyword = [a.strip() for a in listofkeyword]
    # print(listofkeyword)

    # key_paths = []
    # key_texts = []
    # for item in listofquery:
    #     text = item[1]
    #     score = calculate_substring_score(listofkeyword, text)
    #     if score:
    #         key_paths.append(item[0])#Retrieve the path
    #         key_texts.append(text)
    # end = time.time()
    # print(end - start)
    # print(key_texts[:100])
    # return key_paths[:100]

####TESTING 
# query_embedding = embeddingQuery("Two men are arrested at the police station, there are two police officers standing with them.")
# Now you can call retrieve(query_embedding) as many times as needed
# sentence = 'Bé gái được các chú cứu hộ giải cứu thành công'
# sentence = "police drive car"
# print(retrieveKosmos(sentence))



