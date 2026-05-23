"""
Gray-Scott reaction-diffusion model.

PDEs:
  u_t = Du * lap(u) - u*v^2 + F*(1-u)
  v_t = Dv * lap(v) + u*v^2 - (F+k)*v

Notable parameter regimes:
  Spots:     F=0.035, k=0.065  (Du=0.16, Dv=0.08)
  Labyrinths: F=0.040, k=0.060
  Pulsing:   F=0.025, k=0.055
"""

import numpy as np
from scipy.ndimage import label
from . import FieldResult, laplacian_2d_periodic, check_finite


def initialize_gray_scott(N, seed=42, n_seeds=1):
    """Initialize GS with u=1, v=0 everywhere, plus small v-seeds in the center.

    n_seeds: number of seed squares to place (default 1 in center).
    """
    rng = np.random.default_rng(seed)
    u = np.ones((N, N))
    v = np.zeros((N, N))

    r = max(3, N // 16)
    if n_seeds == 1:
        cx, cy = N // 2, N // 2
        u[cx - r : cx + r, cy - r : cy + r] = 0.5
        v[cx - r : cx + r, cy - r : cy + r] = 0.25
        u[cx - r : cx + r, cy - r : cy + r] += 0.01 * rng.standard_normal((2 * r, 2 * r))
        v[cx - r : cx + r, cy - r : cy + r] += 0.01 * rng.standard_normal((2 * r, 2 * r))
    else:
        for _ in range(n_seeds):
            cx = rng.integers(r + 1, N - r - 1)
            cy = rng.integers(r + 1, N - r - 1)
            u[cx - r : cx + r, cy - r : cy + r] = 0.5
            v[cx - r : cx + r, cy - r : cy + r] = 0.25
            u[cx - r : cx + r, cy - r : cy + r] += 0.01 * rng.standard_normal((2 * r, 2 * r))
            v[cx - r : cx + r, cy - r : cy + r] += 0.01 * rng.standard_normal((2 * r, 2 * r))

    u = np.clip(u, 0.0, 1.0)
    v = np.clip(v, 0.0, 1.0)
    return u, v


def simulate_gray_scott(
    N=64,
    L=10.0,
    Du=0.16,
    Dv=0.08,
    F=0.035,
    k=0.065,
    dt=1.0,
    n_steps=3000,
    n_snapshots=10,
    seed=42,
    n_seeds=1,
):
    dx = L / N
    u, v = initialize_gray_scott(N, seed=seed, n_seeds=n_seeds)

    snap_every = max(1, n_steps // n_snapshots)
    snapshots_u = []
    snapshots_v = []
    times = []

    for step in range(n_steps):
        lap_u = laplacian_2d_periodic(u, dx)
        lap_v = laplacian_2d_periodic(v, dx)
        uvv = u * v * v
        du = Du * lap_u - uvv + F * (1.0 - u)
        dv = Dv * lap_v + uvv - (F + k) * v
        u = u + dt * du
        v = v + dt * dv
        u = np.clip(u, 0.0, 1.0)
        v = np.clip(v, 0.0, 1.0)

        if step % snap_every == 0:
            snapshots_u.append(u.copy())
            snapshots_v.append(v.copy())
            times.append(step * dt)

    check_finite(u, "gray_scott u_final")
    check_finite(v, "gray_scott v_final")

    return FieldResult(
        u_final=u,
        v_final=v,
        snapshots_u=np.array(snapshots_u),
        snapshots_v=np.array(snapshots_v),
        times=np.array(times),
        params=dict(N=N, L=L, Du=Du, Dv=Dv, F=F, k=k, dt=dt, n_steps=n_steps),
        shape=(N, N),
    )


def pattern_strength(result):
    """Coefficient of variation of the v field.

    Higher = stronger patterning. Near-zero = uniform or featureless.
    """
    v = result.v_final
    mean = v.mean()
    if mean < 1e-12:
        return 0.0
    return float(v.std() / mean)


def cluster_count(result, threshold=0.1):
    """Number of connected v-regions above threshold."""
    v = result.v_final
    binary = v > threshold
    _, n = label(binary)
    return int(n)
