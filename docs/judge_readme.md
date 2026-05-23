# For Judges: Chirality Atlas

## 30-second summary

Chirality Atlas extends both hackathon tutorials (active particles and Gray-Scott reaction-diffusion)
by adding a chirality parameter omega that gives simulated agents a left or right rotational bias.
The project asks whether this microscopic handedness can change collective behavior,
builds phase diagrams showing it does, and provides a live Streamlit app to explore the results.

---

## How it extends the tutorials

**Tutorial 1 (active particles):**

| Tutorial baseline | This project's extension |
|-------------------|--------------------------|
| Active Brownian Particles (ABP) | Chiral ABP: add `omega_i * dt` to orientation |
| Vicsek alignment model | Chiral Vicsek: omega competes with alignment |
| Polar order parameter phi | + swirl index, boundary accumulation |
| Single parameter run | Phase diagram over Dr x omega |

**Tutorial 2 (Gray-Scott reaction-diffusion):**

| Tutorial baseline | This project's extension |
|-------------------|--------------------------|
| Gray-Scott spots and labyrinths | Same + gradient, obstacle, chiral source |
| Vary F and k | Phase diagram over F x k + chiral source sweep |
| Plot v field | + pattern strength, cluster count, L-R asymmetry |
| Single seed initialization | Multi-seed for full domain coverage |

---

## What was reproduced

- ABP baseline: polar order near 0.05 (disordered gas). Expected.
- Vicsek at low noise: polar order 0.95 (flocked). Expected.
- Gray-Scott at F=0.035, k=0.065: spots with pattern strength ~0.10. Expected.
- Gray-Scott at F=0.04, k=0.06: labyrinth morphology. Expected.
- Phase diagram trends consistent with known literature.

---

## What was creatively extended

- Chiral Vortex Gas: single-handed omega creates circular trajectories. New metric (swirl index) captures this.
- Boundary Edge Current: chiral particles in a circular trap orbit the wall. Directly analogous to bacterial near-surface swimming.
- Racemic Competition: 50/50 left/right mixture with soft repulsion. Control case: net swirl near zero.
- Feed Gradient: linear spatial variation of F. Pattern transitions across the domain.
- Circular Obstacle: topological defect in spot pattern.
- Chiral Source (toy model): rotating injection point breaks L-R symmetry. Small but measurable asymmetry.

---

## What to run

Quick check (under 1 minute):
```
python scripts/smoke_test.py
```

Interactive app:
```
streamlit run app.py
```

Generate all figures (30-50 minutes):
```
python scripts/make_all_assets.py
```

---

## What to look at first

1. `outputs/summary/chirality_atlas_bridge_panel.png` -- both tracks side by side
2. `outputs/summary/chirality_atlas_final_panel.png` -- hero figure with key results
3. `outputs/phase_sweeps/particle_noise_vs_chirality_swirl_index.png` -- shows chirality creates swirl
4. `outputs/phase_sweeps/pattern_chiral_source_asymmetry.png` -- shows source rotation -> L-R asymmetry
5. `outputs/videos/particle_boundary_edge_current.gif` -- most visually striking result

---

## Limitations (honestly stated)

- Chiral source is a toy model: no biological mechanism is claimed
- Phase diagrams are coarse (6x6 grid, short runs)
- Euler integration: stable for given parameters but not validated near instability boundaries
- O(N^2) soft repulsion: not suitable for N > 500
- Swirl index values are small in short simulations
- ABP chirality is phenomenological; no connection to specific microswimmer parameters

See `docs/limitations.md` and `docs/self_audit.md` for a complete list.
