# Prompt Log: Responsible LLM Use

This document records the LLM-assisted workflow used to develop the Chirality Atlas,
following the prompt-run-test-modify-critique cycle from the organizer tutorials.

---

## Round 1: ABP baseline

**Prompt**: "Write a NumPy simulation of N active Brownian particles in a periodic box.
Each particle has position (x,y) and orientation theta. At each step, update theta with
rotational noise sqrt(2*Dr*dt) * xi, then move x += v0*cos(theta)*dt, y += v0*sin(theta)*dt.
Return position and orientation history as numpy arrays."

**Run/Test**: Ran with N=50, checked positions stayed in [0,L], verified polar order near 0
for high noise (Dr=3.0) and near 0 for low noise without alignment (expected -- ABP has
no alignment interaction).

**Critique**: No issues. Code was clean and matched tutorial formula.

---

## Round 2: Adding chirality to ABP

**Prompt**: "Extend the ABP simulation to include per-particle rotation rates omega_i.
The orientation update becomes: theta += omega_i * dt + sqrt(2*Dr*dt) * xi.
Support four assignment modes: all omega_i = +omega (right), all omega_i = -omega (left),
half-half (racemic), and random from N(0, omega)."

**Run/Test**: Ran chiral_mode="right" with omega=2.0, Dr=0.2. Verified swirl_index
was significantly negative (clockwise in my convention). Checked racemic mode produced
near-zero net swirl. Verified all positions finite.

**Modify**: Added "none" mode (omega=0 everywhere) to allow direct comparison with
the plain ABP. Also added optional soft repulsion after running a test that showed
racemic particles clump without it.

**Critique**: Swirl index sign convention needed documentation. Noted that MSD
with periodic boundaries is misleading for chiral particles that circle -- added
a comment in science_notes.md.

---

## Round 3: Vicsek with chirality

**Prompt**: "Extend the Vicsek model with an omega*dt chirality term. Use vectorized
minimum-image convention for pairwise distances. The alignment step is atan2 of the
sum of sin/cos of neighbor headings."

**Run/Test**: Ran with eta=0.15 (should produce high order, phi~0.9+). Confirmed.
Ran with eta=0.5 (should produce low order). Confirmed. Added omega=1.0 and verified
swirl index became nonzero.

**Critique**: The vectorized distance computation is O(N^2) memory. Fine for N<=400
but noted as a scaling limitation. Would need kd-tree or cell-list for N > 1000.

---

## Round 4: Gray-Scott baseline

**Prompt**: "Implement the Gray-Scott reaction-diffusion model with periodic Laplacian.
Use the standard update: u_new = u + dt*(Du*lap(u) - u*v^2 + F*(1-u)).
Start with u=1, v=0 except a small central square."

**Run/Test**: Ran with F=0.035, k=0.065 for 5000 steps on 256x256. Got spots.
Ran with F=0.04, k=0.06. Got labyrinths. Verified u+v stays physically reasonable.

**Critique**: Needed to add hard clipping to [0,1] after each step to prevent occasional
numerical runaway. Added np.clip.

---

## Round 5: Gray-Scott extensions

**Prompt**: "Extend Gray-Scott with: (1) linear feed gradient F(x) = F_left + (F_right-F_left)*x/L,
(2) circular obstacle where u=1, v=0 is reset inside a circle each step."

**Run/Test**: Feed gradient produced clear phase boundary visible in the v field.
Obstacle produced a clean void in the pattern with defects at the boundary.

**Modify**: Added `perturbation_size` parameter to control the initial seed size,
which affects how many distinct pattern nuclei form.

**Critique**: No issues. Both extensions work as expected from the tutorial.

---

## Round 6: Chiral source (creative extension)

**Prompt**: "Add a rotating Gaussian source of v-species to the Gray-Scott update.
The focal point orbits the box center at angular speed source_omega. Measure
left-right asymmetry of the resulting v field."

**Run/Test**: Ran static Gray-Scott vs. chiral source version. The asymmetry metric
was nonzero but small (~0.001-0.003). Confirmed it scales with source_strength.

**Modify**: Reduced default source_strength to avoid dominating the self-organized pattern.
The goal is to nudge, not overwhelm.

**Critique**: The asymmetry is subtle and may not be visually obvious. Added
field_asymmetry metric and noted the toy-model nature prominently in docs.

---

## Round 7: Phase sweeps

**Prompt**: "Write a function that sweeps noise and chirality over a grid, runs a
short simulation at each point, and returns 2D metric arrays."

**Run/Test**: Ran 6x6 sweep with N=80, 200 steps. Runtime ~30s on laptop. Acceptable.

**Modify**: Added save_every=n_steps to only save the final state during sweeps
(saves memory, speeds up slightly). Added verbose progress printing.

**Critique**: The sweep results are noisy due to short run times. Production figures
use n_steps=300. Added note in run_phase_sweeps.py about the tradeoff.

---

## Summary of AI-assisted components

All core simulation equations were written against the tutorial formulas with direct
verification against expected physical behavior. The LLM was used for:
- Vectorizing the Vicsek distance computation
- Generating the phase sweep loops
- Drafting the plotting functions
- Writing the docs

All outputs were verified to be numerically finite and physically sensible before
committing.
