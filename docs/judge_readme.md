# For Judges: Chirality Atlas -- Star Ascidian Edition

---

## The 9 Questions This Project Answers

**1. What image/pattern did we start from?**
A colony of Botryllus schlosseri (star ascidian). The image shows a substrate tiled
with radial star-shaped systems: each star has 5-10 zooids arranged radially around
a shared central atrium, and stars maintain regular spacing without merging.

**2. What local rules did we hypothesize?**
Two rules:
- Colony level: nearby activator and distant inhibitor diffuse at different rates,
  spontaneously breaking symmetry into spots (Turing mechanism).
- Star level: each zooid is attracted to a target radius and repelled tangentially
  from adjacent arm groups, with optional chirality.

**3. What model did we build?**
A two-layer hybrid model:
- Layer 1: Gierer-Meinhardt activator-inhibitor field (PDE, solved with IMEX spectral scheme)
  producing quasi-regular Turing spots as star center positions.
- Layer 2: Active zooid agents (ODE) with 5 forces: self-propulsion, center attraction,
  radial spring, angular repulsion between arm groups, excluded volume. Plus chirality rate omega.

**4. What does the simulation reproduce?**
- Multiple star centers at quasi-regular spacing (from GM field)
- Agents well-confined at r_target: radial_order >= 0.8 at clean_star_systems preset
- Discrete arm structure: visual lobes at default parameters
- Measurable chirality: swirl_score ~0 at omega=0, ~0.3 at omega=2.5

**5. What phase diagram did we explore?**
Four parameter sweeps:
- Sweep A: k_radial vs omega (star-likeness and swirl)
- Sweep B: Dr vs k_angular (fragmentation)
- Sweep C: Dh ratio vs mu_h (center spacing quality)
- Sweep D: combined metrics across all presets

**6. What new states appeared?**
- Uniform mat: weak inhibition, no Turing spots, agents form ring not stars
- Clean stars: moderate k_radial, low omega -- best morphology
- Twisted stars: high omega, arms rotate persistently
- Merged systems: overcrowded, stars lose individuality
- Fragmented: high noise Dr, agents escape their star
- Boundary-pinned: hard wall boundary, arms near edges deform

**7. What does the model explain?**
- Why star systems have regular spacing (Turing mechanism, not explicit center-repulsion)
- How discrete arms form from a continuous ring (angular repulsion between arm groups)
- How chirality can be measured quantitatively (swirl_score, tangential velocity)
- Why stars can coexist with chirality up to a threshold (arm structure survives omega <= 2)

**8. What does it not explain?**
- Why there are 7 arms (n_arms=7 is a parameter, not emergent)
- Blastogenic developmental cycle of Botryllus
- Colonial immune recognition (self/non-self fusion decisions)
- 3D substrate attachment and curvature
- Organism-specific biochemical rates

**9. How did LLM use actually help?**

The two most impactful contributions:

*Decomposing the biological problem:*
We described the star ascidian colony and asked Claude what mechanisms could explain
the two-level spatial organization. Claude proposed separating center placement (a colony-level
process governed by diffusion) from arm formation (a local particle process). This was not
our initial plan. We started with a single-layer model. The decomposition is physically
principled and the two-layer result is cleaner than the single-layer alternative.

*Designing metrics that cannot be fooled:*
Early simulations looked like stars visually but failed quantitative checks.
Claude proposed a hierarchy of five metrics, each targeting a specific failure mode:
radial_order (ring without arms passes visually but fails this), arm_count (ring passes),
angular_uniformity (uneven arms pass), swirl_score (radial pattern cannot fake chirality),
fragmentation (good-looking center but escaped agents at boundary).

Both contributions were verified, not accepted blindly.

---

## What to run (60 seconds)

```
pip install -r requirements.txt
python healthcheck.py
streamlit run app.py
```

The healthcheck runs the full two-layer model and prints 8/8 PASS in under 30 seconds.
The app opens at http://localhost:8501.

---

## What to inspect in the app

Tab order: Target Pattern | Mechanism | Movie Gallery | Phase Explorer | LLM Lab Notebook | Presentation Mode | Model Builder

**Tab 1 (Target Pattern):** Reference image + colony-scale simulation match side by side. Feature checklist. Opens with the biological question.

**Tab 2 (Mechanism):** center_selection_schematic (Layer 1) + single_star_mechanism (Layer 2) side by side. Physical intuition box explains why each rule is necessary.

**Tab 3 (Movie Gallery):** Two hero GIFs: arms self-organizing (clean) and arms rotating (chiral).

**Tab 4 (Phase Explorer):** Pregenerated phase_diagram_with_regimes shown by default for Sweep A. Six named regimes with labels.

**Tab 5 (LLM Lab Notebook):** Two strongest contributions, exact prompts, one failure case, how outputs were validated.

---

## Verification status

- healthcheck: 8/8 PASS
- smoke test: 53/53 PASS
- pytest: 42/42 PASS
- compileall: no syntax errors
- app imports: clean

---

## Backup if live app fails

1. Open `outputs/panels/` -- 11 PNG panels, all slide-ready
2. Open `outputs/movies/star_formation_clean.gif` in Chrome
3. Run `python scripts/05_make_all_assets.py` -- regenerates all 47 outputs (~15 minutes)

---

## Honest limitations (stated in the app, not hidden)

- n_arms=7 is a parameter, not emergent
- arm_count metric reads ~1-3 at default density (angular histogram detection limit at 3 agents/arm)
- Phase diagram at 5x5 resolution (N=32, qualitative trends robust)
- No Botryllus biochemistry, developmental staging, 3D geometry, or immune recognition
