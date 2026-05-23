"""
Fisher-KPP reaction-diffusion model.

PDE: u_t = D * lap(u) + r * u * (1 - u)

Models invasion fronts: a stable state u=1 invades u=0 territory.
Periodic boundary conditions.

Numerical method: IMEX -- implicit diffusion in Fourier space, explicit reaction.
Unconditionally stable for the diffusion part; reaction stability requires
dt * r < 1 (for logistic growth near u=0). dt=0.1 is safe for r=1.
"""

import numpy as np
from . import FieldResult, check_finite


def _make_k2(N, L):
    dx = L / N
    kx = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    ky = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    KX, KY = np.meshgrid(kx, ky, indexing="ij")
    return KX ** 2 + KY ** 2


def simulate_fisher_kpp(
    N=64,
    L=10.0,
    D=0.5,
    r=1.0,
    dt=0.1,
    n_steps=400,
    n_snapshots=10,
    seed=42,
    init="circle",
):
    rng = np.random.default_rng(seed)
    k2 = _make_k2(N, L)
    denom = 1.0 + dt * D * k2

    x = np.linspace(0, L, N, endpoint=False)
    X, Y = np.meshgrid(x, x)

    if init == "circle":
        cx, cy = L / 2.0, L / 2.0
        r_init = L / 8.0
        u = np.where((X - cx) ** 2 + (Y - cy) ** 2 < r_init ** 2, 1.0, 0.01)
    elif init == "random":
        u = rng.uniform(0.0, 0.1, (N, N))
        u[N // 4 : 3 * N // 4, N // 4 : 3 * N // 4] = 1.0
    else:
        raise ValueError(f"Unknown init: {init}")

    snap_every = max(1, n_steps // n_snapshots)
    snapshots_u = []
    times = []

    for step in range(n_steps):
        reaction = r * u * (1.0 - u)
        u_hat = np.fft.fft2(u + dt * reaction)
        u = np.real(np.fft.ifft2(u_hat / denom))
        u = np.clip(u, 0.0, 1.0)

        if step % snap_every == 0:
            snapshots_u.append(u.copy())
            times.append(step * dt)

    check_finite(u, "fisher_kpp u_final")

    return FieldResult(
        u_final=u,
        v_final=None,
        snapshots_u=np.array(snapshots_u),
        snapshots_v=None,
        times=np.array(times),
        params=dict(N=N, L=L, D=D, r=r, dt=dt, n_steps=n_steps, init=init),
        shape=(N, N),
    )


def front_radius(result):
    """Estimate invasion front radius from the final u field.

    Finds the radial distance from the domain center at which u crosses 0.5.
    """
    u = result.u_final
    N = u.shape[0]
    cx, cy = N // 2, N // 2
    rows, cols = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
    dist = np.sqrt((rows - cx) ** 2 + (cols - cy) ** 2)
    L = result.params["L"]
    dx = L / N

    threshold = 0.5
    inside = u > threshold
    if not inside.any():
        return 0.0
    radii = dist[inside] * dx
    return float(np.max(radii))
