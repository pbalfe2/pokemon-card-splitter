from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.routes import upload, jobs, listings

app = FastAPI(title="Pokemon Card Analyzer")

# API routes FIRST
app.include_router(upload.router, prefix="/upload")
app.include_router(jobs.router, prefix="/jobs")
app.include_router(listings.router, prefix="/listings")

# Static files
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

@app.get("/")
def index():
    return FileResponse("backend/static/index.html")

from fastapi.staticfiles import StaticFiles

app.mount("/data", StaticFiles(directory="data"), name="data")
