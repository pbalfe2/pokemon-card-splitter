import json
from pathlib import Path

JOBS = Path("data/jobs")
JOBS.mkdir(parents=True, exist_ok=True)

def job_path(job_id):
    return JOBS / f"{job_id}.json"

def save_job(job_id, data):
    with open(job_path(job_id), "w") as f:
        json.dump(data, f, indent=2)

def load_job(job_id):
    with open(job_path(job_id)) as f:
        return json.load(f)
