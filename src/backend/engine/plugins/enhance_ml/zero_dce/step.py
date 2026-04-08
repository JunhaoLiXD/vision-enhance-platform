from __future__ import annotations

from copy import deepcopy
from threading import Lock
from typing import Any, Dict

from src.backend.app.services.model_manager import ModelManager
from src.backend.engine.core.image_frame import ImageFrame

from .inference import MAX_ZERO_DCE_SIDE, run_zero_dce


class ZeroDCEStep:
    """
    Pipeline step wrapper for Zero-DCE.
    """

    name = "zero_dce"
    _run_lock = Lock()

    def __init__(self, model_manager: ModelManager | None = None) -> None:
        self.model_manager = model_manager or ModelManager()

    def run(self, frame: ImageFrame, params: Dict[str, Any] | None = None) -> ImageFrame:
        params = params or {}
        device = str(params.get("device", "cpu")).lower()

        with self._run_lock:
            output_data, info = run_zero_dce(
                frame=frame,
                model_manager=self.model_manager,
                device=device,
            )

        new_meta = deepcopy(getattr(frame, "meta", {}))
        new_history = deepcopy(getattr(frame, "history", []))

        new_meta["zero_dce_notice"] = (
            f"Web demo resizes the image so the longest side is {MAX_ZERO_DCE_SIDE}px before inference."
        )

        new_history.append(
            {
                "step": self.name,
                "type": "ml",
                "params": {"device": device},
                **info,
            }
        )

        return ImageFrame(
            data=output_data,
            meta=new_meta,
            history=new_history,
        )