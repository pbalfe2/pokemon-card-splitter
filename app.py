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

    f = request.files["image"]
    fname = f"{uuid.uuid4()}.png"
    path = os.path.join("uploads", fname)
    f.save(path)

    boxes = detect_card_boxes(path)
    cropped = crop_cards(path, boxes)

    cards = []
    for idx, cpath in enumerate(cropped, start=1):
        analysis = identify_and_grade_card(cpath)
        thumb = f"static/thumbs/{idx}.jpg"
        create_thumbnail(cpath, thumb)

        cards.append({
            "id": idx,
            "image": cpath,
            "image_thumb": thumb,
            "name": analysis["name"],
            "set": analysis["set"],
            "number": analysis["number"],
            "rarity": analysis["rarity"],
            "condition": analysis["condition"],
            "price_ai_estimate": analysis["price_ai_estimate"]
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

    requests.post(WEBHOOK_URL, json={"approved_cards": approved})

    return render_template("sent.html", count=len(approved))


if __name__ == "__main__":
    app.run(port=5000)
