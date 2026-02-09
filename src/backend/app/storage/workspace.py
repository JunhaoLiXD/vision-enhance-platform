from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


@dataclass(frozen=True)
class JobWorkspace:
    job_id: str
    root: Path
    input_dir: Path
    output_dir: Path
    preview_dir: Path
    logs_dir: Path
    status_path: Path
    manifest_path: Path


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_workspace(base_dir: Path, job_id: str) -> JobWorkspace:
    """
    Create the workspace layout:
    workspaces/{job_id}/
      input/
      output/
      preview/
      logs/
      status.json
      manifest.json
    """
    root = base_dir / job_id
    input_dir = root / "input"
    output_dir = root / "output"
    preview_dir = root / "preview"
    logs_dir = root / "logs"
    status_path = root / "status.json"
    manifest_path = root / "manifest.json"

    for d in (input_dir, output_dir, preview_dir, logs_dir):
        d.mkdir(parents=True, exist_ok=True)

    # Initialize status/manifest if not exist
    if not status_path.exists():
        write_json(status_path, {"job_id": job_id, "status": "created", "created_at": _now_iso()})
    if not manifest_path.exists():
        write_json(manifest_path, {"job_id": job_id, "created_at": _now_iso(), "steps": []})

    return JobWorkspace(
        job_id=job_id,
        root=root,
        input_dir=input_dir,
        output_dir=output_dir,
        preview_dir=preview_dir,
        logs_dir=logs_dir,
        status_path=status_path,
        manifest_path=manifest_path,
    )


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def update_status(status_path: Path, patch: Dict[str, Any]) -> Dict[str, Any]:
    current = read_json(status_path) if status_path.exists() else {}
    current.update(patch)
    current.setdefault("updated_at", _now_iso())
    write_json(status_path, current)
    return current
