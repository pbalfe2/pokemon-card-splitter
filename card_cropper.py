from PIL import Image

def crop_cards(image_path, box_list):
    img = Image.open(image_path)
    paths = []

    for idx, box in enumerate(box_list, start=1):
        x, y, w, h = box["x"], box["y"], box["width"], box["height"]
        crop = img.crop((x, y, x + w, y + h))

        out = f"cropped/front/card_{idx}.png"
        crop.save(out)
        paths.append(out)

    return paths


def crop_back_cards(image_path, box_list):
    img = Image.open(image_path)
    paths = []

    for idx, box in enumerate(box_list, start=1):
        x, y, w, h = box["x"], box["y"], box["width"], box["height"]
        crop = img.crop((x, y, x + w, y + h))

        out = f"cropped/back/card_{idx}.png"
        crop.save(out)
        paths.append(out)

    return paths


def create_thumbnail(input_path, output_path, size=(220, 220)):
    img = Image.open(input_path)

    if img.mode == "RGBA":
        img = img.convert("RGB")

    img.thumbnail(size)
    img.save(output_path, "JPEG", quality=90)
