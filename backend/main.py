from fastapi import FastAPI
from backend.routes import upload, jobs, listings
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Pokemon Card Analyzer")

app.mount("/", StaticFiles(directory="backend/static", html=True), name="static")

app.include_router(upload.router, prefix="/upload")
app.include_router(jobs.router, prefix="/jobs")
app.include_router(listings.router, prefix="/listings")

@app.get("/health")
def health():
    return {"status": "ok"}
