from __future__ import annotations

import gc
import time
from typing import Any, Dict, Tuple

import numpy as np
import torch

from .preprocess import (
    imageframe_to_tensor,
    resize_longest_side,
    restore_to_size,
    tensor_to_image,
)

MAX_ZERO_DCE_SIDE = 384


def run_zero_dce(
    frame,
    model_manager,
    device: str = "cpu",
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Run Zero-DCE inference on an ImageFrame-like object.
    """

    model, resolved_device, weights_path = model_manager.get_zero_dce(device=device)

    resized_input, original_hw, inference_hw, resized = resize_longest_side(
        frame.data,
        max_side=MAX_ZERO_DCE_SIDE,
    )

    input_tensor = imageframe_to_tensor(resized_input, resolved_device)

    start = time.perf_counter()
    with torch.inference_mode():
        enhanced_tensor = model(input_tensor)
    inference_ms = (time.perf_counter() - start) * 1000.0

    output_image = tensor_to_image(enhanced_tensor)

    if resized:
        output_image = restore_to_size(output_image, original_hw)

    output_shape = tuple(output_image.shape)

    info = {
        "model": "Zero-DCE",
        "weights": weights_path.name,
        "device": str(resolved_device),
        "input_shape": tuple(frame.data.shape),
        "inference_shape": (int(inference_hw[0]), int(inference_hw[1]), 3),
        "output_shape": output_shape,
        "inference_ms": round(inference_ms, 3),
        "resized_for_inference": resized,
        "max_inference_side": MAX_ZERO_DCE_SIDE,
    }

    del input_tensor
    del enhanced_tensor
    gc.collect()

    if resolved_device.type == "cuda":
        torch.cuda.empty_cache()

    return output_image, info