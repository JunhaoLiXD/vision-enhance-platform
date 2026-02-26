"""
Luminance-domain Unsharp Mask step.

Algorithm:
1) Convert RGB -> YCrCb
2) Apply unsharp mask on luminance channel Y only
3) Replace Y with enhanced Y
4) Convert YCrCb -> RGB

Notes:
- Pure computation.
- Assumes frame.data is float32 in [0, 1].
- Expects RGB channel order (HxWx3). If your data is BGR, swap conversion codes.
"""
from __future__ import annotations

from typing import Any, Dict
import numpy as np
import cv2

from src.backend.engine.core.image_frame import ImageFrame

class UnsharpMaskLuminanceStep:
    name = "unsharp_luma"

    def run(self, frame: ImageFrame, params: Dict[str, Any]) -> ImageFrame:
        # amount controls how strongly edges/details are boosted
        amount = float(params.get("amount", 1.0))

        # radius controls blur scale (larger -> broader edges)
        radius = float(params.get("radius", 2.0))

        # threshold suppress sharpening in flat/noisy regions
        threshold = float(params.get("threshold", 0.0))

        if amount < 0:
            raise ValueError("amount must be >= 0")
        if radius <= 0:
            raise ValueError("radius must be > 0")
        if threshold < 0:
            raise ValueError("threshold must be >= 0")

        # Ensure input is float32 in [0, 1]
        x = np.clip(frame.data, 0.0, 1.0).astype(np.float32)

        # Case 1: Grayscale image
        if x.ndim == 2:
            y = self._unsharp_2d(x, amount=amount, radius=radius, threshold=threshold)

            out = frame.copy()
            out.data = y.astype(np.float32)

            out.history.append(
                {
                    "step": self.name,
                    "params": {
                        "amount": amount,
                        "radius": radius,
                        "threshold": threshold,
                        "mode": "gray",
                    },
                }
            )
            
            return out

        # Case 2: RGB image expected
        if x.ndim != 3 or x.shape[2] != 3:
            raise ValueError("unsharp_luma expects HxW(gray) or HxWx3(RGB) image")

        # RGB -> YCrCb
        # IMPORTANT:
        # This assumes x is RGB. If your internal is BGR, use COLOR_BGR2YCrCb / COLOR_YCrCb2BGR instead.
        ycrcb = cv2.cvtColor(x, cv2.COLOR_RGB2YCrCb).astype(np.float32)

        Y = ycrcb[..., 0]
        Cr = ycrcb[..., 1]
        Cb = ycrcb[..., 2]

        # Unsharp on luminance channel
        Y_enh = self._unsharp_2d(Y, amount=amount, radius=radius, threshold=threshold)
        
        # Recombine channels and convert backto RGB
        ycrcb_out = np.stack([Y_enh, Cr, Cb], axis=-1).astype(np.float32)
        rgb_out = cv2.cvtColor(ycrcb_out, cv2.COLOR_YCrCb2RGB).astype(np.float32)

        rgb_out = np.clip(rgb_out, 0.0, 1.0).astype(np.float32)

        out = frame.copy()
        out.data = rgb_out

        out.history.append(
            {
                "step": self.name,
                "params": {
                    "amount": amount,
                    "radius": radius,
                    "threshold": threshold,
                    "mode": "ycrcb_luminance",
                    "assume": "RGB",
                },
            }
        )

        return out

    
    @staticmethod
    def _unsharp_2d(img2d: np.ndarray, amount: float, radius: float, threshold: float) -> np.ndarray:
        """
        Unsharp mask for one channel.

        Steps:
        1) blur = GaussianBlur(I, radius)
        2) mask = I - blur
        3) if threshold > 0: only apply where |mask| >= threshold
        4) out = I + amount * mask
        5) clip to [0, 1]
        """
        x = np.clip(img2d.astype(np.float32), 0.0, 1.0)

        # Gaussian blur approximates low-frequency component
        blur = cv2.GaussianBlur(x, (0, 0), sigmaX=float(radius), sigmaY=float(radius))

        # High-frequency detail mask
        mask = x - blur

        if threshold > 0:
            # Apply sharpening only where edge/detail magnitude is large enough
            keep = np.abs(mask) >= float(threshold)
            out = x.copy()
            out[keep] = x[keep] + float(amount) * mask[keep]
        else:
            out = x + float(amount) * mask

        return np.clip(out, 0.0, 1.0).astype(np.float32)
