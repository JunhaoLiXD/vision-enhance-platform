from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Protocol

from src.backend.engine.core.image_frame import ImageFrame


class Step(Protocol):
    name: str

    def run(self, frame: ImageFrame, params: Dict[str, Any]) -> ImageFrame:
        ...
