# Tutorial Connections

This document maps each element of the Chirality Atlas to its origin in the two organizer tutorials.

---

## Tutorial 1: Active Matter

### Random walks and ABP

The tutorial introduces NumPy-based random walks and active Brownian particles.

This project extends that directly: `simulate_abp` in `particle_sim.py` is the tutorial ABP, implemented as a loop over time steps with vectorized position and orientation updates. The extension is `simulate_chiral_abp`, which adds a deterministic rotation `omega * dt` to the orientation update. This is the minimal change needed to go from a standard ABP to a chiral swimmer.

### Periodic boundary conditions

The tutorial shows how to wrap positions modulo L. The project uses this in `_apply_periodic`. Two additional boundary modes (`reflective` and `circular_trap`) are new extensions.

### Vicsek flocking

The tutorial implements the Vicsek model with local alignment and angular noise. `simulate_vicsek_chiral` extends this with:
- Vectorized minimum-image distance computation (no Python loops over pairs)
- An optional `omega * dt` chirality term appended to the alignment step

### Minimum-image convention

The tutorial uses minimum-image for distances. `_minimum_image_dist2` computes the full (N x N) pairwise distance matrix using `np.round` wrapping, consistent with the tutorial approach.

### Polar order parameter

The tutorial measures flocking via `phi = |mean(exp(i * theta))|`. `polar_order` in `particle_metrics.py` is this exact formula. `polar_order_timeseries` tracks it over time.

### Mean squared displacement

The tutorial introduces MSD as a measure of particle transport. `mean_squared_displacement` in `particle_metrics.py` computes displacement from the initial snapshot.

### Neighbor count clustering

The tutorial counts neighbors within a radius. `average_neighbor_count` extends this, and `cluster_count` uses union-find to detect connected clusters.

### One-parameter and two-parameter phase diagrams

The tutorial constructs phase diagrams by sweeping parameters. `phase_sweeps.py` does this systematically for:
- Dr (noise) vs omega (chirality): 2D heatmap of polar_order and swirl_index
- eta (noise) vs omega (chirality) for Vicsek: same structure

### Mini-challenge: chirality

The tutorial explicitly lists chirality as a mini-challenge. `simulate_chiral_abp` with chirality modes (none, left, right, racemic, random) is the direct response to this challenge.

---

## Tutorial 2: Pattern Formation

### 2D fields as images

The tutorial represents fields as 2D NumPy arrays displayed with `imshow`. The project uses this everywhere for `u` and `v` fields.

### Diffusion

`run_diffusion` is the tutorial diffusion-only stepping: `f += D * dt * laplacian(f)`.

### Logistic growth

`run_logistic_growth` is the tutorial local growth without diffusion: `f += r * f * (1 - f/K) * dt`.

### Reaction-diffusion

`run_reaction_diffusion_one_field` combines these: growth + diffusion for a single scalar field.

### Gray-Scott model

`gray_scott_step` implements the standard two-field Gray-Scott update verbatim from the tutorial:

    u_new = u + dt * (Du * lap(u) - u*v^2 + F*(1-u))
    v_new = v + dt * (Dv * lap(v) + u*v^2 - (F+k)*v)

`initialize_gray_scott` creates the tutorial initial condition: u=1, v=0 everywhere except a small central square where u~0.5 and v~0.25.

### Feed and kill parameters

The tutorial shows how F and k control the pattern type. `sweep_gray_scott_F_k` generates the classic 2D phase diagram over these parameters.

### Pattern strength and cluster counting

`pattern_strength(v) = std(v)` is the tutorial pattern strength metric. `count_clusters` is the threshold-then-label approach from the tutorial.

### Feed gradient

`simulate_feed_gradient` extends the tutorial gradient model: F varies linearly from F_left to F_right across x, creating a transition from one pattern regime to another.

### Circular obstacle

`simulate_obstacle` extends the tutorial obstacle: a circular region where u=1 and v=0 is enforced at each step.

### Phase diagrams over F and k

`sweep_gray_scott_F_k` generates a 6x6 (or configurable) grid of F and k values, runs a short simulation at each point, and returns pattern_strength and cluster_count grids. This is the tutorial phase diagram exercise, automated and visualized as a heatmap.

### Mini-challenge: chirality, modify the model, measure one result

`simulate_chiral_source_gray_scott` is the mini-challenge response:
- Modification: add a rotating Gaussian source of v to the Gray-Scott update
- Measure: left-right asymmetry (`field_asymmetry`)
- Interpret: a chiral source can induce a small but detectable asymmetry in the pattern, showing that local symmetry breaking propagates to macroscopic pattern structure

---

## New metrics introduced

Beyond the tutorial metrics, the project adds:

- `swirl_index`: angular momentum proxy for particle simulations, detects circular collective motion
- `boundary_accumulation`: fraction of particles near walls, detects edge currents
- `field_asymmetry`: left-right difference in mean v, detects chiral bias in patterns
- `radial_asymmetry`: top-bottom vs left-right comparison

---

## LLM workflow documentation

See `docs/prompt_log.md` for the prompt-run-test-modify-critique workflow used to develop each simulation.
