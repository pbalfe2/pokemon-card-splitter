from fastapi import FastAPI
from routes import upload, jobs, listings

app = FastAPI(title="Pokemon Card Analyzer")

app.include_router(upload.router, prefix="/upload")
app.include_router(jobs.router, prefix="/jobs")
app.include_router(listings.router, prefix="/listings")

@app.get("/")
def health():
    return {"status": "ok"}
