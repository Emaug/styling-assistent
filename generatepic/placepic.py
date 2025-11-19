import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def load_mask(region_name):
    """Load grayscale mask image which is needed to calculate what area the image should be scaled to"""
    mask_path = f"masks/{region_name}.png"
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    ys_mask = np.where(mask == 255)[0]
    y_min_mask = ys_mask.min()
    y_max_mask = ys_mask.max()  # Gets lowest and highest value in the array of all the white
    return mask, y_min_mask, y_max_mask

def load_transparent_image(product):
    """Load transparent image with an alpha channel."""
    img_path = f"Stylist/Downloadedpicture/Downloadedpicture_{product}_transparent.png"
    img = Image.open(img_path).convert("RGBA")
    return img

def resize_image(img, target_height):
    """Scaling the transparent photo to match mask size"""
    scale_ratio = target_height / (img.height)
    new_size = (int(img.width * scale_ratio), target_height)  # Scale width to keep aspect ratio
    return img.resize(new_size, Image.LANCZOS)

def center_image_on_mask(mask_center_y, resized_img):
    """Compute the correct Y position for pasting the resized image."""
    resized_img_np = np.array(resized_img)
    ys_resized = np.where(resized_img_np[:, :, 3] > 0)[0]
    y_min_resized, y_max_resized = ys_resized.min(), ys_resized.max()
    resized_center_offset = (y_min_resized + y_max_resized) // 2
    paste_top_y = mask_center_y - resized_center_offset
    return paste_top_y

def create_square_mask(mask, background_size):
    """Generate a square bounding box mask based on the region mask."""
    ys, xs = np.where(mask == 255)
    x_min, x_max = xs.min(), xs.max()
    y_min, y_max = ys.min(), ys.max()
    box_size = max(x_max - x_min, y_max - y_min) + int(0.1 * max(x_max - x_min, y_max - y_min))
    x1 = max(0, (x_min + x_max) // 2 - box_size // 2)
    x2 = min(background_size[0], (x_min + x_max) // 2 + box_size // 2)
    y1 = max(0, (y_min + y_max) // 2 - box_size // 2)
    y2 = min(background_size[1], (y_min + y_max) // 2 + box_size // 2)
    
    square_mask = np.zeros((background_size[1], background_size[0]), dtype=np.uint8)
    square_mask[y1:y2, x1:x2] = 1
    return square_mask

def process_region(region_name, picer, product):
    """Main function handling the entire image processing pipeline."""
    
    # Load mask and calculate center
    mask, y_min_mask, y_max_mask = load_mask(region_name)
    mask_center_y = (y_min_mask + y_max_mask) // 2
    mask_height = y_max_mask - y_min_mask

    # Resize clothing item to fit placement
    img2 = load_transparent_image(product)
    resized_img2 = resize_image(img2, mask_height)

    # Load person image to put clothes on
    background = Image.open(f"{picer}").convert("RGBA")

    # Compute paste positions
    paste_top_y = center_image_on_mask(mask_center_y, resized_img2)
    paste_x = (background.width - resized_img2.width) // 2

    # Create final composite image
    composite = background.copy()
    composite.paste(resized_img2, (paste_x, paste_top_y), resized_img2)
    composite.save("generatepic/final_composite_centered.png")

    # Create square mask
    square_mask = create_square_mask(mask, (background.width, background.height))
    Image.fromarray(square_mask * 255).save("generatepic/mask_box.png")

    # Convert composite to numpy array for matplotlib
    composite_np = np.array(composite)

    # Setup matplotlib figure with 2 rows, 1 column
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 15))

    # Show composite image on top axis
    ax1.imshow(composite_np)
    ax1.set_title("Composite Image")
    ax1.axis("off")
    ax1.set_aspect(composite_np.shape[1] / composite_np.shape[0])  # width/height ratio

    # Show mask image on bottom axis
    ax2.imshow(square_mask, cmap='gray')
    ax2.set_title("Mask")
    ax2.axis("off")
    ax2.set_aspect(square_mask.shape[1] / square_mask.shape[0])  # width/height ratio

    plt.tight_layout()
    plt.show()

    print("Saved 'final_composite_centered.png' and 'mask_box.png'.")
