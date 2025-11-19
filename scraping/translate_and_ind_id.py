import json
from deep_translator import GoogleTranslator

def translate_text(text, target='en'):
    try:
        return GoogleTranslator(source='auto', target=target).translate(text)
    except Exception as e:
        return text

def translate_recursive(data):
    if isinstance(data, dict):
        return {key: translate_recursive(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [translate_recursive(item) for item in data]
    elif isinstance(data, str):
        return translate_text(data)
    else:
        return data

def translate():
    with open('Scraping/jackandjones/combined.json', 'r', encoding='utf-8') as f:
        original_data = json.load(f)

    translated_data = []

    if isinstance(original_data, list):
        for idx, item in enumerate(original_data):
            print(f"Translating item {idx + 1}/{len(original_data)}...")
            translated_item = translate_recursive(item)
            translated_item["Ind_id"] = idx  
            translated_data.append(translated_item)
    else:
        print("JSON root is not a list — translating whole structure.")
        translated_item = translate_recursive(original_data)
        translated_item["Ind_id"] = 0
        translated_data.append(translated_item)

    with open('Scraping/jackandjones/translated_combined.json', 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, indent=4, ensure_ascii=False)
