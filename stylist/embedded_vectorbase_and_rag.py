import ollama
import time
import os
import json
import numpy as np
from numpy.linalg import norm

# Define the base directory for all file operations
BASE_DIR = "Stylist"
EMBEDDINGS_DIR = os.path.join(BASE_DIR, "embeddings")

def parse(filename):
    filepath = os.path.join(BASE_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        all = f.read()
    block_list = all.split('\n\n')
    strings = []
    for blocks in block_list:
        row = blocks.replace('\n', ' ')
        strings.append(row)
    return strings

def save_embeddings(filename, embeddings):
    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
    filepath = os.path.join(EMBEDDINGS_DIR, f"{filename}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(embeddings, f)

def load_embeddings(filename):
    filepath = os.path.join(EMBEDDINGS_DIR, f"{filename}.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return False

def get_make_embeddings(filename, modelname, chunks):
    if (embeddings := load_embeddings(filename)):
        return embeddings
    # In case the file does not exist
    embeddings = [ollama.embeddings(model=modelname, prompt=chunk)["embedding"] for chunk in chunks]
    save_embeddings(filename, embeddings)
    return embeddings

def find_most_similar(needle, haystack):
    needle_norm = norm(needle)
    similarity_scores = [
        np.dot(needle, item) / (needle_norm * norm(item)) for item in haystack
    ]
    return sorted(zip(similarity_scores, range(len(haystack))), reverse=True)
