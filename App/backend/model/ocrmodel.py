import os
import json
from pprint import pprint
from copy import deepcopy
from operator import itemgetter



import numpy as np
import pandas as pd


import os
import json

merged_ocr_path = "C:\\Users\\admin\\Projects\\AI challenge\\backend\\Data\\ocr\\merged_result_ocr.json"
merged_results_path = "C:\\Users\\admin\\Projects\\AI challenge\\backend\\Data\\ocr\\merged_results.json"
mapped_data_path = "C:\\Users\\admin\\Projects\\AI challenge\\backend\\Data\\ocr\\updated_results.json"

# Load the merged data from the JSON file
with open(merged_ocr_path, "r") as json_file:
    merged_ocr = json.load(json_file)
with open(merged_results_path, "r") as json_file:
    merged_results = json.load(json_file)
with open(mapped_data_path, "r") as json_file:
    frame_id = json.load(json_file)



# Function to calculate a match score for substring presence
def calculate_substring_score(list_of_querys, text):
    # my_str = 'apple, egg, kiwi'
    # list_of_strings = ['apple', 'egg', 'kiwi']
    if all(substring in text for substring in list_of_querys):
        return 1
    return 0


def convert_paths_b2(original_paths):
    converted_paths = []
    for original_path in original_paths:
        # Split the original path into parts using underscores and remove the file extension
        parts = os.path.splitext(original_path)[0].split('_')
        if len(parts) >= 3:
            # Extract relevant components from the original path
            level, video, frame = parts[0], parts[1], parts[2]
            # Create the new path in the desired format
            new_path = f'Keyframes_{level}/keyframes/{level}_{(video)}/{frame}'
            converted_paths.append(new_path)
        else:
            # Handle paths that don't match the expected format
            print(f"Invalid path format: {original_path}")
    return converted_paths

def merge_txt_files_to_json(base_directory, output_file_path):
    # Initialize an empty dictionary to store the merged data
    merged_data = {}

    # Iterate through L01 to L10
    for n in range(1, 11):
        if n < 10:
          directory_path = os.path.join(base_directory, f'Videos_L0{n}/predict_scene/')
        else:
          directory_path = os.path.join(base_directory, f'Videos_L{n}/predict_scene/')

        if os.path.exists(directory_path):
            # Iterate through the text files in the directory
            print(f"Directory found: {directory_path}")
            for filename in sorted(os.listdir(directory_path)):
                if filename.endswith(".txt"):
                    file_path = os.path.join(directory_path, filename)
                    video_name = os.path.splitext(filename)[0]  # Extract the video name without extension

                    # Read the content of the text file
                    with open(file_path, 'r') as txt_file:
                        lines = txt_file.readlines()

                    # Convert lines to a list of integers
                    lines = [line.strip() for line in lines]

                    # Add the data to the merged_data dictionary
                    merged_data[video_name] = lines
        else:
            print(f"Directory not found: {directory_path}")

    # Write the merged data to the JSON file
    with open(output_file_path, 'w') as json_file:
        json.dump(merged_data, json_file, indent=4)

    print(f"Data merged and saved to {output_file_path}")
    return merged_data
def map_image_to_data(image_filename, merged_data):
    # Extract video name and frame number from the image filename
    parts = image_filename.split("_")
    if len(parts) == 3:
        video_name = "_".join(parts[:2])  # Extract video name with underscores
        frame_number = parts[2].split(".")[0]  # Extract frame number without extension
        # print(video_name,frame_number)
    else:
        return None

    # Construct the key in merged_data
    key = f"{video_name}"

    # Check if the key exists in merged_data
    if key in merged_data:
        data = merged_data[key]
        # Extract the frame number as an integer
        frame_number_int = int(frame_number)
        for line in data:
            # Extract the start and end values from each line
            start, end = map(int, line.strip("[]").split())
            # Check if the frame number is within the range
            if start <= frame_number_int <= end:
                return f"{key}_{start}_{end}"

    return None
def map_format_to_frame_info(format_string, frame_id):
    parts = format_string.split('_')
    if len(parts) == 4:
        n, f, m, p = parts

        n = n[1:]
        f = f[1:]
        frame_idx_range = range(int(m), int(p) + 1)
        # print(m, p)
        if int(n) <10:
          # search_path = f'/content/drive/MyDrive/Transnet/Keyframes/keyframes{n[1:]}/L{n}_V{f}/'
          search_path =f'Keyframes_L{n}/keyframes/L{n}_V{f}/'
        elif int(n) >= 10:
          search_path =f'Keyframes_L{n}/keyframes/L{n}_V{f}/'
        
        flag = 0
        # Iterate through frame_ids to find matching frame_idx and frame_path
        for frame_key, frame_data in frame_id.items():
            frame_idx = frame_data['frame_idx']
            frame_path = frame_data['frame_path']
            # print( frame_idx,frame_path)

            if frame_idx in frame_idx_range and frame_path.startswith(search_path):
                flag = flag + 1
                if(flag == 1):
                    return format_string, frame_idx, frame_path

    return None





# Calculate substring scores for each data entry
def retrieveOCR(query_text, prev_res):
    # if(len(prev_res)):
    results = []
    for key, value in merged_ocr.items():
        substring_score = calculate_substring_score(query_text, value)
        if substring_score > 0:
            results.append((key, value, substring_score))
    # Rank the results by substring score in descending order
    results.sort(key=itemgetter(2), reverse=True)
    listofimgs = [a[0] for a in results]
    listofpaths = []
    listofpathsb2 = []
    l_number = 0
    print(listofimgs)
    for img in listofimgs:
        parts = img.split("_")
        l_number = int(parts[0][1:])
        image_filename = img
        # print(img)
        # print("l number", l_number)
        # For L01 - L10 videos:
        if(l_number <= 10):
            mapped_data = map_image_to_data(image_filename, merged_results)

            # Now, 'merged_results' contains the content of your JSON file


            # format_string = 'L10_V001_347_379'
            matching_entries = map_format_to_frame_info(mapped_data, frame_id)
            if matching_entries:
                mapped_data, frame_idx, frame_path = matching_entries
                listofpaths.append(frame_path)
        # For L10 - L20 videos:
        else:
            print(img)
            listofpathsb2.append(img)
            
    listofpathsb2 = convert_paths_b2(listofpathsb2)
    # print(listofpaths)     
    listofpaths =  listofpaths + listofpathsb2
    unique_paths = list(set(listofpaths))
    return unique_paths[:200]
    # else:
    #     return None




# # # # Test the mapping function
# listofimgs = retrieveOCR(["tien lan"], [])
# # # # # 
# print("retrieval",listofimgs)