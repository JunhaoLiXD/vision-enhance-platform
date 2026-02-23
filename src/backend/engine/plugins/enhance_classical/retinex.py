"""
Luminance-domain Multi-Scale Retinex (MSR) step.

Algorithm:
1) Convert RGB -> YCrCb
2) Apply MSR Retinex on luminance channel Y only
3) Replace Y with enhanced Y
4) Convert YCrCb -> RGB

Notes:
- Pure computation.
- Assumes frame.data is float32 in [0, 1].
- Expects RGB channel order (HxWx3). If your data is BGR, swap conversion codes.
"""
from __future__ import annotations

from typing import Any, Dict, List
import numpy as np
import cv2

from src.backend.engine.core.image_frame import ImageFrame

class RetinexMSRLuminanceStep:
    name = "retinex_msr_luma"

    def run(self, frame: ImageFrame, params: Dict[str, Any]) -> ImageFrame:
        # sigmas define Gaussina scales used to estimate illumination.
        # Small sigma -> local contrast enhancement
        # Large sigma -> global illumination normalization
        sigmas = params.get("sigmas", [15.0, 80.0, 250.0])

        # Optional weights for multi-scale fusion
        weights = params.get("weights", None)

        # small constant to avoid log(0)
        eps = float(params.get("eps", 1e-6))

        # Validate sigmas
        if not isinstance(sigmas, (list, tuple)) or len(sigmas) == 0:
            raise ValueError("sigmas must be a non-empty list/tuple of positive numbers")
        sigmas = [float(s) for s in sigmas]

        if any(s <= 0 for s in sigmas):
            raise ValueError("all sigmas must be > 0")
        
        # Validate weights
        if weights is None:
            w = np.ones(len(sigmas), dtype=np.float32) / float(len(sigmas))
        else:
            if not isinstance(weights, (list, tuple)) or len(weights) != len(sigmas):
                raise ValueError("weights must be None or a list/tuple with the same length as sigmas")
            w = np.array([float(x) for x in weights], dtype=np.float32)
            if np.any(w < 0):
                raise ValueError("weights must be non-negative")
            s = float(np.sum(w))
            if s <= 0:
                raise ValueError("sum(weights) must be > 0")
            
            # Normalize weights so Σw = 1
            w = w / s
        
        # Ensure input is float32 in [0, 1]
        x = np.clip(frame.data, 0.0, 1.0).astype(np.float32)

        # Case 1: Grayscale image
        # Directly apple MSR since luminance already represents intensity.
        if x.ndim == 2:
            y = self._msr_2d(x, sigmas, w, eps)

            # Normalize result back to displayale range
            y = self._minmax01(y)

            out = frame.copy()
            out.data = y.astype(np.float32)

            out.history.append(
                {
                    "step": self.name,
                    "params":{
                        "sigmas": sigmas,
                        "weights": w.tolist(),
                        "eps": eps,
                        "mode": "gray"
                        },
                }
            )
            return out
        
        # Case 2: RGB image expected
        if x.ndim != 3 or x.shape[2] != 3:
            raise ValueError("retinex_msr_luma expects HxW(gray) or HxWx3(RGB) image")
        
        # RGB -> YCrCb
        # IMPORTANT:
        # This assume x is RGB. If your internal is BGR, use COLOR_BGR2YCrCb / COLOR_YCrCb2BGR instead
        ycrcb = cv2.cvtColor(x, cv2.COLOR_RGB2YCrCb).astype(np.float32)

        Y = ycrcb[..., 0]
        Cr = ycrcb[..., 1]
        Cb = ycrcb[..., 2]

        # MSR on luminance channel
        Y_enh = self._msr_2d(Y, sigmas, w, eps)

        # Stretch dynamic range back to [0, 1]
        Y_enh = self._minmax01(Y_enh)

        # Recombine channels and convert back to RGB
        ycrcb_out = np.stack([Y_enh, Cr, Cb], axis=-1).astype(np.float32)

        rgb_out = cv2.cvtColor(ycrcb_out, cv2.COLOR_YCrCb2RGB).astype(np.float32)

        rgb_out = np.clip(rgb_out, 0.0, 1.0).astype(np.float32)

        out = frame.copy()
        out.data = rgb_out

        out.history.append(
            {
                "step": self.name,
                "params": {
                    "sigmas": sigmas,
                    "weights": w.tolist(),
                    "eps": eps,
                    "mode": "ycrcb_luminance",
                    "assume": "RGB",
                },
            }
        )
        return out
    

    # Core MSR implementation (single-channel)
    @staticmethod
    def _msr_2d(img2d: np.ndarray, sigmas: List[float], weights: np.ndarray, eps: float) -> np.ndarray:
        """
        Multi-Scale Retinex for one channel.

        Mathematical form:

            MSR(x) = Σ w_i * [ log(I) - log(Gσ_i * I) ]

        where:
            Gσ_i * I ≈ estimated illumination
            log difference ≈ reflectance estimation

        Log domain converts multiplicative illumination effects
        into additive differences.
        """
        x = np.clip(img2d.astype(np.float32), 0.0, 1.0)

        # Log transform (core Retinex step)
        log_x = np.log(x + eps)

        msr = np.zeros_like(x, dtype=np.float32)

        for wi, sigma in zip(weights, sigmas):

            # Gaissian blur approximates illumination component
            blur = cv2.GaussianBlur(x, (0, 0), sigmaX=float(sigma), sigmaY=float(sigma))

            # Retinex response
            msr += float(wi) * (log_x - np.log(blur + eps)).astype(np.float32)

        return msr.astype(np.float32)
    
    # Normalization utility
    @staticmethod
    def _minmax01(a: np.ndarray) -> np.ndarray:
        """
        Normalize array into [0,1].

        Includes safe fallback for near-constant images
        to avoid division-by-zero amplification.
        """
        a = a.astype(np.float32)

        mn = float(np.min(a))
        mx = float(np.max(a))

        if mx - mn > 1e-6:
            a = (a - mn) / (mx - mn)
        else:
            a = np.zeros_like(a, dtype=np.float32)
        
        return np.clip(a, 0.0, 1.0).astype(np.float32)