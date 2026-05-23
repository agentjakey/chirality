# Five-Slide Deck: Chirality Atlas -- Star Ascidian Edition

---

## Slide 1: Can local rules generate a living star pattern?

**One-sentence question:**
Can a Turing field plus active agents with angular repulsion reproduce the radial geometry
of a Botryllus schlosseri star ascidian colony?

**Visuals:**
- Left: schematic of Botryllus star system (draw_star_ascidian in notebook Section 2)
  or reference image from literature
- Right: `outputs/panels/slide1_target_and_simulation.png`
  (3-panel: schematic / GM field / agent snapshot)

**What to say (30 sec):**
The star ascidian Botryllus schlosseri arranges its animals into star-shaped systems.
Each star has a central opening and about 7 animals radiating out in discrete arms.
Multiple stars tile the colony without merging. Some colonies even twist their arms
in a consistent direction. We asked whether two simple physics rules -- a Turing
field for spacing and active forces for arm shape -- are enough to produce this geometry.

---

## Slide 2: Field selects centers. Agents form stars.

**Model schematic visual:** `outputs/panels/slide2_model_schematic.png`

**Layer 1 equation (Gierer-Meinhardt):**

    da/dt = Da * lap(a) + rho * a^2 / (h * (1 + kappa*a^2)) - mu_a * a + rho_0
    dh/dt = Dh * lap(h) + rho * a^2 - mu_h * h

Short-range activation, long-range inhibition. Dh/Da >> 1 gives quasi-regular spots.

**Layer 2 equation (active zooid update):**

    dx/dt = v0*cos(theta) - k_attract*(x - cx) + k_radial*(r_target - r)*x_hat + F_angular + F_ev
    dtheta/dt = omega + sqrt(2*Dr) * xi(t)

**What to say (30 sec):**
Layer 1 is a Gierer-Meinhardt reaction-diffusion system. Its Turing instability produces
spots at regular spacing -- these become our star centers. Layer 2 is an active particle
model. Each zooid is attracted to its home center, confined to a ring at radius r_target,
and pushed apart from other arms by angular repulsion. Chirality omega rotates the arms.
The two layers run in sequence and have no feedback between them.

---

## Slide 3: From noise to star systems.

**Visual:** `outputs/movies/star_formation_clean.gif`
(16-frame animation from random initialization to final arm structure)

If GIF cannot play: `outputs/panels/slide3_simulation_sequence.png`
(4 snapshots: t=0, t=100, t=200, t=400)

**Key metrics from clean_star_systems preset:**
- radial_order: >= 0.8 (agents at target ring)
- arm_count: detected near 7 (metric is noisy at low N per arm)
- center_spacing: K centers with characteristic separation

**What to say (45 sec):**
Starting from agents scattered randomly around each center, the combined forces
organize them into radial arms in about 400 steps. The radial spring pulls everyone
to the ring. The angular repulsion pushes arms apart until they are evenly spaced.
The swirl is near zero when omega equals zero.
When we add chirality (next slide), the arms rotate -- and we can measure that
rotation as a nonzero swirl score.

Show `outputs/movies/chiral_twist_emergence.gif` alongside the clean version
to make the contrast visible.

---

## Slide 4: Phase diagram reveals regimes.

**Visual:** `outputs/panels/slide4_phase_diagram.png`
(two heatmaps side by side: star_likeness and swirl)

**Regime labels (annotate on slide):**

| Region | k_radial | omega | Description |
|---|---|---|---|
| Uniform mat | (Dh/Da too low) | any | No spots form |
| Spots without stars | low k_radial | any | Centers exist but agents scatter |
| Clean stars | high k_radial | low | Best geometry; target regime |
| Twisted stars | high k_radial | high | Arms rotated; swirl nonzero |
| Merged stars | any | any + n_per_arm high | Stars overlap |
| Fragmented stars | any | any + Dr high | Agents escape |

**What to say (45 sec):**
The left heatmap shows star_likeness -- our composite score of arm quality.
The green region at high k_radial and low omega is the target regime.
As we increase chirality, star_likeness holds but swirl increases -- the arms
rotate without losing their structure. At very high chirality, arms lose coherence
because agents circle faster than they can maintain arm membership.
The right heatmap shows swirl: it's near zero for omega=0 and grows with omega,
confirming that the metric captures the biological handedness signature.

---

## Slide 5: Insight and LLM proficiency.

**Visual:** `outputs/panels/slide5_insight_and_limits.png`

**What the model explains:**

- Spatial periodicity of star centers (Turing instability, Dh/Da ratio)
- Radial arm geometry (center attraction + radial spring)
- Even arm spacing (angular repulsion)
- Chirality-induced arm rotation (omega parameter)
- Non-merging stars (center spacing from GM field)

**What the model does NOT explain:**

- Arm count is a parameter (n_arms), not emergent
- No Botryllus biochemistry or signaling molecules
- No blastogenic timing or colonial cycle
- No 3D geometry or substrate
- No immune recognition (fusibility)

**Best LLM use (one line each):**

1. IMEX scheme for GM: prompt specified exact denominator; code was correct on first try.
2. Angular repulsion: prompt specified arm_assignments and formula; vectorized correctly.

**What LLM got wrong:**

The swirl_score function had a numpy broadcast bug (`[:, None]` in column_stack).
We caught it by checking output shape and comparing to the manually-written force code.

**Takeaway:**

A two-stage mechanism -- a Turing field for center placement plus angular repulsion
for arm formation -- can turn local rules into star-shaped colonial order.
Chirality adds global rotation without destroying the arm structure.
