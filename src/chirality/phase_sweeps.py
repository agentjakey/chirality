"""
Systematic parameter sweeps for phase diagram generation.

Each sweep function runs a grid of simulations, computes metrics at each
grid point, and returns a dict of 2D result arrays.

Defaults use small N and short run times for laptop/Colab speed.
"""
import numpy as np
from .particle_sim import simulate_chiral_abp, simulate_vicsek_chiral
from .particle_metrics import (
    polar_order,
    swirl_index,
    average_neighbor_count,
    boundary_accumulation,
)
from .pattern_sim import simulate_gray_scott, simulate_chiral_source_gray_scott
from .pattern_metrics import pattern_strength, count_clusters, field_asymmetry


# -----------------------------------------------------------------------
# Particle phase sweeps
# -----------------------------------------------------------------------

def sweep_noise_vs_chirality(
    noise_values=None,
    chirality_values=None,
    N=100,
    L=10.0,
    v0=0.5,
    dt=0.01,
    n_steps=300,
    seed=0,
    verbose=True,
):
    """
    Sweep rotational noise (Dr) vs chirality strength (omega).

    Returns dict with keys:
      noise_values, chirality_values,
      polar_order, swirl_index, boundary_accumulation, avg_neighbors
    All metric arrays are shape (len(noise_values), len(chirality_values)).
    """
    if noise_values is None:
        noise_values = np.linspace(0.1, 3.0, 8)
    if chirality_values is None:
        chirality_values = np.linspace(0.0, 4.0, 8)

    n_noise = len(noise_values)
    n_chiral = len(chirality_values)

    polar_grid = np.zeros((n_noise, n_chiral))
    swirl_grid = np.zeros((n_noise, n_chiral))
    accum_grid = np.zeros((n_noise, n_chiral))
    neighbor_grid = np.zeros((n_noise, n_chiral))

    total = n_noise * n_chiral
    count = 0

    for i, Dr in enumerate(noise_values):
        for j, omega in enumerate(chirality_values):
            hist = simulate_chiral_abp(
                N=N, L=L, v0=v0, Dr=Dr, omega=omega,
                chirality_mode="right",
                dt=dt, n_steps=n_steps,
                seed=seed + i * 100 + j,
                boundary_mode="periodic",
                repulsion=False,
                save_every=n_steps,
            )
            final_pos = hist.positions[-1]
            final_th = hist.thetas[-1]

            polar_grid[i, j] = polar_order(final_th)
            swirl_grid[i, j] = swirl_index(final_pos, final_th, L)
            accum_grid[i, j] = boundary_accumulation(final_pos, L)
            neighbor_grid[i, j] = average_neighbor_count(final_pos, L, R=1.0)

            count += 1
            if verbose and count % 10 == 0:
                print(f"  particle sweep {count}/{total}")

    return {
        "noise_values": noise_values,
        "chirality_values": chirality_values,
        "polar_order": polar_grid,
        "swirl_index": swirl_grid,
        "boundary_accumulation": accum_grid,
        "avg_neighbors": neighbor_grid,
    }


def sweep_vicsek_eta_vs_chirality(
    eta_values=None,
    chirality_values=None,
    N=100,
    L=10.0,
    v0=0.5,
    R=1.0,
    dt=0.1,
    n_steps=200,
    seed=0,
    verbose=True,
):
    """
    Sweep Vicsek noise (eta) vs chirality (omega).
    """
    if eta_values is None:
        eta_values = np.linspace(0.05, 0.8, 8)
    if chirality_values is None:
        chirality_values = np.linspace(0.0, 2.0, 8)

    n_eta = len(eta_values)
    n_chiral = len(chirality_values)

    polar_grid = np.zeros((n_eta, n_chiral))
    swirl_grid = np.zeros((n_eta, n_chiral))

    total = n_eta * n_chiral
    count = 0

    for i, eta in enumerate(eta_values):
        for j, omega in enumerate(chirality_values):
            hist = simulate_vicsek_chiral(
                N=N, L=L, v0=v0, R=R, eta=eta, omega=omega,
                dt=dt, n_steps=n_steps,
                seed=seed + i * 100 + j,
                boundary_mode="periodic",
                save_every=n_steps,
            )
            final_pos = hist.positions[-1]
            final_th = hist.thetas[-1]
            polar_grid[i, j] = polar_order(final_th)
            swirl_grid[i, j] = swirl_index(final_pos, final_th, L)

            count += 1
            if verbose and count % 10 == 0:
                print(f"  vicsek sweep {count}/{total}")

    return {
        "eta_values": eta_values,
        "chirality_values": chirality_values,
        "polar_order": polar_grid,
        "swirl_index": swirl_grid,
    }


# -----------------------------------------------------------------------
# Pattern phase sweeps
# -----------------------------------------------------------------------

def sweep_gray_scott_F_k(
    F_values=None,
    k_values=None,
    nx=64,
    ny=64,
    Du=0.16,
    Dv=0.08,
    dt=1.0,
    n_steps=2000,
    seed=42,
    verbose=True,
):
    """
    Classic Gray-Scott phase diagram: feed rate F vs kill rate k.

    Returns dict with pattern_strength and n_clusters grids.
    """
    if F_values is None:
        F_values = np.linspace(0.01, 0.07, 8)
    if k_values is None:
        k_values = np.linspace(0.04, 0.07, 8)

    nF = len(F_values)
    nk = len(k_values)
    strength_grid = np.zeros((nF, nk))
    cluster_grid = np.zeros((nF, nk))

    total = nF * nk
    count = 0

    for i, F in enumerate(F_values):
        for j, k in enumerate(k_values):
            hist = simulate_gray_scott(
                nx=nx, ny=ny, Du=Du, Dv=Dv, F=F, k=k,
                dt=dt, n_steps=n_steps,
                seed=seed,
                save_every=n_steps,
                perturbation_size=5,
            )
            v = hist.v_final
            strength_grid[i, j] = pattern_strength(v)
            n_clust, _ = count_clusters(v, threshold=0.1)
            cluster_grid[i, j] = n_clust

            count += 1
            if verbose and count % 8 == 0:
                print(f"  GS sweep {count}/{total}")

    return {
        "F_values": F_values,
        "k_values": k_values,
        "pattern_strength": strength_grid,
        "n_clusters": cluster_grid,
    }


def sweep_chiral_source(
    source_omega_values=None,
    F_values=None,
    nx=64,
    ny=64,
    Du=0.16,
    Dv=0.08,
    k=0.065,
    dt=1.0,
    n_steps=2000,
    seed=42,
    verbose=True,
):
    """
    Sweep chiral source rotation speed vs feed rate.
    Measures pattern strength and left-right asymmetry.
    """
    if source_omega_values is None:
        source_omega_values = np.linspace(0.0, 0.2, 6)
    if F_values is None:
        F_values = np.linspace(0.025, 0.055, 6)

    n_omega = len(source_omega_values)
    n_F = len(F_values)

    strength_grid = np.zeros((n_omega, n_F))
    asym_grid = np.zeros((n_omega, n_F))

    total = n_omega * n_F
    count = 0

    for i, omega in enumerate(source_omega_values):
        for j, F in enumerate(F_values):
            hist = simulate_chiral_source_gray_scott(
                nx=nx, ny=ny, Du=Du, Dv=Dv, F=F, k=k,
                dt=dt, n_steps=n_steps,
                seed=seed,
                source_strength=0.015,
                source_omega=omega,
                source_r_orbit=0.18,
                source_sigma=0.04,
                save_every=n_steps,
                perturbation_size=3,
            )
            v = hist.v_final
            strength_grid[i, j] = pattern_strength(v)
            asym_grid[i, j] = abs(field_asymmetry(v))

            count += 1
            if verbose and count % 6 == 0:
                print(f"  chiral source sweep {count}/{total}")

    return {
        "source_omega_values": source_omega_values,
        "F_values": F_values,
        "pattern_strength": strength_grid,
        "field_asymmetry": asym_grid,
    }
