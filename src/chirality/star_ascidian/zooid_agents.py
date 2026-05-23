"""
Layer 2: Active zooid-like agent dynamics.

Each agent represents one zooid. Agents are initialized in discrete arm groups
around each center and settle into radial star-like lobes under the combined
effect of center attraction, radial targeting, angular repulsion, and optional chirality.

Key physics:
  - Radial spring: soft confinement at r_target from assigned center
  - Center attraction: prevents agents from drifting to wrong center
  - Angular repulsion: pushes agents from different arms apart, maintaining equal spacing
  - Self-propulsion + orientation noise: thermal fluctuations
  - Chirality (omega): rotation rate twists arm geometry over time
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class ZooidResult:
    positions: np.ndarray        # (n_snapshots, N, 2)
    thetas: np.ndarray           # (n_snapshots, N)
    omegas: np.ndarray           # (N,)
    assignments: np.ndarray      # (N,) center index
    arm_assignments: np.ndarray  # (N,) arm index (unique per arm, across all centers)
    centers: np.ndarray          # (K, 2)
    times: np.ndarray            # (n_snapshots,)
    L: float
    N: int
    K: int
    n_arms: int
    r_target: float
    params: Dict[str, Any]


def simulate_zooid_agents(
    centers,
    n_per_center=21,
    n_arms=7,
    L=10.0,
    r_target=1.5,
    v0=0.05,
    Dr=0.05,
    omega=0.0,
    k_attract=0.3,
    k_radial=2.0,
    k_angular=0.6,
    k_ev=0.4,
    sigma_ev=0.18,
    dt=0.02,
    n_steps=400,
    n_snapshots=10,
    mode="radial_clean",
    boundary="periodic",
    seed=42,
):
    """Simulate active zooid agents around star centers.

    Args:
        centers:       (K, 2) array of star center positions in physical coordinates
        n_per_center:  total agents per center (should be n_arms * n_per_arm)
        n_arms:        target number of arms per center (used for initialization and angular repulsion)
        L:             domain size (square [0, L] x [0, L])
        r_target:      target radius of the arm ring from center
        v0:            self-propulsion speed
        Dr:            rotational diffusion coefficient
        omega:         chiral rotation rate (0 = no chirality)
        k_attract:     center attraction strength (prevents cross-center drift)
        k_radial:      radial spring constant (toward r_target)
        k_angular:     angular repulsion strength between different arms
        k_ev:          excluded volume repulsion strength
        sigma_ev:      excluded volume cutoff distance
        dt:            time step
        n_steps:       number of simulation steps
        n_snapshots:   number of snapshots to record
        mode:          one of: radial_clean, chiral_twist, racemic_mixed,
                               noisy_fragmented, overcrowded, boundary_pinned
        boundary:      "periodic" or "box"
        seed:          random seed

    Returns:
        ZooidResult dataclass
    """
    rng = np.random.default_rng(seed)
    K = len(centers)
    n_per_arm = max(1, n_per_center // n_arms)
    n_per_center_actual = n_arms * n_per_arm
    N = K * n_per_center_actual

    # Apply mode overrides
    omega, Dr, v0 = _apply_mode(mode, omega, Dr, v0)

    # Initialize positions, orientations, assignments
    pos, theta, assignments, arm_assignments = _initialize_agents(
        centers, K, n_arms, n_per_arm, r_target, L, rng
    )

    # Per-particle chirality
    if mode == "racemic_mixed":
        omegas = np.where(
            np.arange(N) % 2 == 0, abs(omega), -abs(omega)
        ).astype(float)
    else:
        omegas = np.full(N, omega, dtype=float)

    # Precompute angular repulsion cutoff
    sigma_angular = 1.5 * 2.0 * np.pi / n_arms

    snap_every = max(1, n_steps // n_snapshots)
    positions_hist = []
    thetas_hist = []
    times = []

    noise_scale = np.sqrt(2.0 * Dr * dt)

    for step in range(n_steps):
        # Update orientations
        theta += omegas * dt + noise_scale * rng.standard_normal(N)

        # Compute forces
        forces = _compute_forces(
            pos, theta, centers, assignments, arm_assignments,
            k_attract, k_radial, r_target,
            k_angular, sigma_angular,
            k_ev, sigma_ev, v0, L
        )

        # Update positions
        pos = pos + dt * forces

        # Apply boundary conditions
        if boundary == "periodic":
            pos = pos % L
        elif boundary == "box":
            pos = np.clip(pos, 0.0, L)
            # Reflect velocity for next step (approximate by clamping)

        if step % snap_every == 0:
            positions_hist.append(pos.copy())
            thetas_hist.append(theta.copy())
            times.append(step * dt)

    return ZooidResult(
        positions=np.array(positions_hist),
        thetas=np.array(thetas_hist),
        omegas=omegas,
        assignments=assignments,
        arm_assignments=arm_assignments,
        centers=centers,
        times=np.array(times),
        L=L,
        N=N,
        K=K,
        n_arms=n_arms,
        r_target=r_target,
        params=dict(
            n_per_center=n_per_center_actual, n_arms=n_arms, n_per_arm=n_per_arm,
            r_target=r_target, v0=v0, Dr=Dr, omega=omega,
            k_attract=k_attract, k_radial=k_radial, k_angular=k_angular,
            k_ev=k_ev, sigma_ev=sigma_ev, dt=dt, n_steps=n_steps, mode=mode,
        ),
    )


def _apply_mode(mode, omega, Dr, v0):
    """Return (omega, Dr, v0) adjusted for the requested mode."""
    if mode == "radial_clean":
        return 0.0, max(Dr, 0.03), v0
    elif mode == "chiral_twist":
        return abs(omega) if omega != 0 else 2.0, Dr, v0
    elif mode == "racemic_mixed":
        return abs(omega) if omega != 0 else 2.0, Dr, v0
    elif mode == "noisy_fragmented":
        return omega, max(Dr, 0.8), max(v0, 0.3)
    elif mode == "overcrowded":
        return omega, Dr, v0
    elif mode == "boundary_pinned":
        return omega, Dr, v0
    else:
        return omega, Dr, v0


def _initialize_agents(centers, K, n_arms, n_per_arm, r_target, L, rng):
    """Place agents in discrete arm groups around each center.

    Returns: positions (N,2), thetas (N,), assignments (N,), arm_assignments (N,)
    """
    N = K * n_arms * n_per_arm
    pos = np.zeros((N, 2))
    theta = np.zeros(N)
    assignments = np.zeros(N, dtype=int)
    arm_assignments = np.zeros(N, dtype=int)

    arm_angles = np.linspace(0, 2.0 * np.pi, n_arms, endpoint=False)

    # Radii for particles within each arm: evenly spread around r_target
    if n_per_arm == 1:
        arm_radii = np.array([r_target])
    else:
        dr = r_target * 0.35
        arm_radii = np.linspace(r_target - dr, r_target + dr, n_per_arm)

    idx = 0
    for k, center in enumerate(centers):
        for arm_i, base_angle in enumerate(arm_angles):
            global_arm_id = k * n_arms + arm_i
            for j, r in enumerate(arm_radii):
                # Small noise in angle and radius for visual variation
                angle = base_angle + rng.normal(0, 0.04)
                radius = r + rng.normal(0, 0.04 * r_target)
                radius = max(0.1 * r_target, radius)

                x = center[0] + radius * np.cos(angle)
                y = center[1] + radius * np.sin(angle)

                pos[idx, 0] = x
                pos[idx, 1] = y
                theta[idx] = rng.uniform(-np.pi, np.pi)
                assignments[idx] = k
                arm_assignments[idx] = global_arm_id
                idx += 1

    return pos, theta, assignments, arm_assignments


def _compute_forces(
    pos, theta, centers, assignments, arm_assignments,
    k_attract, k_radial, r_target,
    k_angular, sigma_angular,
    k_ev, sigma_ev, v0, L
):
    """Compute total force on each agent.

    Forces:
      1. Self-propulsion
      2. Center attraction (soft)
      3. Radial spring (toward r_target)
      4. Angular repulsion (between different-arm agents at same center)
      5. Excluded volume (all pairs within cutoff)
    """
    N = len(pos)
    forces = np.zeros((N, 2))

    # 1. Self-propulsion
    forces[:, 0] += v0 * np.cos(theta)
    forces[:, 1] += v0 * np.sin(theta)

    # 2 & 3. Center attraction + radial spring (vectorized per center)
    for k, center in enumerate(centers):
        mask = assignments == k
        if not mask.any():
            continue
        p = pos[mask]
        r_vecs = p - center          # (n_k, 2), pointing away from center
        r = np.linalg.norm(r_vecs, axis=1, keepdims=True) + 1e-9
        r_hats = r_vecs / r          # unit vectors away from center

        # Attraction toward center
        forces[mask] -= k_attract * r_vecs

        # Radial spring toward r_target
        forces[mask] += k_radial * (r_target - r) * r_hats

    # 4. Angular repulsion (per center, between different arms)
    K = len(centers)
    for k, center in enumerate(centers):
        mask = assignments == k
        idx_k = np.where(mask)[0]
        if len(idx_k) < 2:
            continue

        p = pos[idx_k]                  # (n_k, 2)
        r_vecs = p - center             # (n_k, 2)
        r_norms = np.linalg.norm(r_vecs, axis=1) + 1e-9   # (n_k,)
        r_hats = r_vecs / r_norms[:, None]
        t_hats = np.column_stack([-r_hats[:, 1], r_hats[:, 0]])  # CCW tangential

        phis = np.arctan2(r_vecs[:, 1], r_vecs[:, 0])  # (n_k,)
        arms_k = arm_assignments[idx_k]                 # (n_k,)

        # Pairwise angular differences
        dphi = phis[:, None] - phis[None, :]           # (n_k, n_k)
        dphi = (dphi + np.pi) % (2.0 * np.pi) - np.pi # wrap to [-pi, pi]

        # Only repel different-arm pairs
        diff_arm = arms_k[:, None] != arms_k[None, :]  # (n_k, n_k)
        abs_dphi = np.abs(dphi)

        # Soft linear cutoff in angular space
        active = diff_arm & (abs_dphi < sigma_angular) & (abs_dphi > 1e-9)
        strength = np.where(
            active,
            k_angular * (1.0 - abs_dphi / sigma_angular),
            0.0
        )

        # Force direction: push i away from j in tangential direction
        # sign(dphi[i,j]) > 0 means j is CCW from i, push i CW (-tangent)
        sign_dphi = np.sign(dphi)
        ang_force_mag = np.sum(strength * (-sign_dphi), axis=1)  # (n_k,)
        ang_forces = ang_force_mag[:, None] * t_hats              # (n_k, 2)
        forces[idx_k] += ang_forces

    # 5. Excluded volume (all pairs within sigma_ev)
    if k_ev > 0 and sigma_ev > 0:
        diff = pos[:, None, :] - pos[None, :, :]         # (N, N, 2)
        dist2 = np.sum(diff ** 2, axis=2) + 1e-12        # (N, N)
        dist = np.sqrt(dist2)
        active_ev = (dist < sigma_ev) & ~np.eye(N, dtype=bool)
        strength_ev = np.where(active_ev, k_ev * (1.0 - dist / sigma_ev), 0.0)
        ev_force = (strength_ev[:, :, None] * diff / dist[:, :, None]).sum(axis=1)
        forces += ev_force

    return forces
