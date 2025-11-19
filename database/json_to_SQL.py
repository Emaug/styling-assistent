import json
import sqlite3

def json_to_sql():
    # Create or update Full_database.db
    conn = sqlite3.connect("Database/Full_database.db")
    cursor = conn.cursor()

    # Create "Template"
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        Id TEXT PRIMARY KEY,
        Name TEXT,
        Brand TEXT,
        Description TEXT,
        Color TEXT,
        Hex TEXT,
        Producttype TEXT,
        Sleeve TEXT,
        Neck TEXT,
        Product TEXT,
        Picture1 TEXT,
        Picture2 TEXT,
        Picture3 TEXT,
        Picture4 TEXT,
        Picture5 TEXT,
        Picture6 TEXT,
        Picture7 TEXT,
        Ind_id INTEGER
    )
    ''')

    # Read whole file
    with open('Scraping/Jackandjones/translated_combined.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Iterating through JSON format, using '?' to prevent SQL injections
    for item in data:
        cursor.execute('''
            INSERT OR REPLACE INTO products (
                Id, Name, Brand, Description, Color, Hex, Producttype,
                Sleeve, Neck, Product,
                Picture1, Picture2, Picture3, Picture4, Picture5, Picture6, Picture7,
                Ind_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item.get('Id'),
            item.get('Name'),
            item.get('Brand'),
            item.get('Description'),
            item.get('Color'),
            item.get('Hex'),
            item.get('Producttype'),
            item.get('Sleeve'),
            item.get('Neck'),
            item.get('Product'),
            item.get('Picture1'),
            item.get('Picture2'),
            item.get('Picture3'),
            item.get('Picture4'),
            item.get('Picture5'),
            item.get('Picture6'),
            item.get('Picture7'),
            item.get('Ind_id')  
        ))

    # Save changes and close connection
    conn.commit()
    conn.close()

    print("Products have been saved to SQL Database")
