"""
Cahn-Hilliard phase field model.

PDEs:
  phi_t = M * lap(mu)
  mu = -A*phi + B*phi^3 - kappa*lap(phi)

Models phase separation of a binary mixture (spinodal decomposition).
phi = +1 and phi = -1 are the two equilibrium phases.
Conserved order parameter: mean(phi) is constant.

Numerical method: spectral semi-implicit scheme.
  Linear terms (A*phi and kappa*del^2(phi)) treated implicitly in Fourier space.
  Nonlinear term (B*phi^3) treated explicitly.

This gives stability condition dt < 4*kappa/(M*A^2), which for A=B=M=kappa=1
is dt < 4.0 -- far more permissive than the explicit bilaplacian limit.
"""

import numpy as np
from . import FieldResult, check_finite


def _make_k2(N, L):
    dx = L / N
    kx = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    ky = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    KX, KY = np.meshgrid(kx, ky, indexing="ij")
    return KX ** 2 + KY ** 2


def simulate_cahn_hilliard(
    N=64,
    L=10.0,
    A=1.0,
    B=1.0,
    M=1.0,
    kappa=0.5,
    dt=0.5,
    n_steps=2000,
    n_snapshots=10,
    seed=42,
    phi0=0.0,
):
    rng = np.random.default_rng(seed)
    k2 = _make_k2(N, L)

    # Correct semi-implicit denominator: treat A*phi and kappa*bilaplacian implicitly.
    # Linearized CH: dphi_hat/dt = M*k^2*(A - kappa*k^2)*phi_hat - M*k^2*B*(phi^3)_hat
    # Semi-implicit: (phi_hat_new - phi_hat)/dt = M*k^2*A*phi_hat_new - M*k^2*kappa*k^2*phi_hat_new - M*k^2*B*(phi^3_old)_hat
    # => denom = 1 - dt*M*A*k^2 + dt*M*kappa*k^4
    # Stable when dt < 4*kappa/(M*A^2); for A=B=M=kappa=1: dt < 4.0
    denom = 1.0 - dt * M * A * k2 + dt * M * kappa * k2 ** 2

    phi = phi0 + 0.05 * rng.standard_normal((N, N))

    snap_every = max(1, n_steps // n_snapshots)
    snapshots_u = []
    times = []

    for step in range(n_steps):
        phi_hat = np.fft.fft2(phi)
        # Explicit nonlinear: -M*k^2*B*(phi^3)
        nonlinear_hat = np.fft.fft2(B * phi ** 3)
        phi_hat_new = (phi_hat - dt * M * k2 * nonlinear_hat) / denom
        phi = np.real(np.fft.ifft2(phi_hat_new))

        if step % snap_every == 0:
            snapshots_u.append(phi.copy())
            times.append(step * dt)

    check_finite(phi, "cahn_hilliard phi_final")

    return FieldResult(
        u_final=phi,
        v_final=None,
        snapshots_u=np.array(snapshots_u),
        snapshots_v=None,
        times=np.array(times),
        params=dict(N=N, L=L, A=A, B=B, M=M, kappa=kappa, dt=dt, n_steps=n_steps, phi0=phi0),
        shape=(N, N),
    )


def domain_size_proxy(result):
    """Estimate characteristic domain size via peak of the structure factor.

    Returns the mean wavenumber weighted by power spectrum.
    Larger values indicate smaller domains.
    """
    phi = result.u_final
    L = result.params["L"]
    N = phi.shape[0]

    fft = np.fft.rfft2(phi - phi.mean())
    power = np.abs(fft) ** 2

    freqs_r = np.fft.rfftfreq(N, d=L / N)
    freqs_c = np.fft.fftfreq(N, d=L / N)
    fy, fx = np.meshgrid(freqs_c, freqs_r, indexing="ij")
    k = np.sqrt(fy ** 2 + fx ** 2)

    k_flat = k.ravel()
    p_flat = power.ravel()
    total = p_flat.sum()
    if total < 1e-12:
        return 0.0

    return float(np.sum(k_flat * p_flat) / total)
