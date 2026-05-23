# Demo Script: Chirality Atlas -- 2-Minute Live App Walk-through

---

## Before you start

Have these open and ready:
- Terminal with `streamlit run app.py` already running at http://localhost:8501
- Browser tab on the Overview tab
- Backup: `outputs/` directory open in file explorer
- Backup GIF: `outputs/videos/particle_boundary_edge_current.gif` in a browser tab

---

## 2-minute flow (exact tabs and clicks)

### 0:00 -- Overview tab (20 sec)

Open the Overview tab.
Point to the title and say:
"The question: can microscopic handedness change collective behavior?
The app has two simulation tracks and a bridge between them."

Scroll down to show the summary figure.

---

### 0:20 -- Particle Lab (35 sec)

Click the Particle Lab tab.

In the sidebar (or preset dropdown), select "Chiral Vortex Gas."
Click Run Full Simulation.
While it runs (about 10 seconds):
"This model extends the Tutorial 1 ABP -- we just added omega*dt to the orientation update."

When it finishes:
Point to the snapshot.
"Green particles are right-handed -- they trace circles. The swirl index is nonzero.
Now watch what happens at a circular boundary."

Change preset to "Boundary Edge Current." Click Run.
"Particles accumulate on the wall and orbit. That is the edge current."

---

### 0:55 -- Pattern Lab (25 sec)

Click the Pattern Lab tab.

Select "Gray-Scott Spots." Click Run.
"This is the Tutorial 2 baseline -- spots at F=0.035, k=0.065."

Change to "Chiral Source." Click Run.
"This one has a rotating injection point. It looks similar, but the field is slightly asymmetric left-right. Small effect, but reproducible with fixed seeds."

---

### 1:20 -- Phase Atlas (25 sec)

Click the Phase Atlas tab.

Show the polar order heatmap.
"Low noise and zero chirality: disordered gas. Add chirality: still disordered, but for a different reason. The swirl diagram tells a different story."

Click to the Gray-Scott F-k heatmap.
"This is the spot/labyrinth transition region from the tutorial. Pattern strength peaks where the tutorial predicts spots."

---

### 1:45 -- Bridge Lab (15 sec)

Click the Bridge Lab tab.
"Both models show the same thing: a small change at the local level -- one extra parameter -- reshapes what the system does at the collective level. That is what we mean by chirality as a control knob."

End demo.

---

## Backup plan if app fails

If Streamlit is not loading or is slow:

1. Open `outputs/demo/` in a file browser. Show:
   - `particle_boundary_edge_current.png`
   - `particle_racemic_competition.png`
   - `pattern_chiral_source.png`
   - `pattern_obstacle_disrupted.png`

2. Play GIF directly in browser:
   - `outputs/videos/particle_boundary_edge_current.gif`
   - `outputs/videos/particle_chiral_vortex.gif`

3. Show phase diagrams:
   - `outputs/phase_sweeps/particle_noise_vs_chirality_polar_order.png`
   - `outputs/phase_sweeps/particle_noise_vs_chirality_swirl_index.png`

4. Show summary panels:
   - `outputs/summary/chirality_atlas_bridge_panel.png`
   - `outputs/summary/chirality_atlas_final_panel.png`

All these can be opened in a browser or image viewer without any running code.

---

## Timing notes

- Full simulation for chiral presets: ~5-10 sec in Particle Lab (N=200, 800-1000 steps)
- Full simulation for Gray-Scott 256x256 presets: ~30-60 sec in Pattern Lab
- Phase sweeps in Phase Atlas: precomputed at startup if cached, else ~30 sec for 6x6 grid

If the audience is watching live pattern simulations, say:
"The 256x256 Gray-Scott takes about a minute. While it runs -- let me show the phase diagram."
