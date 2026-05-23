"""
Named simulation presets for the Chirality Atlas.

Each preset is a dict of keyword arguments passed directly to a simulation
function. Import and use like:

    from chirality.presets import PRESETS
    from chirality.particle_sim import simulate_chiral_abp
    hist = simulate_chiral_abp(**PRESETS["chiral_vortex_gas"])
"""
from typing import Dict, Any

# -----------------------------------------------------------------------
# Particle presets
# -----------------------------------------------------------------------

BASELINE_ACTIVE_BROWNIAN = dict(
    N=200,
    L=10.0,
    v0=0.5,
    Dr=0.5,
    dt=0.01,
    n_steps=600,
    seed=42,
    boundary_mode="periodic",
    save_every=10,
)

VICSEK_FLOCKING = dict(
    N=200,
    L=10.0,
    v0=0.5,
    R=1.0,
    eta=0.15,
    omega=0.0,
    dt=0.1,
    n_steps=600,
    seed=42,
    boundary_mode="periodic",
    save_every=10,
)

CHIRAL_VORTEX_GAS = dict(
    N=200,
    L=10.0,
    v0=0.5,
    Dr=0.2,
    omega=2.0,
    chirality_mode="right",
    dt=0.01,
    n_steps=800,
    seed=42,
    boundary_mode="periodic",
    repulsion=False,
    save_every=10,
)

BOUNDARY_EDGE_CURRENT = dict(
    N=200,
    L=10.0,
    v0=0.5,
    Dr=0.3,
    omega=3.0,
    chirality_mode="right",
    dt=0.01,
    n_steps=1000,
    seed=42,
    boundary_mode="circular_trap",
    repulsion=False,
    save_every=10,
)

RACEMIC_LEFT_RIGHT_COMPETITION = dict(
    N=200,
    L=10.0,
    v0=0.5,
    Dr=0.3,
    omega=2.0,
    chirality_mode="racemic",
    dt=0.01,
    n_steps=800,
    seed=42,
    boundary_mode="periodic",
    repulsion=True,
    repulsion_strength=2.0,
    repulsion_range=0.4,
    save_every=10,
)

# -----------------------------------------------------------------------
# Pattern presets
# -----------------------------------------------------------------------

GRAY_SCOTT_SPOTS = dict(
    nx=256,
    ny=256,
    Du=0.16,
    Dv=0.08,
    F=0.035,
    k=0.065,
    dt=1.0,
    n_steps=8000,
    seed=42,
    save_every=800,
    perturbation_size=4,
    n_seeds=12,
)

GRAY_SCOTT_LABYRINTH = dict(
    nx=256,
    ny=256,
    Du=0.16,
    Dv=0.08,
    F=0.04,
    k=0.06,
    dt=1.0,
    n_steps=6000,
    seed=42,
    save_every=600,
    perturbation_size=5,
    n_seeds=8,
)

FEED_GRADIENT_PATTERN = dict(
    nx=256,
    ny=256,
    Du=0.16,
    Dv=0.08,
    F_left=0.02,
    F_right=0.055,
    k=0.063,
    dt=1.0,
    n_steps=6000,
    seed=42,
    save_every=600,
    perturbation_size=4,
    n_seeds=8,
)

OBSTACLE_DISRUPTED_PATTERN = dict(
    nx=256,
    ny=256,
    Du=0.16,
    Dv=0.08,
    F=0.035,
    k=0.065,
    dt=1.0,
    n_steps=8000,
    seed=42,
    obstacle_cx=0.5,
    obstacle_cy=0.5,
    obstacle_r=0.12,
    save_every=800,
    perturbation_size=4,
    n_seeds=12,
)

CHIRAL_SOURCE_PATTERN = dict(
    nx=256,
    ny=256,
    Du=0.16,
    Dv=0.08,
    F=0.035,
    k=0.065,
    dt=1.0,
    n_steps=8000,
    seed=42,
    source_strength=0.02,
    source_omega=0.1,
    source_r_orbit=0.2,
    source_sigma=0.05,
    save_every=800,
    perturbation_size=5,
    n_seeds=None,
)


# -----------------------------------------------------------------------
# Unified lookup dict
# -----------------------------------------------------------------------

PRESETS: Dict[str, Dict[str, Any]] = {
    "baseline_active_brownian": BASELINE_ACTIVE_BROWNIAN,
    "vicsek_flocking": VICSEK_FLOCKING,
    "chiral_vortex_gas": CHIRAL_VORTEX_GAS,
    "boundary_edge_current": BOUNDARY_EDGE_CURRENT,
    "racemic_left_right_competition": RACEMIC_LEFT_RIGHT_COMPETITION,
    "gray_scott_spots": GRAY_SCOTT_SPOTS,
    "gray_scott_labyrinth": GRAY_SCOTT_LABYRINTH,
    "feed_gradient_pattern": FEED_GRADIENT_PATTERN,
    "obstacle_disrupted_pattern": OBSTACLE_DISRUPTED_PATTERN,
    "chiral_source_pattern": CHIRAL_SOURCE_PATTERN,
}
