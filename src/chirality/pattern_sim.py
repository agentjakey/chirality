"""
Field-based pattern formation simulations.

Implements:
  - Laplacian with periodic BCs  (from tutorial track 2)
  - Diffusion-only stepping
  - Logistic growth
  - One-field reaction-diffusion
  - Gray-Scott model  (from tutorial track 2)
  - Feed gradient variant
  - Circular obstacle variant
  - Chiral source variant (toy model, not real biology)

All fields are 2D numpy arrays of shape (nx, ny).
"""
import numpy as np
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class FieldHistory:
    u_final: np.ndarray          # (nx, ny)
    v_final: np.ndarray          # (nx, ny)
    snapshots_u: Optional[List[np.ndarray]] = None  # list of (nx, ny)
    snapshots_v: Optional[List[np.ndarray]] = None
    times: Optional[np.ndarray] = None


# -----------------------------------------------------------------------
# Laplacian with periodic boundary conditions
# -----------------------------------------------------------------------

def laplacian(f):
    """
    2D discrete Laplacian with periodic boundaries using np.roll.
    dx = dy = 1 (lattice units).
    """
    return (
        np.roll(f, 1, axis=0) + np.roll(f, -1, axis=0) +
        np.roll(f, 1, axis=1) + np.roll(f, -1, axis=1) -
        4.0 * f
    )


# -----------------------------------------------------------------------
# Diffusion-only sanity check
# -----------------------------------------------------------------------

def run_diffusion(field, D=0.1, dt=0.5, n_steps=100):
    """
    Diffuse a scalar field without reaction.
    Stable when D * dt < 0.5 (dx=1).
    Returns the final field.
    """
    f = field.copy()
    for _ in range(n_steps):
        f = f + D * dt * laplacian(f)
    return f


# -----------------------------------------------------------------------
# Logistic growth (no diffusion)
# -----------------------------------------------------------------------

def run_logistic_growth(field, r=0.1, K=1.0, dt=0.5, n_steps=100):
    """
    Local logistic growth: df/dt = r * f * (1 - f/K).
    Returns the final field.
    """
    f = field.copy()
    for _ in range(n_steps):
        f = f + r * f * (1.0 - f / K) * dt
        f = np.clip(f, 0.0, K * 2)  # prevent blow-up
    return f


# -----------------------------------------------------------------------
# One-field reaction-diffusion (growth + diffusion)
# -----------------------------------------------------------------------

def run_reaction_diffusion_one_field(
    field, D=0.1, r=0.1, K=1.0, dt=0.5, n_steps=100
):
    """
    Single field with diffusion and logistic growth.
    df/dt = D * lap(f) + r * f * (1 - f/K)
    Returns the final field.
    """
    f = field.copy()
    for _ in range(n_steps):
        f = f + dt * (D * laplacian(f) + r * f * (1.0 - f / K))
        f = np.clip(f, 0.0, K * 2)
    return f


# -----------------------------------------------------------------------
# Gray-Scott initialization
# -----------------------------------------------------------------------

def initialize_gray_scott(nx, ny, seed=42, perturbation_size=5, n_seeds=None):
    """
    Gray-Scott initial conditions.

    If n_seeds is None (default): single central square seed.
    If n_seeds > 1: multiple randomly placed seeds, which lets patterns
    develop much faster across the full domain (better for short runs).

    Returns u, v each of shape (nx, ny).
    """
    rng = np.random.default_rng(seed)
    u = np.ones((nx, ny))
    v = np.zeros((nx, ny))

    # add tiny background noise to break symmetry
    u += 0.02 * rng.standard_normal((nx, ny))

    half = perturbation_size

    if n_seeds is None or n_seeds <= 1:
        # single central seed
        cx, cy = nx // 2, ny // 2
        u[cx - half:cx + half, cy - half:cy + half] = 0.5 + 0.1 * rng.standard_normal((2 * half, 2 * half))
        v[cx - half:cx + half, cy - half:cy + half] = 0.25 + 0.1 * rng.standard_normal((2 * half, 2 * half))
    else:
        for _ in range(n_seeds):
            cx = rng.integers(half + 1, nx - half - 1)
            cy = rng.integers(half + 1, ny - half - 1)
            u[cx - half:cx + half, cy - half:cy + half] = 0.5 + 0.1 * rng.standard_normal((2 * half, 2 * half))
            v[cx - half:cx + half, cy - half:cy + half] = 0.25 + 0.1 * rng.standard_normal((2 * half, 2 * half))

    u = np.clip(u, 0.0, 1.0)
    v = np.clip(v, 0.0, 1.0)
    return u, v


# -----------------------------------------------------------------------
# Gray-Scott step
# -----------------------------------------------------------------------

def gray_scott_step(u, v, Du, Dv, F, k, dt):
    """
    One time step of the Gray-Scott reaction-diffusion model.

    u_t = Du * lap(u) - u*v^2 + F*(1-u)
    v_t = Dv * lap(v) + u*v^2 - (F+k)*v

    F: feed rate
    k: kill rate (actually F + k is the removal rate of v)
    """
    uvv = u * v * v
    u_new = u + dt * (Du * laplacian(u) - uvv + F * (1.0 - u))
    v_new = v + dt * (Dv * laplacian(v) + uvv - (F + k) * v)
    # hard clip to [0, 1] for stability
    return np.clip(u_new, 0.0, 1.0), np.clip(v_new, 0.0, 1.0)


# -----------------------------------------------------------------------
# Full Gray-Scott simulation
# -----------------------------------------------------------------------

def simulate_gray_scott(
    nx=256,
    ny=256,
    Du=0.16,
    Dv=0.08,
    F=0.035,
    k=0.065,
    dt=1.0,
    n_steps=5000,
    seed=42,
    save_every=500,
    perturbation_size=5,
    n_seeds=None,
):
    """
    Run the full Gray-Scott simulation and return a FieldHistory.
    Standard parameters with dt=1.0 (lattice units).
    """
    u, v = initialize_gray_scott(nx, ny, seed, perturbation_size, n_seeds=n_seeds)

    snapshots_u = [u.copy()]
    snapshots_v = [v.copy()]
    snap_times = [0.0]

    for step in range(1, n_steps + 1):
        u, v = gray_scott_step(u, v, Du, Dv, F, k, dt)
        if step % save_every == 0:
            snapshots_u.append(u.copy())
            snapshots_v.append(v.copy())
            snap_times.append(step * dt)

    return FieldHistory(
        u_final=u,
        v_final=v,
        snapshots_u=snapshots_u,
        snapshots_v=snapshots_v,
        times=np.array(snap_times),
    )


# -----------------------------------------------------------------------
# Feed gradient variant
# -----------------------------------------------------------------------

def simulate_feed_gradient(
    nx=256,
    ny=256,
    Du=0.16,
    Dv=0.08,
    F_left=0.02,
    F_right=0.06,
    k=0.065,
    dt=1.0,
    n_steps=5000,
    seed=42,
    save_every=500,
    perturbation_size=5,
    n_seeds=8,
):
    """
    Gray-Scott with a linear feed gradient from F_left (x=0) to F_right (x=nx-1).
    This creates a phase gradient across the domain.
    """
    u, v = initialize_gray_scott(nx, ny, seed, perturbation_size, n_seeds=n_seeds)
    xs = np.linspace(0, 1, nx)
    F_field = F_left + (F_right - F_left) * xs
    F_2d = np.tile(F_field[:, np.newaxis], (1, ny))   # (nx, ny)

    snapshots_u = [u.copy()]
    snapshots_v = [v.copy()]
    snap_times = [0.0]

    for step in range(1, n_steps + 1):
        uvv = u * v * v
        u_new = u + dt * (Du * laplacian(u) - uvv + F_2d * (1.0 - u))
        v_new = v + dt * (Dv * laplacian(v) + uvv - (F_2d + k) * v)
        u = np.clip(u_new, 0.0, 1.0)
        v = np.clip(v_new, 0.0, 1.0)
        if step % save_every == 0:
            snapshots_u.append(u.copy())
            snapshots_v.append(v.copy())
            snap_times.append(step * dt)

    return FieldHistory(
        u_final=u,
        v_final=v,
        snapshots_u=snapshots_u,
        snapshots_v=snapshots_v,
        times=np.array(snap_times),
    )


# -----------------------------------------------------------------------
# Obstacle variant
# -----------------------------------------------------------------------

def simulate_obstacle(
    nx=256,
    ny=256,
    Du=0.16,
    Dv=0.08,
    F=0.035,
    k=0.065,
    dt=1.0,
    n_steps=5000,
    seed=42,
    obstacle_cx=0.5,
    obstacle_cy=0.5,
    obstacle_r=0.15,
    save_every=500,
    perturbation_size=4,
    n_seeds=12,
):
    """
    Gray-Scott with a circular obstacle that blocks reaction.
    Inside the obstacle: no u*v^2 reaction; u is held near 1, v near 0.
    obstacle_cx, obstacle_cy, obstacle_r are fractions of box size.
    """
    u, v = initialize_gray_scott(nx, ny, seed, perturbation_size, n_seeds=n_seeds)

    xs = np.arange(nx) / nx
    ys = np.arange(ny) / ny
    XX, YY = np.meshgrid(xs, ys, indexing="ij")
    dist_from_center = np.sqrt((XX - obstacle_cx) ** 2 + (YY - obstacle_cy) ** 2)
    inside = dist_from_center < obstacle_r

    snapshots_u = [u.copy()]
    snapshots_v = [v.copy()]
    snap_times = [0.0]

    for step in range(1, n_steps + 1):
        u, v = gray_scott_step(u, v, Du, Dv, F, k, dt)
        # reset obstacle interior
        u[inside] = 1.0
        v[inside] = 0.0
        if step % save_every == 0:
            snapshots_u.append(u.copy())
            snapshots_v.append(v.copy())
            snap_times.append(step * dt)

    return FieldHistory(
        u_final=u,
        v_final=v,
        snapshots_u=snapshots_u,
        snapshots_v=snapshots_v,
        times=np.array(snap_times),
    )


# -----------------------------------------------------------------------
# Chiral source variant (toy model)
# -----------------------------------------------------------------------

def simulate_chiral_source_gray_scott(
    nx=256,
    ny=256,
    Du=0.16,
    Dv=0.08,
    F=0.035,
    k=0.065,
    dt=1.0,
    n_steps=5000,
    seed=42,
    source_strength=0.02,
    source_omega=0.05,
    source_r_orbit=0.2,
    source_sigma=0.05,
    save_every=500,
    perturbation_size=4,
    n_seeds=8,
):
    """
    Gray-Scott with a rotating point source that injects v-species.

    A focal point orbits the box center at angular speed source_omega,
    injecting a Gaussian blob of v at each time step. This breaks left-right
    symmetry in the resulting pattern.

    NOTE: This is a toy model constructed to illustrate symmetry breaking.
    It is not derived from a specific biological mechanism.
    """
    u, v = initialize_gray_scott(nx, ny, seed, perturbation_size, n_seeds=n_seeds)

    xs = np.arange(nx) / nx
    ys = np.arange(ny) / ny
    XX, YY = np.meshgrid(xs, ys, indexing="ij")

    cx, cy = 0.5, 0.5

    snapshots_u = [u.copy()]
    snapshots_v = [v.copy()]
    snap_times = [0.0]

    for step in range(1, n_steps + 1):
        u, v = gray_scott_step(u, v, Du, Dv, F, k, dt)

        # rotating source
        angle = source_omega * step * dt
        sx = cx + source_r_orbit * np.cos(angle)
        sy = cy + source_r_orbit * np.sin(angle)
        dist2 = (XX - sx) ** 2 + (YY - sy) ** 2
        source_blob = source_strength * np.exp(-dist2 / (2 * source_sigma ** 2))
        v = np.clip(v + source_blob * dt, 0.0, 1.0)
        u = np.clip(u - source_blob * dt, 0.0, 1.0)

        if step % save_every == 0:
            snapshots_u.append(u.copy())
            snapshots_v.append(v.copy())
            snap_times.append(step * dt)

    return FieldHistory(
        u_final=u,
        v_final=v,
        snapshots_u=snapshots_u,
        snapshots_v=snapshots_v,
        times=np.array(snap_times),
    )
