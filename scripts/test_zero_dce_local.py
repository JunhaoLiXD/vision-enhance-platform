# scripts/test_zero_dce_local.py

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

# Make project root importable when running as a script.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.backend.app.services.model_manager import ModelManager
from src.backend.engine.core.image_frame import ImageFrame
from src.backend.engine.plugins.enhance_ml.zero_dce.inference import run_zero_dce


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python scripts/test_zero_dce_local.py <input_image> <output_image>")
        return

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not input_path.exists():
        raise FileNotFoundError(f"Input image not found: {input_path}")

    image = Image.open(input_path).convert("RGB")
    image_np = np.asarray(image).astype(np.float32) / 255.0

    frame = ImageFrame(
        data=image_np,
        meta={"source": str(input_path)},
        history=[],
    )

    model_manager = ModelManager()
    output_np, info = run_zero_dce(frame, model_manager, device="auto")

    output_uint8 = (np.clip(output_np, 0.0, 1.0) * 255.0).astype(np.uint8)
    output_image = Image.fromarray(output_uint8)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_image.save(output_path)

    print("Saved enhanced image to:", output_path)
    print("Inference info:", info)


if __name__ == "__main__":
    main()