# Model Library Notes

## Overview

`src/chirality/model_library/` contains six self-contained reference implementations
of physics models relevant to active matter and pattern formation. Each model is
independent: no shared state, all parameters passed explicitly.

---

## Shared data structures

Both `FieldResult` and `ParticleResult` are dataclasses defined in `__init__.py`.

`FieldResult`:
- `u_final`, `v_final`: final 2D arrays (v_final is None for single-field models)
- `snapshots_u`, `snapshots_v`: 3D arrays (n_snapshots, N, N) for animation
- `times`: 1D array of snapshot times
- `params`: dict of all simulation parameters
- `shape`: (N, N) tuple

`ParticleResult`:
- `positions`: (n_snapshots, N, 2) array
- `thetas`: (n_snapshots, N) array of orientations
- `omegas`: (N,) per-particle rotation rates
- `times`, `L`, `N`, `params`

---

## Model reference

### Fisher-KPP (fisher_kpp.py)

PDE: u_t = D * lap(u) + r * u * (1 - u)

Key physics: logistic growth + diffusion produces invasion fronts.
Front speed: c = 2 * sqrt(D * r) (analytical result for the pulled front).

Reference parameters: D=0.5, r=1.0, N=64, dt=0.05
Stability: dt < dx^2 / (2*D)

Metric: front_radius -- maximum radial extent of u > 0.5


### FitzHugh-Nagumo (fitzhugh_nagumo.py)

PDEs: u_t = Du*lap(u) + u - u^3/3 - v + I_ext
      v_t = epsilon*(u + a - b*v)

Key physics: excitable medium with fast activator (u) and slow inhibitor (v).
Resting state computed numerically via brentq for a=0.7, b=0.8: u ~ -1.2, v ~ -0.625.
Stimulate one corner: generates a wave that propagates across the domain.

Reference parameters: Du=1.0, epsilon=0.08, a=0.7, b=0.8, dt=0.02
Stability: dt < dx^2 / (2*Du); at N=64, L=10, dx=0.156, limit ~ 0.012

Metric: wave_activity -- fraction of domain with u > 0


### Gierer-Meinhardt (gierer_meinhardt.py)

PDEs: da/dt = Da*lap(a) + rho*a^2/(h*(1+kappa*a^2)) - mu_a*a + rho_0
      dh/dt = Dh*lap(h) + rho*a^2 - mu_h*h

Key physics: short-range activation + long-range inhibition -> Turing spots.
Turing condition: Dh/Da >> (mu_h/mu_a)^2 (approximately).
With Da=0.05, Dh=5.0, ratio=100 (well above threshold with mu_a = mu_h).
Steady state: a_ss ~ (mu_h + rho_0)/mu_a, h_ss = rho*a_ss^2/mu_h.

Reference parameters: Da=0.05, Dh=5.0, mu_a=mu_h=0.05, rho=0.1, rho_0=0.001, kappa=0.1, dt=0.1
Stability: dt < dx^2/(2*Dh) at N=64, L=10, dx=0.156, limit ~ 0.24. dt=0.1 is safe.

Metrics: pattern_strength (CV of a-field), cluster_count, find_activator_centers


### Cahn-Hilliard (cahn_hilliard.py)

PDEs: phi_t = M * lap(mu)
      mu = -A*phi + B*phi^3 - kappa*lap(phi)

Key physics: conserved phase field; spinodal decomposition of a binary mixture.
phi = +1 and phi = -1 are equilibrium phases.
Conservation: mean(phi) is exactly preserved.

Reference parameters: A=B=M=kappa=1.0 (symmetric double-well), dt=0.05
Stability: dt < dx^4 / (16*M*kappa). At N=64, L=10, dx=0.156, limit ~ 0.23.

Metric: domain_size_proxy -- mean wavenumber of the structure factor power spectrum


### Gray-Scott (gray_scott.py)

PDEs: u_t = Du*lap(u) - u*v^2 + F*(1-u)
      v_t = Dv*lap(v) + u*v^2 - (F+k)*v

Key physics: autocatalytic reaction. Spots at F=0.035, k=0.065. Labyrinths at F=0.040, k=0.060.

Reference parameters: Du=0.16, Dv=0.08, F=0.035, k=0.065, dt=1.0
Note: dt=1.0 works here because Du and Dv are small and the grid spacing accounts for it.
Actual stability limit: dt < dx^2/(2*Du). At N=64, L=10: dx=0.156, limit ~ 0.076.
This means dt=1.0 is technically violating the diffusion stability limit for GS.
In practice it works for these parameter values because the GS system is self-stabilizing
(u,v clipped to [0,1]). For robustness, use dt=0.5 or smaller if you see blow-up.

Metrics: pattern_strength (CV of v-field), cluster_count


### Active Particles (active_particles.py)

Three models: ABP, chiral ABP, Vicsek.

ABP:
  theta += sqrt(2*Dr*dt) * noise
  pos += v0 * [cos(theta), sin(theta)] * dt

Chiral ABP:
  theta += omega_i * dt + sqrt(2*Dr*dt) * noise
  Modes: uniform, left, right, racemic, random

Vicsek:
  Align with neighbors within R, add noise eta, optional omega.

Metrics: polar_order (|mean exp(i*theta)|), swirl_index (net angular velocity),
msd (mean squared displacement), avg_neighbors

---

## Numerical methods

All field models use IMEX (implicit-explicit) or spectral semi-implicit schemes.

- Explicit Euler for diffusion blows up when dt > dx^2/(4*D) (2D stability limit).
  At N=64, dx=0.156: limit is dt < 0.0024 for D=5 (GM), < 0.006 for D=1 (FHN).
- All models now use implicit diffusion (in Fourier space) to remove this constraint.
  The only remaining dt requirement comes from the reaction terms.

| Model       | Scheme              | dt ref  | Notes                            |
|-------------|---------------------|---------|----------------------------------|
| Fisher-KPP  | IMEX                | 0.1     | reaction limit dt < 2/r          |
| FHN         | IMEX (u) + semi (v) | 0.1     | reaction: dt < 2 for r(u)~1      |
| GM          | IMEX                | 0.5     | steady-state computed via brentq  |
| CH          | spectral semi-implicit | 0.5  | stable for dt < 4*kappa/(M*A^2)  |
| GS          | explicit (clipped)  | 1.0     | works empirically with u,v clipped|
| ABP         | explicit Euler      | 0.01    | no diffusion, stable always       |

GM specifics: IMEX denominator = 1 + dt*(D*k^2 + mu). This treats both diffusion
and linear decay implicitly. The production term rho*a^2/(h*(1+kappa*a^2)) is explicit.

CH specifics: spectral semi-implicit treats A*phi (destabilizing) and kappa*lap^2 (stabilizing)
both implicitly. denom = 1 - dt*M*A*k^2 + dt*M*kappa*k^4. Stable when dt < 4*kappa/(M*A^2).

FHN init: use init="spiral" for reliable wave generation in periodic domains. The "stimulate"
(corner) init works for non-periodic or large domains but fails in periodic domains because
implicit diffusion spreads the stimulated region over the whole domain before the wave can form.

---

## Design decisions

1. All models are tutorial-aligned: parameter names match the tutorial notation exactly.
2. `model_library` is independent of the old `particle_sim.py` and `pattern_sim.py`.
   This allows the star ascidian simulation to import model_library without touching app.py.
3. Periodic boundary conditions everywhere (np.roll). No Neumann or Dirichlet BCs
   in the reference models (added in star_sim.py if needed).
4. `check_finite` is called at the end of every simulate_* function. If the simulation
   blows up, you get a clear error message rather than silent NaN propagation.
5. `FieldResult.v_final = None` for single-field models (Fisher-KPP, Cahn-Hilliard).
   Callers must check `result.v_final is not None` before using it.
