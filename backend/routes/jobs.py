from backend.state import load_job
from backend.services.ebay_listing import generate_listing


router = APIRouter()

@router.get("/{job_id}")
def job_status(job_id: str):
    return load_job(job_id)
