# Baseline Audit: Chirality Atlas Repository

Audit date: 2026-05-23
Purpose: map existing repo against Star Ascidian Edition requirements.
Determines what to keep, what to remove, and what to build.

---

## What currently exists

### Python package: src/chirality/ (12 modules, ~2600 lines)

| File | Lines | Description |
|------|-------|-------------|
| __init__.py | 96 | Public API exports |
| config.py | 86 | ABP, Vicsek, Gray-Scott config dataclasses |
| particle_sim.py | 374 | ABP, chiral ABP, Vicsek simulations + boundary modes |
| particle_metrics.py | 177 | polar_order, swirl_index, MSD, clustering, boundary_accumulation |
| pattern_sim.py | 378 | Gray-Scott + feed gradient + obstacle + chiral source |
| pattern_metrics.py | 101 | pattern_strength, count_clusters, field_asymmetry |
| phase_sweeps.py | 265 | noise vs chirality sweep, Vicsek sweep, GS F-k sweep |
| plotting.py | 642 | All visualization functions, custom chirality colormap, summary panels |
| export.py | 124 | save_figure, GIF export, CSV export, sanity report |
| validation.py | 61 | all_finite_report |
| presets.py | 193 | 10 named parameter dicts (5 particle, 5 pattern) |
| storytelling.py | 120 | Human-readable metric summaries |

### Scripts: scripts/ (7 files, ~2170 lines)

| File | Lines | Role |
|------|-------|------|
| smoke_test.py | 279 | 27-check module validation |
| run_particle_demo.py | 120 | 5 particle snapshots |
| run_pattern_demo.py | 117 | 5 Gray-Scott snapshots |
| run_phase_sweeps.py | 228 | 7 phase diagrams + 3 CSV exports |
| make_video.py | 88 | 4 GIF animations |
| make_summary_panels.py | 203 | 4 presentation summary panels |
| make_all_assets.py | 62 | Orchestrates all above |
| _build_notebook.py | 1073 | Generates Colab notebook JSON |

### Application: app.py (1523 lines)

7-tab Streamlit application: Overview, Particle Lab, Pattern Lab, Bridge Lab,
Phase Atlas, Presentation Mode, Methods & Limits.
Uses session_state for simulation caching. CSS loaded from assets/style.css.
Heavy Gray-Scott content (tabs 3, 4 are pattern-focused).

### Notebooks: notebooks/

Chirality_Atlas_Colab.ipynb (39 cells, 11 parts)
Covers ABP, chiral ABP, Vicsek, Gray-Scott, 3 creative hacks, bridge section,
mini-challenge template, slide checklist.

### Docs: docs/ (13 files, ~1340 lines)

science_notes.md -- ABP + Gray-Scott equations, metrics, limitations
tutorial_connections.md -- mapping to two tutorial tracks
judge_readme.md, speaker_script.md, demo_script.md
final_5_slide_deck.md, final_readiness_report.md
self_audit.md -- scoring table + weakness analysis
ui_design_notes.md -- Streamlit design rationale
limitations.md -- model limitations
prompt_log.md -- LLM workflow documentation
deployment_local.md, deployment_huggingface.md
CLAUDE_CONTEXT.md -- this project's full brief (just created)
baseline_audit.md -- this file (just created)

### Assets: assets/

style.css -- warm notebook CSS (F7F3EA background, C15A3A accent, Georgia serif)
logo.svg -- 44x44 chirality orbit icon
favicon.svg -- 32x32 simplified icon

### Infrastructure

Dockerfile -- python:3.11-slim, port 7860, runs healthcheck then streamlit
.dockerignore -- excludes outputs/, notebooks/, docs/
healthcheck.py -- 5-check health validation
requirements.txt -- numpy, matplotlib, scipy, Pillow, imageio, streamlit
pyproject.toml -- package metadata
.gitignore -- outputs/ gitignored

### Generated outputs (gitignored)

outputs/demo/ -- 30 files (particle and pattern snapshots)
outputs/phase_sweeps/ -- 19 files (phase diagrams, .npz, .csv, sanity_check.txt)
outputs/videos/ -- 10 files (GIFs, some duplicate-named)
outputs/summary/ -- 4 summary panels
outputs/data/ -- 3 CSV files

---

## What to preserve (keep as-is or with minor edits)

### Keep verbatim

- `src/chirality/particle_sim.py`
  simulate_abp, simulate_chiral_abp, simulate_vicsek_chiral, ParticleHistory.
  The chiral ABP simulation is the exact zooid-particle implementation needed for Layer 2.
  boundary_mode="circular_trap" will be used for colony boundary experiments.
  No changes needed.

- `src/chirality/particle_metrics.py`
  polar_order, swirl_index, boundary_accumulation, average_neighbor_count, MSD.
  All of these are reused in the star model:
  swirl_index -> used directly for swirl score around each center
  average_neighbor_count -> used for occupation density
  polar_order -> sanity check for arm alignment
  New star-specific metrics (arm_count, radial_order, star_likeness) go in star_metrics.py.

- `src/chirality/export.py`
  save_figure, save_frames_as_gif, save_frame_sequence, save_sweep_csv, save_sanity_report.
  All used unchanged.

- `src/chirality/validation.py`
  all_finite_report used by healthcheck.

- `assets/style.css`
  Color palette (#F7F3EA, #C15A3A, #315C4C) is specified in the design brief.
  Keep exactly as-is.

- `assets/logo.svg`, `assets/favicon.svg`
  Chirality orbit motif is still thematically correct. Keep.

- `Dockerfile`, `.dockerignore`
  Infrastructure is correct. Update CMD if app.py filename changes, else keep.

- `requirements.txt`
  scipy needed for GM simulation laplacian and signal.find_peaks.
  No new dependencies required (GM uses numpy, scipy.ndimage for spot detection).

- `pyproject.toml`, `.gitignore`
  Keep as-is.

### Keep with targeted edits

- `src/chirality/plotting.py`
  Keep: color conventions, _CHIRALITY_CMAP, _style_dark_ax/_style_light_ax,
  plot_particle_snapshot, plot_trajectory_trails, render_particle_frame,
  make_particle_frames, render_field_frame, make_field_frames, plot_phase_diagram,
  plot_combined_summary.
  Remove: make_particle_summary_panel, make_pattern_summary_panel (replace with star versions).
  Add: plot_gm_field, plot_star_colony, plot_star_metric_panel, make_star_summary_panel,
  make_final_star_panel.

- `src/chirality/config.py`
  Keep: ABPConfig, ChiralABPConfig, VicsekConfig.
  Remove: GrayScottConfig, FeedGradientConfig, ObstacleConfig, ChiralSourceConfig.
  Add: GiererMeinhardtConfig, StarSimConfig (zooid particle + GM combined).

- `src/chirality/presets.py`
  Remove all pattern presets (GRAY_SCOTT_*, FEED_GRADIENT_PATTERN, etc.).
  Keep: BASELINE_ACTIVE_BROWNIAN, VICSEK_FLOCKING as reference baselines.
  Add: GM_SPOT_FORMATION, STAR_CLEAN, STAR_CHIRAL_TWIST, STAR_RACEMIC,
  STAR_OVERCROWDED, STAR_BOUNDARY, STAR_DEFECT_PINNED.

- `src/chirality/phase_sweeps.py`
  Keep: sweep_noise_vs_chirality (reused directly for zooid layer).
  Remove: sweep_vicsek_eta_vs_chirality, sweep_gray_scott_F_k, sweep_chiral_source.
  Add: sweep_gm_diffusion_ratio, sweep_star_chirality_vs_attraction,
  sweep_star_particles_vs_noise.

- `src/chirality/storytelling.py`
  Remove Gray-Scott summary functions.
  Keep particle summary structure.
  Add: summarize_star_metrics(metrics, label).

- `src/chirality/__init__.py`
  Remove all Gray-Scott exports.
  Add new module exports (gm_sim, gm_metrics, star_sim, star_metrics).

- `src/chirality/validation.py`
  Keep all_finite_report.
  No other changes needed.

- `healthcheck.py`
  Replace Gray-Scott simulation check with GM simulation check.
  Replace pattern_strength check with star_likeness check.

- `scripts/smoke_test.py`
  Keep structure (section-by-section PASS/FAIL checks).
  Remove Gray-Scott tests.
  Add GM and star simulation tests.

- `scripts/make_all_assets.py`
  Update script list (new script names).

### Keep for reference, do not run

- `docs/science_notes.md` -- reference for ABP equations, keep, update to add GM equations
- `docs/limitations.md` -- keep, update for new model
- `docs/prompt_log.md` -- keep as template, add new entries

---

## What to remove (don't carry forward into new build)

### Remove entirely (modules not needed in new model)

- `src/chirality/pattern_sim.py`
  Gray-Scott, feed gradient, obstacle, chiral source Gray-Scott.
  Replaced by gm_sim.py.
  Do not delete yet (may break __init__.py imports during transition).
  Remove from __init__.py exports and presets.py references.
  Archive or delete once new modules pass smoke test.

- `src/chirality/pattern_metrics.py`
  pattern_strength, count_clusters, field_asymmetry, obstacle_disruption_score.
  None of these apply to the new star model.
  Replace with gm_metrics.py and star_metrics.py.

### Remove scripts (replaced by new versions)

- `scripts/run_pattern_demo.py` -- not applicable
- `scripts/_build_notebook.py` -- replaced by new notebook builder
- `scripts/make_summary_panels.py` -- replaced by new panel builder
- `scripts/run_particle_demo.py` -- replaced by run_star_demo.py (broader scope)
- `scripts/run_phase_sweeps.py` -- replaced by run_star_sweeps.py

### Remove docs (outdated)

- `docs/final_5_slide_deck.md` -- completely rewrite for star ascidian pitch
- `docs/speaker_script.md` -- completely rewrite
- `docs/demo_script.md` -- completely rewrite
- `docs/judge_readme.md` -- completely rewrite
- `docs/final_readiness_report.md` -- will regenerate at end
- `docs/ui_design_notes.md` -- update when app is rewritten
- `docs/tutorial_connections.md` -- update to map to new tutorial connections

### Remove from app.py

- The Pattern Lab tab (Gray-Scott content)
- The Bridge Lab tab (old bridge)
- Presentation Mode tab (old slides)
- All Gray-Scott presets and related session_state logic

### Do NOT delete outputs/

Outputs are gitignored and not committed. Safe to leave.

---

## What to build from scratch

### New modules (must be written)

**src/chirality/gm_sim.py** (~250 lines)
- GiererMeinhardtConfig parameters
- initialize_gm: set up a field near a uniform steady state + small perturbation
- gm_step: one explicit Euler step with saturation
- simulate_gm: run for n_steps, return FieldHistory-compatible object
- extract_spot_positions: find local maxima in a-field using scipy.ndimage
- Boundary conditions: periodic (default), reflective (for boundary experiment)
- Must be stable for standard parameters (Da=0.05, Dh=1.0, rho=1.0, mu_a=1.0, mu_h=1.0, kappa=0.1)

**src/chirality/gm_metrics.py** (~100 lines)
- spot_count(a_field): count spots above threshold
- spot_spacing(positions): mean nearest-neighbor distance between spots
- field_uniformity(a_field): how smooth (low = patterned, high = uniform)
- activation_peak_height(a_field): max(a) - mean(a)

**src/chirality/star_sim.py** (~350 lines)
- StarHistory dataclass: positions, thetas, omegas, center_assignments, times, L, centers
- assign_centers(positions, centers): for each particle, index of nearest center
- angular_repulsion_forces: for each center, push same-center particles apart tangentially
- center_attraction_force: pull particle toward its center at r_target
- simulate_star: GM field + particle dynamics combined
  - Run GM to find centers
  - Initialize N_per_center particles per center in a ring
  - Evolve particles with: self-propulsion + center attraction + angular repulsion +
    excluded volume + chirality + noise
  - Return StarHistory
- StarHistory should store center positions for plotting

**src/chirality/star_metrics.py** (~200 lines)
- compute_arm_count(positions, center, r_target, r_tol=0.3, min_separation_deg=20):
  count angular clusters of particles near the center at approximately r_target
- compute_radial_order(positions, center, r_target, r_tol=0.3):
  fraction of particles within [r_target*(1-r_tol), r_target*(1+r_tol)]
- compute_angular_uniformity(arm_angles):
  1 - circular_variance(inter-arm-angle differences)
- compute_star_likeness(positions, center, r_target, n_arms_target):
  composite of radial_order and angular_uniformity, normalized to [0, 1]
- compute_colony_swirl(positions, thetas, centers):
  mean signed angular momentum of particles around their assigned center
- compute_all_star_metrics(star_hist):
  returns dict with per-center and colony-level metrics

**src/chirality/phase_sweeps.py** (rewrite)
- sweep_gm_diffusion_ratio(ratio_values, mu_h_values, ...):
  maps D_h/D_a and mu_h -> spot_count, spot_spacing
- sweep_star_chirality_vs_attraction(omega_values, k_attract_values, ...):
  maps omega x k_attract -> star_likeness, swirl
- sweep_star_particles_vs_noise(n_per_center_values, Dr_values, ...):
  maps occupation x noise -> arm_count, radial_order

### New scripts (must be written)

**scripts/run_gm_demo.py**
- Run 5 GM parameter sets showing different spot regimes
- Save field images to outputs/field/

**scripts/run_star_demo.py**
- Run 5-7 star presets covering: clean stars, chiral twist, overcrowded,
  fragmented, boundary-biased, defect-pinned
- Save combined field+particle images to outputs/star/

**scripts/run_star_sweeps.py**
- Run 3 phase sweeps (see above)
- Save diagrams to outputs/phase/
- Save CSVs to outputs/data/
- Write sanity_check.txt

**scripts/make_star_video.py**
- 3 GIF animations: GM formation, star self-organization, chiral twist dynamics

**scripts/make_summary_panels.py** (rewrite)
- chirality_atlas_star_panel.png: colony overview
- chirality_atlas_phase_panel.png: key phase diagrams
- chirality_atlas_comparison_panel.png: target vs simulation
- chirality_atlas_final_panel.png: hero figure

### New notebook

**notebooks/Star_Ascidian_Colab.ipynb**
Sections:
0. Setup
1. The biological target (Botryllus schlosseri star patterns)
2. Layer 1: Gierer-Meinhardt field (activator-inhibitor spots)
3. Layer 2: Zooid-like particles (attraction + angular repulsion + chirality)
4. Combined model: star colony formation
5. Phase diagram: D_h/D_a vs spot count
6. Phase diagram: omega vs attraction -> star-likeness and swirl
7. Creative exploration: boundary effects, defect pinning, racemic mixture
8. Comparison to target image
9. LLM prompts that made a difference
10. Mini-challenge template
11. Hackathon checklist + limitations

### New app (major rewrite of app.py)

Tabs:
1. Overview: star ascidian target image, model summary, key result
2. Field Lab: GM field interactive explorer (Da, Dh, mu_a, mu_h, n_steps)
3. Star Lab: full combined model (omega, k_attract, Dr, N_per_center)
4. Phase Atlas: interactive phase diagrams
5. Presentation Mode: 5-slide deck view
6. Model & Limits: equations, limitations, LLM log

---

## Build order

1. gm_sim.py + gm_metrics.py (field layer, can be tested standalone)
2. star_sim.py + star_metrics.py (particle layer, depends on gm for center positions)
3. Update config.py, presets.py, storytelling.py
4. Update plotting.py (add star visualization functions)
5. Update phase_sweeps.py (new sweep functions)
6. Update __init__.py (remove pattern_sim, add new modules)
7. Rewrite smoke_test.py
8. Rewrite scripts (run_gm_demo, run_star_demo, run_star_sweeps, make_star_video)
9. Rewrite make_summary_panels.py
10. Generate all outputs
11. Rewrite app.py (Streamlit)
12. Write Star_Ascidian_Colab.ipynb
13. Update docs (science_notes, judge_readme, speaker_script, etc.)
14. Update healthcheck.py
15. Final smoke_test + healthcheck pass

---

## Risk assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| GM field does not produce clean spots | Medium | Use validated parameters from Gierer-Meinhardt 1972 paper; saturation term prevents blow-up |
| Particles don't form arms | Medium | Angular repulsion force is the key; test with 2-3 particles per center first |
| Star-likeness metric too noisy | Low | Use peak-finding with min_distance constraint; test on synthetic arm configurations first |
| Phase diagrams too coarse | Low | Use 4x4 for Colab speed; note on all figures |
| GM runtime too slow | Low | 128x128 with 5000 steps at dt=0.05 is ~10 sec; smaller grids for sweeps |
| Arm count systematically off | Medium | n_arms is approximately correct for toy model; don't claim n_arms=7 as exact Botryllus match |

---

## What makes this scientifically defensible

1. Gierer-Meinhardt is a well-studied, citable model (Gierer and Meinhardt 1972).
   Its spot-forming behavior in the relevant parameter regime is established.

2. Chiral ABP with center attraction is a reasonable toy for zooid-like particles.
   The mechanism (self-propulsion + radial confinement + angular repulsion) produces
   arm-like structures that are physically plausible.

3. The metrics are computed from the simulation, not hand-tuned to match the target.

4. The comparison to Botryllus is visual and qualitative, not quantitative.
   We do not claim to match specific arm lengths, zooid counts, or growth rates.

5. All limitations are listed explicitly in docs and on the final slide.
