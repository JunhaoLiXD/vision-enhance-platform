"""
Global plugin registry for enhancement algorithms.

Responsibilities:
- Map algorithm names to their Step implementations.
- Provide a single registry for classical, ML, and future astronomy plugins.
- Keep pipeline execution independent from plugin category layout.

"""
from __future__ import annotations

from typing import Any, Dict, Optional

from src.backend.app.services.model_manager import ModelManager

from src.backend.engine.plugins.enhance_classical.gamma import GammaStep
from src.backend.engine.plugins.enhance_classical.clahe import CLAHEStep
from src.backend.engine.plugins.enhance_classical.retinex import RetinexMSRLuminanceStep
from src.backend.engine.plugins.enhance_classical.unsharp_luma import UnsharpMaskLuminanceStep
from src.backend.engine.plugins.enhance_classical.bilateral import BilateralLuminanceStep

from src.backend.engine.plugins.enhance_ml.zero_dce.step import ZeroDCEStep

# Process-level singletons — created once when this module is first imported.
# ModelManager caches loaded model weights; sharing it across all requests
# ensures Zero-DCE weights are loaded from disk exactly once per process.
_model_manager: ModelManager = ModelManager()
_registry: Optional[Dict[str, object]] = None


def get_algorithms_schema() -> Dict[str, Any]:
    """
    Collect description and params_schema from every registered classical step.
    ML-only steps (zero_dce) are excluded because they are exposed via presets,
    not the custom pipeline builder.
    """
    _EXCLUDE = {"zero_dce"}
    return {
        name: {
            "description": getattr(step, "description", ""),
            "params": getattr(step, "params_schema", {}),
        }
        for name, step in build_registry().items()
        if name not in _EXCLUDE
    }


def build_registry() -> Dict[str, object]:
    global _registry
    if _registry is None:
        _registry = {
            "gamma": GammaStep(),
            "clahe": CLAHEStep(),
            "retinex_msr_luma": RetinexMSRLuminanceStep(),
            "unsharp_luma": UnsharpMaskLuminanceStep(),
            "bilateral_luma": BilateralLuminanceStep(),
            "zero_dce": ZeroDCEStep(model_manager=_model_manager),
        }
    return _registry
