from fastapi import APIRouter
from backend.state import load_job

router = APIRouter()

@router.get("/{job_id}")
def job_status(job_id: str):
    return load_job(job_id)
