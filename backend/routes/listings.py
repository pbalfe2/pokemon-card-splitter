from fastapi import APIRouter
from backend.state import load_job
from backend.services.ebay_listing import generate_listing

router = APIRouter()

@router.post("/{job_id}")
async def create_listing(job_id: str):
    job = load_job(job_id)
    listing = await generate_listing(job["cards"])
    return {"listing": listing}
