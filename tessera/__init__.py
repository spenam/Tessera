"""Tessera: lightweight parametric regular and aperiodic tiling art."""
from .render import render
from .presets import preset
from .catalogue import uniform_catalogue, uniform_by_id, uniform_counts, known_uniform_counts
from .tilings.uniform import generate_uniform
__version__ = "0.4.0"
__all__ = ["render", "preset", "uniform_catalogue", "uniform_by_id", "uniform_counts", "known_uniform_counts", "generate_uniform"]
