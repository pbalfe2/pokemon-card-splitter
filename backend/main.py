from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import upload, jobs, listings

app = FastAPI(title="Pokemon Card Analyzer")

app.mount("/", StaticFiles(directory="backend/static", html=True), name="static")

app.include_router(upload.router, prefix="/upload")
app.include_router(jobs.router, prefix="/jobs")
app.include_router(listings.router, prefix="/listings")