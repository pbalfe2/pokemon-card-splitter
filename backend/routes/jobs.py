from fastapi import APIRouter, HTTPException
from backend.state import load_job
import os

router = APIRouter()

@router.get("/{job_id}")
def job_status(job_id: str):
    try:
        return load_job(job_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Job not found")
