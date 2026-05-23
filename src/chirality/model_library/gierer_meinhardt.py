"""
Gierer-Meinhardt activator-inhibitor model.

PDEs:
  da/dt = Da * lap(a) + rho * a^2 / (h * (1 + kappa*a^2)) - mu_a * a + rho_0
  dh/dt = Dh * lap(h) + rho * a^2 - mu_h * h

Turing instability condition: Dh >> Da (use ratio >= 50).
Steady state: a_ss ~ mu_h/(mu_a*(1+kappa*a_ss^2)) + rho_0/mu_a (solved numerically)

Numerical method: IMEX -- implicit diffusion and linear decay in Fourier space,
explicit nonlinear reaction. This makes the diffusion unconditionally stable.
The explicit reaction step requires dt small enough; dt=0.5 works for reference params.
"""

import numpy as np
from scipy.ndimage import label
from . import FieldResult, check_finite


def _make_k2(N, L):
    dx = L / N
    kx = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    ky = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    KX, KY = np.meshgrid(kx, ky, indexing="ij")
    return KX ** 2 + KY ** 2


def _steady_state(mu_a, mu_h, rho, rho_0, kappa):
    """Compute homogeneous steady state numerically via bisection."""
    from scipy.optimize import brentq

    def f(a):
        return mu_h / (1.0 + kappa * a ** 2) + rho_0 - mu_a * a

    try:
        a_ss = brentq(f, 1e-6, 100.0)
    except ValueError:
        a_ss = (mu_h + rho_0) / mu_a
    h_ss = rho * a_ss ** 2 / mu_h
    return a_ss, h_ss


def simulate_gierer_meinhardt(
    N=64,
    L=10.0,
    Da=0.05,
    Dh=5.0,
    mu_a=0.05,
    mu_h=0.05,
    rho=0.1,
    rho_0=0.001,
    kappa=0.1,
    dt=0.5,
    n_steps=3000,
    n_snapshots=10,
    seed=42,
):
    rng = np.random.default_rng(seed)
    k2 = _make_k2(N, L)

    # IMEX denominators: implicit diffusion + implicit linear decay
    denom_a = 1.0 + dt * (Da * k2 + mu_a)
    denom_h = 1.0 + dt * (Dh * k2 + mu_h)

    a_ss, h_ss = _steady_state(mu_a, mu_h, rho, rho_0, kappa)

    a = a_ss * (1.0 + 0.05 * rng.standard_normal((N, N)))
    h = h_ss * (1.0 + 0.05 * rng.standard_normal((N, N)))
    a = np.clip(a, 1e-6, None)
    h = np.clip(h, 1e-6, None)

    snap_every = max(1, n_steps // n_snapshots)
    snapshots_u = []
    snapshots_v = []
    times = []

    for step in range(n_steps):
        # Explicit nonlinear reaction
        production = rho * a ** 2 / (h * (1.0 + kappa * a ** 2))
        ra = production + rho_0
        rh = rho * a ** 2

        # IMEX step in Fourier space
        a_hat = np.fft.fft2(a + dt * ra)
        h_hat = np.fft.fft2(h + dt * rh)

        a = np.real(np.fft.ifft2(a_hat / denom_a))
        h = np.real(np.fft.ifft2(h_hat / denom_h))
        a = np.clip(a, 1e-9, None)
        h = np.clip(h, 1e-9, None)

        if step % snap_every == 0:
            snapshots_u.append(a.copy())
            snapshots_v.append(h.copy())
            times.append(step * dt)

    check_finite(a, "gm a_final")
    check_finite(h, "gm h_final")

    return FieldResult(
        u_final=a,
        v_final=h,
        snapshots_u=np.array(snapshots_u),
        snapshots_v=np.array(snapshots_v),
        times=np.array(times),
        params=dict(N=N, L=L, Da=Da, Dh=Dh, mu_a=mu_a, mu_h=mu_h, rho=rho,
                    rho_0=rho_0, kappa=kappa, dt=dt, n_steps=n_steps),
        shape=(N, N),
    )


def find_activator_centers(result, threshold_fraction=0.6, min_separation=3):
    """Find local maxima in the activator field.

    Returns array of (row, col) indices for spot centers.
    threshold_fraction: spots above this fraction of max(a) are candidates.
    min_separation: minimum pixel distance between distinct centers.
    """
    from scipy.ndimage import maximum_filter

    a = result.u_final
    threshold = threshold_fraction * a.max()
    local_max = (a == maximum_filter(a, size=min_separation)) & (a > threshold)
    labeled, n_spots = label(local_max)
    centers = []
    for i in range(1, n_spots + 1):
        locs = np.argwhere(labeled == i)
        centers.append(locs.mean(axis=0))
    return np.array(centers) if centers else np.empty((0, 2))


def pattern_strength(result):
    """Coefficient of variation of the activator field.

    Higher = stronger spatial patterning. Near-zero = uniform.
    """
    a = result.u_final
    mean = a.mean()
    if mean < 1e-12:
        return 0.0
    return float(a.std() / mean)


def cluster_count(result, threshold_fraction=0.6):
    """Number of connected high-activator regions."""
    a = result.u_final
    threshold = threshold_fraction * a.max()
    binary = a > threshold
    _, n = label(binary)
    return int(n)
