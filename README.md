# Chirality Atlas: Star Ascidian Edition

UCSD Vibe Coding Active Matter 2026 Hackathon

**Can local rules generate a living star pattern?**

---

## Project Pitch

*Botryllus schlosseri* (the star ascidian) arranges its zooids into radial star-shaped
systems: 7 arms per star, multiple stars per colony, consistent spacing, and measurable
chirality in some strains. We ask whether two local physical rules can reproduce this
geometry from scratch.

Our answer is a two-layer hybrid model:

- **Layer 1:** A Gierer-Meinhardt reaction-diffusion Turing field places star centers
  at quasi-regular spacing (short-range activation, long-range inhibition, Dh/Da=100).

- **Layer 2:** Active zooid agents with radial confinement, angular repulsion, and
  optional chirality (omega) self-organize into radial arms around those centers.

Adding chirality measurably rotates the arm pattern. The swirl score rises from near
zero to ~0.3 at omega=2.5. The arm structure is preserved.

A live Streamlit app lets you adjust parameters, run simulations, and explore the
phase diagram. A Jupyter notebook walks through every step from observation to conclusion.

---

## Quickstart

```
pip install -r requirements.txt
python healthcheck.py
streamlit run app.py
```

The healthcheck runs the full model pipeline and prints PASS in under 30 seconds.
The app opens at http://localhost:8501.

To regenerate all presentation assets (takes 15-30 minutes):

```
python scripts/05_make_all_assets.py
```

---

## Generated Outputs

| Path | Contents |
|---|---|
| `outputs/panels/` | 6 slide-ready PNG panels |
| `outputs/movies/` | 4 GIF animations of arm formation and chirality |
| `outputs/star_ascidian/` | Per-preset demo figures |
| `outputs/phase_diagrams/` | 4 parameter sweep heatmaps |
| `outputs/reference/` | 6 reference model figures (GM, GS, FHN, etc.) |
| `outputs/data/` | metrics CSV, phase diagram CSV, presets JSON |

---

## Repo Structure

```
src/chirality/
  star_ascidian/
    __init__.py           public API
    hybrid_model.py       two-layer combined model + 7 presets
    center_field.py       Layer 1: GM field + center extraction
    zooid_agents.py       Layer 2: active zooid agent dynamics
    metrics.py            7 quantitative metrics
    phase_diagram.py      4 parameter sweeps
    compare.py            target vs simulation comparison figures
    target.py             biological target reference data
  model_library/
    gierer_meinhardt.py   GM reference model
    gray_scott.py         Gray-Scott reference model
    fisher_kpp.py         Fisher-KPP reference model
    cahn_hilliard.py      Cahn-Hilliard reference model
    fitzhugh_nagumo.py    FitzHugh-Nagumo reference model
    active_particles.py   ABP, chiral ABP, Vicsek
  visualization/
    style.py              palette constants, matplotlib style
    plots.py              field and particle plots
    panels.py             slide panel generators
    animations.py         GIF and PNG frame output

scripts/
  01_run_reference_models.py
  02_run_star_ascidian_demo.py
  03_run_phase_diagram.py
  04_make_movies.py
  05_make_all_assets.py
  06_final_smoke_test.py

notebooks/
  Star_Ascidian_Chirality_Atlas.ipynb   12-section runnable notebook
  Chirality_Atlas_Colab.ipynb           legacy particle/pattern notebook

docs/
  project_brief.md         30-second summary
  model_notes.md           equation quick reference
  star_ascidian_model_notes.md  full model derivation
  tutorial_mapping.md      how each resource maps to the project
  llm_proficiency.md       full LLM workflow documentation
  prompt_log.md            6 rounds of prompt-run-test-modify-critique
  scientific_audit.md      equation audit, metric audit, sanity checks
  final_5_slide_deck.md    exact slide content
  speaker_script.md        5-minute timed script
  demo_script.md           2-minute live app walk-through
  judge_readme.md          this file for judges
  limitations.md           honest capability boundaries
  asset_manifest.md        all output files with slide assignments
  final_readiness_report.md pre-hackathon status report
  ui_design_notes.md       Streamlit app design decisions
  deployment_local.md      local setup instructions
  deployment_huggingface.md Hugging Face Spaces Docker deployment

assets/
  style.css
  logo.svg
  favicon.svg

app.py                     Streamlit entry point
healthcheck.py             fast model verification
Dockerfile                 Hugging Face Spaces container
requirements.txt
```

---

## Model Overview

### Layer 1: Gierer-Meinhardt Field

Turing instability in two chemical species. Short-range activation, long-range inhibition.

    da/dt = Da * lap(a) + rho * a^2 / (h * (1 + kappa*a^2)) - mu_a * a + rho_0
    dh/dt = Dh * lap(h) + rho * a^2 - mu_h * h

Numerical scheme: IMEX (implicit diffusion, explicit reaction). Fourier space.
Unconditionally stable for diffusion term. Default Dh/Da = 100.

### Layer 2: Active Zooid Agents

N active self-propelled particles with five force contributions:

    dx/dt = v0*cos(theta) + F_attract + F_radial + F_angular + F_ev
    dtheta/dt = omega_i + sqrt(2*Dr) * xi(t)

Angular repulsion (the key creative force):

    For pairs from different arm groups at the same center:
    F = -k_angular * (1 - |dphi|/sigma_angular) * sign(dphi) * t_hat

This converts a ring of agents into discrete arms with even angular spacing.

### Presets

| Preset | omega | Dr | Phase |
|---|---|---|---|
| clean_star_systems | 0.0 | 0.04 | Clean radial stars |
| chiral_twisted_stars | 2.5 | 0.04 | Twisted arms |
| racemic_mixed | 2.5 mixed | 0.04 | Mixed handedness |
| overcrowded_merged_systems | 0.0 | 0.04 | Stars merging |
| noisy_fragmented_systems | 0.0 | 0.9 | Agents escape |
| boundary_pinned_stars | 0.0 | 0.04 | Box boundary |
| weak_inhibition_uniform_mat | 0.0 | 0.04 | No Turing spots |

---

## Final Deliverables

| File | Purpose |
|---|---|
| `app.py` | Live interactive demo |
| `notebooks/Star_Ascidian_Chirality_Atlas.ipynb` | Full walkthrough notebook |
| `outputs/panels/slide*.png` | 5-slide deck visuals |
| `outputs/movies/*.gif` | Animation visuals |
| `docs/llm_proficiency.md` | LLM workflow documentation |
| `docs/scientific_audit.md` | Scientific claims audit |

---

## Limitations

- Arm count (n_arms=7) is a model parameter, not emergent from the physics.
- Arm count detection metric under-counts at low agent density (3 agents per arm).
  Use radial_order as the primary quality metric.
- No Botryllus biochemistry, signaling molecules, blastogenic timing, or 3D geometry.
- Phase diagram computed at reduced resolution (N=32, n_steps=150) for speed.
- O(N^2) excluded volume; not suitable for N > ~500 agents.

See `docs/limitations.md` and `docs/scientific_audit.md` for full audit.

---

## Deployment

### Local

```
python -m venv .venv
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
python healthcheck.py
streamlit run app.py
```

### Docker

```
docker build -t chirality-atlas-star .
docker run -p 7860:7860 chirality-atlas-star
```

### Hugging Face Spaces

See `docs/deployment_huggingface.md`.
Push the repo to a Hugging Face Space with Docker SDK and port 7860.
