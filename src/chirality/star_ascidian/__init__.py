"""
Star Ascidian Colony Model for Chirality Atlas.

Two-layer hybrid model:
  Layer 1: Gierer-Meinhardt field -> star center positions
  Layer 2: Active zooid agents    -> radial arm morphology + chirality

Submodules:
  target       -- biological target description and feature checklist
  center_field -- GM field simulation and center extraction
  zooid_agents -- active particle dynamics
  hybrid_model -- combined simulation with presets
  metrics      -- quantitative scoring functions
  phase_diagram -- parameter sweep infrastructure
  compare      -- visual comparison of target vs simulation
"""

from .hybrid_model import simulate_star_ascidian_colony, StarColonyResult, PRESETS
from .zooid_agents import simulate_zooid_agents, ZooidResult
from .center_field import generate_star_centers, compute_center_quality
from . import metrics
from . import phase_diagram
from . import compare
from . import target

__all__ = [
    "simulate_star_ascidian_colony",
    "StarColonyResult",
    "PRESETS",
    "simulate_zooid_agents",
    "ZooidResult",
    "generate_star_centers",
    "compute_center_quality",
    "metrics",
    "phase_diagram",
    "compare",
    "target",
]
