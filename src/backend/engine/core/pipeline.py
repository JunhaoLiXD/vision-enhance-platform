"""
Processing pipeline execution engine.

Responsibilities:
- Construct processing steps based on job specifications.
- Retrieve algorithm implementations from plugin registries.
- Execute processing steps sequentially.
- Optionally record step timing and metadata.

Notes:
- Does NOT handle HTTP logic.
- Does NOT manage file persistence directly.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple
import time

from src.backend.engine.core.image_frame import ImageFrame


def run_pipeline(frame: ImageFrame, spec: List[Dict[str, Any]], registry: Dict[str, object]) -> Tuple[ImageFrame, Dict[str, Any]]:
    cur = frame
    steps_report: List[Dict[str, Any]] = []

    t0 = time.perf_counter()

    for item in spec:
        name = item["name"]
        params = item.get("params", {})

        if name not in registry:
            raise ValueError(f"Unknown step: {name}")

        step = registry[name]

        t_step0 = time.perf_counter()
        cur = step.run(cur, params)
        t_step1 = time.perf_counter()

        steps_report.append(
            {
                "name": name,
                "params": params,
                "time_sec": round(t_step1 - t_step0, 6),
            }
        )

    total_time_sec = round(time.perf_counter() - t0, 6)

    report = {
        "steps": steps_report,
        "total_time_sec": total_time_sec,
    }

    return cur, report
