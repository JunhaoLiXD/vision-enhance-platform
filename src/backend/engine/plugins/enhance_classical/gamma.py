from __future__ import annotations

from typing import Any, Dict
import numpy as np

from src.backend.engine.core.image_frame import ImageFrame

class GammaStep:
    name = "gamma"

    def run(self, frame: ImageFrame, params: Dict[str, Any]) -> ImageFrame:
        gamma = float(params.get("gamma", 1.2))
        if gamma <= 0:
            raise ValueError("gamma must be > 0")
    
        x = frame.data
        x = np.clip(x, 0.0, 1.0)
        y = np.power(x, 1.0 / gamma).astype(np.float32)

        out = frame.copy()
        out.data = y
        out.history.append({"step": self.name, "params": {"gamma": gamma}})
        return out