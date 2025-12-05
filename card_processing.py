import cv2
import numpy as np
import imutils
import os
import requests


def send_to_make_webhook(file_path, webhook_url):
    """Send cropped card image to Make.com webhook."""
    with open(file_path, "rb") as f:
        files = {
            "file": (os.path.basename(file_path), f, "image/png")
        }
        response = requests.post(webhook_url, files=files)
    return response.status_code


def extract_cards(image_path, output_folder="processed", min_area=5000, webhook_url=None):
    """Detect, crop, and send Pokémon cards to Make."""
    
    os.makedirs(output_folder, exist_ok=True)

    image = cv2.imread(image_path)
    orig = image.copy()

    # Preprocessing
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blur, 50, 150)
    kernel = np.ones((5,5), np.uint8)
    dilated = cv2.dilate(edged, kernel, iterations=1)

    cnts = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    # Find contours
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    card_regions = []

    for c in cnts:
        area = cv2.contourArea(c)
        if area < min_area:
            continue

        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            if h > w:
                card_regions.append((x, y, w, h))

    # Sort cropped cards by (row, col)
    card_regions = sorted(card_regions, key=lambda r: (r[1], r[0]))

    saved_cards = []
    index = 1

    for (x, y, w, h) in card_regions:
        filename = f"card_{index}.png"
        path = os.path.join(output_folder, filename)

        card_crop = orig[y:y+h, x:x+w]
        cv2.imwrite(path, card_crop)

        # Send card to Make webhook
        if webhook_url:
            send_to_make_webhook(path, webhook_url)

        saved_cards.append(path)
        index += 1

    return saved_cards
