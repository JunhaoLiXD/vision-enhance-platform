from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import torch

from src.backend.engine.plugins.enhance_ml.zero_dce.network import ZeroDCENet


class ModelManager:
    """
    Simple model manager for ML inference models.

    Responsibilities:
    - resolve device
    - lazy-load model
    - cache loaded model instances
    """

    def __init__(self) -> None:
        self._cache: Dict[Tuple[str, str], torch.nn.Module] = {}

        self.project_root = Path(__file__).resolve().parents[4]
        self.models_root = self.project_root / "models"

    def resolve_device(self, requested_device: str = "auto") -> torch.device:
        requested_device = (requested_device or "auto").lower()

        if requested_device == "auto":
            return torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if requested_device == "cpu":
            return torch.device("cpu")

        if requested_device == "cuda":
            if not torch.cuda.is_available():
                raise RuntimeError("CUDA was requested but is not available on this machine.")
            return torch.device("cuda")

        raise ValueError(
            f"Unsupported device option: {requested_device}. Use auto, cpu, or cuda."
        )

    def _load_state_dict(self, weights_path: Path, device: torch.device) -> dict:
        checkpoint = torch.load(weights_path, map_location=device)

        if isinstance(checkpoint, dict):
            for key in ("state_dict", "model_state_dict", "model"):
                if key in checkpoint and isinstance(checkpoint[key], dict):
                    return checkpoint[key]

        if isinstance(checkpoint, dict):
            return checkpoint

        raise RuntimeError(f"Unexpected checkpoint format at {weights_path}")

    def get_zero_dce(self, device: str = "auto") -> tuple[torch.nn.Module, torch.device, Path]:
        resolved_device = self.resolve_device(device)
        cache_key = ("zero_dce", str(resolved_device))

        weights_path = self.models_root / "zero_dce" / "Epoch99.pth"

        if cache_key in self._cache:
            return self._cache[cache_key], resolved_device, weights_path

        if not weights_path.exists():
            raise FileNotFoundError(
                f"Zero-DCE weights not found: {weights_path}\n"
                f"Please place Epoch99.pth at models/zero_dce/Epoch99.pth"
            )

        model = ZeroDCENet()
        state_dict = self._load_state_dict(weights_path, resolved_device)
        model.load_state_dict(state_dict, strict=True)
        model.to(resolved_device)
        model.eval()

        for param in model.parameters():
            param.requires_grad_(False)

        self._cache[cache_key] = model
        return model, resolved_device, weights_path