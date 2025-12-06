# card_cropper.py
from PIL import Image
import os


def crop_cards(image_path, boxes):
    img = Image.open(image_path)
    out_paths = []

    for card in boxes:
        x, y = card["x"], card["y"]
        w, h = card["width"], card["height"]

        crop = img.crop((x, y, x + w, y + h))

        out_path = f"cropped/card_{card['index']}.png"
        os.makedirs("cropped", exist_ok=True)
        crop.save(out_path)

        out_paths.append(out_path)

    return out_paths


def create_thumbnail(source, dest):
    img = Image.open(source)

    if img.mode == "RGBA":
        img = img.convert("RGB")

    img.thumbnail((300, 300))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    img.save(dest, format="JPEG")
