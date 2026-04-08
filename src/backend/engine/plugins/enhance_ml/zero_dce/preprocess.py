from __future__ import annotations

import numpy as np
import torch


def ensure_rgb_float01(data: np.ndarray) -> np.ndarray:
    """
    Ensure image is HWC, 3-channel, float32, contiguous, and in [0, 1].
    """
    if data.ndim != 3:
        raise ValueError(f"Expected HWC image with 3 dimensions, got shape={data.shape}")

    if data.shape[2] != 3:
        raise ValueError(f"Expected 3-channel RGB image, got shape={data.shape}")

    out = data.astype(np.float32, copy=False)

    if out.max() > 1.0:
        out = out / 255.0

    out = np.clip(out, 0.0, 1.0)
    out = np.ascontiguousarray(out)
    return out


def imageframe_to_tensor(data: np.ndarray, device: torch.device) -> torch.Tensor:
    """
    Convert HWC float image in [0,1] to BCHW float32 torch tensor.
    """
    data = ensure_rgb_float01(data)
    tensor = torch.from_numpy(data).permute(2, 0, 1).unsqueeze(0)
    tensor = tensor.to(device=device, dtype=torch.float32)
    return tensor


def tensor_to_image(tensor: torch.Tensor) -> np.ndarray:
    """
    Convert BCHW or CHW tensor back to HWC float32 numpy array in [0,1].
    """
    if tensor.ndim == 4:
        if tensor.shape[0] != 1:
            raise ValueError(f"Expected batch size 1, got shape={tuple(tensor.shape)}")
        tensor = tensor.squeeze(0)

    if tensor.ndim != 3:
        raise ValueError(f"Expected CHW tensor, got shape={tuple(tensor.shape)}")

    image = tensor.detach()
    if image.device.type != "cpu":
        image = image.cpu()

    image = image.permute(1, 2, 0).numpy()
    image = np.clip(image, 0.0, 1.0).astype(np.float32, copy=False)
    return image