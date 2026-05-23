# Prompt Log: LLM-Assisted Development

This log records the prompt-run-test-modify-critique cycle used in the Chirality Atlas
Star Ascidian project. Entries are ordered chronologically.

---

## Round 1: Gierer-Meinhardt IMEX solver

**Prompt:**
"Implement the Gierer-Meinhardt reaction-diffusion system in Fourier space using an
IMEX scheme. Treat diffusion implicitly with denominators:
  denom_a = 1 + dt * (Da * k2 + mu_a)
  denom_h = 1 + dt * (Dh * k2 + mu_h)
Treat nonlinear reaction terms explicitly. Each step: compute reactions in real space,
FFT, update: a_hat = (a_hat + dt * fft(reaction_a)) / denom_a. IFFT and clip to > 0.
Return (n_snapshots, N, N) history arrays."

**Run/Test:** Ran at default parameters (N=64, dt=0.5, 3000 steps). Spots appeared by
step ~1000. Verified: a_final > 0 everywhere, pattern_strength > 0, cluster_count >= 2.

**Stability test:** Ran at dt=5.0 (ten times default). Field stayed finite. IMEX scheme
confirmed unconditionally stable for diffusion term.

**Critique:** No issues. First attempt was correct. Confirmed IMEX denominators match
the spec exactly.

---

## Round 2: Active zooid agent forces

**Prompt:**
"Write a numpy simulation of N active agents. Each agent has position (x,y) and heading
theta. Five forces per agent:
1. Self-propulsion: F = v0 * (cos(theta), sin(theta))
2. Center attraction: F = -k_attract * (pos - center_k)
3. Radial spring: r_vec = pos - center; r = |r_vec|; F = k_radial * (r_target - r) * r_hat
4. Excluded volume: for pairs with dist < sigma_ev: F = k_ev * (1 - dist/sigma_ev) * sep_hat
5. Orientation noise: dtheta += omega_i * dt + sqrt(2*Dr*dt) * xi
Agents assigned to centers (assignments array) and arms (arm_assignments array).
Return position and orientation histories."

**Run/Test:** Ran clean_star_systems preset at n_steps=400. Verified positions finite
and in [0, L] for periodic boundary. radial_order score >= 0.7. Visual check: agents
organized into lobes around centers.

**Modify:** Added boundary="box" mode with reflective walls after initial test.
Adjusted sigma_ev from 0.2 to 0.18 to reduce agent clumping at initialization.

**Critique:** Orientation singularity at r=0 needed a 1e-9 guard in r_hat computation.
Added. No other issues.

---

## Round 3: Angular repulsion force

**Prompt:**
"Add an angular repulsion force between agents from different arms at the same center.
For pair (i,j) with assignments[i]==assignments[j] and arm_assignments[i]!=arm_assignments[j]:
  phi_i = atan2(pos[i] - center)
  dphi = phi_i - phi_j, wrapped to [-pi, pi]
  sigma = 1.5 * 2*pi / n_arms
  if |dphi| < sigma:
    F = -k_angular * (1 - |dphi|/sigma) * sign(dphi) * t_hat_i
  where t_hat_i = [-r_hat_i_y, r_hat_i_x]
Vectorize with numpy masks. Return (N, 2) force array."

**Run/Test:** Tested with two agents in same arm (dphi ~ 0, force should be zero).
Passed. Tested with two agents in adjacent arms (dphi ~ 2*pi/7, force should push apart).
Passed. Ran full simulation: arms spacing became regular over 400 steps.

**Critique:** No issues. Force correctly produces zero for same-arm pairs via sign(0) = 0.

---

## Round 4: Swirl metric (with bug)

**Prompt:**
"Compute swirl score for ZooidResult. For each center k, compute the net tangential
velocity of assigned agents. tangential_hat = [-r_hat_y, r_hat_x]. Project velocity
v = v0 * (cos(theta), sin(theta)) onto t_hat. Mean over agents, normalize by v0.
Return mean over centers."

**Generated code (WRONG):**
```python
t_hats = np.column_stack([-r_hats[:, 0][:, None] * 0 - r_hats[:, 1], r_hats[:, 0]])
```

**Error:** The `[:, None]` created shape (N, 1); subtracted from shape (N,) broadcast to (N, N).
Subsequent dot product raised ValueError: shapes (N, N) and (N, 2) not aligned.

**Fix:** Compared against manually written t_hat computation in zooid_agents.py:
```python
t_hats = np.column_stack([-r_hats[:, 1], r_hats[:, 0]])
```

**Lesson:** numpy column_stack with mixed `[:, None]` and `[:, 0]` indexing in the same
expression is a broadcast trap. Check output shapes explicitly.

---

## Round 5: Phase diagram sweep

**Prompt:**
"Write run_sweep_A(n_x=5, n_y=5, seed=42) that sweeps k_radial over [0.5, 3.0] and
omega over [0.0, 4.0]. At each grid point, run a fast simulation (grid_size=32, n_steps=1500
for field, n_steps=150 for agents). Return x_vals, y_vals, and a grids dict with
star_likeness and swirl 2D arrays."

**Run/Test:** Ran 5x5 grid. Verified: star_likeness high at high k_radial/low omega,
swirl high at high omega. Shape of grids was (5, 5). All values finite.

**Modify (bug 1):** BASE_FIELD_PARAMS included `seed=42`; calling code also passed
`seed=seed`. Error: "multiple values for keyword argument 'seed'". Fixed by removing
seed from BASE_FIELD_PARAMS.

**Modify (bug 2):** BASE_AGENT_PARAMS included `n_per_arm=3`; simulate_zooid_agents
does not accept n_per_arm (it expects n_per_center). Fixed by filtering _agent_keys_excluded.

**Critique:** Both bugs were clean errors (not logic errors). Caught by smoke test
before any figures were generated.

---

## Round 6: Phase diagram CSV writer

**Prompt (partial):** "Write the CSV export for phase diagram data using csv.DictWriter."

**Generated code (WRONG):**
```python
with open(path, "w", newline="") as f:
    csv.DictWriter(f, fieldnames=["x","y","metric"]).writeheader()
    csv.DictWriter(f, fieldnames=["x","y","metric"]).writerows(rows)
```

**Error:** Two separate DictWriter instances; the second instance's writerows had no
effect because its rows were empty (it was a fresh object). Output file had only the header.

**Fix:** Single writer instance:
```python
w = csv.DictWriter(f, fieldnames=["x","y","metric"])
w.writeheader()
w.writerows(rows)
```

---

## Summary

| Round | Component | Outcome | Bug found? |
|---|---|---|---|
| 1 | GM IMEX solver | Correct on first try | None |
| 2 | Zooid forces | Correct; minor param tuning | None |
| 3 | Angular repulsion | Correct on first try | None |
| 4 | Swirl metric | numpy broadcast bug | Yes -- fixed manually |
| 5 | Phase sweep | 2 parameter bugs | Yes -- caught by smoke test |
| 6 | CSV export | double-writer bug | Yes -- caught by file inspection |

Total: 3 bugs in 6 rounds. All caught before affecting generated assets.
All three were in code structure (broadcasting, kwargs, object state), not in physics.
All physics implementations were correct on the first try when the formula was specified precisely.
