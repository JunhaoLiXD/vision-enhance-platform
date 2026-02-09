from fastapi import APIRouter, UploadFile, File

from src.backend.app.services.job_service import create_job, get_job_status

router = APIRouter(prefix="/api")

@router.post("/jobs")
def api_create_job(file: UploadFile = File(...)):
    return create_job(file)

@router.get("/jobs/{job_id}")
def api_get_job(job_id: str):
    return get_job_status(job_id)
