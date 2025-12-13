from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.routes import upload, jobs, listings

app = FastAPI(title="Pokemon Card Analyzer")

STATIC_DIR = Path("backend/static")
DATA_DIR = Path("data")

STATIC_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")

app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
app.include_router(listings.router, prefix="/listings", tags=["Listings"])

@app.get("/")
def serve_ui():
    return FileResponse(STATIC_DIR / "index.html")
