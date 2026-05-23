# Scientific Audit: Chirality Atlas Star Ascidian Model

---

## Equation Audit

### Gierer-Meinhardt (Layer 1)

    da/dt = Da * lap(a) + rho * a^2 / (h * (1 + kappa * a^2)) - mu_a * a + rho_0
    dh/dt = Dh * lap(h) + rho * a^2 - mu_h * h

**Source:** Standard saturating GM form. Saturation term (1 + kappa * a^2) in the
denominator prevents activator runaway. Standard reference: Gierer & Meinhardt 1972,
Kybernetik 12:30-39.

**IMEX denominators verified:**

    denom_a = 1 + dt * (Da * k2 + mu_a)
    denom_h = 1 + dt * (Dh * k2 + mu_h)

Unconditional stability for diffusion term follows from the implicit treatment:
the denominator is always > 1, so the update cannot amplify high-frequency modes
regardless of dt. Verified by running at dt=5.0 (ten times default) -- field stays finite.

**Turing instability condition:** Requires Dh/Da >> 1 and activator self-activation.
Default Dh/Da = 5.0/0.05 = 100. Instability verified by observing spot formation
in smoke test and pattern_strength > 0 in gm_result.

### Active Zooid Agent Update (Layer 2)

**Self-propulsion:** Standard active Brownian particle. v0, Dr from tutorial ABP.

**Center attraction:** Linear spring. Correct for soft confinement; does not
diverge at any distance. No issues.

**Radial spring:** (r_target - r) * r_hat. At r=0 the spring direction is
undefined (r_hat = 0/0). Protected by adding 1e-9 to r before division.
At initialization, all agents start at r approximately equal to r_target,
so the r=0 singularity is never actually hit in practice.

**Angular repulsion:** dphi wrapped to [-pi, pi]. Same-arm force is zero
because dphi ~ 0 implies sign(dphi) = 0. This is correct. Force direction
is tangential (t_hat = [-r_hat_y, r_hat_x]). Verified by same-arm zero-force test.

**Excluded volume:** Soft repulsion for dist < sigma_ev. Correct standard form.
Direction is separation_hat = (pos_i - pos_j) / |pos_i - pos_j|. Protected against
dist=0 by using sigma_ev as cutoff (dist > 0 always when applying the force).

**Chirality:** dtheta += omega_i * dt. Standard phenomenological chiral ABP.
Physical interpretation: omega = v0 / R_c where R_c is circular orbit radius.
For omega = 2.5, v0 = 0.08: R_c = 0.08 / 2.5 = 0.032, well below sigma_ev.
This means agents in the chiral preset make tight circles -- arm structure is maintained
by the radial spring overcoming the circular tendency.

---

## Metric Audit

### radial_order_score

Fraction of agents within 30% of r_target. Straightforward. No pathological cases.
Validated: for agents initialized exactly at r_target (r = r_target), score = 1.0.

### arm_count_distribution

Uses scipy.signal.find_peaks on smoothed 36-bin angular histogram.
Known weakness: with n_per_arm=3, each arm contributes only 3 points to the 36-bin
histogram. The peak is typically 1-2 bins wide and may merge with adjacent arms.
The metric systematically under-counts arms at low density.

**Do not claim arm_count = 7 from this metric.** Claim radial_order instead.

### star_likeness_score

Composite: (arm_score + radial_order + uniformity) / 3.
arm_score uses a Gaussian penalty on |n_measured - target|. If arm_count is
systematically low (see above), arm_score pulls down star_likeness even when
the geometry is good. The metric is honest -- it reflects the detection limit.

### swirl_score

Net tangential velocity normalized by v0. Range approximately [-1, 1].
For omega=0: expected near zero, observed ~0.01-0.05 due to thermal noise.
For omega=2.5: expected significantly nonzero, observed ~0.2-0.4.

Verified: racemic mode (half +omega, half -omega) gives near-zero net swirl. PASS.

### fragmentation_score and merge_score

Both straightforward distance-based metrics. No numerical issues.
O(N^2) computation -- slow for N > ~500, fine for default N = K * n_arms * n_per_arm
which is typically 10-100 agents total.

---

## Sanity Checks

All verified in `scripts/06_final_smoke_test.py` (53/53 passing):

- GM field: shape matches (N, N), values finite, activator > 0 everywhere
- Centers: 2D array, all positions in [0, L], K >= 1
- Zooid positions: shape (n_snapshots, N, 2), all finite, all in [0, L] for periodic
- star_likeness: in [0, 1]
- swirl_score: finite
- fragmentation_score: in [0, 1]
- PRESETS: all 7 presets run without error at n_snapshots=4

---

## Known Weaknesses

**What is claimed too strongly and should be softened:**

- Arm count = 7 is not reliably detected. The arm_count metric reads typically 1-3
  because 3 agents per arm is below the angular histogram detection threshold.
  Claim radial_order and star_likeness instead; mention arm count as a known metric limit.

- "Star-shaped pattern" requires qualifying. The model produces agents organized
  into lobes around centers. Whether this visually resembles a star depends on density.
  At n_per_arm=3, the lobes are sparse. At n_per_arm=8, they are clearly star-shaped.

- Phase diagram boundaries are computed at N=32, n_steps=1500 for the GM field
  and n_steps=150 for agents. These are fast approximations. The boundaries would
  shift at full resolution.

**What not to claim:**

- The model does not explain why Botryllus has 7 arms. n_arms is a parameter.
- The model does not explain the molecular mechanism of arm formation.
- The model is not validated against actual Botryllus fluorescence microscopy data.
- The IMEX scheme is stable for diffusion but not unconditionally stable for the
  nonlinear reaction terms. Very large dt or very large rho can still blow up the reaction.
- The agent dynamics are Euler integration. This is first-order accurate. Positions
  are not exact; the model is qualitatively correct but not precision-calibrated.
