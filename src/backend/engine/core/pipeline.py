from __future__ import annotations

from typing import Any, Dict, List

from src.backend.engine.core.image_frame import ImageFrame


def run_pipeline(frame: ImageFrame, spec: List[Dict[str, Any]], registry: Dict[str, object]) -> ImageFrame:
    cur = frame
    for item in spec:
        name = item["name"]
        params = item.get("params", {})

        if name not in registry:
            raise ValueError(f"Unknown step: {name}")

        step = registry[name]
        cur = step.run(cur, params)
    return cur
