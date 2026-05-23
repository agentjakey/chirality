"""
Particle-based active matter simulations.

Implements:
  - Active Brownian Particles (ABP) -- from tutorial track 1
  - Chiral ABP (omega term added to orientation update)
  - Vicsek model with optional chirality

All simulations return position and orientation histories as numpy arrays.
Positions are in [0, L) x [0, L).
"""
import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParticleHistory:
    """Snapshots saved every `save_every` steps."""
    positions: np.ndarray   # (n_snapshots, N, 2)
    thetas: np.ndarray      # (n_snapshots, N)
    omegas: np.ndarray      # (N,) chirality rates, constant over time
    times: np.ndarray       # (n_snapshots,)
    L: float
    N: int


# -----------------------------------------------------------------------
# Boundary conditions
# -----------------------------------------------------------------------

def _apply_periodic(positions, L):
    return positions % L


def _apply_reflective(positions, thetas, L):
    pos = positions.copy()
    th = thetas.copy()
    # x walls
    mask = pos[:, 0] < 0
    pos[mask, 0] = -pos[mask, 0]
    th[mask] = np.pi - th[mask]
    mask = pos[:, 0] > L
    pos[mask, 0] = 2 * L - pos[mask, 0]
    th[mask] = np.pi - th[mask]
    # y walls
    mask = pos[:, 1] < 0
    pos[mask, 1] = -pos[mask, 1]
    th[mask] = -th[mask]
    mask = pos[:, 1] > L
    pos[mask, 1] = 2 * L - pos[mask, 1]
    th[mask] = -th[mask]
    # secondary clamp to prevent escaping on bounce
    pos = np.clip(pos, 0.0, L)
    return pos, th


def _apply_circular_trap(positions, thetas, L, trap_r=None):
    """Confine particles inside a circle of radius trap_r centered at L/2."""
    if trap_r is None:
        trap_r = L * 0.45
    center = np.array([L / 2, L / 2])
    r_vec = positions - center
    r_mag = np.linalg.norm(r_vec, axis=1, keepdims=True)
    r_mag_1d = r_mag[:, 0]
    outside = r_mag_1d > trap_r
    if outside.any():
        # push back to boundary
        r_hat = r_vec[outside] / r_mag[outside]
        positions[outside] = center + trap_r * r_hat * 0.999
        # reflect angular component of velocity
        r_hat_1d = r_hat  # (n_out, 2)
        th = thetas[outside]
        vx = np.cos(th)
        vy = np.sin(th)
        dot = vx * r_hat_1d[:, 0] + vy * r_hat_1d[:, 1]
        vx_new = vx - 2 * dot * r_hat_1d[:, 0]
        vy_new = vy - 2 * dot * r_hat_1d[:, 1]
        thetas[outside] = np.arctan2(vy_new, vx_new)
    return positions, thetas


def _apply_boundary(positions, thetas, L, mode):
    if mode == "periodic":
        return _apply_periodic(positions, L), thetas
    elif mode == "reflective":
        return _apply_reflective(positions, thetas, L)
    elif mode == "circular_trap":
        return _apply_circular_trap(positions.copy(), thetas.copy(), L)
    else:
        raise ValueError(f"Unknown boundary mode: {mode}")


# -----------------------------------------------------------------------
# Soft repulsion (optional)
# -----------------------------------------------------------------------

def _soft_repulsion(positions, L, repulsion_strength, repulsion_range):
    """
    Returns displacement corrections due to soft repulsive interactions.
    Uses minimum-image convention.
    Complexity O(N^2) -- keep N <= 400 when enabled.
    """
    N = len(positions)
    disp = np.zeros_like(positions)
    for i in range(N):
        for j in range(i + 1, N):
            dr = positions[i] - positions[j]
            # minimum image
            dr = dr - L * np.round(dr / L)
            d = np.linalg.norm(dr)
            if 0 < d < repulsion_range:
                force_mag = repulsion_strength * (repulsion_range - d) / repulsion_range
                f = force_mag * dr / d
                disp[i] += f
                disp[j] -= f
    return disp


# -----------------------------------------------------------------------
# Chirality assignment
# -----------------------------------------------------------------------

def _assign_omegas(N, omega_magnitude, chirality_mode, rng):
    """Return per-particle rotation rates (rad/step)."""
    if chirality_mode == "none":
        return np.zeros(N)
    elif chirality_mode == "right":
        return np.full(N, abs(omega_magnitude))
    elif chirality_mode == "left":
        return np.full(N, -abs(omega_magnitude))
    elif chirality_mode == "racemic":
        omegas = np.full(N, abs(omega_magnitude))
        omegas[:N // 2] = -abs(omega_magnitude)
        rng.shuffle(omegas)
        return omegas
    elif chirality_mode == "random":
        return rng.normal(0, abs(omega_magnitude), N)
    else:
        raise ValueError(f"Unknown chirality_mode: {chirality_mode}")


# -----------------------------------------------------------------------
# Minimum-image distance helper for Vicsek
# -----------------------------------------------------------------------

def _minimum_image_dist2(positions, L):
    """
    Returns (N, N) matrix of squared minimum-image distances.
    Vectorized: O(N^2) memory.
    """
    dx = positions[:, 0:1] - positions[:, 0]   # (N, N)
    dy = positions[:, 1:2] - positions[:, 1]
    dx = dx - L * np.round(dx / L)
    dy = dy - L * np.round(dy / L)
    return dx ** 2 + dy ** 2


# -----------------------------------------------------------------------
# simulate_abp -- tutorial direct extension
# -----------------------------------------------------------------------

def simulate_abp(
    N=200,
    L=10.0,
    v0=0.5,
    Dr=0.5,
    dt=0.01,
    n_steps=500,
    seed=42,
    boundary_mode="periodic",
    save_every=10,
):
    """
    Active Brownian Particles (no alignment, no chirality).

    theta_i(t + dt) = theta_i(t) + sqrt(2 * Dr * dt) * xi_i(t)
    x_i(t + dt)     = x_i(t) + v0 * cos(theta_i) * dt
    y_i(t + dt)     = y_i(t) + v0 * sin(theta_i) * dt

    Returns a ParticleHistory object.
    """
    rng = np.random.default_rng(seed)
    pos = rng.uniform(0, L, (N, 2))
    theta = rng.uniform(0, 2 * np.pi, N)
    omegas = np.zeros(N)

    noise_scale = np.sqrt(2 * Dr * dt)
    n_snapshots = n_steps // save_every + 1

    pos_hist = np.zeros((n_snapshots, N, 2))
    th_hist = np.zeros((n_snapshots, N))
    times = np.zeros(n_snapshots)
    snap = 0

    pos_hist[snap] = pos
    th_hist[snap] = theta
    times[snap] = 0.0
    snap += 1

    for step in range(1, n_steps + 1):
        theta = theta + noise_scale * rng.standard_normal(N)
        pos[:, 0] += v0 * np.cos(theta) * dt
        pos[:, 1] += v0 * np.sin(theta) * dt
        pos, theta = _apply_boundary(pos, theta, L, boundary_mode)

        if step % save_every == 0 and snap < n_snapshots:
            pos_hist[snap] = pos
            th_hist[snap] = theta
            times[snap] = step * dt
            snap += 1

    return ParticleHistory(
        positions=pos_hist[:snap],
        thetas=th_hist[:snap],
        omegas=omegas,
        times=times[:snap],
        L=L,
        N=N,
    )


# -----------------------------------------------------------------------
# simulate_chiral_abp -- tutorial extension with omega
# -----------------------------------------------------------------------

def simulate_chiral_abp(
    N=200,
    L=10.0,
    v0=0.5,
    Dr=0.5,
    omega=1.0,
    chirality_mode="right",
    dt=0.01,
    n_steps=500,
    seed=42,
    boundary_mode="periodic",
    repulsion=False,
    repulsion_strength=2.0,
    repulsion_range=0.3,
    save_every=10,
):
    """
    Chiral Active Brownian Particles.

    theta_i(t + dt) = theta_i(t) + omega_i * dt + sqrt(2 * Dr * dt) * xi_i(t)

    chirality_mode options:
      "none"    -- no chirality (reduces to standard ABP)
      "right"   -- all particles rotate clockwise (omega > 0)
      "left"    -- all particles rotate counter-clockwise (omega < 0)
      "racemic" -- half left, half right
      "random"  -- each particle gets a random omega from N(0, |omega|)

    Returns a ParticleHistory object.
    """
    rng = np.random.default_rng(seed)
    pos = rng.uniform(0, L, (N, 2))
    theta = rng.uniform(0, 2 * np.pi, N)
    omegas = _assign_omegas(N, omega, chirality_mode, rng)

    noise_scale = np.sqrt(2 * Dr * dt)
    n_snapshots = n_steps // save_every + 1

    pos_hist = np.zeros((n_snapshots, N, 2))
    th_hist = np.zeros((n_snapshots, N))
    times = np.zeros(n_snapshots)
    snap = 0

    pos_hist[snap] = pos
    th_hist[snap] = theta
    times[snap] = 0.0
    snap += 1

    for step in range(1, n_steps + 1):
        theta = theta + omegas * dt + noise_scale * rng.standard_normal(N)

        if repulsion:
            disp = _soft_repulsion(pos, L, repulsion_strength, repulsion_range)
            pos += disp * dt

        pos[:, 0] += v0 * np.cos(theta) * dt
        pos[:, 1] += v0 * np.sin(theta) * dt
        pos, theta = _apply_boundary(pos, theta, L, boundary_mode)

        if step % save_every == 0 and snap < n_snapshots:
            pos_hist[snap] = pos
            th_hist[snap] = theta
            times[snap] = step * dt
            snap += 1

    return ParticleHistory(
        positions=pos_hist[:snap],
        thetas=th_hist[:snap],
        omegas=omegas,
        times=times[:snap],
        L=L,
        N=N,
    )


# -----------------------------------------------------------------------
# simulate_vicsek_chiral -- tutorial extension with chirality
# -----------------------------------------------------------------------

def simulate_vicsek_chiral(
    N=200,
    L=10.0,
    v0=0.5,
    R=1.0,
    eta=0.2,
    omega=0.0,
    dt=0.1,
    n_steps=500,
    seed=42,
    boundary_mode="periodic",
    save_every=10,
):
    """
    Vicsek model with optional uniform chirality term.

    Each particle aligns with neighbors within radius R (minimum-image),
    adds angular noise eta * Uniform[-pi, pi], then rotates by omega * dt.

    Returns a ParticleHistory object.
    """
    rng = np.random.default_rng(seed)
    pos = rng.uniform(0, L, (N, 2))
    theta = rng.uniform(-np.pi, np.pi, N)

    # for racemic-style vicsek, omega could be per-particle too
    omegas = np.full(N, omega)

    n_snapshots = n_steps // save_every + 1
    pos_hist = np.zeros((n_snapshots, N, 2))
    th_hist = np.zeros((n_snapshots, N))
    times = np.zeros(n_snapshots)
    snap = 0

    pos_hist[snap] = pos
    th_hist[snap] = theta
    times[snap] = 0.0
    snap += 1

    for step in range(1, n_steps + 1):
        dist2 = _minimum_image_dist2(pos, L)
        in_range = dist2 < R ** 2   # (N, N), includes self (dist=0)

        # vectorized average heading of neighbors
        cos_sum = (in_range * np.cos(theta)).sum(axis=1)
        sin_sum = (in_range * np.sin(theta)).sum(axis=1)
        avg_theta = np.arctan2(sin_sum, cos_sum)

        noise = eta * rng.uniform(-np.pi, np.pi, N)
        theta = avg_theta + noise + omegas * dt

        pos[:, 0] += v0 * np.cos(theta) * dt
        pos[:, 1] += v0 * np.sin(theta) * dt
        pos, theta = _apply_boundary(pos, theta, L, boundary_mode)

        if step % save_every == 0 and snap < n_snapshots:
            pos_hist[snap] = pos
            th_hist[snap] = theta
            times[snap] = step * dt
            snap += 1

    return ParticleHistory(
        positions=pos_hist[:snap],
        thetas=th_hist[:snap],
        omegas=omegas,
        times=times[:snap],
        L=L,
        N=N,
    )
