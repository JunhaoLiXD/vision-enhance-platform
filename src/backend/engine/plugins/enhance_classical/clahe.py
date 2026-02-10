from __future__ import annotations

from typing import Any, Dict, Tuple

import numpy as np
import cv2

from src.backend.engine.core.image_frame import ImageFrame


class CLAHEStep:
    name = "clahe"

    def run(self, frame: ImageFrame, params: Dict[str, Any]) -> ImageFrame:
        """
        Apply CLAHE on luminance channel (LAB space) for RGB images.

        Expected input:
          - frame.data: float32 numpy array in [0,1], shape (H,W,3) RGB

        Params:
          - clip_limit: float (default 2.0)  # higher -> stronger contrast, more risk of noise
          - tile_grid_size: [int, int] (default [8,8])  # tile size in CLAHE
        """
        clip_limit = float(params.get("clip_limit", 2.0))
        tgs = params.get("tile_grid_size", [8, 8])

        # Normalize/validate tile size
        if not (isinstance(tgs, (list, tuple)) and len(tgs) == 2):
            raise ValueError("tile_grid_size must be a list/tuple like [8, 8]")
        tile_grid_size: Tuple[int, int] = (int(tgs[0]), int(tgs[1]))
        if tile_grid_size[0] <= 0 or tile_grid_size[1] <= 0:
            raise ValueError("tile_grid_size values must be > 0")
        if clip_limit <= 0:
            raise ValueError("clip_limit must be > 0")

        x = frame.data
        if x.ndim != 3 or x.shape[2] != 3:
            raise ValueError("CLAHEStep expects an RGB image with shape (H, W, 3)")

        # float32 [0,1] -> uint8 [0,255] for OpenCV CLAHE
        x01 = np.clip(x, 0.0, 1.0)
        rgb_u8 = (x01 * 255.0).astype(np.uint8)

        # OpenCV uses BGR by default; we currently treat data as RGB,
        # so convert RGB -> BGR before using cv2 color conversions.
        bgr = cv2.cvtColor(rgb_u8, cv2.COLOR_RGB2BGR)

        # BGR -> LAB, apply CLAHE on L channel
        lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        l2 = clahe.apply(l)

        lab2 = cv2.merge((l2, a, b))
        bgr2 = cv2.cvtColor(lab2, cv2.COLOR_LAB2BGR)
        rgb2 = cv2.cvtColor(bgr2, cv2.COLOR_BGR2RGB)

        # back to float32 [0,1]
        y = (rgb2.astype(np.float32) / 255.0).astype(np.float32)

        out = frame.copy()
        out.data = y
        out.history.append(
            {
                "step": self.name,
                "params": {"clip_limit": clip_limit, "tile_grid_size": [tile_grid_size[0], tile_grid_size[1]]},
            }
        )
        return out
