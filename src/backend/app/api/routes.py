"""
API routing layer for the Vision Enhance Platform.

Responsibilities:
- Define HTTP endpoints under /api.
- Parse incoming requests (file uploads, JSON bodies, query parameters).
- Delegate business logic to the service layer.
- Return structured HTTP responses.

Notes:
- Does NOT implement image processing logic.
- Does NOT directly manage file system operations.
"""
import json
from json import JSONDecodeError
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi import HTTPException
from pathlib import Path

from src.backend.app.services.job_service import create_job, get_job_status
from src.backend.engine.core.presets import list_presets
from src.backend.engine.plugins.registry import get_algorithms_schema

router = APIRouter(prefix="/api")

@router.post("/jobs")
def api_create_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    preset_id: Optional[str] = Form(None),
    pipeline_spec_json: Optional[str] = Form(None),
):

    pipeline_spec = None

    if pipeline_spec_json:
        try:
            pipeline_spec = json.loads(pipeline_spec_json)
        except JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid pipeline_spec_json")

    try:
        return create_job(
            file=file,
            background_tasks=background_tasks,
            preset_id=preset_id,
            pipeline_spec=pipeline_spec,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal processing error: {str(e)}")


@router.get("/jobs/{job_id}")
def api_get_job(job_id: str):
    return get_job_status(job_id)


@router.get("/algorithms")
def api_algorithms():
    return get_algorithms_schema()


@router.get("/jobs/{job_id}/download/{name}")
def api_download(job_id: str, name: str):
    path = Path("workspaces") / job_id / "output" / name
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="artifact not found")
    return FileResponse(path)


@router.get("/jobs/{job_id}/artifacts")
def api_list_artifacts(job_id: str):
    """
    List output files under workspaces/{job_id}/output
    """
    out_dir = Path("workspaces") / job_id / "output"
    if not out_dir.exists():
        raise HTTPException(status_code=404, detail="job not found")

    files = []
    for p in out_dir.iterdir():
        if p.is_file():
            files.append(
                {
                    "name": p.name,
                    "path": str(p.as_posix()),
                    "download_url": f"/api/jobs/{job_id}/download/{p.name}",
                }
            )
    return {"job_id": job_id, "artifacts": sorted(files, key=lambda x: x["name"])}


@router.get("/presets")
def api_presets():
    presets = list_presets()

    return {
        "presets": [
            {
                "id": "natural_enhance",
                "name": "Natural Enhance",
                "description": "Balanced enhancement for general photos.",
                "steps": presets["natural_enhance"],
            },
            {
                "id": "low_light_enhance",
                "name": "Low Light Enhance",
                "description": "Boost visibility in dim images.",
                "steps": presets["low_light_enhance"],
            },
            {
                "id": "detail_boost",
                "name": "Detail Boost",
                "description": "Increase local contrast and sharpen fine details.",
                "steps": presets["detail_boost"],
            },
            {
                "id": "zero_dce_enhance",
                "name": "Zero-DCE Enhance",
                "description": "Low-light enhancement using the Zero-DCE neural model. For the web demo, Zero-DCE resizes the image so the longest side is 384 px before inference.",
                "steps": presets["zero_dce_enhance"],
            },
        ]
    }