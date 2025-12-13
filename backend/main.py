from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.routes import upload, jobs, listings

app = FastAPI(title="Pokemon Card Analyzer")

# -------------------------------------------------
# Static directories
# -------------------------------------------------

# Frontend static files
STATIC_DIR = Path("backend/static")
DATA_DIR = Path("data")

STATIC_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Serve frontend assets
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Serve uploaded & processed images
app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")

# -------------------------------------------------
# Routes
# -------------------------------------------------

app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
app.include_router(listings.router, prefix="/listings", tags=["Listings"])

# -------------------------------------------------
# Root: serve UI
# -------------------------------------------------

@app.get("/")
def serve_ui():
    return FileResponse(STATIC_DIR / "index.html")
