import os
import json
import uuid
import requests
from flask import Flask, request, jsonify, render_template, redirect
from flask_basicauth import BasicAuth

from card_detection import detect_card_boxes
from card_cropper import crop_cards, create_thumbnail
from card_ai import identify_and_grade_card, lookup_prices

# ----------------------------------------------------
# Ensure required directories exist (Render safe)
# ----------------------------------------------------
REQUIRED_FOLDERS = [
    "uploads",
    "cropped",
    "session_data",
    "static",
    "static/thumbs"
]

for folder in REQUIRED_FOLDERS:
    os.makedirs(folder, exist_ok=True)

# ----------------------------------------------------
# Flask app
# ----------------------------------------------------
app = Flask(__name__)
app.config.from_object("config")

basic_auth = BasicAuth(app)

# Webhook for Make
WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")


# ----------------------------------------------------
# HOME PAGE (login-protected)
# ----------------------------------------------------
@app.route("/")
@basic_auth.required
def home():
    return render_template("home.html")


# ----------------------------------------------------
# UPLOAD PAGE (login protected)
# ----------------------------------------------------
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

    # Detect bounding boxes
    boxes = detect_card_boxes(filepath)

    # Crop cards
    cropped_paths = crop_cards(filepath, boxes)

    # Identify + grade
    results = []
    for index, card_path in enumerate(cropped_paths, start=1):
        analysis = identify_and_grade_card(card_path)

        # Create thumbnail
        thumb_path = f"static/thumbs/{uuid.uuid4()}.jpg"
        create_thumbnail(card_path, thumb_path)

        results.append({
            "id": index,
            "image": card_path,
            "image_thumb": thumb_path,
            "analysis": analysis
        })

    # Store session file
    session_id = str(uuid.uuid4())
    session_file = f"session_data/{session_id}.json"
    with open(session_file, "w") as f:
        json.dump(results, f, indent=2)

    return redirect(f"/review/{session_id}")


# ----------------------------------------------------
# REVIEW PAGE
# ----------------------------------------------------
@app.route("/review/<session_id>")
@basic_auth.required
def review(session_id):
    session_file = f"session_data/{session_id}.json"

    with open(session_file) as f:
        cards = json.load(f)

    # Add placeholder pricing section
    for card in cards:
        card.setdefault("prices", {})
        card.setdefault("pricing_loaded", False)

    return render_template("review.html", cards=cards, session_id=session_id)


# ----------------------------------------------------
# MULTI-SOURCE PRICE LOOKUP (GPT-5)
# ----------------------------------------------------
@app.route("/price_lookup_multi", methods=["POST"])
@basic_auth.required
def price_lookup_multi():
    data = request.get_json()
    name = data.get("name")
    set_name = data.get("set")

    prices = lookup_prices(name, set_name)

    return jsonify(prices)


# ----------------------------------------------------
# APPROVE CARDS & SEND TO MAKE
# ----------------------------------------------------
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

            # Update user-edited fields
            card["name"] = request.form.get(f"name_{i}")
            card["set"] = request.form.get(f"set_{i}")
            card["number"] = request.form.get(f"number_{i}")
            card["rarity"] = request.form.get(f"rarity_{i}")
            card["condition"] = request.form.get(f"condition_{i}")
            card["price"] = request.form.get(f"price_{i}")

            approved.append(card)

    # Send to Make webhook
    if WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json={"approved_cards": approved})

    return render_template("sent.html", count=len(approved))


# ----------------------------------------------------
# MAIN ENTRYPOINT
# ----------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
