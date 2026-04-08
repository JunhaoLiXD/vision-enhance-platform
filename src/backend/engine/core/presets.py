"""
Preset pipeline definitions for common enhancement tasks.

Responsibilities:
- Provide reusable enhancement pipeline specifications.
- Group existing algorithm plugins into ready-to-use workflows.
- Allow the backend or frontend to select a preset by name
  instead of manually constructing every pipeline step.

Notes:
- Each preset expands into a standard pipeline spec:
  [{"name": ..., "params": {...}}, ...]
- Presets do NOT execute anything themselves.
- Presets should only reference steps already registered in the plugin registry.
"""
from __future__ import annotations

from typing import Dict, List, Any


PRESET_PIPELINES: Dict[str, List[Dict[str, Any]]] = {
    "natural_enhance": [
        {
            "name": "bilateral_luma",
            "params": {
                "d": -1,
                "sigma_color": 0.06,
                "sigma_space": 3.0,
            },
        },
        {
            "name": "retinex_msr_luma",
            "params": {
                "sigmas": [15.0, 80.0, 250.0],
                "weights": None,
                "eps": 1e-6,
            },
        },
        {
            "name": "clahe",
            "params": {
                "clip_limit": 2.0,
                "tile_grid_size": [8, 8],
            },
        },
        {
            "name": "gamma",
            "params": {
                "gamma": 1.1,
            },
        },
        {
            "name": "unsharp_luma",
            "params": {
                "amount": 1.0,
                "radius": 2.0,
                "threshold": 0.0,
            },
        },
    ],

    "low_light_enhance": [
        {
            "name": "bilateral_luma",
            "params": {
                "d": -1,
                "sigma_color": 0.08,
                "sigma_space": 4.0,
            },
        },
        {
            "name": "retinex_msr_luma",
            "params": {
                "sigmas": [15.0, 80.0, 250.0],
                "weights": None,
                "eps": 1e-6,
            },
        },
        {
            "name": "gamma",
            "params": {
                "gamma": 1.2,
            },
        },
        {
            "name": "clahe",
            "params": {
                "clip_limit": 2.5,
                "tile_grid_size": [8, 8],
            },
        },
        {
            "name": "unsharp_luma",
            "params": {
                "amount": 0.8,
                "radius": 2.0,
                "threshold": 0.01,
            },
        },
    ],

    "detail_boost": [
        {
            "name": "clahe",
            "params": {
                "clip_limit": 2.5,
                "tile_grid_size": [8, 8],
            },
        },
        {
            "name": "gamma",
            "params": {
                "gamma": 1.05,
            },
        },
        {
            "name": "unsharp_luma",
            "params": {
                "amount": 1.5,
                "radius": 1.5,
                "threshold": 0.0,
            },
        },
    ],

    "zero_dce_enhance": [
        {
            "name": "zero_dce",
            "params": {
                "device": "auto",
            },
        },
    ],
}


def get_preset_pipeline(name: str) -> List[Dict[str, Any]]:
    """
    Return a preset pipeline spec by name.

    Raises:
        ValueError: if the preset name is unknown.
    """
    if name not in PRESET_PIPELINES:
        raise ValueError(f"Unknown preset: {name}")
    return PRESET_PIPELINES[name]


def list_presets() -> Dict[str, List[Dict[str, Any]]]:
    """
    Return all available preset definitions.
    """
    return PRESET_PIPELINES