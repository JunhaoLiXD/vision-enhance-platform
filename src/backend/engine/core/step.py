"""
Abstract processing step definition.

Responsibilities:
- Define the interface that all processing steps must implement.
- Enforce a standard method signature (e.g., run(ImageFrame) -> ImageFrame).
- Enable pipeline execution to treat all algorithms uniformly.

Notes:
- Concrete algorithm implementations live in plugin modules.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Protocol

from src.backend.engine.core.image_frame import ImageFrame


class Step(Protocol):
    name: str

    def run(self, frame: ImageFrame, params: Dict[str, Any]) -> ImageFrame:
        ...
