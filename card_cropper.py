import os
from PIL import Image

# Ensure output directories exist
os.makedirs("cropped", exist_ok=True)
os.makedirs("thumbnails", exist_ok=True)


def crop_cards(image_path, box_list):
    """
    Crops card images from the detected bounding boxes.
    Returns a list of paths to the cropped images.
    """
    img = Image.open(image_path)
    cropped_paths = []

    for idx, box in enumerate(box_list, start=1):
        x = box["x"]
        y = box["y"]
        w = box["width"]
        h = box["height"]

        crop = img.crop((x, y, x + w, y + h))
        output_path = f"cropped/card_{idx}.png"
        crop.save(output_path)

        cropped_paths.append(output_path)

    return cropped_paths


def create_thumbnail(input_path, output_path, size=(200, 200)):
    """
    Creates a thumbnail of the cropped card image.
    Ensures PNG → JPEG conversion works on Render by removing alpha channels.
    """
    img = Image.open(input_path)

    # Convert RGBA → RGB (fixes “cannot write mode RGBA as JPEG” error)
    if img.mode == "RGBA":
        img = img.convert("RGB")

    img.thumbnail(size)
    img.save(output_path, "JPEG", quality=90)
