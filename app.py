from flask import Flask, render_template, request, jsonify
from card_processing import extract_cards
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "Card Splitter API Running!"

@app.route("/upload", methods=["GET", "POST"])
def upload_form():
    if request.method == "GET":
        return render_template("upload.html")

    if "image" not in request.files:
        return "No file uploaded", 400

    file = request.files["image"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    result = extract_cards(filepath, output_folder=PROCESSED_FOLDER)

    return jsonify({
        "cards_detected": len(result),
        "processed_cards": result
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
