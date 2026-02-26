"""
Business service layer for managing enhancement jobs.

Responsibilities:
- Create and initialize new jobs.
- Generate unique job identifiers.
- Coordinate workspace creation and input storage.
- Construct and execute processing pipelines.
- Update job status and manifest metadata.
- Provide job status and artifact retrieval logic.

Notes:
- Acts as the orchestration layer between API, storage, and engine.
- Does NOT implement algorithm logic.
"""
from __future__ import annotations
import numpy as np
from PIL import Image

from src.backend.engine.core.image_frame import ImageFrame
from src.backend.engine.core.pipeline import run_pipeline
from src.backend.engine.plugins.enhance_classical.registry import build_registry

import uuid
from pathlib import Path
from typing import Dict, Any

from fastapi import UploadFile

from src.backend.app.storage.workspace import create_workspace, update_status, read_json, write_json


WORKSPACES_DIR = Path("workspaces")


def create_job(file: UploadFile) -> Dict[str, Any]:
    """
    Create a job workspace, save the uploaded input file, and write status.json.
    """
    job_id = uuid.uuid4().hex  # stable, filesystem-friendly
    ws = create_workspace(WORKSPACES_DIR, job_id)

    # Save input
    filename = file.filename or "input.bin"
    input_path = ws.input_dir / filename

    # Mark job as created/uploading
    status = update_status(
        ws.status_path,
        {
            "status": "uploading",
            "input_filename": filename,
        },
    )

    # Read/Write in chunks (safer for large files)
    try:
        with input_path.open("wb") as f:
            while True:
                chunk = file.file.read(1024 * 1024)  # 1MB per read
                if not chunk:
                    break
                f.write(chunk)
    finally:
        # Close the underlying upload stream
        try:
            file.file.close()
        except Exception:
            pass

    status = update_status(
        ws.status_path,
        {
            "status": "uploaded",
            "input_filename": filename,
            "input_path": str(input_path.as_posix()),
        },
    )

    try:
        img = Image.open(input_path).convert("RGB")
        arr = np.asarray(img).astype(np.float32) / 255.0  # normalize to [0,1]

        frame = ImageFrame(data=arr, meta={"mode": "RGB"})
        registry = build_registry()

        spec = [
            {"name": "gamma", "params": {"gamma": 1.2}},
            {"name": "clahe", "params": {"clip_limit": 2.0, "tile_grid_size": [8, 8]}},
            {"name": "retinex_msr_luma", "params":{"sigmas": [15.0, 80.0, 250.0], "weights": None, "eps": 1e-6}},
            {"name": "unsharp_luma", "params": {"amount": 1.0, "radius": 2.0, "threshold": 0.0}},
        ]
        out_frame, report = run_pipeline(frame, spec, registry)

        out_img = (np.clip(out_frame.data, 0.0, 1.0) * 255.0).astype(np.uint8)
        out_pil = Image.fromarray(out_img, mode="RGB")

        out_name = f"enhanced_{filename.rsplit('.', 1)[0]}.png"
        out_path = ws.output_dir / out_name
        out_pil.save(out_path)

        manifest = {
            "job_id": job_id,
            "input": {
                "filename": filename,
                "path": str(input_path.as_posix()),
            },
            "output": {
                "filename": out_name,
                "path": str(out_path.as_posix()),
                "download_url": f"/api/jobs/{job_id}/download/{out_name}",
            },
            "pipeline": spec,
            "timing": report,  # report = {"steps":[...], "total_time_sec": ...}
        }

        write_json(ws.manifest_path, manifest)

        status = update_status(
            ws.status_path,
            {
                "status": "done",
                "output_filename": out_name,
                "output_path": str(out_path.as_posix()),
                "output_download_url": f"/api/jobs/{job_id}/download/{out_name}",
                "manifest_path": str(ws.manifest_path.as_posix()),
                "pipeline": spec,
            },
        )

        return {"job_id": job_id, "status": status}
    
    except Exception as e:
        status = update_status(
            ws.status_path,
            {
                "status": "failed",
                "error": str(e),
            },
        )
        return {"job_id": job_id, "status": status}


def get_job_status(job_id: str) -> Dict[str, Any]:
    status_path = WORKSPACES_DIR / job_id / "status.json"
    if not status_path.exists():
        return {"job_id": job_id, "status": "not_found"}
    return read_json(status_path)
