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
    f = request.files["image"]
    fname = f"{uuid.uuid4()}.png"
    path = os.path.join("uploads", fname)
    f.save(path)

    # ---------------------------
    # 2. Detect bounding boxes
    # ---------------------------
    detection = detect_card_boxes(path)
    boxes = detection.get("cards", [])
    print("=== RAW DETECTION OUTPUT ===")
    print(detection)

    # ---------------------------
    # 3. Crop cards into images
    # ---------------------------
    cropped = crop_cards(path, boxes)

    cards = []

    # ---------------------------
    # 4. Process each cropped card
    # ---------------------------
    for idx, cpath in enumerate(cropped, start=1):

        print(f"=== CARD AI ANALYSIS: {cpath}")

        # ---- AI identification (name, set, rarity, etc.) ----
        analysis = identify_and_grade_card(cpath)

        # Clean condition → enforce TCG language if needed
        condition = analysis.get("condition", "Near Mint")

        # ---- Live Price Lookup ----
        prices = lookup_prices(analysis["name"], analysis["set"])
        tcg = prices.get("tcgplayer")
        mk = prices.get("cardmarket")

        # Determine best auto price
        auto_price = None
        if tcg and tcg.get("market"):
            auto_price = f"{tcg['market']} CAD"
        elif mk and mk.get("trend"):
            auto_price = f"{mk['trend']} CAD"
        else:
            auto_price = analysis.get("price_ai_estimate", "N/A")

        # ---- Thumbnail ----
        thumb_path = f"static/thumbs/{idx}.jpg"
        create_thumbnail(cpath, thumb_path)

        # ---- Collect card data ----
        cards.append({
            "id": idx,
            "image": cpath,
            "image_thumb": thumb_path,
            "name": analysis.get("name"),
            "set": analysis.get("set"),
            "number": analysis.get("number"),
            "rarity": analysis.get("rarity"),
            "condition": condition,
            "price_ai_estimate": analysis.get("price_ai_estimate"),

            "tcg": tcg,
            "mk": mk,
            "auto_price": auto_price
        })

    # ---------------------------
    # 5. Save session JSON
    # ---------------------------
    session_id = str(uuid.uuid4())
    with open(f"session_data/{session_id}.json", "w") as f:
        json.dump(cards, f, indent=2)

    return redirect(f"/review/{session_id}")


@app.route("/review/<session_id>")
@basic_auth.required
def review(session_id):
    with open(f"session_data/{session_id}.json") as f:
        cards = json.load(f)

    updated_cards = []

    for card in cards:
        # Fetch TCGplayer + Cardmarket live prices
        prices = lookup_prices(card["name"], card["set"])

        # Attach price objects directly to card
        card["tcg"] = prices.get("tcg")
        card["mk"]  = prices.get("mk")

        # Determine best auto price
        ai_est = card.get("price_ai_estimate")

        tcg_market = prices.get("tcg", {}).get("market")
        mk_trend   = prices.get("mk", {}).get("trend")

        if tcg_market:
            card["auto_price"] = tcg_market
        elif mk_trend:
            card["auto_price"] = mk_trend
        else:
            card["auto_price"] = ai_est

        updated_cards.append(card)

    return render_template("review.html", cards=updated_cards, session_id=session_id)



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
        i = card["id"]

        if f"approve_{i}" in request.form:

            card["name"] = request.form.get(f"name_{i}")
            card["set"] = request.form.get(f"set_{i}")
            card["number"] = request.form.get(f"number_{i}")
            card["rarity"] = request.form.get(f"rarity_{i}")
            card["condition"] = request.form.get(f"condition_{i}")
            card["price"] = request.form.get(f"price_{i}")

            approved.append(card)

    # Send to webhook (Make.com)
    requests.post(WEBHOOK_URL, json={"approved_cards": approved})

    return render_template("sent.html", count=len(approved))


if __name__ == "__main__":
    app.run(port=5000)
