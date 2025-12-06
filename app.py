import os
import json
import uuid
import requests
from flask import Flask, request, jsonify, render_template, redirect
from flask_basicauth import BasicAuth

from card_detection import detect_card_boxes
from card_cropper import crop_cards, create_thumbnail
from card_ai import identify_and_grade_card

# --------------------------------------
# Ensure directories exist on Render
# --------------------------------------
REQUIRED_FOLDERS = [
    "uploads",
    "cropped",
    "session_data",
    "static",
    "static/thumbs"
]

for folder in REQUIRED_FOLDERS:
    os.makedirs(folder, exist_ok=True)

app = Flask(__name__)
app.config.from_object("config")

basic_auth = BasicAuth(app)

WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")


# -----------------------------------------
# HOME PAGE (Protected)
# -----------------------------------------
@app.route("/")
@basic_auth.required
def home():
    return render_template("home.html")


# -----------------------------------------
# UPLOAD PAGE (Protected)
# -----------------------------------------
@app.route("/upload", methods=["GET", "POST"])
@basic_auth.required
def upload():
    if request.method == "GET":
        return render_template("upload.html")

    # Save uploaded file
    uploaded = request.files["image"]
    filename = f"{uuid.uuid4()}.png"
    filepath = os.path.join("uploads", filename)
    uploaded.save(filepath)

    # 1. Detect card bounding boxes
    boxes = detect_card_boxes(filepath)

    # 2. Crop cards
    cropped_paths = crop_cards(filepath, boxes)

    # 3. Identify + grade each card
    results = []
    for index, card_path in enumerate(cropped_paths, start=1):
        analysis = identify_and_grade_card(card_path)

        # 4. Create thumbnail
        thumb_path = f"static/thumbs/card_{index}.jpg"
        create_thumbnail(card_path, thumb_path)

results.append({
    "id": index,
    "image": card_path,
    "image_thumb": thumb_path,
    "name": analysis.get("name", ""),
    "set": analysis.get("set", ""),
    "number": analysis.get("number", ""),
    "rarity": analysis.get("rarity", ""),
    "condition": analysis.get("condition", ""),
    "price": analysis.get("price", "")
})


    # 5. Save session data
    session_id = str(uuid.uuid4())
    session_file = f"session_data/{session_id}.json"
    with open(session_file, "w") as f:
        json.dump(results, f, indent=2)

    return redirect(f"/review/{session_id}")


# -----------------------------------------
# REVIEW PAGE (Protected)
# -----------------------------------------
@app.route("/review/<session_id>")
@basic_auth.required
def review(session_id):
    session_file = f"session_data/{session_id}.json"
    with open(session_file) as f:
        cards = json.load(f)

    return render_template("review.html", cards=cards, session_id=session_id)


# -----------------------------------------
# APPROVAL SUBMISSION (Protected)
# -----------------------------------------
@app.route("/approve/<session_id>", methods=["POST"])
@basic_auth.required
def approve(session_id):
    session_file = f"session_data/{session_id}.json"
    with open(session_file) as f:
        cards = json.load(f)

    approved = []

    for card in cards:
        i = card["id"]
        if f"approve_{i}" in request.form:

            card["name"] = request.form.get(f"name_{i}")
            card["set"] = request.form.get(f"set_{i}")
            card["number"] = request.form.get(f"number_{i}")
            card["rarity"] = request.form.get(f"rarity_{i}")
            card["condition"] = request.form.get(f"condition_{i}")
            card["price"] = request.form.get(f"price_{i}")

            approved.append(card)

    # Send approved cards to Make
    requests.post(WEBHOOK_URL, json={"approved_cards": approved})

    return render_template("sent.html", count=len(approved))


# -----------------------------------------
# RUN APP
# -----------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
