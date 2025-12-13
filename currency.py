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
from currency import convert_prices  # NEW for USD/EUR/CAD support

app = Flask(__name__)
app.config.from_object("config")

basic_auth = BasicAuth(app)

WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")

# Ensure required folders exist
for folder in ["uploads/front", "uploads/back", "cropped/front", "cropped/back",
               "static/thumbs/front", "static/thumbs/back", "session_data"]:
    os.makedirs(folder, exist_ok=True)


# ------------------------------------------------------------
# HOME
# ------------------------------------------------------------
@app.route("/")
@basic_auth.required
def home():
    return render_template("home.html")


# ------------------------------------------------------------
# UPLOAD PAGE (FRONT + BACK)
# ------------------------------------------------------------
@app.route("/upload", methods=["GET", "POST"])
@basic_auth.required
def upload():
    if request.method == "GET":
        return render_template("upload.html")

    # ---------------------------
    # 1. Save FRONT image
    # ---------------------------
    f_front = request.files["image_front"]
    front_name = f"{uuid.uuid4()}.png"
    front_path = os.path.join("uploads/front", front_name)
    f_front.save(front_path)

    # ---------------------------
    # 2. Optional BACK image
    # ---------------------------
    has_back = "use_back" in request.form
    back_path = None

    if has_back and "image_back" in request.files:
        f_back = request.files["image_back"]
        back_name = f"{uuid.uuid4()}.png"
        back_path = os.path.join("uploads/back", back_name)
        f_back.save(back_path)

    # ---------------------------
    # 3. Detect bounding boxes on FRONT ONLY
    # ---------------------------
    det = detect_card_boxes(front_path)
    boxes = det.get("cards", [])

    print("=== RAW DETECTION FRONT ===")
    print(det)

    # ---------------------------
    # 4. Crop FRONT
    # ---------------------------
    cropped_front = crop_cards(front_path, boxes)

    # ---------------------------
    # 5. Crop BACK (if uploaded)
    # ---------------------------
    cropped_back = []
    if has_back and back_path:
        cropped_back = crop_cards(back_path, boxes)

    # ---------------------------
    # 6. Process each paired card
    # ---------------------------
    cards = []

    for idx, front_card_path in enumerate(cropped_front, start=1):
        print(f"=== AI ANALYSIS CARD FRONT {idx}: {front_card_path}")

        back_card_path = cropped_back[idx - 1] if idx - 1 < len(cropped_back) else None

        # AI analysis uses front + back if available
        analysis = identify_and_grade_card(front_card_path, back_card_path)

        condition = analysis.get("condition", "Near Mint")

        # ---------- LIVE PRICES ----------
        prices = lookup_prices(analysis["name"], analysis["set"])
        prices = convert_prices(prices)  # Add USD/EUR/CAD conversions

        # Best market price (CAD)
        auto_price_cad = (
            prices.get("tcg", {}).get("market_cad")
            or prices.get("mk", {}).get("trend_cad")
            or analysis.get("price_ai_estimate")
        )

        # ---------- Thumbnails ----------
        thumb_front = f"static/thumbs/front/{idx}.jpg"
        create_thumbnail(front_card_path, thumb_front)

        if back_card_path:
            thumb_back = f"static/thumbs/back/{idx}.jpg"
            create_thumbnail(back_card_path, thumb_back)
        else:
            thumb_back = None

        # ---------- Save card record ----------
        cards.append({
            "id": idx,
            "front": front_card_path,
            "back": back_card_path,
            "thumb_front": thumb_front,
            "thumb_back": thumb_back,
            "has_back": back_card_path is not None,

            "name": analysis.get("name"),
            "set": analysis.get("set"),
            "number": analysis.get("number"),
            "rarity": analysis.get("rarity"),
            "condition": condition,

            "price_ai_estimate": analysis.get("price_ai_estimate"),

            "tcg": prices.get("tcg"),
            "mk": prices.get("mk"),

            "auto_price_cad": auto_price_cad,
            "auto_price_usd": prices.get("auto_price_usd"),
            "auto_price_eur": prices.get("auto_price_eur")
        })

    # ---------------------------
    # 7. Save session JSON
    # ---------------------------
    session_id = str(uuid.uuid4())
    with open(f"session_data/{session_id}.json", "w") as f:
        json.dump(cards, f, indent=2)

    return redirect(f"/review/{session_id}")


# ------------------------------------------------------------
# REVIEW PAGE
# ------------------------------------------------------------
@app.route("/review/<session_id>")
@basic_auth.required
def review(session_id):
    with open(f"session_data/{session_id}.json") as f:
        cards = json.load(f)

    return render_template("review.html", cards=cards, session_id=session_id)


# ------------------------------------------------------------
# APPROVE PAGE (SEND TO MAKE.COM)
# ------------------------------------------------------------
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
            card["final_price"] = request.form.get(f"price_{i}")

            approved.append(card)

    requests.post(WEBHOOK_URL, json={"approved_cards": approved})

    return render_template("sent.html", count=len(approved))


if __name__ == "__main__":
    app.run(port=5000)
