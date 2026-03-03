"""
Luminance-domain Bilateral Filter (denoise) step.

Algorithm:
1) Convert RGB -> YCrCb
2) Apply bilateral filter on luminance channel Y only
3) Replace Y with denoised Y
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


class BilateralLuminanceStep:
    name = "bilateral_luma"

    def run(self, frame: ImageFrame, params: Dict[str, Any]) -> ImageFrame:
        # d: Diameter of each pixel neighborhood used during filtering.
        # If d <= 0, OpenCV will compute it from sigmaSpace.
        d = int(params.get("d", -1))

        # sigma_color controls how different colors/brightness can be while still averaging.
        # Since we use [0,1] float, typical range is ~0.02 to 0.2.
        sigma_color = float(params.get("sigma_color", 0.08))

        # sigma_space controls spatial extent (pixels).
        sigma_space = float(params.get("sigma_space", 3.0))

        if sigma_color < 0:
            raise ValueError("sigma_color must be >= 0")
        if sigma_space <= 0:
            raise ValueError("sigma_space must be > 0")

        # Ensure input is float32 in [0, 1]
        x = np.clip(frame.data, 0.0, 1.0).astype(np.float32)

        # Case 1: Grayscale image
        # Apply bilateral directly on intensity.
        if x.ndim == 2:
            y = self._bilateral_2d(x, d=d, sigma_color=sigma_color, sigma_space=sigma_space)

            out = frame.copy()
            out.data = y.astype(np.float32)

            out.history.append(
                {
                    "step": self.name,
                    "params": {
                        "d": d,
                        "sigma_color": sigma_color,
                        "sigma_space": sigma_space,
                        "mode": "gray",
                    },
                }
            )
            return out

        # Case 2: RGB image expected
        if x.ndim != 3 or x.shape[2] != 3:
            raise ValueError("bilateral_luma expects HxW(gray) or HxWx3(RGB) image")

        # RGB -> YCrCb
        # IMPORTANT:
        # This assume x is RGB. If your internal is BGR, use COLOR_BGR2YCrCb / COLOR_YCrCb2BGR instead
        ycrcb = cv2.cvtColor(x, cv2.COLOR_RGB2YCrCb).astype(np.float32)

        Y = ycrcb[..., 0]
        Cr = ycrcb[..., 1]
        Cb = ycrcb[..., 2]

        # Bilateral on luminance channel
        Y_den = self._bilateral_2d(Y, d=d, sigma_color=sigma_color, sigma_space=sigma_space)

        # Recombine channels and convert back to RGB
        ycrcb_out = np.stack([Y_den, Cr, Cb], axis=-1).astype(np.float32)

        rgb_out = cv2.cvtColor(ycrcb_out, cv2.COLOR_YCrCb2RGB).astype(np.float32)
        rgb_out = np.clip(rgb_out, 0.0, 1.0).astype(np.float32)

        out = frame.copy()
        out.data = rgb_out

        out.history.append(
            {
                "step": self.name,
                "params": {
                    "d": d,
                    "sigma_color": sigma_color,
                    "sigma_space": sigma_space,
                    "mode": "ycrcb_luminance",
                    "assume": "RGB",
                },
            }
        )
        return out

    @staticmethod
    def _bilateral_2d(img2d: np.ndarray, d: int, sigma_color: float, sigma_space: float) -> np.ndarray:
        """
        Bilateral filter for one channel.

        OpenCV definition:
            dst = bilateralFilter(src, d, sigmaColor, sigmaSpace)
        """
        x = np.clip(img2d.astype(np.float32), 0.0, 1.0)

        # OpenCV bilateralFilter supports float images.
        # Input/output are float32 in same scale.
        y = cv2.bilateralFilter(
            x,
            d=d,
            sigmaColor=float(sigma_color),
            sigmaSpace=float(sigma_space),
        )

        return np.clip(y, 0.0, 1.0).astype(np.float32)