from PIL import Image
import matplotlib.pyplot as plt
from stylist.ollama_rag import suggestion
from stylist.get_info_db import fetch_info_by_ids
from stylist.downloadpictures import download_and_remove_background
from stylist.filter_by_attribute import load_answer_from_lines
from generatepic.placepic import process_region
from generatepic.Inpaint_with_Lora import inpaint_image
import random
import os

initimage = ""
initmask= ""

def check(link, product):
    global initimage, initmask
    if product == "Shoes":
        initimage = "generatepic/output_image.png"
        initmask= "generatepic/mask_box.png" 
        return
    initimage = "generatepic/final_composite_centered.png"
    initmask= "generatepic/mask_box.png" 
    download_and_remove_background(link, product)
    if product == "Pants":
        process_region("lowerbody", "generatepic/output_image.png",product)
    if product == "Sweatshirt":
        process_region("midtorso", "generatepic/output_image.png",product)
    if product == "Jacket":
        process_region("midtorso", "generatepic/output_image.png",product)

def generatepic(id_list):
    for ids in id_list[:3]:
        link = fetch_info_by_ids(ids, "Picture3")[0]
        print(link)
        product = fetch_info_by_ids(ids, "Product")[0]
        print("Här har vi all info ", ids, fetch_info_by_ids(ids, "Name")[0])

        check(link, product)
        prompt = fetch_info_by_ids(ids, "Color")[0] + " " + fetch_info_by_ids(ids, "Name")[0]


        inpaint_image(initimage, initmask, prompt, 15)
        print(product)

        
def attributes_to_id(attribute_list):
    clothing_id=[]
    for ids in attribute_list:
        clothing_id.extend(load_answer_from_lines([ids], count=3))
    print("\nThis is the outfit I could generate for you: ")
    for ids in clothing_id:
        print(fetch_info_by_ids(ids,"Product")[0], ", ", fetch_info_by_ids(ids,"Color")[0], ", ", fetch_info_by_ids(ids,"Producttype")[0])
        
    print("\nIf you are not satisfied, remake your outfit, y or any key")
    answer = input("input your wish ->: ")
    if answer == "y":
        return randomness()
    print("Clothing id ",clothing_id)
    generatepic(clothing_id)
    

def ask():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Ok, you need a style match a certain event")
    print("This will work if you describe where you are going, if its hot or cold, and during what season, more detail the better! ")
    suggestion()
    
    with open("Stylist/OllamaTestOutput.txt", "r", encoding="utf-8") as f:
        test = f.readlines()
    print("\nThese are the attributes would match your event: ")
    attributes_to_id(test)

def get_pants():
    pants = input("(Jeans or Pants)->: ").strip().capitalize()
    if pants == '':
        pants = random.choice(["Pants", "Jeans"])
        style = "Jeans"
    elif pants == "Pants":
        pants = "Pants"
        style = input("(Trousers/Joggers etc)->: ") or "None"

    elif(pants == "Jeans"):
        style = "Jeans"
    else:
        print("Invalid option")
        return get_pants()
    color = input(f"Color of {pants}->: ").capitalize() or "None"
    fit = input("Fit->: ").capitalize() or "None"
    
    return f"{pants}: {style}, {color}, {fit}"

def get_upper():
    upper = input("(Sweatshirt/Jacket)->: ").strip().capitalize()
    if upper == '':
        upper = random.choice(["Sweatshirt", "Jacket"])
    if upper == "Sweatshirt":
        style = input("(Hoodie/Crewneck etc)->: ") or "None"
    elif upper == "Jacket":
        style = input("(Bomber/Teddy etc)->: ") or "None"
    elif(upper != "Jeans"):
        print("Invalid option")
        return get_upper()
    color = input("Color->: ") or "None"
    return f"{upper}: {style}, {color}"

def get_shoes():
    shoes = input("Shoes->: ") or "None"
    color = input("Color->: ") or "None"
    return f"Shoes: {shoes}, {color}"

def randomness():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\nOk, you need help finding new clothes, got it!")
    print("If you have any preferences I will do my best and try to see if we have that in stock.")
    print("Follow the instructions below and if you are unsure hit enter to not include that attribute")
    attributes = [get_pants(), get_shoes(), get_upper()]
    print(attributes)
    print("\nThank you, I will now try and do my best\n")
    attributes_to_id(attributes)
    
def display_welcome_message():
    """Displays the welcome message for the StyleMate application."""
    print("\n Welcome to StyleMate – Your Personal Fashion Assistant! \n")
    print("Whether you're heading to a meeting, going out with friends,")
    print("or just looking for fashion advice for a trip, StyleMate is here to help.\n")
    print("You can choose from the following options:\n")

def display_menu():
    """Displays the main menu options."""
    print("1. Get a random outfit suggestion based on your destination.")
    print("2. Receive style tips to upgrade your look.")
    print("0. Exit")
    print()

def load_default_image():
    """Loads and saves the default image."""
    try:
        image = Image.open("Stylist/Downloadedpicture/person.png")
        image.save("generatepic/output_image.png")
    except FileNotFoundError:
        print("Default image not found. Please check the file path.\n")

def get_user_choice():
    """Prompts the user for input and returns the validated choice."""
    return input("How can I help you -> ").strip()

def show_image_with_matplotlib(image_path):
    img = Image.open(image_path)
    plt.imshow(img)
    plt.axis('off')  
    plt.title("Output Image")
    plt.show()

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    display_welcome_message()
    while True:
        load_default_image()
        display_menu()
        choice = get_user_choice()
        if choice == "1":
            ask()
            show_image_with_matplotlib("generatepic/output_image.png")
        elif choice == "2":
            randomness()
            show_image_with_matplotlib("generatepic/output_image.png")
        elif choice == "0":
            print("\nThanks for using StyleMate. Stay stylish!\n")
            break
        else:
            print("Invalid input. Please choose 1, 2, or 0.\n")
if __name__ == "__main__":
    main()

