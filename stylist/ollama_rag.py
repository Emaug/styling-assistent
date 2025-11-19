import ollama
from Stylist.embedded_vectorbase_and_rag import get_make_embeddings
from Stylist.embedded_vectorbase_and_rag import parse
from Stylist.embedded_vectorbase_and_rag import find_most_similar
from Stylist.get_info_db import fetch_info_by_ids


def suggestion():
    system_prompt = f"""
You are a fashion assistant who gives suggestions based on the user's question and previous outfits.
Only respond based on the context below. Create a new unique outfit idea with only the following options:

Jackets: Tackvast, Coat, Parkas, Bomber Jacket

Pants: Jeans, Chinos, Trouser (fit: Loose, Relaxed, Loose, Baggy, Normal, Slim)

Shoes: Sneakers, Boots, Boots, Slippers, Loafers

Sweatshirts: Hoodie, Sweatshirt

Colors: Blue, Green, Red, Black, White, Beige, Yellow

The format of the response should only be, no sentences:
max 3 items
Pants or Jeans (depending on the one you chose): [pants type], [color], [fit]
Shoes: [shoe type], [color]
sweatshirt for warmer and jacket for colder and t-shirt for warmest [type] [color]

answer in this format
Example:

Pants: Jeans, Blue, Slim,
Shoes: Sneakers, White,
Sweatshirt: Hoodie, Red,
Jacket: Bomber Jacket, Beige

Only answer with one outfit with no sentence
\n\n
""".strip()

    filename = "outfit-databas.txt"
    chunks = parse(filename)
    embeddings = get_make_embeddings(filename, "nomic-embed-text", chunks)

    prompt = input("What outfit are you looking for ->: ")
    prompt_embedding = ollama.embeddings(model="nomic-embed-text", prompt=prompt)["embedding"]

    most_similar_chunks = find_most_similar(prompt_embedding, embeddings)[:2]
    response = ollama.chat(
        model="gemma3", # Not the best model for rag but it works ok
        messages=[
            {
                "role": "system",
                "content": system_prompt + "\n\n".join(chunks[i[1]] for i in most_similar_chunks),
            },
            {"role": "user", "content": prompt},
        ],
    )
    output = response['message']['content']
    with open("Stylist/OllamaTestOutput.txt", "w", encoding="utf-8") as f:
        f.write(output)

def prepare_product_data(id_groups):
    """
    Takes a list of ID groups and returns a structured list of product info dictionaries.
    """
    all_values = []
    for group in id_groups:
        values = []
        for item_id in group:
            product_info = {
                "id": item_id,
                "color": fetch_info_by_ids([item_id], "Color")[0],
                "product_type": fetch_info_by_ids([item_id], "Producttype")[0]
            }
            values.append(product_info)
        all_values.append(values)
    return all_values

