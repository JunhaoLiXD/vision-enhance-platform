from __future__ import annotations

import uuid
from pathlib import Path
from typing import Dict, Any

from fastapi import UploadFile

from src.backend.app.storage.workspace import create_workspace, update_status, read_json


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

    # Read/Write in chunks (safer for large files)
    with input_path.open("wb") as f:
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)

    status = update_status(
        ws.status_path,
        {
            "status": "uploaded",
            "input_filename": filename,
            "input_path": str(input_path.as_posix()),
        },
    )
    return {"job_id": job_id, "status": status}


def get_job_status(job_id: str) -> Dict[str, Any]:
    status_path = WORKSPACES_DIR / job_id / "status.json"
    if not status_path.exists():
        return {"job_id": job_id, "status": "not_found"}
    return read_json(status_path)
