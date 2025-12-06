from PIL import Image
import os

def crop_cards(image_path, box_list):
    img = Image.open(image_path)

    cropped_paths = []
    index = 1

    for box in box_list:
        x = box["x"]
        y = box["y"]
        w = box["width"]
        h = box["height"]

        crop = img.crop((x, y, x + w, y + h))

        output_path = f"cropped/card_{index}.png"
        crop.save(output_path)

        cropped_paths.append(output_path)
        index += 1

    return cropped_paths
