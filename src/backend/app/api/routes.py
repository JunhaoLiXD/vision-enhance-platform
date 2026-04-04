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
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi import HTTPException
from pathlib import Path

from src.backend.app.services.job_service import create_job, get_job_status
from src.backend.engine.core.presets import list_presets

router = APIRouter(prefix="/api")

@router.post("/jobs")
def api_create_job(
    file: UploadFile = File(...),
    preset_name: Optional[str] = Form(None),
    pipeline_spec_json: Optional[str] = Form(None),
):

    pipeline_spec = None
    
    if pipeline_spec_json:
        pipeline_spec = json.loads(pipeline_spec_json)

    return create_job(
        file=file,
        preset_name=preset_name,
        pipeline_spec=pipeline_spec,
    )


@router.get("/jobs/{job_id}")
def api_get_job(job_id: str):
    return get_job_status(job_id)


@router.get("/algorithms")
def api_algorithms():
    return {
        "gamma": {
            "description": "Gamma correction on normalized RGB",
            "params": {
                "gamma": {"type": "float", "default": 1.2, "min": 0.1, "max": 5.0}
            },
        },
        "clahe": {
            "description": "CLAHE on luminance channel (LAB)",
            "params": {
                "clip_limit": {"type": "float", "default": 2.0, "min": 0.1, "max": 10.0},
                "tile_grid_size": {"type": "list[int,int]", "default": [8, 8]},
            },
        },
        "retinex_msr_luma":{
            "description": "Multi-scale Retinex applied on luminance channel (YCrCb)",
            "params": {
                "sigmas": {
                    "type": "list[float]",
                    "default": [15.0, 80.0, 250.0]
                },
                "weights": {
                    "type": "list[float]",
                    "default": None
                },
                "eps": {
                    "type": "float",
                    "default": 1e-6,
                    "min": 1e-8,
                    "max": 1e-2
                },
            },
        },
        "unsharp_luma": {
            "description": "Unsharp mask applied on luminance channel (YCrCb)",
            "params": {
                "amount": {
                    "type": "float",
                    "default": 1.0,
                    "min": 0.0,
                    "max": 5.0
                },
                "radius": {
                    "type": "float",
                    "default": 2.0,
                    "min": 0.1,
                    "max": 20.0
                },
                "threshold": {
                    "type": "float",
                    "default": 0.0,
                    "min": 0.0,
                    "max": 0.5
                }
            },
        },
        "bilateral_luma":{
            "description": "Edge-preserving bilateral denoising applied on luminance channel (YCrCb). Reduces noise while maintaining sharp edges and structural details.",
            "params":{
                "d": -1,
                "sigma_color": 0.08,
                "sigma_space": 3.0
            }
        },
    }


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
    return list_presets()
