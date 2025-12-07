# app.py
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

# Ensure required folders exist
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

    # ---------------------------
    # 1. Save uploaded image
    # ---------------------------
    file = request.files["image"]
    fname = f"{uuid.uuid4()}.png"
    path = os.path.join("uploads", fname)
    file.save(path)

    # ---------------------------
    # 2. Detect bounding boxes
    # ---------------------------
    detection = detect_card_boxes(path)
    boxes = detection.get("cards", [])

    # ---------------------------
    # 3. Crop cards
    # ---------------------------
    cropped_paths = crop_cards(path, boxes)

    cards = []

    # ---------------------------
    # 4. Process each card
    # ---------------------------
    for idx, cpath in enumerate(cropped_paths, start=1):

        # AI identification
        info = identify_and_grade_card(cpath)

        # Live price lookup
        prices = lookup_prices(info["name"], info["set"])

        # Format price block
        tcg = prices.get("tcg")
        mk = prices.get("mk")
        fx = prices.get("fx")

        # Convert to CAD if available
        cad_values = {
            "tcg_cad": prices.get("tcg_cad"),
            "mk_cad": prices.get("mk_cad")
        }

        # Determine auto price
        if prices.get("tcg_cad"):
            auto_price = f"{prices['tcg_cad']} CAD"
        elif prices.get("mk_cad"):
            auto_price = f"{prices['mk_cad']} CAD"
        else:
            auto_price = info.get("price_ai_estimate")

        # Create thumbnail
        thumb = f"static/thumbs/{idx}.jpg"
        create_thumbnail(cpath, thumb)

        # Build card object
        cards.append({
            "id": idx,
            "image": cpath,
            "image_thumb": thumb,

            "name": info.get("name"),
            "set": info.get("set"),
            "number": info.get("number"),
            "rarity": info.get("rarity"),
            "condition": info.get("condition", "Near Mint"),
            "price_ai_estimate": info.get("price_ai_estimate"),

            "tcg": tcg,
            "mk": mk,
            "fx": fx,
            "tcg_cad": cad_values["tcg_cad"],
            "mk_cad": cad_values["mk_cad"],

            "auto_price": auto_price
        })

    # Save to session file
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
    prices = lookup_prices(data["name"], data["set"])
    return jsonify(prices)


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
            card["price"] = request.form.get(f"price_{cid}")

            approved.append(card)

    requests.post(WEBHOOK_URL, json={"approved_cards": approved})

    return render_template("sent.html", count=len(approved))


if __name__ == "__main__":
    app.run(port=5000)
