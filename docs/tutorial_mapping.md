# Tutorial Mapping: How Each Resource Maps to the Project

This document records how every uploaded hackathon resource was used in
the Chirality Atlas Star Ascidian project.

---

## Active Matter Tutorial

**Used in:** `src/chirality/star_ascidian/zooid_agents.py`, Layer 2 dynamics

The zooid agent model is a direct extension of the active Brownian particle (ABP)
baseline from the tutorial. Specifically:

| Tutorial concept | Project implementation |
|---|---|
| ABP: self-propulsion v0*cos(theta), v0*sin(theta) | `F_self = v0 * (cos(theta), sin(theta))` in zooid update |
| Orientation noise: dtheta = sqrt(2*Dr*dt) * xi | Identical formula in zooid_agents.py orientation update |
| Chirality: dtheta += omega * dt | `dtheta += omega_i * dt` in zooid_agents.py |
| Order parameter (polar order) | Used in active particle baseline check in smoke_test.py |
| MSD | Computed in particle library; used for baseline verification |
| Phase diagram (noise vs chirality) | Sweep B in phase_diagram.py: Dr vs k_angular |
| Periodic boundary conditions | Default boundary in all zooid presets |

The tutorial ABP has no forces beyond self-propulsion. The zooid model adds
four force terms (center attraction, radial spring, angular repulsion, excluded volume)
that are not in the tutorial -- these are the creative extension that produces arm structure.

---

## Starter Pack

**Used in:** force design in `zooid_agents.py`, boundary modes

| Starter pack concept | Project implementation |
|---|---|
| Alignment interaction (Vicsek) | Not used in zooid model; used in particle library baseline |
| Soft repulsion (excluded volume) | `F_ev = k_ev * (1 - dist/sigma_ev) * sep_hat` |
| Reflective boundary | `boundary="box"` mode in boundary_pinned_stars preset |
| Multiple species (racemic) | `racemic_mixed` preset: half omega=+|omega|, half omega=-|omega| |

---

## Pattern Formation Tutorial

**Used in:** `src/chirality/star_ascidian/center_field.py`, Layer 1 field

| Tutorial concept | Project implementation |
|---|---|
| Diffusion operator (Laplacian) | FFT-based Laplacian in IMEX scheme |
| Reaction-diffusion framework | GM equations in `center_field.py` and `model_library/gierer_meinhardt.py` |
| Gray-Scott spots | Used as fallback center placement method if GM fails |
| Pattern strength metric | `gm_result.pattern_strength` used as a center quality indicator |
| Cluster count | `gm_result.cluster_count` used to estimate number of star centers |

---

## Fisher-KPP

**Used in:** `src/chirality/model_library/fisher_kpp.py`, reference model only

Fisher-KPP is included as a reference model in the Model Library tab of the app.
It is not part of the star ascidian model. Its role is educational: it shows
how a single-species reaction-diffusion equation produces a traveling invasion front,
contrasting with the two-species GM system that produces stationary spots.

---

## Gierer-Meinhardt

**Used in:** `src/chirality/star_ascidian/center_field.py` (Layer 1), central to project

The GM model is the core of Layer 1. We use it to place star centers because:

1. The activator-inhibitor structure (short-range activation, long-range inhibition)
   produces quasi-regular spot arrays -- matching the characteristic spacing of Botryllus stars.
2. The spacing is controlled by Dh/Da, a single interpretable parameter.
3. The IMEX scheme keeps the field numerically stable for the long runs (3000 steps)
   needed to fully equilibrate the pattern.

Equations:

    da/dt = Da * lap(a) + rho * a^2 / (h * (1 + kappa * a^2)) - mu_a * a + rho_0
    dh/dt = Dh * lap(h) + rho * a^2 - mu_h * h

IMEX denominators:

    denom_a = 1 + dt * (Da * k2 + mu_a)
    denom_h = 1 + dt * (Dh * k2 + mu_h)

---

## Cahn-Hilliard

**Used in:** `src/chirality/model_library/cahn_hilliard.py`, reference model only

Included as a reference model to show phase separation via spinodal decomposition.
Not used in the star ascidian model. Its educational role is to contrast with GM:
Cahn-Hilliard produces domains of characteristic size but no distinct localized spots.

---

## FitzHugh-Nagumo

**Used in:** `src/chirality/model_library/fitzhugh_nagumo.py`, reference model only

Included as a reference model to show excitable-medium wave behavior (spiral waves).
Not used in the star ascidian model. Demonstrates that the same diffusion-reaction
framework produces qualitatively different patterns depending on the reaction kinetics.

---

## Pattern Formation Slides

**Used in:** Notebook structure and presentation slide structure

The slides defined the five-step scientific method structure:
Observe, Hypothesize, Simulate, Compare, Explain.

| Slide step | Notebook section | App tab |
|---|---|---|
| Observe | Section 3: Observe visual features | Tab 1: Target Pattern |
| Hypothesize | Section 4: Hypothesize two-layer mechanism | Tab 1 + Tab 2 header |
| Simulate | Section 5-6: Baseline + hybrid model | Tab 2: Model Builder |
| Compare | Section 9: Target vs simulation | Tab 2 metric bars |
| Explain | Section 10: What model explains/does not | Tab 7 Presentation, Slide 5 |

The five-slide deck structure in `docs/final_5_slide_deck.md` follows the same
Observe / Hypothesize / Simulate / Explore / Explain arc.
