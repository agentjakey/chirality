"""
Phase diagram sweeps for the star ascidian model.

Four sweeps:
  A. radial attraction (k_radial) vs chirality (omega) -> star_likeness_score
  B. noise (Dr) vs repulsion (k_angular) -> fragmentation_score
  C. inhibition ratio (Dh/Da) vs mu_h -> center spacing quality (1 - spacing_cv)
  D. chirality (omega) vs agent count per center -> swirl_score

Each sweep uses small grids and short agent runs for speed.
"""

import os
import numpy as np
import csv

from .center_field import generate_star_centers, compute_center_quality
from .zooid_agents import simulate_zooid_agents
from . import metrics as star_metrics
from chirality.model_library import ensure_dir

BASE_FIELD_PARAMS = dict(
    grid_size=32, L=10.0,
    Da=0.05, Dh=5.0, mu_a=0.05, mu_h=0.05, rho=0.1, rho_0=0.001, kappa=0.1,
    dt=0.5, n_steps=1500, n_snapshots=3,
    min_distance=2.0,
)

BASE_AGENT_PARAMS = dict(
    n_arms=7, n_per_arm=3, L=10.0, r_target=1.5,
    v0=0.05, Dr=0.04, omega=0.0,
    k_attract=0.3, k_radial=2.0, k_angular=0.6, k_ev=0.4, sigma_ev=0.18,
    dt=0.02, n_steps=150, n_snapshots=3,
    mode="radial_clean", boundary="periodic",
)


def _run_one_point(field_params, agent_params, seed=42):
    """Run one (field + agents) simulation and return scalar metrics dict."""
    fd = generate_star_centers(**field_params, seed=seed)
    centers = fd["centers"]
    if len(centers) == 0:
        centers = np.array([[5.0, 5.0]])

    n_per_center = agent_params["n_arms"] * agent_params["n_per_arm"]
    _agent_keys_excluded = {"n_per_arm"}
    zr = simulate_zooid_agents(
        centers=centers,
        n_per_center=n_per_center,
        **{k: v for k, v in agent_params.items() if k not in _agent_keys_excluded},
        seed=seed + 1,
    )

    sl = star_metrics.star_likeness_score(zr, target_arms=agent_params["n_arms"])
    swirl = star_metrics.swirl_score(zr)
    frag = star_metrics.fragmentation_score(zr)
    cq = fd["quality"]
    spacing_quality = max(0.0, 1.0 - cq["spacing_cv"])

    return dict(
        star_likeness=sl,
        swirl=swirl,
        fragmentation=frag,
        spacing_quality=spacing_quality,
        n_centers=cq["n_centers"],
        spacing_mean=cq["spacing_mean"],
        spacing_cv=cq["spacing_cv"],
    )


def sweep_attraction_vs_chirality(k_radial_vals=None, omega_vals=None, seed=42):
    """Sweep A: radial attraction (k_radial) vs chirality (omega).

    Returns x_vals, y_vals, grids dict.
    """
    if k_radial_vals is None:
        k_radial_vals = np.array([0.5, 1.0, 2.0, 3.5, 5.0])
    if omega_vals is None:
        omega_vals = np.array([0.0, 0.5, 1.5, 3.0, 5.0])

    nx, ny = len(k_radial_vals), len(omega_vals)
    sl_grid = np.zeros((ny, nx))
    swirl_grid = np.zeros((ny, nx))

    for ix, k_r in enumerate(k_radial_vals):
        for iy, om in enumerate(omega_vals):
            fp = dict(BASE_FIELD_PARAMS)
            ap = dict(BASE_AGENT_PARAMS)
            ap["k_radial"] = float(k_r)
            ap["omega"] = float(om)
            if om > 0:
                ap["mode"] = "chiral_twist"
            else:
                ap["mode"] = "radial_clean"
            m = _run_one_point(fp, ap, seed=seed)
            sl_grid[iy, ix] = m["star_likeness"]
            swirl_grid[iy, ix] = abs(m["swirl"])

    return k_radial_vals, omega_vals, dict(star_likeness=sl_grid, swirl=swirl_grid)


def sweep_noise_vs_repulsion(Dr_vals=None, k_angular_vals=None, seed=42):
    """Sweep B: noise (Dr) vs angular repulsion (k_angular).

    Returns x_vals, y_vals, grids dict.
    """
    if Dr_vals is None:
        Dr_vals = np.array([0.01, 0.1, 0.3, 0.7, 1.5])
    if k_angular_vals is None:
        k_angular_vals = np.array([0.1, 0.3, 0.6, 1.0, 1.5])

    nx, ny = len(Dr_vals), len(k_angular_vals)
    frag_grid = np.zeros((ny, nx))
    sl_grid = np.zeros((ny, nx))

    for ix, dr in enumerate(Dr_vals):
        for iy, ka in enumerate(k_angular_vals):
            fp = dict(BASE_FIELD_PARAMS)
            ap = dict(BASE_AGENT_PARAMS)
            ap["Dr"] = float(dr)
            ap["k_angular"] = float(ka)
            ap["v0"] = float(0.05 + 0.2 * dr)
            m = _run_one_point(fp, ap, seed=seed)
            frag_grid[iy, ix] = m["fragmentation"]
            sl_grid[iy, ix] = m["star_likeness"]

    return Dr_vals, k_angular_vals, dict(fragmentation=frag_grid, star_likeness=sl_grid)


def sweep_inhibition_ratio(Dh_vals=None, mu_h_vals=None, seed=42):
    """Sweep C: inhibition ratio (Dh/Da) vs mu_h.

    Returns x_vals, y_vals, grids dict.
    """
    Da = 0.05
    if Dh_vals is None:
        Dh_vals = np.array([0.5, 1.0, 2.0, 5.0, 10.0])
    if mu_h_vals is None:
        mu_h_vals = np.array([0.02, 0.05, 0.10, 0.20, 0.40])

    nx, ny = len(Dh_vals), len(mu_h_vals)
    n_centers_grid = np.zeros((ny, nx))
    spacing_cv_grid = np.zeros((ny, nx))
    spacing_quality_grid = np.zeros((ny, nx))

    for ix, dh in enumerate(Dh_vals):
        for iy, muh in enumerate(mu_h_vals):
            fp = dict(BASE_FIELD_PARAMS)
            fp["Dh"] = float(dh)
            fp["mu_h"] = float(muh)
            ap = dict(BASE_AGENT_PARAMS)
            ap["n_steps"] = 50
            m = _run_one_point(fp, ap, seed=seed)
            n_centers_grid[iy, ix] = m["n_centers"]
            spacing_cv_grid[iy, ix] = m["spacing_cv"]
            spacing_quality_grid[iy, ix] = m["spacing_quality"]

    ratio_vals = Dh_vals / Da
    return ratio_vals, mu_h_vals, dict(
        n_centers=n_centers_grid,
        spacing_cv=spacing_cv_grid,
        spacing_quality=spacing_quality_grid,
    )


def sweep_chirality_vs_occupancy(omega_vals=None, n_per_arm_vals=None, seed=42):
    """Sweep D: chirality (omega) vs agents per center (via n_per_arm).

    Returns x_vals, y_vals, grids dict.
    """
    if omega_vals is None:
        omega_vals = np.array([0.0, 0.5, 1.5, 3.0, 5.0])
    if n_per_arm_vals is None:
        n_per_arm_vals = np.array([1, 2, 3, 5, 8])

    nx, ny = len(omega_vals), len(n_per_arm_vals)
    swirl_grid = np.zeros((ny, nx))
    sl_grid = np.zeros((ny, nx))

    for ix, om in enumerate(omega_vals):
        for iy, npa in enumerate(n_per_arm_vals):
            fp = dict(BASE_FIELD_PARAMS)
            ap = dict(BASE_AGENT_PARAMS)
            ap["omega"] = float(om)
            ap["n_per_arm"] = int(npa)
            if om > 0:
                ap["mode"] = "chiral_twist"
            else:
                ap["mode"] = "radial_clean"
            m = _run_one_point(fp, ap, seed=seed)
            swirl_grid[iy, ix] = abs(m["swirl"])
            sl_grid[iy, ix] = m["star_likeness"]

    return omega_vals, n_per_arm_vals, dict(swirl=swirl_grid, star_likeness=sl_grid)


def save_phase_diagram_csv(results_dict, x_vals, y_vals, x_name, y_name, output_path):
    """Save phase diagram grids as a flat CSV file."""
    ensure_dir(os.path.dirname(output_path))
    rows = []
    metric_names = list(results_dict.keys())
    for iy, yv in enumerate(y_vals):
        for ix, xv in enumerate(x_vals):
            row = {x_name: xv, y_name: yv}
            for mn in metric_names:
                row[mn] = results_dict[mn][iy, ix]
            rows.append(row)

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[x_name, y_name] + metric_names)
        writer.writeheader()
        writer.writerows(rows)
