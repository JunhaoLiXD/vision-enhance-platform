"""
Business service layer for managing enhancement jobs.

Responsibilities:
- Create and initialize new jobs.
- Generate unique job identifiers.
- Coordinate workspace creation and input storage.
- Schedule pipeline execution as a background task.
- Update job status and manifest metadata.
- Provide job status and artifact retrieval logic.

Notes:
- Acts as the orchestration layer between API, storage, and engine.
- Does NOT implement algorithm logic.
"""
from __future__ import annotations
import numpy as np
from PIL import Image

import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import UploadFile, BackgroundTasks

from src.backend.engine.core.image_frame import ImageFrame
from src.backend.engine.core.pipeline import run_pipeline
from src.backend.engine.core.presets import get_preset_pipeline
from src.backend.engine.plugins.registry import build_registry
from src.backend.app.storage.workspace import (
    JobWorkspace,
    create_workspace,
    update_status,
    read_json,
    write_json,
)


WORKSPACES_DIR = Path("workspaces")


def _validate_pipeline_spec(pipeline_spec: List[Dict[str, Any]]) -> None:
    if not isinstance(pipeline_spec, list) or len(pipeline_spec) == 0:
        raise ValueError("pipeline_spec must be a non-empty list")

    for i, step in enumerate(pipeline_spec):
        if not isinstance(step, dict):
            raise ValueError(f"pipeline_spec[{i}] must be a dict")
        if "name" not in step:
            raise ValueError(f"pipeline_spec[{i}] missing required field: name")
        if not isinstance(step["name"], str):
            raise ValueError(f"pipeline_spec[{i}].name must be a string")
        if "params" in step and not isinstance(step["params"], dict):
            raise ValueError(f"pipeline_spec[{i}].params must be a dict")


def _execute_pipeline(
    ws: JobWorkspace,
    input_path: Path,
    filename: str,
    spec: List[Dict[str, Any]],
    mode: str,
    selected_preset: Optional[str],
    job_id: str,
) -> None:
    """
    Run the enhancement pipeline and persist results.
    Executed in a background thread after the HTTP response is returned.
    """
    try:
        img = Image.open(input_path).convert("RGB")
        arr = np.asarray(img).astype(np.float32) / 255.0

        frame = ImageFrame(data=arr, meta={"mode": "RGB"})
        registry = build_registry()

        out_frame, report = run_pipeline(frame, spec, registry)

        out_img = (np.clip(out_frame.data, 0.0, 1.0) * 255.0).astype(np.uint8)
        out_pil = Image.fromarray(out_img, mode="RGB")

        out_name = f"enhanced_{filename.rsplit('.', 1)[0]}.png"
        out_path = ws.output_dir / out_name
        out_pil.save(out_path)

        manifest = {
            "job_id": job_id,
            "mode": mode,
            "preset": selected_preset,
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
            "timing": report,
            "history": getattr(out_frame, "history", []),
        }
        write_json(ws.manifest_path, manifest)

        update_status(
            ws.status_path,
            {
                "status": "done",
                "mode": mode,
                "preset": selected_preset,
                "output_filename": out_name,
                "output_path": str(out_path.as_posix()),
                "output_download_url": f"/api/jobs/{job_id}/download/{out_name}",
                "manifest_path": str(ws.manifest_path.as_posix()),
                "pipeline": spec,
            },
        )

    except Exception as e:
        update_status(
            ws.status_path,
            {
                "status": "failed",
                "mode": mode,
                "preset": selected_preset,
                "pipeline": spec,
                "error": str(e),
            },
        )


def create_job(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    preset_id: Optional[str] = None,
    pipeline_spec: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Validate the request, save the uploaded file, and schedule pipeline
    execution as a background task. Returns immediately with the job_id.
    """
    # Resolve and validate the pipeline spec before touching the filesystem
    # so that invalid requests get a 400 without creating orphaned workspaces.
    mode: Optional[str] = None
    selected_preset: Optional[str] = None
    spec: List[Dict[str, Any]] = []

    if pipeline_spec is not None:
        _validate_pipeline_spec(pipeline_spec)
        spec = pipeline_spec
        mode = "custom"
    elif preset_id is not None:
        spec = get_preset_pipeline(preset_id)
        mode = "preset"
        selected_preset = preset_id
    else:
        selected_preset = "natural_enhance"
        spec = get_preset_pipeline(selected_preset)
        mode = "preset"

    job_id = uuid.uuid4().hex
    ws = create_workspace(WORKSPACES_DIR, job_id)

    filename = file.filename or "input.bin"
    input_path = ws.input_dir / filename

    update_status(
        ws.status_path,
        {
            "status": "uploading",
            "input_filename": filename,
            "mode": mode,
            "preset": selected_preset,
        },
    )

    # Save uploaded file in chunks to avoid loading large images into memory
    try:
        with input_path.open("wb") as f:
            while True:
                chunk = file.file.read(1024 * 1024)  # 1 MB per read
                if not chunk:
                    break
                f.write(chunk)
    finally:
        try:
            file.file.close()
        except Exception:
            pass

    status = update_status(
        ws.status_path,
        {
            "status": "processing",
            "input_filename": filename,
            "input_path": str(input_path.as_posix()),
            "mode": mode,
            "preset": selected_preset,
            "pipeline": spec,
        },
    )

    # Schedule the heavy work; HTTP response is returned before this runs.
    background_tasks.add_task(
        _execute_pipeline,
        ws=ws,
        input_path=input_path,
        filename=filename,
        spec=spec,
        mode=mode,
        selected_preset=selected_preset,
        job_id=job_id,
    )

    return {"job_id": job_id, "status": status}


def get_job_status(job_id: str) -> Dict[str, Any]:
    status_path = WORKSPACES_DIR / job_id / "status.json"
    if not status_path.exists():
        return {"job_id": job_id, "status": "not_found"}
    return read_json(status_path)
