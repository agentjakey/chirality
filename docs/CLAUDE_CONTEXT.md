# CLAUDE_CONTEXT.md
# Chirality Atlas: Star Ascidian Edition
# Full project brief for use across Claude sessions

---

## Project identity

**Title:** Chirality Atlas: Star Ascidian Edition

**Repo:** agentjakey/chirality

**Context:** UCSD Vibe Coding Active Matter 2026 hackathon.
Modeling-based competition. Goal: choose a striking biological pattern, build a minimal
model, simulate dynamics, find parameter regimes that recreate the target, explore phase
diagrams, and pitch the insight in 5 slides and 5 minutes.

**Biological target:** Star ascidian colony patterns, specifically Botryllus schlosseri.
Visual signature: repeated star-shaped systems, each with radial zooid-like lobes arranged
around a shared center, many stars tiling a substrate. The goal is a model that generates
this two-level organization -- star centers spread across a surface, lobes radiating from
each center -- using simple local rules.

---

## The scientific question

Can local growth, inhibition, active motion, and chirality generate star-shaped colonial
organization?

More concretely: does a two-layer model -- (1) an activator-inhibitor field that places
star centers and (2) active particles that orbit those centers with angular repulsion and
optional chirality -- produce a set of quantitatively star-like configurations across a
tunable parameter space?

---

## The model (two layers)

### Layer 1: Gierer-Meinhardt activator-inhibitor field

Generates repeated spot positions that serve as star centers.

Standard Gierer-Meinhardt equations:
    da/dt = D_a * laplacian(a) + rho * a^2 / (h * (1 + kappa * a^2)) - mu_a * a
    dh/dt = D_h * laplacian(h) + rho * a^2 - mu_h * h

where:
- a = activator (short range, creates local growth signal)
- h = inhibitor (long range, suppresses neighboring growth)
- D_a << D_h is the core condition for Turing-type pattern formation
- rho = production coupling constant
- kappa = saturation term (prevents blow-up)
- mu_a, mu_h = decay rates

Key tunable ratio: D_h / D_a. Higher ratio = better-separated spots.
Number of spots per domain controlled by mu_h / mu_a and D_h / D_a jointly.

Spots in the a field mark star-center positions.

### Layer 2: Active zooid-like particles

Each particle represents one zooid. Particles live in the same 2D domain as the field.

Forces on each particle:
1. Self-propulsion: constant speed v0 in direction theta_i
2. Center attraction: drift toward nearest GM spot with strength k_attract
3. Soft radial targeting: prefer to sit at radius r_target from the center
4. Angular repulsion: particles repel each other angularly around the same center
5. Excluded volume: soft pairwise repulsion at short range
6. Chirality: optional rotation rate omega added to orientation update
7. Rotational noise: Dr term (standard chiral ABP orientation diffusion)

Orientation update:
    theta_i += omega_i * dt + sqrt(2 * Dr * dt) * xi_i

Position update:
    x_i += v0 * cos(theta_i) * dt + k_attract * (x_center - x_i) * dt
    y_i += v0 * sin(theta_i) * dt + k_attract * (y_center - y_i) * dt

### Layer coupling

The field runs first for n_field_steps to establish spot positions.
Spot positions are extracted from the a-field using a local-maximum finder.
Particles are then initialized near the spots and evolved with the center-attraction force.
Optionally, the field continues to evolve slowly during the particle simulation.

---

## Target metrics (what makes it star-like)

All metrics computed per star, then averaged across the colony.

1. **Arm count**: angular cluster count of particles around each center.
   Method: histogram of polar angles, count peaks with scipy.signal.find_peaks.
   Target: n_arms = 7 for Botryllus (approximate). Range 4-10 is visually convincing.

2. **Radial order**: fraction of particles within [0.7 * r_target, 1.3 * r_target].
   Higher = particles well-localized at the right radius.

3. **Angular uniformity**: circular variance of inter-arm angles.
   Lower = arms equally spaced. Quantifies "how star-like" vs. "how lumpy."

4. **Star-likeness score**: composite of arm count, radial order, and angular uniformity.
   A single scalar in [0, 1].

5. **Swirl score**: net signed angular momentum of particles around their center.
   Zero = no chirality. Nonzero = chiral arms (twisted stars).
   Sign determines CW vs CCW.

6. **Center spacing**: mean nearest-neighbor distance between GM spots.
   Controlled by D_h / D_a. Target: stars should not merge.

7. **Occupation number**: mean particles per center.
   Too many -> merged stars. Too few -> incomplete arms.

---

## Expected phases (creative exploration targets)

From the phase diagram over (omega, k_attract, Dr, D_h/D_a):

1. **Uniform mat**: no GM pattern, no organization. Field does not Turing-bifurcate.
2. **Spots without stars**: GM spots present, particles dispersed (k_attract too low or Dr too high).
3. **Clean star systems**: target regime. Arms visible, angular uniformity high.
4. **Twisted chiral stars**: omega > 0. Arms spiral instead of pointing radially.
5. **Overcrowded merged stars**: too many particles per center, stars merge.
6. **Fragmented noisy systems**: too much noise, no arms form despite centers.
7. **Boundary-biased stars**: near a hard wall, edge stars deform.
8. **Defect-pinned stars**: an obstacle in the field pins a topological defect.

---

## Final deliverables

1. Runnable notebook (notebooks/Star_Ascidian_Colab.ipynb)
   Sections: setup, the question, field baseline, particle baseline, combined model,
   phase diagram, creative exploration, comparison to target image, interpretation.

2. Simulation movies
   - GM spot formation (field animation)
   - Particle self-organization around spots (particle + field animation)
   - Chiral twist: omega > 0 showing swirling arms

3. Phase diagrams
   - (D_h/D_a) vs (mu_h): number of spots and spot spacing
   - (omega) vs (Dr): swirl score and arm count
   - (k_attract) vs (n_particles_per_center): star-likeness score

4. Model equations clearly displayed in notebook and docs

5. Comparison panel:
   Left: real Botryllus image or schematic description
   Right: simulation at clean-stars regime
   Third panel: metric bar chart showing arm count, radial order, angular uniformity

6. 5-slide pitch:
   target image -> model -> simulation results -> phase diagram -> insight + limits

7. LLM proficiency: 1-2 prompts explicitly shown in the notebook where LLM use
   made a real difference (model design choice, parameter debugging, hypothesis)

8. Honest limitations statement in docs and in final slide

---

## Rubric to optimize

### Scientific accuracy (weight: high)
- GM equations implemented correctly (correct signs, saturation term, laplacian)
- Chirality term in particle orientation update is the standard omega*dt formulation
- Metrics are honest (arm count is measured, not asserted)
- Claims are scoped: "toy model" explicitly stated
- Known limitations listed (no hydrodynamics, no actual Botryllus biochemistry)

### Creative insight (weight: high)
- Phase diagram shows qualitatively different regimes
- At least one "surprising" regime identified and explained
- Chiral twist is visually distinctive and not just "noise"
- Boundary/defect exploration adds one non-obvious result

### LLM proficiency (weight: medium)
- Show explicit prompt-run-test-modify-critique iterations
- At least one LLM-generated hypothesis that was tested
- At least one example where LLM suggested a model modification that improved output
- Document these in docs/llm_log.md and in the notebook

---

## Design style (non-negotiable)

Scientific field notebook, not generic AI dashboard.

Color palette:
- Background: #F7F3EA (warm off-white)
- Ink: #1F2421 (charcoal)
- Accent: #C15A3A (muted terracotta)
- Green: #315C4C (deep forest green)
- Panel: #FFFFFF / #EFE8DC
- Border: #DDD5C8

Typography: Georgia serif throughout.

Particle color convention:
- non-chiral: dark gray #666666
- left-handed: terracotta #C15A3A
- right-handed: deep forest green #315C4C

Field colormap: YlOrBr (warm, projector-safe). Not magma. Not jet.

No emojis. No neon. No glassmorphism. No generic AI SaaS language.
No overclaiming. No "revolutionary" or "powerful" or "cutting-edge."
One honest limitation per major claim.

---

## What the model does and does not explain

Does explain (toy model level):
- How short-range activation + long-range inhibition places multiple star centers across a surface
- How active particles with center attraction can self-organize into radial arm structures
- How chirality (omega) changes arm geometry from radial to spiral
- How the number of arms and their regularity depend on particle count and noise

Does NOT explain (explicitly disclaim):
- Actual Botryllus developmental biology (signaling molecules, blastogenic cycle)
- Quantitative matching to any measured Botryllus geometry
- Hydrodynamic interactions between zooids
- The colonial immune recognition system that determines which colonies fuse
- Any 3D structure or substrate mechanics

---

## Code style (non-negotiable)

From global CLAUDE.md:
- NO Unicode or special characters in code (no em-dashes, smart quotes, arrows)
- Human-looking code: clear variable names, no over-engineering
- Always complete and production-quality: no stubs, no TODOs unless asked
- No f-string Unicode
- Prefer explicit over implicit
- No magic
- Default: no comments unless the WHY is non-obvious
- pip installs: always include --break-system-packages

---

## Module structure (target)

src/chirality/
  __init__.py          -- updated public API
  config.py            -- updated parameter dataclasses
  particle_sim.py      -- KEEP: ABP, chiral ABP (used for zooid layer)
  particle_metrics.py  -- KEEP: polar_order, swirl_index, etc. (reused + extended)
  gm_sim.py            -- NEW: Gierer-Meinhardt field simulation
  gm_metrics.py        -- NEW: spot detection, center spacing, field metrics
  star_sim.py          -- NEW: combined GM + zooid particle simulation
  star_metrics.py      -- NEW: arm count, radial order, star-likeness, swirl
  phase_sweeps.py      -- REWRITE: sweeps over star-relevant parameters
  plotting.py          -- EXTEND: add star-specific visualizations
  export.py            -- KEEP: save_figure, save_frames_as_gif, save_sweep_csv
  validation.py        -- KEEP: all_finite_report
  presets.py           -- REWRITE: star ascidian presets
  storytelling.py      -- REWRITE: star-specific summaries

NOT needed (remove from imports, keep files for now if they compile):
  pattern_sim.py       -- Gray-Scott not used in new model
  pattern_metrics.py   -- Gray-Scott metrics not used

---

## File naming conventions

Outputs:
  outputs/field/        -- GM field snapshots and animations
  outputs/star/         -- combined star colony figures
  outputs/phase/        -- phase diagrams
  outputs/videos/       -- GIF animations
  outputs/summary/      -- presentation-ready panels
  outputs/data/         -- CSV exports

Scripts:
  scripts/run_gm_demo.py       -- GM field baseline
  scripts/run_star_demo.py     -- full star colony demo
  scripts/run_star_sweeps.py   -- phase diagrams
  scripts/make_star_video.py   -- animations
  scripts/make_summary_panels.py -- presentation panels
  scripts/smoke_test.py        -- updated
  scripts/make_all_assets.py   -- updated orchestrator

---

## Key design decisions already made

1. Use Gierer-Meinhardt (not Gray-Scott) for the field layer.
   Gray-Scott requires multi-seed initialization tricks to get good patterns in finite time.
   GM is more parameter-transparent and produces clean spots with standard parameters.
   Saturation term prevents blow-up.

2. Decouple field and particle evolution.
   Run GM to steady state first, extract spot positions, then run particle simulation.
   This avoids slow coupled dynamics and gives cleaner control over each layer.

3. Chirality enters only in the particle layer.
   Field is achiral. All chirality effects are from the omega parameter in particle orientation.
   This makes it easy to run matched-pair experiments: same field, different omega.

4. Angular repulsion between particles on the same center.
   Without this, particles all pile up at the minimum-potential point.
   Angular repulsion is what drives arm formation.
   Implemented as a force pushing particles apart along the tangential direction.

5. Star-likeness is a composite scalar metric.
   Makes phase diagrams readable: one number, one colormap.
   Decomposed into arm_count, radial_order, angular_uniformity for diagnosis.
