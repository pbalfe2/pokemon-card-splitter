from flask import Flask, render_template, request, jsonify
from card_processing import extract_cards
import os

app = Flask(__name__)

# --------- CONFIGURATION ----------
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"

# 🔵 Your Make Webhook URL:
WEBHOOK_URL = "https://hook.us2.make.com/0t8oinao8c0yaumj3y81v8ncxgo8yp3n"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
# ---------------------------------

@app.route("/")
def home():
    return "Card Splitter API Running!"

@app.route("/upload", methods=["GET", "POST"])
def upload_form():
    if request.method == "GET":
        return render_template("upload.html")

    if "image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["image"]

    # Save uploaded image
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Process image + send cropped cards to Make webhook
    results = extract_cards(
        image_path=filepath,
        output_folder=PROCESSED_FOLDER,
        webhook_url=WEBHOOK_URL
    )

    return jsonify({
        "cards_detected": len(results),
        "cropped_cards": results,
        "sent_to_make": True
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
