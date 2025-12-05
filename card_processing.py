import cv2
import numpy as np
import os
import requests


def send_to_make_webhook(file_path, webhook_url):
    """
    Sends a cropped Pokémon card image to Make.com using a POST webhook.
    """
    with open(file_path, "rb") as f:
        files = {
            "file": (os.path.basename(file_path), f, "image/png")
        }
        response = requests.post(webhook_url, files=files)
    return response.status_code


def extract_cards(image_path, output_folder="processed", webhook_url=None):
    """
    Extracts Pokémon cards from an image arranged horizontally (1–10 cards).
    Uses vertical edge projection for robust detection even with clean PNGs.

    Saves cropped cards to output folder and optionally sends each card
    to a Make.com webhook.
    """

    os.makedirs(output_folder, exist_ok=True)

    # Load image
    img = cv2.imread(image_path)
    if img is None:
        print("ERROR: Could not load image:", image_path)
        return []

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # ---- Vertical Gradient Detection (SobelX) ----
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
    abs_sobelx = np.absolute(sobelx)
    sobel_norm = np.uint8(255 * abs_sobelx / np.max(abs_sobelx))

    # Collapse columns into vertical projection
    col_sums = np.sum(sobel_norm, axis=0)

    # Threshold to find major edges
    threshold = np.max(col_sums) * 0.40
    edges = np.where(col_sums > threshold)[0]

    boundaries = []
    prev = -100

    # Group neighboring edge columns into boundary markers
    for col in edges:
        if col - prev > 10:
            boundaries.append(col)
        prev = col

    # If too few boundaries, fallback to full image (unlikely)
    if len(boundaries) < 2:
        boundaries = [0, img.shape[1]]

    # Convert boundaries into left/right pairs
    pairs = []
    for i in range(len(boundaries) - 1):
        left = boundaries[i]
        right = boundaries[i + 1]

        if right - left > 80:  # Only accept card-sized widths
            pairs.append((left, right))

    saved_cards = []
    index = 1

    # ---- Crop each card ----
    for left, right in pairs:
        crop = img[:, left:right]

        filename = f"card_{index}.png"
        path = os.path.join(output_folder, filename)
        cv2.imwrite(path, crop)

        # ---- Send to Make webhook ----
        if webhook_url:
            send_to_make_webhook(path, webhook_url)

        saved_cards.append(path)
        index += 1

    return saved_cards
