# Known Limitations

## Star Ascidian Model (primary)

**Arm count is a parameter, not emergent.**
n_arms is passed to the zooid agent model. The angular repulsion spacing assumes
n_arms arms per center. The model does not explain why Botryllus has 7 arms.
It only shows that given n_arms=7, the agent forces produce ~7 evenly-spaced lobes.

**Arm count detection is unreliable at low agent density.**
With n_per_arm=3, each arm contributes 3 points to a 36-bin angular histogram.
The scipy.signal.find_peaks algorithm requires a visible peak, which 3 agents
often do not produce. The metric typically reads 1-3 detected arms even when the
geometry clearly shows 7. The radial_order score is more reliable. Both are reported;
judges should use radial_order as the primary geometric quality indicator.

**Phase diagram at reduced resolution.**
The phase diagram sweeps use grid_size=32 and n_field_steps=1500 for the GM field
and n_steps=150 for agents. Full-resolution runs use grid_size=64, n_field_steps=3000,
n_steps=400. Phase boundaries at full resolution would shift, possibly significantly
for the GM-dependent metrics (n_centers, spacing_quality).

**O(N^2) excluded volume.**
The pairwise excluded volume loop is O(N^2) in agent count. For default presets
with K=4, n_arms=7, n_per_arm=3, N=84 agents total, this is fast. For N > 500
the excluded volume computation becomes a bottleneck.

**No biological mechanism.**
The model has no Botryllus biochemistry, no signaling molecules (Wnt, BMP, Notch),
no blastogenic timing, no colonial immune recognition, no substrate mechanics.
It is a minimal geometric model. The claim is only that the spatial pattern geometry
can arise from local rules -- not that these specific rules operate in the real organism.

**2D only.**
Real Botryllus colonies are thin sheets on a 3D substrate. The model is 2D.
Curvature, substrate mechanics, and depth-dependent signaling are not captured.

**Euler integration.**
Both layers use first-order Euler integration. This is appropriate for qualitative
phase diagrams but not for precision calibration against experimental data.

---

## Metrics Limitations

**swirl_score is unsigned per-center, signed total.**
The metric returns the mean signed tangential velocity across centers. If two centers
have opposite chirality (racemic mode), they cancel. The magnitude of chirality
at each center is not reported separately.

**merge_score is O(N^2) and slow at high N.**
The merge detection loops over all cross-center agent pairs. At N > 300 this becomes
slow enough to affect interactive use. Not an issue for default presets.

**angular_uniformity depends on find_peaks quality.**
If arm_count is under-detected (see above), uniformity is computed from fewer peaks
and may be misleadingly high (1 peak has undefined spacing, defaults to 0).

---

## Reference Models (secondary)

**Gray-Scott explicit Euler.**
The Gray-Scott model uses explicit Euler with dt=1.0 and dx=1.0 grid. Stability
requires D * dt / dx^2 < 0.25. With Du=0.16 this is 0.16 -- safe but marginal.
Large parameter deviations may require reducing dt.

**Chiral source is not a biological mechanism.**
The rotating Gaussian source in simulate_chiral_source_gray_scott is a toy construction.
No specific organism uses this mechanism. It is included as a minimal demonstration
of how a broken symmetry in a boundary condition produces a measurable field asymmetry.

**Phase sweep resolution (all sweeps).**
All phase sweeps use 5x5 grids. Qualitative trends are correct; quantitative
boundaries require denser grids and longer per-point simulations.

**O(N^2) Vicsek neighbor search.**
The Vicsek model uses an all-pairs distance computation. Fine for N <= 400.
Not suitable for large-scale simulations without cell lists or kd-trees.
