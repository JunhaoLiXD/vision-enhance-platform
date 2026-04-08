"""
Global plugin registry for enhancement algorithms.

Responsibilities:
- Map algorithm names to their Step implementations.
- Provide a single registry for classical, ML, and future astronomy plugins.
- Keep pipeline execution independent from plugin category layout.

"""
from __future__ import annotations

from typing import Dict

from src.backend.app.services.model_manager import ModelManager

from src.backend.engine.plugins.enhance_classical.gamma import GammaStep
from src.backend.engine.plugins.enhance_classical.clahe import CLAHEStep
from src.backend.engine.plugins.enhance_classical.retinex import RetinexMSRLuminanceStep
from src.backend.engine.plugins.enhance_classical.unsharp_luma import UnsharpMaskLuminanceStep
from src.backend.engine.plugins.enhance_classical.bilateral import BilateralLuminanceStep

from src.backend.engine.plugins.enhance_ml.zero_dce.step import ZeroDCEStep

def build_registry() -> Dict[str, object]:
    model_manager = ModelManager()

    return {
        "gamma": GammaStep(),
        "clahe": CLAHEStep(),
        "retinex_msr_luma": RetinexMSRLuminanceStep(),
        "unsharp_luma": UnsharpMaskLuminanceStep(),
        "bilateral_luma": BilateralLuminanceStep(),

        # ML
        "zero_dce": ZeroDCEStep(model_manager=model_manager)
    }
