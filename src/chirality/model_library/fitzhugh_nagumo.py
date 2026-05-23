"""
FitzHugh-Nagumo excitable medium model.

PDEs:
  u_t = Du * lap(u) + u - u^3/3 - v + I_ext
  v_t = epsilon * (u + a - b*v)

where u is the activator (fast) and v is the inhibitor (slow).
Produces traveling waves and spiral patterns.

Numerical method: IMEX for u (implicit diffusion, explicit reaction),
semi-implicit for v (implicit linear decay b*v).
"""

import numpy as np
from . import FieldResult, check_finite


def _make_k2(N, L):
    dx = L / N
    kx = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    ky = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    KX, KY = np.meshgrid(kx, ky, indexing="ij")
    return KX ** 2 + KY ** 2


def _resting_state(a, b):
    """Compute resting (homogeneous) steady state for FHN.

    Solves u - u^3/3 - v = 0 and u + a - b*v = 0 numerically.
    For typical parameters (a=0.7, b=0.8): u ~ -1.2, v ~ -0.625.
    """
    from scipy.optimize import brentq

    def f(u_val):
        v_val = (u_val + a) / b
        return u_val - u_val ** 3 / 3.0 - v_val

    u_rest = brentq(f, -2.5, 0.5)
    v_rest = (u_rest + a) / b
    return u_rest, v_rest


def simulate_fitzhugh_nagumo(
    N=64,
    L=10.0,
    Du=1.0,
    epsilon=0.08,
    a=0.7,
    b=0.8,
    I_ext=0.0,
    dt=0.1,
    n_steps=2000,
    n_snapshots=10,
    seed=42,
    init="spiral",
):
    rng = np.random.default_rng(seed)
    k2 = _make_k2(N, L)

    # IMEX denominator for u: implicit diffusion
    denom_u = 1.0 + dt * Du * k2
    # Semi-implicit denominator for v: implicit linear decay b*v
    denom_v = 1.0 + dt * epsilon * b

    u_rest, v_rest = _resting_state(a, b)

    u = np.full((N, N), u_rest)
    v = np.full((N, N), v_rest)

    if init == "stimulate":
        stim_size = max(2, N // 8)
        u[:stim_size, :stim_size] = 2.0
        v[:stim_size, :stim_size] = v_rest + 0.5
    elif init == "noise":
        u = u + rng.normal(0, 0.1, (N, N))
        v = v + rng.normal(0, 0.05, (N, N))
    elif init == "spiral":
        x = np.linspace(0, L, N, endpoint=False)
        X, Y = np.meshgrid(x, x)
        cx, cy = L / 2.0, L / 2.0
        angle = np.arctan2(Y - cy, X - cx)
        u = u_rest + 1.5 * np.cos(angle)
        v = v_rest + 0.5 * np.sin(angle)
    else:
        raise ValueError(f"Unknown init: {init}")

    snap_every = max(1, n_steps // n_snapshots)
    snapshots_u = []
    snapshots_v = []
    times = []

    for step in range(n_steps):
        # IMEX step for u: implicit diffusion, explicit nonlinear reaction
        reaction_u = u - u ** 3 / 3.0 - v + I_ext
        u_hat = np.fft.fft2(u + dt * reaction_u)
        u = np.real(np.fft.ifft2(u_hat / denom_u))

        # Semi-implicit step for v
        v = (v + dt * epsilon * (u + a)) / denom_v

        if step % snap_every == 0:
            snapshots_u.append(u.copy())
            snapshots_v.append(v.copy())
            times.append(step * dt)

    check_finite(u, "fhn u_final")
    check_finite(v, "fhn v_final")

    return FieldResult(
        u_final=u,
        v_final=v,
        snapshots_u=np.array(snapshots_u),
        snapshots_v=np.array(snapshots_v),
        times=np.array(times),
        params=dict(N=N, L=L, Du=Du, epsilon=epsilon, a=a, b=b, I_ext=I_ext, dt=dt, n_steps=n_steps),
        shape=(N, N),
    )


def wave_activity(result):
    """Fraction of domain where u > 0 (excited state).

    Values near 0: medium mostly at rest.
    Values near 1: sustained excitation.
    """
    return float(np.mean(result.u_final > 0.0))
