import cv2
import numpy as np
import imutils
import os

def extract_cards(image_path, output_folder="processed", min_area=15000):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image = cv2.imread(image_path)
    orig = image.copy()

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blur, 50, 150)

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

    card_regions = sorted(card_regions, key=lambda r: (r[1], r[0]))

    saved_cards = []

    index = 1
    for (x, y, w, h) in card_regions:
        card = orig[y:y+h, x:x+w]
        filename = f"card_{index}.png"
        path = os.path.join(output_folder, filename)
        cv2.imwrite(path, card)
        saved_cards.append(path)
        index += 1

    return saved_cards
