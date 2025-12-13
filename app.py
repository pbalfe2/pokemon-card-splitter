import os
import json
import uuid
import requests

from flask import Flask, request, jsonify, render_template, redirect
from flask_basicauth import BasicAuth

from card_detection import detect_card_boxes
from card_cropper import crop_cards, crop_back_cards, create_thumbnail
from card_ai import identify_and_grade_card
from price_lookup import lookup_prices

app = Flask(__name__)
app.config.from_object("config")

basic_auth = BasicAuth(app)

WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")

# Required folders
for folder in ["uploads", "cropped/front", "cropped/back", "static/thumbs", "session_data"]:
    os.makedirs(folder, exist_ok=True)


@app.route("/")
@basic_auth.required
def home():
    return render_template("home.html")


@app.route("/upload", methods=["GET", "POST"])
@basic_auth.required
def upload():
    if request.method == "GET":
        return render_template("upload.html")

    # FRONT upload
    f_front = request.files["front_image"]
    fname_front = f"{uuid.uuid4()}_front.png"
    path_front = os.path.join("uploads", fname_front)
    f_front.save(path_front)

    # detect front card bounding boxes
    detection = detect_card_boxes(path_front)
    boxes = detection.get("cards", [])
    print("=== RAW DETECTION OUTPUT ===")
    print(detection)

    front_cards = crop_cards(path_front, boxes)

    # BACK upload (optional)
    back_cards = None
    if request.form.get("include_back") == "yes" and "back_image" in request.files:
        f_back = request.files["back_image"]
        fname_back = f"{uuid.uuid4()}_back.png"
        path_back = os.path.join("uploads", fname_back)
        f_back.save(path_back)

        back_cards = crop_back_cards(path_back, boxes)

    # AI processing
    cards = []

    for idx, front_path in enumerate(front_cards, start=1):
        print(f"=== CARD AI ANALYSIS: {front_path}")

        analysis = identify_and_grade_card(front_path)
        condition = analysis.get("condition", "Near Mint")

        # LIVE PRICES
        prices = lookup_prices(analysis["name"], analysis["set"])

        tcg = prices.get("tcg")
        mk = prices.get("mk")
        converted = prices.get("converted")

        auto_price = converted.get("cad") or analysis.get("price_ai_estimate", "N/A")

        # thumbnail
        thumb_path = f"static/thumbs/{idx}.jpg"
        create_thumbnail(front_path, thumb_path)

        cards.append({
            "id": idx,
            "front_image": front_path,
            "back_image": back_cards[idx - 1] if back_cards else None,
            "image_thumb": thumb_path,
            "name": analysis["name"],
            "set": analysis["set"],
            "number": analysis["number"],
            "rarity": analysis["rarity"],
            "condition": condition,
            "price_ai_estimate": analysis.get("price_ai_estimate"),
            "tcg": tcg,
            "mk": mk,
            "converted": converted,
            "auto_price": auto_price
        })

    session_id = str(uuid.uuid4())
    with open(f"session_data/{session_id}.json", "w") as f:
        json.dump(cards, f, indent=2)

    return redirect(f"/review/{session_id}")


@app.route("/review/<session_id>")
@basic_auth.required
def review(session_id):
    with open(f"session_data/{session_id}.json") as f:
        cards = json.load(f)
    return render_template("review.html", cards=cards, session_id=session_id)


@app.route("/approve/<session_id>", methods=["POST"])
@basic_auth.required
def approve(session_id):
    with open(f"session_data/{session_id}.json") as f:
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

    requests.post(WEBHOOK_URL, json={"approved_cards": approved})

    return render_template("sent.html", count=len(approved))


if __name__ == "__main__":
    app.run(port=5000)
