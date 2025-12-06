from PIL import Image

def crop_cards(image_path, boxes):
    image = Image.open(image_path)
    cropped_paths = []

    for b in boxes:
        left = b["x"]
        top = b["y"]
        right = left + b["width"]
        bottom = top + b["height"]

        crop = image.crop((left, top, right, bottom))
        out_path = f"cropped/card_{b['index']}.png"
        crop.save(out_path)

        cropped_paths.append(out_path)

    return cropped_paths


def create_thumbnail(input_path, output_path, size=(200, 200)):
    from PIL import Image

    img = Image.open(input_path)

    # Convert RGBA → RGB so JPEG can be written
    if img.mode == "RGBA":
        img = img.convert("RGB")

    img.thumbnail(size)
    img.save(output_path, "JPEG")
