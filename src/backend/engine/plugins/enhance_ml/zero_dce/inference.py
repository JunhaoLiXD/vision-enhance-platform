from __future__ import annotations

import gc
import time
from typing import Any, Dict, Tuple

import numpy as np
import torch

from .preprocess import imageframe_to_tensor, tensor_to_image


def run_zero_dce(
    frame,
    model_manager,
    device: str = "cpu",
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Run Zero-DCE inference on an ImageFrame-like object.

    Assumes:
    - frame.data is HWC image data
    - frame.data is RGB or convertible RGB
    """

    model, resolved_device, weights_path = model_manager.get_zero_dce(device=device)

    input_shape = tuple(frame.data.shape)
    input_tensor = imageframe_to_tensor(frame.data, resolved_device)

    start = time.perf_counter()
    with torch.inference_mode():
        enhanced_tensor = model(input_tensor)
    inference_ms = (time.perf_counter() - start) * 1000.0

    output_image = tensor_to_image(enhanced_tensor)
    output_shape = tuple(output_image.shape)

    info = {
        "model": "Zero-DCE",
        "weights": weights_path.name,
        "device": str(resolved_device),
        "input_shape": input_shape,
        "output_shape": output_shape,
        "inference_ms": round(inference_ms, 3),
    }

    del input_tensor
    del enhanced_tensor
    gc.collect()

    if resolved_device.type == "cuda":
        torch.cuda.empty_cache()

    return output_image, info