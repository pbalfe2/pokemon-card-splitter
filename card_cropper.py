from PIL import Image
import os
import uuid

def crop_cards(original_path, boxes):
    cropped_paths = []
    img = Image.open(original_path)

    for box in boxes:
        x = box["x"]
        y = box["y"]
        w = box["width"]
        h = box["height"]

        crop = img.crop((x, y, x + w, y + h))

        # force RGB output (no PNG alpha problems)
        crop = crop.convert("RGB")

        filename = f"cropped/card_{uuid.uuid4()}.jpg"
        os.makedirs("cropped", exist_ok=True)
        crop.save(filename, "JPEG", quality=95)

        cropped_paths.append(filename)

    return cropped_paths


def create_thumbnail(input_path, output_path, size=(300, 300)):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    img = Image.open(input_path)

    # Convert to RGB to avoid RGBA → JPEG crash
    if img.mode in ("RGBA", "LA"):
        img = img.convert("RGB")

    img.thumbnail(size)
    img.save(output_path, "JPEG", quality=90)
