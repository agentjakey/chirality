# Model Notes: Chirality Atlas Star Ascidian

Short reference card for the two-layer model. For full derivations see
`docs/star_ascidian_model_notes.md`.

---

## Layer 1: Gierer-Meinhardt Field

Produces star center positions via Turing instability.

    da/dt = Da * lap(a) + rho * a^2 / (h * (1 + kappa * a^2)) - mu_a * a + rho_0
    dh/dt = Dh * lap(h) + rho * a^2 - mu_h * h

Numerical scheme: IMEX (implicit diffusion, explicit reaction), Fourier space.

    denom_a = 1 + dt * (Da * k2 + mu_a)
    denom_h = 1 + dt * (Dh * k2 + mu_h)

Key parameter: Dh/Da controls spot spacing. Default: Dh=5.0, Da=0.05 (ratio=100).

Center extraction: local maxima of activator field above 55% of peak value,
filtered by minimum pixel separation.

---

## Layer 2: Zooid Agent Dynamics

N active self-propelled agents. Five force contributions per agent:

    dx/dt = v0 * cos(theta) + F_attract + F_radial + F_angular + F_ev
    dy/dt = v0 * sin(theta) + (same)
    dtheta/dt = omega_i + sqrt(2*Dr) * xi(t)

**F_attract (center attraction):**

    F = -k_attract * (pos_i - center_k)

Prevents agents from drifting to neighboring stars.

**F_radial (radial spring):**

    r_vec = pos_i - center_k
    r = |r_vec|
    F = k_radial * (r_target - r) * r_hat

Confines agents to a ring at r_target.

**F_angular (inter-arm repulsion):**

    For pairs from different arm groups at the same center:
    dphi = phi_i - phi_j  (wrapped to [-pi, pi])
    sigma_angular = 1.5 * 2*pi / n_arms
    F = -k_angular * (1 - |dphi|/sigma_angular) * sign(dphi) * t_hat
    (where t_hat is the tangential unit vector)

Same-arm pairs: sign(dphi) = 0 (dphi ~ 0), force is zero automatically.

**F_ev (excluded volume):**

    if dist < sigma_ev:
    F = k_ev * (1 - dist/sigma_ev) * separation_hat

Applied between all agent pairs within cutoff.

---

## Default Preset Parameters (clean_star_systems)

    grid_size = 64, L = 10.0
    Da = 0.05, Dh = 5.0, mu_a = 0.05, mu_h = 0.05
    rho = 0.1, rho_0 = 0.001, kappa = 0.1
    dt_field = 0.5, n_field_steps = 3000
    n_arms = 7, n_per_arm = 3, r_target = 1.5
    v0 = 0.05, Dr = 0.04, omega = 0.0
    k_attract = 0.3, k_radial = 2.0, k_angular = 0.6
    k_ev = 0.4, sigma_ev = 0.18
    dt = 0.02, n_steps = 400

---

## Metrics Summary

| Metric | Formula | Target |
|---|---|---|
| radial_order | fraction of agents within 0.3*r_target of ring | high (> 0.5) |
| arm_count | mean peaks in angular histogram per center | ~7 |
| angular_uniformity | 1 - CV(inter-arm angles) | high (> 0.5) |
| star_likeness | (arm_score + radial + uniformity) / 3 | high (> 0.6) |
| swirl_score | net tangential velocity / v0 | ~0 (achiral), nonzero (chiral) |
| fragmentation | fraction of agents > 1.8*r_target from center | low (< 0.2) |
| merge_score | fraction of cross-center pairs < r_target | low (< 0.1) |

---

## Phase Regimes

| Regime | Cause | Signature |
|---|---|---|
| Uniform mat | Dh/Da too low (< ~5) | No Turing spots; all agents spread uniformly |
| Spots without stars | GM runs but agent forces too weak | Centers present; radial_order low |
| Clean stars | Default k_radial, low omega | star_likeness high, swirl near zero |
| Twisted stars | omega > ~1.5 | swirl nonzero; arm angles rotated |
| Merged stars | n_per_arm high or k_angular low | merge_score high |
| Fragmented stars | Dr high or v0 high | fragmentation high |
