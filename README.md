# Chirality Atlas: Particles, Patterns, and Handedness in Active Matter

UCSD Vibe Coding Active Matter 2026 Hackathon

---

## What it is

This project unifies two computational tracks around a single scientific question:
**can microscopic handedness act as a control knob for macroscopic biological order?**

Track 1 -- particles: Active Brownian Particles and Vicsek-style flocking, extended
with per-particle chirality. Chiral particles trace circles, accumulate at boundaries,
and form edge currents. The transition between ordered and disordered states changes
qualitatively when you add a rotation rate.

Track 2 -- patterns: Gray-Scott reaction-diffusion, extended with a linear feed
gradient, a circular obstacle, and a rotating point source (the "chiral source").
The chiral source introduces handedness into an otherwise symmetric pattern-forming system,
producing a small but detectable left-right asymmetry.

Both tracks are direct extensions of the organizer tutorials. See `docs/tutorial_connections.md`
for a line-by-line mapping.

---

## Why it fits the hackathon

The hackathon asks participants to extend the tutorials by adding chirality, measuring
something, and interpreting the result. This project does exactly that, twice -- once
for each tutorial track -- and adds a systematic phase diagram sweep over the key parameters.

---

## Quickstart

```bash
git clone https://github.com/agentjakey/chirality.git
cd chirality
pip install -r requirements.txt
python scripts/smoke_test.py
```

If smoke_test.py prints `PASS: all checks passed.`, the installation is working.

### Interactive UI

```bash
streamlit run app.py
```

Opens a browser at `http://localhost:8501` with the full Chirality Atlas interface.

---

## What runs where

### Local (laptop)

```bash
# Particle demos (~1-2 min)
python scripts/run_particle_demo.py

# Pattern demos (~5-10 min)
python scripts/run_pattern_demo.py

# Phase sweeps (~10-20 min)
python scripts/run_phase_sweeps.py

# Animations (~3-5 min)
python scripts/make_video.py

# Everything at once
python scripts/make_all_assets.py
```

All output goes to `outputs/`. Nothing large is committed.

### Colab

Open `notebooks/Chirality_Atlas_Colab.ipynb` in Google Colab or Jupyter.

The notebook has 11 parts and is designed to be run top-to-bottom:
1. Setup (install + import)
2. The question (active matter, pattern formation, chirality)
3. Particle model baseline (ABP)
4. Add chirality to particles (chiral ABP, edge current)
5. Vicsek alignment (order parameter, sanity check)
6. Particle phase diagram (noise vs chirality)
7. Pattern formation baseline (Gray-Scott spots and labyrinths)
8. Pattern phase diagram (F vs k)
9. Creative hacks (feed gradient, obstacle, chiral source)
10. Bridge (side-by-side comparison of both tracks)
11. Mini-challenge template + hackathon slide checklist

**Estimated runtime in Colab**: 10-20 minutes for all cells.

All sweeps in the notebook use small grids (4x4) to keep Colab runtime reasonable.
Larger sweeps are in `scripts/run_phase_sweeps.py` (6x6).

---

## Generated outputs

| Path | Contents |
|------|----------|
| `outputs/demo/` | Particle snapshots, trail plots, pattern images |
| `outputs/phase_sweeps/` | Phase diagram heatmaps, sweep data .npz files |
| `outputs/videos/` | GIF animations of particle and pattern dynamics |

---

## How it extends the tutorials

**Tutorial 1 (particles):**
- `simulate_abp` is the tutorial ABP baseline
- `simulate_chiral_abp` adds `omega_i * dt` to the orientation update, with five chirality mode options
- `simulate_vicsek_chiral` adds chirality to the Vicsek alignment step
- `particle_metrics.py` extends the tutorial metrics with swirl index and boundary accumulation
- `phase_sweeps.py` automates the tutorial's one-parameter and two-parameter diagram exercises

**Tutorial 2 (patterns):**
- `simulate_gray_scott` is the tutorial Gray-Scott model
- `simulate_feed_gradient` extends the tutorial gradient exercise
- `simulate_obstacle` extends the tutorial circular obstacle exercise
- `simulate_chiral_source_gray_scott` adds a rotating point source (toy model, new)
- `pattern_metrics.py` extends tutorial metrics with left-right asymmetry and obstacle disruption score

---

## Source layout

```
src/chirality/
  __init__.py          -- public API
  config.py            -- parameter dataclasses
  particle_sim.py      -- ABP, chiral ABP, Vicsek
  particle_metrics.py  -- polar order, MSD, swirl, etc.
  pattern_sim.py       -- Gray-Scott, gradient, obstacle, chiral source
  pattern_metrics.py   -- pattern strength, cluster count, asymmetry
  phase_sweeps.py      -- systematic parameter sweeps
  plotting.py          -- all visualization
  presets.py           -- 10 named parameter sets
  export.py            -- save figures and arrays
  validation.py        -- finite-value checks
  storytelling.py      -- human-readable result summaries

scripts/
  smoke_test.py        -- fast correctness check
  run_particle_demo.py -- particle figures
  run_pattern_demo.py  -- pattern figures
  run_phase_sweeps.py  -- phase diagrams
  make_video.py        -- GIF animations
  make_all_assets.py   -- run everything

notebooks/
  Chirality_Atlas_Colab.ipynb

docs/
  science_notes.md     -- equations and physical interpretation
  tutorial_connections.md
  judge_readme.md
  final_5_slide_deck.md
  speaker_script.md
  demo_script.md
  prompt_log.md
  limitations.md
  self_audit.md
```

---

## Deployment

### Local

See `docs/deployment_local.md` for full instructions including virtual environment setup.

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Hugging Face Spaces (Docker)

See `docs/deployment_huggingface.md` for step-by-step instructions.

The repo includes a `Dockerfile` that runs Streamlit on port 7860.
Push to a Hugging Face Space with Docker SDK and the app deploys automatically.

```bash
docker build -t chirality-atlas .
docker run -p 7860:7860 chirality-atlas
```

No GPU required. No API keys. No external network calls.

---

## Scientific limitations

The chiral source for pattern formation is a toy model. It is not a model of any
specific biological mechanism. Real chiral symmetry breaking in development (e.g.,
left-right axis determination) involves specific signaling pathways and tissue-level
mechanics not captured here.

The particle chirality is phenomenological. Connecting omega to real microswimmer
parameters requires organism-specific measurement.

See `docs/limitations.md` for a complete list.

---

## Dependencies

```
numpy>=1.24
matplotlib>=3.7
scipy>=1.11
Pillow>=10.0
imageio>=2.31
streamlit>=1.30
```

No external APIs, no paid services, no large data files.
