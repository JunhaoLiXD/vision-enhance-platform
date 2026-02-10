from __future__ import annotations

from typing import Dict

from src.backend.engine.plugins.enhance_classical.gamma import GammaStep
from src.backend.engine.plugins.enhance_classical.clahe import CLAHEStep


def build_registry() -> Dict[str, object]:
    # Later you'll add CLAHE, Retinex, etc.
    return {
        "gamma": GammaStep(),
        "clahe": CLAHEStep(),
    }
