from PIL import Image
import os

# ------------------------------------------------------------
# Crop cards from the source image using bounding boxes
# ------------------------------------------------------------
def crop_cards(src_path, boxes):
    img = Image.open(src_path)

    cropped_files = []
    index = 1

    for box in boxes:
        x = int(box["x"])
        y = int(box["y"])
        w = int(box["width"])
        h = int(box["height"])

        cropped = img.crop((x, y, x + w, y + h))

        path = f"cropped/card_{index}.png"
        cropped.save(path)
        cropped_files.append(path)

        index += 1

    return cropped_files


# ------------------------------------------------------------
# Create thumbnail (auto-converts RGBA → RGB for JPEG)
# ------------------------------------------------------------
def create_thumbnail(src_path, output_path, size=(200, 200)):
    img = Image.open(src_path)

    # Fix: JPEG cannot save RGBA images
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img.thumbnail(size)
    img.save(output_path, "JPEG")
