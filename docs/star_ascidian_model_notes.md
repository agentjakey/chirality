# Star Ascidian Colony Model: Technical Notes

## Biological Target

**Organism:** *Botryllus schlosseri* (star ascidian / colonial tunicate)

The colony is organized as a set of star-shaped systems, each with a shared central
atrium and approximately 5-10 zooids radiating outward in discrete arms. Neighboring
stars maintain characteristic spacing and do not merge under normal conditions.
The colony is capable of chirality: some species and strains exhibit a consistent
rotational handedness in arm geometry.

This model reproduces the **spatial geometry** of these patterns using minimal local
rules. It is not a mechanistic developmental model and does not incorporate Botryllus
biochemistry, blastogenic timing, or colonial immune recognition.

---

## Model Architecture

Two decoupled layers run in sequence.

### Layer 1: Activator-Inhibitor Field (Center Placement)

A Gierer-Meinhardt (GM) reaction-diffusion system produces spatially periodic
Turing spots. These spots are used as the star center positions for Layer 2.

**GM equations:**

    da/dt = Da * lap(a) + rho * a^2 / (h * (1 + kappa * a^2)) - mu_a * a + rho_0
    dh/dt = Dh * lap(h) + rho * a^2 - mu_h * h

**Why GM?** The short-range activation / long-range inhibition structure
naturally produces a quasi-regular array of spots with characteristic spacing
controlled by Dh/Da. This mimics the spacing regularity of Botryllus star centers
without requiring explicit agent-to-agent distance rules.

**Numerical scheme:** IMEX (implicit diffusion in Fourier space, explicit
nonlinear reaction). Unconditionally stable for the diffusion term. Denominators:

    denom_a = 1 + dt * (Da * k2 + mu_a)
    denom_h = 1 + dt * (Dh * k2 + mu_h)

**Key parameters:**
- `Dh/Da` -- controls number of spots (higher ratio = more spots, smaller spacing)
- `mu_h` -- inhibitor decay rate; affects spot regularity
- `min_distance` -- post-processing filter removes centers closer than this value

**Center extraction:** local maxima of the activator field above 55% of peak,
filtered by minimum pixel separation. Centers converted to physical coordinates.

---

### Layer 2: Active Zooid Agents (Arm Formation)

N active self-propelled particles (zooids) are initialized around each center
in discrete arm groups and evolve under five force contributions.

**Initialization:**
- n_arms arms per center, n_per_arm particles per arm
- Arm angles: uniformly distributed around 2*pi
- Each arm stacks particles radially at slightly different distances from r_target
- Small angular jitter per particle for visual variation

**Forces on particle i:**

1. **Self-propulsion:**  `F = v0 * (cos(theta), sin(theta))`

2. **Center attraction** (soft, linear):  `F = -k_attract * r_vec`

   Prevents particles from drifting to a neighboring center.

3. **Radial spring** (toward r_target):  `F = k_radial * (r_target - r) * r_hat`

   Confines particles to a ring at the target radius. Positive when too close,
   negative when too far.

4. **Angular repulsion** (between different arms only):

   For pairs from different arm groups at the same center:

       dphi = phi_i - phi_j (wrapped to [-pi, pi])
       F_angular = -k_angular * (1 - |dphi|/sigma_angular) * sign(dphi) * t_hat

   Where `sigma_angular = 1.5 * 2*pi/n_arms`. This pushes co-located arm
   neighbors apart in the tangential direction, enforcing equal arm spacing.
   Same-arm particles have dphi ~ 0, so sign(dphi) = 0 and force is zero.

5. **Excluded volume** (all pairs, cutoff sigma_ev):

       F_ev = k_ev * (1 - dist/sigma_ev) * separation_hat   (if dist < sigma_ev)

**Orientation update:**

    theta_i += omega_i * dt + sqrt(2*Dr*dt) * N(0,1)

**Chirality:** `omega > 0` twists arm orientations over time. In `racemic_mixed`
mode, half of particles have `omega = +|omega|` and half have `omega = -|omega|`.

---

## Phase Space and Presets

Seven named presets cover distinct morphological phases:

| Preset | Key parameters | Expected phase |
|---|---|---|
| `clean_star_systems` | Dr=0.04, omega=0 | Well-formed radial arms, no chirality |
| `chiral_twisted_stars` | omega=2.5, mode=chiral_twist | All arms rotate same direction |
| `racemic_mixed` | omega=2.5, mode=racemic_mixed | Mixed CW/CCW handedness per particle |
| `overcrowded_merged_systems` | n_per_arm=9, k_angular=0.2 | Stars overlap, arms merge |
| `noisy_fragmented_systems` | Dr=0.9, v0=0.35 | High noise, agents escape stars |
| `boundary_pinned_stars` | boundary=box | Stars distorted near domain walls |
| `weak_inhibition_uniform_mat` | Dh=0.15 (Dh/Da=3) | Few or no Turing spots form |

---

## Metrics

All metrics are computed from the final agent snapshot in a ZooidResult.

**radial_order_score:** Fraction of agents within [r_target*(1-0.3), r_target*(1+0.3)]
from their assigned center. High = ring structure preserved.

**arm_count_distribution:** Angular histogram of agent positions per center.
Peaks found via scipy.signal.find_peaks. Returns mean arm count across centers.

**angular_uniformity_score:** CV of inter-arm angular spacings (1 - CV).
High = arms evenly spaced.

**star_likeness_score:** Composite:

    (arm_score + radial_order + angular_uniformity) / 3

where arm_score = exp(-0.5 * ((n_arms_measured - target_arms) / arm_tolerance)^2).

**swirl_score:** Net signed tangential velocity of agents around their centers,
normalized by v0. Positive = net CCW rotation. Near zero = radial_clean.

**fragmentation_score:** Fraction of agents farther than 1.8 * r_target from
their center. High = agents have escaped their star.

**merge_score:** Fraction of cross-center agent pairs closer than r_target.
High = stars are overlapping.

---

## Phase Diagram Sweeps

Four parameter sweeps are implemented in `phase_diagram.py`. Each uses a
5x5 grid of points with short simulations (n_steps=150 for agents, n_steps=1500
for the GM field at reduced grid size N=32).

- **Sweep A:** k_radial vs omega -> star_likeness, swirl
- **Sweep B:** Dr vs k_angular -> fragmentation, star_likeness
- **Sweep C:** Dh/Da vs mu_h -> n_centers, spacing_cv, spacing_quality
- **Sweep D:** omega vs n_per_arm -> swirl, star_likeness

---

## Known Limitations

- Arm count detection (find_peaks on angular histogram) works well when arms are
  clearly separated but can under-count when angular repulsion is weak or noise
  is high. The 36-bin histogram may not resolve 7 narrow arms with only 3 agents
  each.

- The GM field at N=32 with n_steps=1500 may not fully equilibrate; use N=64 and
  n_steps=3000 for publication-quality center placement (preset defaults).

- Short sweeps (n_steps=150) are for speed only. The true phase boundaries require
  longer runs for the agent dynamics to reach steady state.

- Excluded volume uses an O(N^2) all-pairs loop. For N > ~500 agents this becomes
  a bottleneck. For larger colony sizes, implement a neighbor list or cell list.

- No hydrodynamics, no substrate mechanics, no blastogenic timing.
