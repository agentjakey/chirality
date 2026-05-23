# Chirality Atlas: 5-Slide Deck

---

## Slide 1: Can microscopic handedness reshape living matter?

**Key question (10-second version):**
Active systems -- cells, bacteria, migrating tissues -- often have a built-in left or right bias.
Does that tiny handedness change how the whole system organizes?

**Background (2-3 bullets):**
- Active matter: units consume energy and move. Flocks, bacterial colonies, motility assays.
- Chirality: a left/right asymmetry in motion, shape, or organization.
- This project: two minimal computational models, one control knob (omega), one question.

**Biological relevance:**
- Chiral ABP: models bacteria near surfaces, sperm cells, rotating organelles
- Gray-Scott chiral source: toy model for symmetry-breaking morphogenetic signals
- Both models connect well-studied tutorials to an open research question

**Suggested visual:**
  outputs/summary/chirality_atlas_final_panel.png

---

## Slide 2: Two tutorial models, one scientific idea

**Particle track (Tutorial 1 extension):**
- Baseline: Active Brownian Particles (ABP). Self-propulsion + rotational diffusion.
- Extension: add omega*dt to orientation update. Each particle curves left or right.
- Vicsek model: local alignment. Chirality competes with collective order.
- New metric: swirl index (net angular momentum proxy)

**Pattern track (Tutorial 2 extension):**
- Baseline: Gray-Scott reaction-diffusion. F, k control whether spots or labyrinths form.
- Extensions: feed gradient (linear F), circular obstacle (no-reaction zone), chiral source (rotating injection point)
- New metric: left-right field asymmetry

**Both tracks:**
- Reproduce tutorial baseline behavior first
- Extend with one new parameter (omega)
- Build phase diagrams to map how omega interacts with existing control knobs

**Suggested visual:**
  outputs/summary/chirality_atlas_bridge_panel.png

---

## Slide 3: Baseline reproduction

**Particles:**
- ABP with no chirality: polar order phi ~ 0.05 (disordered gas). Expected.
- Vicsek with low noise: phi ~ 0.95 (flocking). Expected.
- Phase diagram (6x6 grid, N=80, 250 steps per point): polar order drops with Dr, swirl index grows with omega.

**Patterns:**
- F=0.035, k=0.065: self-organized spots, pattern_strength ~ 0.10. Expected.
- F=0.04, k=0.06: labyrinth morphology. Cluster count higher.
- F-k phase diagram (6x6 grid, 64x64, 2000 steps per point): pattern strength peaks in known spot/labyrinth region.

**Note on coarse grids:**
Phase diagrams use small grids for speed. The qualitative trends are correct;
quantitative boundaries would shift with finer grids.

**Suggested visuals:**
  outputs/phase_sweeps/particle_noise_vs_chirality_polar_order.png
  outputs/phase_sweeps/pattern_F_vs_k_pattern_strength.png

---

## Slide 4: Creative hack -- broken symmetry reorganizes the system

**Particle hacks:**
- Chiral vortex gas: all omega > 0. Particles trace circles, cluster weakly at boundaries.
- Boundary edge current: omega > 0 in circular trap. Particles accumulate on the wall and orbit.
- Racemic competition: 50% left, 50% right, with soft repulsion. Neither side dominates; swirl index near zero.

**Pattern hacks:**
- Feed gradient: F varies linearly. Pattern transitions from spots on one side to uniform field on the other.
- Circular obstacle: no-reaction zone creates a topology defect in the spot pattern.
- Chiral source (toy model): a rotating injection point breaks left-right symmetry.
  Measured L-R asymmetry increases from ~0.0001 (no source) to ~0.002+ (omega=0.1).

**Key point for judges:**
Chirality and noise are competing control knobs.
Chirality suppresses polar order (individual circling breaks collective alignment),
but creates a new kind of order (swirl, edge current) invisible to polar order.

**Suggested visuals:**
  outputs/videos/particle_boundary_edge_current.gif
  outputs/demo/pattern_chiral_source.png
  outputs/demo/particle_racemic_competition.png

---

## Slide 5: Biological meaning and limits

**What this connects to:**
- Bacteria near walls: right-handed swimmers accumulate at surfaces and orbit (matches BOUNDARY_EDGE_CURRENT)
- Left-right axis determination in embryos: local symmetry breaking propagates to tissue scale
- Chiral active nematics: defect topology controlled by chirality
- Morphogenetic gradients: feed gradient tutorial is a minimal model of spatial signal gradients

**Honest caveats:**
- Chiral ABP: omega is phenomenological. Real microswimmer chirality depends on flagella geometry.
- Gray-Scott chiral source: this is a toy model. No specific organism has this mechanism.
- Phase diagrams are coarse (6x6). Boundaries should be treated as indicative only.
- Simulations use Euler integration, which has known stability limits.
- O(N^2) soft repulsion in particle models; not suitable for N > 500.

**Takeaway:**
Handedness can be a design principle in active systems.
It shifts which order parameters matter and creates emergent structures
(edge currents, asymmetric patterns) that do not appear in the achiral baseline.

**Suggested visual:**
  outputs/summary/chirality_atlas_final_panel.png
