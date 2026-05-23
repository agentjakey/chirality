"""
Active particle simulations: ABP, chiral ABP, and Vicsek model.

Tutorial-aligned implementations matching UCSD Active Matter tutorial equations.
All simulations use periodic boundary conditions (wrapping in [0, L]).
"""

import numpy as np
from . import ParticleResult, check_finite


def simulate_abp(
    N=200,
    L=10.0,
    v0=0.5,
    Dr=0.5,
    dt=0.01,
    n_steps=500,
    n_snapshots=10,
    seed=42,
):
    """Active Brownian Particle (ABP) simulation.

    Each particle self-propels at speed v0 in direction theta_i.
    Orientation diffuses with rotational diffusion Dr.

    theta_i += sqrt(2*Dr*dt) * xi_i
    x_i += v0 * cos(theta_i) * dt
    y_i += v0 * sin(theta_i) * dt
    """
    rng = np.random.default_rng(seed)

    pos = rng.uniform(0, L, (N, 2))
    theta = rng.uniform(-np.pi, np.pi, N)
    omegas = np.zeros(N)

    snap_every = max(1, n_steps // n_snapshots)
    positions = []
    thetas = []
    times = []

    noise_scale = np.sqrt(2.0 * Dr * dt)

    for step in range(n_steps):
        theta += noise_scale * rng.standard_normal(N)
        pos[:, 0] += v0 * np.cos(theta) * dt
        pos[:, 1] += v0 * np.sin(theta) * dt
        pos = pos % L

        if step % snap_every == 0:
            positions.append(pos.copy())
            thetas.append(theta.copy())
            times.append(step * dt)

    check_finite(pos, "abp pos_final")

    return ParticleResult(
        positions=np.array(positions),
        thetas=np.array(thetas),
        omegas=omegas,
        times=np.array(times),
        L=L,
        N=N,
        params=dict(N=N, L=L, v0=v0, Dr=Dr, dt=dt, n_steps=n_steps),
    )


def simulate_chiral_abp(
    N=200,
    L=10.0,
    v0=0.5,
    Dr=0.5,
    omega=2.0,
    mode="uniform",
    dt=0.01,
    n_steps=500,
    n_snapshots=10,
    seed=42,
):
    """Chiral ABP simulation.

    Adds a rotation rate omega_i to each particle's orientation update:
    theta_i += omega_i * dt + sqrt(2*Dr*dt) * xi_i

    mode options:
      "uniform"  -- all particles have omega_i = omega
      "left"     -- all omega_i = -|omega|
      "right"    -- all omega_i = +|omega|
      "racemic"  -- half +omega, half -omega
      "random"   -- omega_i ~ Uniform(-omega, omega)
    """
    rng = np.random.default_rng(seed)

    pos = rng.uniform(0, L, (N, 2))
    theta = rng.uniform(-np.pi, np.pi, N)

    if mode == "uniform":
        omegas = np.full(N, omega)
    elif mode == "left":
        omegas = np.full(N, -abs(omega))
    elif mode == "right":
        omegas = np.full(N, abs(omega))
    elif mode == "racemic":
        omegas = np.where(np.arange(N) < N // 2, abs(omega), -abs(omega))
        rng.shuffle(omegas)
    elif mode == "random":
        omegas = rng.uniform(-abs(omega), abs(omega), N)
    else:
        raise ValueError(f"Unknown mode: {mode}")

    snap_every = max(1, n_steps // n_snapshots)
    positions = []
    thetas = []
    times = []

    noise_scale = np.sqrt(2.0 * Dr * dt)

    for step in range(n_steps):
        theta += omegas * dt + noise_scale * rng.standard_normal(N)
        pos[:, 0] += v0 * np.cos(theta) * dt
        pos[:, 1] += v0 * np.sin(theta) * dt
        pos = pos % L

        if step % snap_every == 0:
            positions.append(pos.copy())
            thetas.append(theta.copy())
            times.append(step * dt)

    check_finite(pos, "chiral_abp pos_final")

    return ParticleResult(
        positions=np.array(positions),
        thetas=np.array(thetas),
        omegas=omegas,
        times=np.array(times),
        L=L,
        N=N,
        params=dict(N=N, L=L, v0=v0, Dr=Dr, omega=omega, mode=mode, dt=dt, n_steps=n_steps),
    )


def simulate_vicsek(
    N=200,
    L=10.0,
    v0=0.5,
    eta=0.3,
    R=1.0,
    omega=0.0,
    dt=0.1,
    n_steps=500,
    n_snapshots=10,
    seed=42,
):
    """Vicsek model with optional chirality.

    Particles align with neighbors within radius R, with noise eta.
    omega adds a chiral rotation rate (omega=0 for standard Vicsek).

    theta_i = mean(theta_neighbors) + eta * Uniform(-pi, pi) + omega * dt
    """
    rng = np.random.default_rng(seed)

    pos = rng.uniform(0, L, (N, 2))
    theta = rng.uniform(-np.pi, np.pi, N)
    omegas = np.full(N, omega)

    snap_every = max(1, n_steps // n_snapshots)
    positions = []
    thetas = []
    times = []

    for step in range(n_steps):
        dx = pos[:, 0:1] - pos[:, 0]
        dy = pos[:, 1:2] - pos[:, 1]
        dx = dx - L * np.round(dx / L)
        dy = dy - L * np.round(dy / L)
        dist2 = dx ** 2 + dy ** 2
        neighbors = dist2 < R ** 2

        sin_avg = (neighbors * np.sin(theta)).sum(axis=1) / neighbors.sum(axis=1)
        cos_avg = (neighbors * np.cos(theta)).sum(axis=1) / neighbors.sum(axis=1)
        theta_avg = np.arctan2(sin_avg, cos_avg)
        theta = theta_avg + eta * rng.uniform(-np.pi, np.pi, N) + omega * dt

        pos[:, 0] += v0 * np.cos(theta) * dt
        pos[:, 1] += v0 * np.sin(theta) * dt
        pos = pos % L

        if step % snap_every == 0:
            positions.append(pos.copy())
            thetas.append(theta.copy())
            times.append(step * dt)

    check_finite(pos, "vicsek pos_final")

    return ParticleResult(
        positions=np.array(positions),
        thetas=np.array(thetas),
        omegas=omegas,
        times=np.array(times),
        L=L,
        N=N,
        params=dict(N=N, L=L, v0=v0, eta=eta, R=R, omega=omega, dt=dt, n_steps=n_steps),
    )


def polar_order(result):
    """Instantaneous polar order parameter at the final snapshot.

    phi = |mean(exp(i*theta))| in [0, 1].
    0 = disordered, 1 = fully aligned.
    """
    theta = result.thetas[-1]
    return float(np.abs(np.mean(np.exp(1j * theta))))


def swirl_index(result):
    """Mean signed angular velocity of particles around the domain center.

    Positive = net CCW rotation, negative = CW.
    Magnitude reflects strength of chiral circulation.
    """
    if len(result.times) < 2:
        return 0.0

    cx = result.L / 2.0
    cy = result.L / 2.0

    pos = result.positions[-1]
    theta = result.thetas[-1]
    N = result.N

    rx = pos[:, 0] - cx
    ry = pos[:, 1] - cy
    r = np.sqrt(rx ** 2 + ry ** 2) + 1e-8

    vx = result.params.get("v0", 0.5) * np.cos(theta)
    vy = result.params.get("v0", 0.5) * np.sin(theta)

    angular_v = (rx * vy - ry * vx) / r
    return float(np.mean(angular_v))


def msd(result):
    """Mean squared displacement between first and last snapshot.

    Returns mean over all particles of |r(t_final) - r(t_0)|^2.
    Does not account for periodic boundary crossings; use for short runs.
    """
    if len(result.times) < 2:
        return 0.0
    pos0 = result.positions[0]
    posf = result.positions[-1]
    L = result.L
    disp = posf - pos0
    disp = disp - L * np.round(disp / L)
    return float(np.mean(np.sum(disp ** 2, axis=1)))


def avg_neighbors(result, R=None):
    """Mean number of neighbors within radius R at the final snapshot.

    Defaults to R = L/10.
    """
    L = result.L
    if R is None:
        R = L / 10.0
    pos = result.positions[-1]
    N = pos.shape[0]

    dx = pos[:, 0:1] - pos[:, 0]
    dy = pos[:, 1:2] - pos[:, 1]
    dx = dx - L * np.round(dx / L)
    dy = dy - L * np.round(dy / L)
    dist2 = dx ** 2 + dy ** 2
    count = (dist2 < R ** 2).sum(axis=1) - 1
    return float(count.mean())
