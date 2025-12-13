from pathlib import Path
import shutil
import uuid

BASE = Path("data")
UPLOADS = BASE / "uploads"
CARDS = BASE / "cards"

UPLOADS.mkdir(parents=True, exist_ok=True)
CARDS.mkdir(parents=True, exist_ok=True)

def save_upload(file, job_id, side):
    path = UPLOADS / f"{job_id}_{side}.jpg"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return str(path)

def duplicate_as_card(image_path, job_id):
    card_id = str(uuid.uuid4())
    dest = CARDS / f"{job_id}_{card_id}.jpg"
    shutil.copy(image_path, dest)
    return str(dest)
