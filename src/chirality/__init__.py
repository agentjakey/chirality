"""
Chirality Atlas: Particles, Patterns, and Handedness in Active Matter.

A unified scientific simulation package for the UCSD Vibe Coding
Active Matter 2026 hackathon.

Two tracks:
  1. Particle simulations (ABP, chiral ABP, chiral Vicsek)
  2. Pattern formation (Gray-Scott reaction-diffusion with gradients,
     obstacles, and a chiral source)
"""

from .particle_sim import (
    simulate_abp,
    simulate_chiral_abp,
    simulate_vicsek_chiral,
    ParticleHistory,
)
from .particle_metrics import (
    polar_order,
    time_averaged_order,
    mean_squared_displacement,
    average_neighbor_count,
    swirl_index,
    boundary_accumulation,
    compute_all_particle_metrics,
)
from .pattern_sim import (
    laplacian,
    run_diffusion,
    run_logistic_growth,
    run_reaction_diffusion_one_field,
    initialize_gray_scott,
    gray_scott_step,
    simulate_gray_scott,
    simulate_feed_gradient,
    simulate_obstacle,
    simulate_chiral_source_gray_scott,
    FieldHistory,
)
from .pattern_metrics import (
    pattern_strength,
    count_clusters,
    field_asymmetry,
    obstacle_disruption_score,
    compute_all_pattern_metrics,
)
from .presets import PRESETS
from .config import (
    ABPConfig,
    ChiralABPConfig,
    VicsekConfig,
    GrayScottConfig,
    FeedGradientConfig,
    ObstacleConfig,
    ChiralSourceConfig,
)

__version__ = "0.1.0"
__all__ = [
    "simulate_abp",
    "simulate_chiral_abp",
    "simulate_vicsek_chiral",
    "ParticleHistory",
    "polar_order",
    "time_averaged_order",
    "mean_squared_displacement",
    "average_neighbor_count",
    "swirl_index",
    "boundary_accumulation",
    "compute_all_particle_metrics",
    "laplacian",
    "run_diffusion",
    "run_logistic_growth",
    "run_reaction_diffusion_one_field",
    "initialize_gray_scott",
    "gray_scott_step",
    "simulate_gray_scott",
    "simulate_feed_gradient",
    "simulate_obstacle",
    "simulate_chiral_source_gray_scott",
    "FieldHistory",
    "pattern_strength",
    "count_clusters",
    "field_asymmetry",
    "obstacle_disruption_score",
    "compute_all_pattern_metrics",
    "PRESETS",
    "ABPConfig",
    "ChiralABPConfig",
    "VicsekConfig",
    "GrayScottConfig",
    "FeedGradientConfig",
    "ObstacleConfig",
    "ChiralSourceConfig",
]
