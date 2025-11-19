import json
import glob

def merge():
    directory = "jackandjones/*.json"

    # Gets all Json files in folder and saves it in filenames
    filenames = glob.glob(directory)

    # Temporary storing all Json files 
    merged_data = []

    for filename in filenames:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list):  
                merged_data.extend(data)
            else:
                merged_data.append(data)


    output_file = "jackandjones/combined.json"
    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(merged_data, outfile, indent=4, ensure_ascii=False)