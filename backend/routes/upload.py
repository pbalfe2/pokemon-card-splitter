from fastapi import APIRouter, UploadFile, File
from backend.services.filesystem import save_upload
from backend.state import save_job
from backend.tasks import enqueue_job
import uuid

router = APIRouter()

@router.post("/")
async def upload(front: UploadFile = File(...), back: UploadFile | None = None):
    job_id = str(uuid.uuid4())

    front_path = save_upload(front, job_id, "front")
    back_path = save_upload(back, job_id, "back") if back else None

    save_job(job_id, {
        "status": "queued",
        "front": front_path,
        "back": back_path
    })

    await enqueue_job(job_id)

    return {"job_id": job_id}
