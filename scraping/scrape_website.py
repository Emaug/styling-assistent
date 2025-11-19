import requests
from bs4 import BeautifulSoup
import re
import os
from tqdm import tqdm
import time
import json

def sanitize_filename(filename):
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename.replace('\u00E4', 'a')
    filename = filename.strip()
    return filename

def scrape_website(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        with open('Scraping/scraped.txt', 'w', encoding='utf-8') as file:
            file.write(soup.prettify())
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

def extract_info(input_file, product_input):
    data_dict = {
        "Name": "", "Brand": "Jack & Jones", "Description": None, "Color": None, "Hex": None, 
        "Producttype": None, "Waist": None, "Sleeve": None, "Neck": None, "Fit": None, "Id": None,
        "Product": product_input, "Function": None
    }

    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    if '<title>' in content and '</title>' in content:
        start_index = content.find('<title>') + len('<title>')
        end_index = content.find('|')
        title_content = content[start_index:end_index].strip()
    else:
        return None

    sanitized_product_name = sanitize_filename(title_content)
    name = sanitized_product_name.replace(' ', '_')
    data_dict["Name"] = name

    patterns = {
        'Brand': r'"brand":"(.*?)"',
        'Description': r'"og:description","content":"(.*?) - Produkttyp',
        'Color': r'"colour":\{.*?"name":"(.*?)".*?"hexCode":"(.*?)"',
        'Images': r'"images":\[(.*?)\]',
        'Fit': r'Passform : (.*?)(?=\s*")',
        'Produkttyp': r'<title>\s*(.*?)\s*\|',
        'Waist': r'Livhöjd\s*:\s*([^"-]+)',
        'Manga': r'Manga\s*:\s*(.*?)(?=\s*[-"]|$)',
        'Neck': r'Nacken\s*:\s*(.*?)(?=\s*[-"]|$)',
        'Fill': r'Fyllning\s*:\s*(.*?)(?=\s*[-"\n]|$)',
        'Foder': r'Foder\s*:\s*(.*?)(?=\s*[-"\n]|$)',
        'Cuffs': r'Manschetter\s*:\s*(.*?)(?=\s*[-"\n]|$)',
        'Pocket': r'Fickor\s*:\s*(.*?)(?=\s*[-"\n]|$)',
        'Closure': r'Stängning\s*:\s*(.*?)(?=\s*[-"\n]|$)',
        'Functionality': r'Funktionalitet\s*:\s*(.*?)(?=\s*[-"\n]|$)',
        'Id': r'"sku"\s*:\s*"(\d[^_"]*)'
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            if field == 'Color':
                data_dict["Color"] = match.group(1)
                data_dict["Hex"] = match.group(2)
            elif field == 'Id':
                data_dict["Id"] = match.group(1)
            elif field == 'Produkttyp':
                data_dict["Producttype"] = match.group(1)
            elif field == 'Fill':
                data_dict["Filling"] = match.group(1)
            elif field == 'Functionality':
                data_dict["Function"] = match.group(1)
            elif field == 'Manga':
                data_dict["Sleeve"] = match.group(1)
            elif field == 'Neck':
                data_dict["Neck"] = match.group(1)
            elif field == 'Brand':
                data_dict["Brand"] = match.group(1)
            elif field == 'Description':
                data_dict["Description"] = match.group(1).replace(r'\r\n', '').replace(r'\n', '')
            elif field == 'Images':
                urls = re.findall(r'"(https?://[^"]+)"', match.group(1))
                for i, url in enumerate(urls, start=1):
                    data_dict[f"Picture{i}"] = url
            elif field == 'Fit':
                data_dict["Fit"] = match.group(1)
            elif field == 'Waist':
                data_dict["Waist"] = match.group(1)
            elif field == 'Foder':
                data_dict["Foder"] = match.group(1)
            elif field == 'Cuffs':
                data_dict["Cuffs"] = match.group(1)
            elif field == 'Pocket':
                data_dict["Pocket"] = match.group(1)
            elif field == 'Closure':
                data_dict["Closure"] = match.group(1)


    # If the link is valid or not, so if the item is removed but link is still active dont count it
    if data_dict["Description"] is None and data_dict["Color"] is None and data_dict["Hex"] is None:
        return None

    return data_dict

def remove_null_fields(data_dict):
    return {k: v for k, v in data_dict.items() if v is not None}

def save_to_big_json(data_list, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data_list, f, indent=4, ensure_ascii=False)

def scrape(name):
    product_input = name
    start_time = time.time()
    filename = f"links/{name}.txt"
    line_count = sum(1 for _ in open(filename, "r", encoding='utf-8'))
    all_products = []
    with open(filename, "r", encoding='utf-8') as file:
        for line in tqdm(file, total=line_count, desc="Processing", unit="line", ncols=100):
            url = line.strip()
            if not url:
                continue
            scrape_website(url)
            product_data = extract_info("scraped.txt", product_input)
            if product_data:
                product_data = remove_null_fields(product_data)
                all_products.append(product_data)

    output_json_file = os.path.join(f"jackandjones_json", {product_data}+".json")
    if not os.path.exists(os.path.dirname(output_json_file)):
        os.makedirs(os.path.dirname(output_json_file))

    save_to_big_json(all_products, output_json_file)

    end_time = time.time()
    duration = end_time - start_time
    hours, rem = divmod(duration, 3600)
    minutes, seconds = divmod(rem, 60)
    print(f"Execution time: {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds")
    print(f"All products saved to {output_json_file}")

