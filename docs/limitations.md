# Known Limitations

## Particle simulations

**O(N^2) scaling**: The Vicsek neighbor search and soft repulsion both loop over all
pairs. For N > 400, runtime grows quadratically. Real-scale active matter simulations
use spatial data structures (cell lists, kd-trees) to achieve O(N) neighbor lookups.
This project is sized for N = 100-400 as a demonstration tool.

**Periodic MSD**: Mean squared displacement in a periodic box is valid only when
displacement is much less than L. Chiral particles that travel many multiples of L
before being wrapped will have artificially small MSD. For quantitative MSD analysis,
use larger boxes or track unwrapped positions.

**Chirality as a free parameter**: The omega parameter in the chiral ABP is
phenomenological. Real microswimmers have chirality that arises from their shape
and propulsion mechanism. The radius of circular motion R_c = v0 / |omega| is a
useful physical interpretation, but connecting omega to any specific organism requires
independent calibration.

**No hydrodynamics**: All simulations use point particles with no fluid-mediated
interactions. Bacterial suspensions, for example, have long-range hydrodynamic
interactions that can qualitatively change the collective behavior (e.g., pusher vs
puller swimmers). This project does not capture those effects.

**Euler integration**: Time integration is explicit Euler throughout. This is
first-order accurate. For precision over long times, Runge-Kutta would be better.
The current implementation is accurate enough for qualitative phase diagrams.

## Pattern simulations

**Explicit Euler for Gray-Scott**: The standard Gray-Scott simulations use explicit
Euler with dt=1.0. This is stable for the default diffusion coefficients (Du=0.16,
Dv=0.08) but will blow up for larger dt or Du. The stability condition is roughly
D * dt / dx^2 < 0.25 in 2D. With dx=1, dt=1, Du=0.16 this is satisfied (barely).

**Lattice artifacts**: The discrete Laplacian on a square grid introduces fourfold
rotational symmetry artifacts. Real continuous Laplacians have circular symmetry.
For high-resolution studies, spectral methods (FFT-based Laplacian) are more accurate.

**Chiral source is not a real biological mechanism**: The rotating source in
`simulate_chiral_source_gray_scott` is a toy construction to demonstrate symmetry
breaking. It has no direct biological analog. Real chiral pattern formation (e.g.,
in left-right body axis determination) involves specific signaling molecules and
tissue geometry that this model does not capture.

**Gray-Scott is not a specific organism model**: The Gray-Scott equations are a
mathematical toy that produces Turing-like patterns. They are useful for qualitative
intuition but should not be interpreted as a model of any specific biological system
without careful parameter fitting and experimental validation.

**Phase sweep resolution**: The sweep grids (6x6 or 8x8) are coarse due to runtime
constraints. Fine-grained phase boundaries require denser grids and longer simulations.
The phase diagrams here are illustrative, not publication-quality maps.

## Metrics

**Pattern asymmetry signal is small**: The left-right asymmetry induced by the chiral
source is typically on the order of 0.001-0.005 (in units of v concentration). This
is a small fraction of the typical v variation (~0.1-0.2 std). Statistical
significance would require ensemble averaging over multiple seeds, which is not done here.

**Cluster count sensitivity**: The cluster count metric depends strongly on the
threshold value (default 0.1). Different thresholds produce very different counts.
The metric should be interpreted as a rough indicator of pattern morphology, not
a precise measurement.
