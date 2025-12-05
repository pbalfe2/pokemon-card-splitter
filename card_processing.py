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


def extract_cards(image_path, output_folder="processed", webhook_url=None):
    import numpy as np
    import cv2
    import os
    import requests

    os.makedirs(output_folder, exist_ok=True)

    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Compute vertical gradient to detect card boundaries
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
    abs_sobelx = np.absolute(sobelx)
    sobel_norm = np.uint8(255 * abs_sobelx / np.max(abs_sobelx))

    # Sum columns to find vertical edges
    col_sums = np.sum(sobel_norm, axis=0)

    # Threshold peaks to find boundaries
    threshold = np.max(col_sums) * 0.4
    edges = np.where(col_sums > threshold)[0]

    # Group edge columns into boundaries
    boundaries = []
    prev = -100

    for col in edges:
        if col - prev > 10:
            boundaries.append(col)
        prev = col

    # If fewer than 2 boundaries, fallback to full image
    if len(boundaries) < 2:
        boundaries = [0, img.shape[1]]

    # Pair boundaries
    pairs = []
    for i in range(0, len(boundaries) - 1, 1):
        left = boundaries[i]
        right = boundaries[i+1]
        if right - left > 100:  # ensure width > 100px
            pairs.append((left, right))

    saved_cards = []

    index = 1
    for left, right in pairs:
        crop = img[:, left:right]
        
        filename = f"card_{index}.png"
        path = os.path.join(output_folder, filename)
        cv2.imwrite(path, crop)

        # Send to Make webhook
        if webhook_url:
            with open(path, "rb") as f:
                requests.post(webhook_url, files={"file": f})

        saved_cards.append(path)
        index += 1

    return saved_cards
