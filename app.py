import os
import json
import uuid
import requests

from flask import Flask, request, jsonify, render_template, redirect
from flask_basicauth import BasicAuth

from card_detection import detect_card_boxes
from card_cropper import crop_cards, create_thumbnail
from card_ai import identify_and_grade_card
from price_lookup import lookup_prices

app = Flask(__name__)
app.config.from_object("config")

basic_auth = BasicAuth(app)

WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")

# Ensure folders exist
for folder in ["uploads", "cropped", "static/thumbs", "session_data"]:
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

    # 1. Save uploaded image
    f = request.files["image"]
    fname = f"{uuid.uuid4()}.png"
    path = os.path.join("uploads", fname)
    f.save(path)

    print("=== CARD DETECTION START:", path)

    # 2. Detect bounding boxes
    det = detect_card_boxes(path)
    print("=== RAW DETECTION OUTPUT ===")
    print(det)

    boxes = det.get("cards", [])
    if not isinstance(boxes, list):
        boxes = []

    # 3. Crop cards
    cropped_paths = crop_cards(path, boxes)

    cards = []

    # 4. Identify & grade each card individually
    for idx, cpath in enumerate(cropped_paths, start=1):
        print(f"=== CARD AI ANALYSIS: {cpath}")

        analysis = identify_and_grade_card(cpath)

        # 5. Lookup live prices
        prices = lookup_prices(
            analysis.get("name", ""),
            analysis.get("set", "")
        )

        # OR fallback to AI
        auto_price = (
            prices.get("best_price")
            or analysis.get("price_ai_estimate")
            or "N/A"
        )

        # 6. Thumbnail
        thumb = f"static/thumbs/{uuid.uuid4()}.jpg"
        create_thumbnail(cpath, thumb)

        # 7. Build card object for review.html (no nested dicts!)
        cards.append({
            "id": idx,
            "image": cpath,
            "image_thumb": thumb,

            "name": analysis.get("name"),
            "set": analysis.get("set"),
            "number": analysis.get("number"),
            "rarity": analysis.get("rarity"),
            "condition": analysis.get("condition"),

            "price_ai_estimate": analysis.get("price_ai_estimate"),

            # Live market prices
            "tcg": prices.get("tcgplayer"),
            "mk": prices.get("cardmarket"),
            "auto_price": auto_price
        })

    # 8. Save session
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


@app.route("/price_lookup", methods=["POST"])
def price_api():
    data = request.json
    name = data["name"]
    set_name = data["set"]

    prices = lookup_prices(name, set_name)
    return jsonify(prices=prices)


@app.route("/approve/<session_id>", methods=["POST"])
@basic_auth.required
def approve(session_id):
    with open(f"session_data/{session_id}.json") as f:
        cards = json.load(f)

    approved = []

    for card in cards:
        cid = card["id"]

        if f"approve_{cid}" in request.form:
            card["name"] = request.form.get(f"name_{cid}")
            card["set"] = request.form.get(f"set_{cid}")
            card["number"] = request.form.get(f"number_{cid}")
            card["rarity"] = request.form.get(f"rarity_{cid}")
            card["condition"] = request.form.get(f"condition_{cid}")

            # If user wants live prices
            use_live = f"use_live_{cid}" in request.form
            if use_live:
                prices = lookup_prices(card["name"], card["set"])
                card["price"] = (
                    prices.get("best_price")
                    or card.get("price_ai_estimate")
                    or "N/A"
                )
            else:
                card["price"] = request.form.get(f"price_{cid}")

            approved.append(card)

    # Send to Make.com webhook
    requests.post(WEBHOOK_URL, json={"approved_cards": approved})

    return render_template("sent.html", count=len(approved))


if __name__ == "__main__":
    app.run(port=5000)
