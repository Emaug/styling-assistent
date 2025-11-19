import requests
import numpy as np
from PIL import Image
from io import BytesIO

def download_and_remove_background(url, name, threshold=10):
    response = requests.get(url, stream=True)
    save_path_png=f"stylist/Downloadedpicture/Downloadedpicture_{name}_transparent.png"
    
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        data = np.array(img)
        
        # Depending if the picture has white or black background
        black_pixels = np.all(data[:, :, :3] < threshold, axis=2)
        white_pixels = np.all(data[:, :, :3] > 255 - threshold, axis=2)

        mask = black_pixels | white_pixels
        data[mask] = [0, 0, 0, 0]

        result_img = Image.fromarray(data) 
        result_img.save(save_path_png)
    else:
        print("Picture did not downlaod")

