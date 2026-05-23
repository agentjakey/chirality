"""
Combined two-layer star ascidian colony model.

Steps:
  1. Run GM field to establish star center positions (Layer 1)
  2. Initialize zooid agents around those centers (Layer 2 init)
  3. Evolve agent dynamics under attraction, repulsion, chirality (Layer 2 dynamics)
  4. Compute star-likeness metrics on final state

Named presets cover the expected phases from CLAUDE_CONTEXT.md.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from .center_field import generate_star_centers, compute_center_quality
from .zooid_agents import simulate_zooid_agents, ZooidResult
from . import metrics as star_metrics


@dataclass
class StarColonyResult:
    field: np.ndarray               # (N, N) activator field
    inhibitor: np.ndarray           # (N, N) inhibitor field
    field_snapshots: np.ndarray     # (n_snapshots, N, N)
    centers: np.ndarray             # (K, 2) physical coordinates
    center_quality: Dict[str, Any]
    zooid: ZooidResult
    metrics: Dict[str, Any]
    params: Dict[str, Any]
    preset: str


PRESETS = {
    "clean_star_systems": dict(
        grid_size=64, L=10.0,
        Da=0.05, Dh=5.0, mu_a=0.05, mu_h=0.05, rho=0.1, rho_0=0.001, kappa=0.1,
        dt_field=0.5, n_field_steps=3000,
        n_arms=7, n_per_arm=3, r_target=1.5,
        v0=0.05, Dr=0.04, omega=0.0,
        k_attract=0.3, k_radial=2.0, k_angular=0.6, k_ev=0.4, sigma_ev=0.18,
        dt=0.02, n_steps=400, n_snapshots=10,
        mode="radial_clean", boundary="periodic",
        min_distance=2.5,
    ),
    "chiral_twisted_stars": dict(
        grid_size=64, L=10.0,
        Da=0.05, Dh=5.0, mu_a=0.05, mu_h=0.05, rho=0.1, rho_0=0.001, kappa=0.1,
        dt_field=0.5, n_field_steps=3000,
        n_arms=7, n_per_arm=3, r_target=1.5,
        v0=0.08, Dr=0.04, omega=2.5,
        k_attract=0.3, k_radial=2.0, k_angular=0.5, k_ev=0.4, sigma_ev=0.18,
        dt=0.02, n_steps=600, n_snapshots=10,
        mode="chiral_twist", boundary="periodic",
        min_distance=2.5,
    ),
    "racemic_mixed": dict(
        grid_size=64, L=10.0,
        Da=0.05, Dh=5.0, mu_a=0.05, mu_h=0.05, rho=0.1, rho_0=0.001, kappa=0.1,
        dt_field=0.5, n_field_steps=3000,
        n_arms=7, n_per_arm=3, r_target=1.5,
        v0=0.08, Dr=0.04, omega=2.5,
        k_attract=0.3, k_radial=2.0, k_angular=0.5, k_ev=0.4, sigma_ev=0.18,
        dt=0.02, n_steps=600, n_snapshots=10,
        mode="racemic_mixed", boundary="periodic",
        min_distance=2.5,
    ),
    "overcrowded_merged_systems": dict(
        grid_size=64, L=10.0,
        Da=0.05, Dh=5.0, mu_a=0.05, mu_h=0.05, rho=0.1, rho_0=0.001, kappa=0.1,
        dt_field=0.5, n_field_steps=3000,
        n_arms=7, n_per_arm=9, r_target=1.5,
        v0=0.05, Dr=0.04, omega=0.0,
        k_attract=0.2, k_radial=1.5, k_angular=0.2, k_ev=0.3, sigma_ev=0.18,
        dt=0.02, n_steps=400, n_snapshots=10,
        mode="overcrowded", boundary="periodic",
        min_distance=2.5,
    ),
    "noisy_fragmented_systems": dict(
        grid_size=64, L=10.0,
        Da=0.05, Dh=5.0, mu_a=0.05, mu_h=0.05, rho=0.1, rho_0=0.001, kappa=0.1,
        dt_field=0.5, n_field_steps=3000,
        n_arms=7, n_per_arm=3, r_target=1.5,
        v0=0.35, Dr=0.9, omega=0.0,
        k_attract=0.3, k_radial=1.0, k_angular=0.3, k_ev=0.3, sigma_ev=0.18,
        dt=0.02, n_steps=400, n_snapshots=10,
        mode="noisy_fragmented", boundary="periodic",
        min_distance=2.5,
    ),
    "boundary_pinned_stars": dict(
        grid_size=64, L=10.0,
        Da=0.05, Dh=5.0, mu_a=0.05, mu_h=0.05, rho=0.1, rho_0=0.001, kappa=0.1,
        dt_field=0.5, n_field_steps=3000,
        n_arms=7, n_per_arm=3, r_target=1.5,
        v0=0.05, Dr=0.04, omega=0.0,
        k_attract=0.3, k_radial=2.0, k_angular=0.6, k_ev=0.4, sigma_ev=0.18,
        dt=0.02, n_steps=400, n_snapshots=10,
        mode="boundary_pinned", boundary="box",
        min_distance=2.5,
    ),
    "weak_inhibition_uniform_mat": dict(
        grid_size=64, L=10.0,
        Da=0.05, Dh=0.15, mu_a=0.05, mu_h=0.05, rho=0.1, rho_0=0.001, kappa=0.1,
        dt_field=0.5, n_field_steps=2000,
        n_arms=7, n_per_arm=3, r_target=1.5,
        v0=0.05, Dr=0.04, omega=0.0,
        k_attract=0.3, k_radial=2.0, k_angular=0.6, k_ev=0.4, sigma_ev=0.18,
        dt=0.02, n_steps=200, n_snapshots=10,
        mode="radial_clean", boundary="periodic",
        min_distance=1.0,
    ),
    "hero_reference_match": dict(
        grid_size=64, L=10.0,
        Da=0.05, Dh=5.0, mu_a=0.05, mu_h=0.05, rho=0.1, rho_0=0.001, kappa=0.1,
        dt_field=0.5, n_field_steps=3000,
        n_arms=7, n_per_arm=5, r_target=1.4,
        v0=0.04, Dr=0.03, omega=0.3,
        k_attract=0.35, k_radial=2.5, k_angular=0.7, k_ev=0.5, sigma_ev=0.16,
        dt=0.02, n_steps=500, n_snapshots=10,
        mode="chiral_twist", boundary="periodic",
        min_distance=2.5,
    ),
}


def simulate_star_ascidian_colony(
    preset="clean_star_systems",
    seed=42,
    n_snapshots=10,
    **kwargs,
):
    """Simulate one star ascidian colony.

    Loads the named preset, applies any keyword overrides, runs both layers,
    and returns a StarColonyResult.
    """
    if preset not in PRESETS:
        raise ValueError(f"Unknown preset '{preset}'. Available: {list(PRESETS)}")

    params = dict(PRESETS[preset])
    params.update(kwargs)

    n_arms = params["n_arms"]
    n_per_arm = params["n_per_arm"]
    n_per_center = n_arms * n_per_arm

    # Layer 1: generate field + centers
    field_data = generate_star_centers(
        grid_size=params["grid_size"],
        L=params["L"],
        Da=params["Da"],
        Dh=params["Dh"],
        mu_a=params["mu_a"],
        mu_h=params["mu_h"],
        rho=params["rho"],
        rho_0=params["rho_0"],
        kappa=params["kappa"],
        dt=params["dt_field"],
        n_steps=params["n_field_steps"],
        n_snapshots=n_snapshots,
        min_distance=params["min_distance"],
        seed=seed,
    )

    centers = field_data["centers"]

    # Fallback: if no centers found, place 4 default centers in a grid
    if len(centers) == 0:
        L = params["L"]
        centers = np.array([
            [L * 0.25, L * 0.25],
            [L * 0.75, L * 0.25],
            [L * 0.25, L * 0.75],
            [L * 0.75, L * 0.75],
        ])

    # Layer 2: simulate zooid agents
    zooid_result = simulate_zooid_agents(
        centers=centers,
        n_per_center=n_per_center,
        n_arms=n_arms,
        L=params["L"],
        r_target=params["r_target"],
        v0=params["v0"],
        Dr=params["Dr"],
        omega=params["omega"],
        k_attract=params["k_attract"],
        k_radial=params["k_radial"],
        k_angular=params["k_angular"],
        k_ev=params["k_ev"],
        sigma_ev=params["sigma_ev"],
        dt=params["dt"],
        n_steps=params["n_steps"],
        n_snapshots=n_snapshots,
        mode=params["mode"],
        boundary=params["boundary"],
        seed=seed + 1,
    )

    # Compute metrics
    m = star_metrics.visual_similarity_report(zooid_result, target_arms=n_arms)

    return StarColonyResult(
        field=field_data["field"],
        inhibitor=field_data["inhibitor"],
        field_snapshots=field_data["snapshots_u"],
        centers=centers,
        center_quality=field_data["quality"],
        zooid=zooid_result,
        metrics=m,
        params=params,
        preset=preset,
    )
