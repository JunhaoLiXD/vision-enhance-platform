"""
Plugin registry for classical enhancement algorithms.

Responsibilities:
- Map algorithm names (strings) to their corresponding Step implementations.
- Provide a centralized lookup mechanism for the pipeline.
- Enable plugin-based extensibility without modifying pipeline logic.

Current registrations:
- "gamma" -> GammaStep
- "clahe" -> CLAHEStep

Notes:
- Adding new algorithms requires registration here.
"""
from __future__ import annotations

from typing import Dict

from src.backend.engine.plugins.enhance_classical.gamma import GammaStep
from src.backend.engine.plugins.enhance_classical.clahe import CLAHEStep
from src.backend.engine.plugins.enhance_classical.clahe import RetinexMSRLuminanceStep



def build_registry() -> Dict[str, object]:
    # Later will add CLAHE, Retinex, etc.
    return {
        "gamma": GammaStep(),
        "clahe": CLAHEStep(),
        "retinex_msr_luma": RetinexMSRLuminanceStep(),
    }
