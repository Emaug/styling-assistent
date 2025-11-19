import sqlite3
import re
import random
def fetch_info_by_ids(id_list, lookfor):
    conn = sqlite3.connect("Database/Full_database.db")
    cursor = conn.cursor()

    valid_columns = ["Id", "Name", "Brand", "Description", "Color", "Hex", "Producttype", 
                     "Sleeve", "Neck", "Product", "Picture1", "Picture2", "Picture3", 
                     "Picture4", "Picture5", "Picture6", "Picture7"]

    if lookfor not in valid_columns:
        print("Ogiltigt fält angivet.")
        return None

    placeholders = ','.join(['?'] * len(id_list))

    query = f"""
        SELECT {lookfor} 
        FROM products
        WHERE Id IN ({placeholders})
    """

    cursor.execute(query, id_list)
    results = cursor.fetchall()
    print(results)

    conn.close()

    if results:
        return [item[0] for item in results]
    else:
        print("Inga produkter hittades för de angivna ID:na.")
        return None


def load_by_attribute(product, name_in_name=None, color=None, fit=None, count=3):
    conn = sqlite3.connect("Database/Full_database.db")
    cursor = conn.cursor()

    query = "SELECT Id FROM products WHERE Product = ?"
    params = [product]

    if name_in_name is not None:
        query += " AND Name LIKE ?"
        params.append(f"%{name_in_name}%")

    if color is not None:
        query += " AND Color = ?"
        params.append(color)

    if fit is not None:
        query += " AND Producttype LIKE ?"
        params.append(f"%{fit}%")

    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()

    if result:
        result_ids = list(set([r[0] for r in result]))
        if count == 1:
            return random.choice(result_ids)  
        return random.sample(result_ids, min(count, len(result_ids)))
    else:
        return None if count == 1 else []

def extract_numbers(filename= "Stylist/OllamaTestOutput.txt"):
    with open(filename, 'r') as file:
        content = file.read()
    numbers = re.findall(r'\d+', content)
    return [int(num) for num in numbers]


