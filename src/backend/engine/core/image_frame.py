"""
Unified internal image representation.

Responsibilities:
- Wrap raw image data into a consistent ImageFrame object.
- Standardize internal dtype (typically float32).
- Store image metadata and processing history.
- Serve as the common data structure passed between processing steps.

Notes:
- Ensures decoupling between pipeline logic and raw NumPy arrays.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass
class ImageFrame:
    """
    Internal unified image representation:
    - data: float32 numpy array, range typically [0, 1]
    - meta: misc metadata (source, original dtype, etc.)
    - history: list of executed steps
    """
    data: np.ndarray
    meta: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def copy(self) -> "ImageFrame":
        return ImageFrame(
            data=self.data.copy(),
            meta=dict(self.meta),
            history=list(self.history),
        )
