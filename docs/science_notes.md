# Science Notes

## Active Brownian Particles (ABP)

The tutorial ABP model updates each particle's position and orientation as:

    theta_i(t + dt) = theta_i(t) + sqrt(2 * Dr * dt) * xi_i(t)
    x_i(t + dt) = x_i(t) + v0 * cos(theta_i) * dt
    y_i(t + dt) = y_i(t) + v0 * sin(theta_i) * dt

where xi_i(t) is a standard normal random variable and Dr is the rotational diffusivity.
Each particle self-propels at fixed speed v0 but gradually loses directional memory
over a persistence time of order 1/Dr. This is the tutorial baseline.

## Chiral ABP (tutorial extension)

Adding a deterministic rotation rate omega to the orientation update:

    theta_i(t + dt) = theta_i(t) + omega_i * dt + sqrt(2 * Dr * dt) * xi_i(t)

If omega > 0, the particle curves in one direction with radius R_c = v0 / |omega|.
If omega < 0, it curves the other way. The competition between rotation and noise
determines whether particles trace persistent circles or diffuse freely.

The "racemic" mode assigns half the particles omega = +|omega| and half omega = -|omega|,
mimicking a mixture of left- and right-handed swimmers.

This extension is one extra line in the orientation update step.

## Vicsek Model (tutorial baseline)

Each particle aligns its heading with the average heading of neighbors within radius R,
then adds noise:

    phi_avg = atan2( sum_{|r_ij| < R} sin(theta_j), sum_{|r_ij| < R} cos(theta_j) )
    theta_i(t + dt) = phi_avg + eta * Uniform[-pi, pi]

The minimum-image convention is used for periodic boundaries.

The polar order parameter phi = |mean(exp(i * theta))| measures collective alignment.
phi = 1 means all particles point the same way (flock). phi ~ 0 means disordered (gas phase).
The Vicsek transition between these phases as eta varies is a well-studied nonequilibrium
phase transition.

## Chiral Vicsek (tutorial extension)

Adding omega * dt to the Vicsek update introduces a tendency for the flock to curve.
High omega competes with the alignment interaction.

## Soft Repulsion

Optional pairwise interaction: when two particles are within repulsion_range, they receive
a displacement proportional to (range - distance) pointing away from each other.
This is a simple contact-force model with no physical units attached.

## Boundary Conditions

Periodic: positions are taken modulo L. Standard for bulk active matter.

Reflective: particles bounce off walls (angle of incidence = angle of reflection).

Circular trap: particles confined inside a circle of radius ~0.45*L.
Chiral particles with reflective circular boundaries tend to accumulate at the edge
and orbit -- this is related to "edge currents" observed in chiral active fluids.

## Polar Order Parameter

    phi = |mean_i(exp(i * theta_i))| = sqrt( mean(cos theta)^2 + mean(sin theta)^2 )

Standard Vicsek order parameter. Lies in [0, 1].

## Swirl Index

    swirl = mean_i( (v_i_hat . t_i_hat) )

where t_i_hat is the unit tangent to the circle centered at L/2 passing through
particle i's position, and v_i_hat = (cos theta_i, sin theta_i).
This measures how aligned particle velocities are with circular orbits around the box center.

Note: swirl is a noisy quantity in short simulations with small N.
It is best interpreted as a relative measurement (chirality vs no chirality) rather than
an absolute value.

## Mean Squared Displacement

    MSD(tau) = mean_i( |r_i(t + tau) - r_i(t)|^2 )

For a free random walk: MSD ~ 4*D*tau (2D).
Active particles: ballistic at short times, diffusive at long times.
Chiral particles may show oscillatory MSD if they trace circles.

Known issue: MSD is ill-defined with periodic boundaries once particles have diffused
more than L/2. Restrict to short times for meaningful results.

## Gray-Scott Reaction-Diffusion

The Gray-Scott model (Pearson 1993) describes two interacting chemical species u and v:

    u_t = Du * laplacian(u) - u*v^2 + F*(1 - u)
    v_t = Dv * laplacian(v) + u*v^2 - (F + k)*v

u is a substrate fed at rate F and consumed by the autocatalytic reaction u + 2v -> 3v.
v is an activator created by the reaction and destroyed at rate F + k.
Du > Dv allows Turing-type instability.

The Laplacian uses periodic boundary conditions:

    laplacian(f)[i,j] = f[i+1,j] + f[i-1,j] + f[i,j+1] + f[i,j-1] - 4*f[i,j]

Standard parameter regimes:
- Spots: F ~ 0.035, k ~ 0.065
- Labyrinths: F ~ 0.04, k ~ 0.06
- Uniform (no pattern): F too high or k too high

## Feed Gradient (tutorial extension)

Replacing uniform F with F(x) = F_left + (F_right - F_left) * x/L creates a spatial gradient.
Different regions fall in different Gray-Scott regimes, so a phase gradient appears in the pattern.
Direct extension of the tutorial gradient exercise.

## Circular Obstacle (tutorial extension)

Setting u = 1 and v = 0 inside a circular region at every step prevents the reaction there.
The obstacle acts as a no-reaction zone. Patterns form around the boundary but not inside.
Can create topological defects in stripe patterns.

## Chiral Source (toy model, creative extension)

A small Gaussian source of v rotates around the box center:

    focal_x(t) = 0.5*nx + r_orbit * cos(source_omega * t)
    focal_y(t) = 0.5*ny + r_orbit * sin(source_omega * t)
    v += source_strength * exp(-|r - focal|^2 / (2 * sigma^2)) * dt

The handedness of the rotation (sign of source_omega) can break the left-right symmetry
of the resulting pattern.

This is NOT a model of any real biological mechanism. It is a proof of concept that
a rotating symmetry-breaking perturbation can propagate to macroscopic pattern asymmetry.
Real biological chiral symmetry breaking (e.g., left-right axis determination in vertebrates)
involves specific molecular motors, signaling pathways, and tissue-level mechanics
not captured here.

## Pattern Strength Metric

    pattern_strength(v) = std(v)

Standard deviation of the v field. Near zero for an unpatterned state.
Large for well-developed spots or stripes.

## Cluster Count Metric

Threshold v at 0.1, apply connected-component labeling (scipy.ndimage.label),
count the number of connected regions. Approximate count of spots or stripe segments.

## Left-Right Asymmetry Metric

    field_asymmetry(v) = mean(v[nx/2:, :]) - mean(v[:nx/2, :])

Positive means more v on the right half. Near zero for a symmetric pattern.
Expected to be near zero without a chiral source and nonzero with one.

The asymmetry is small for the default parameters (~0.002 with omega=0.1).
It is best interpreted as a relative measurement relative to the no-source control.

## Known Limitations

1. O(N^2) pairwise operations for Vicsek and repulsion. Practical N limit: ~400.

2. Explicit Euler integration in Gray-Scott. Stable for default parameters;
   not guaranteed stable for arbitrary (Du, Dv, dt).

3. Chiral source asymmetry is a small effect. It may be statistically indistinguishable
   from noise at small grid sizes. Scales with source_strength.

4. MSD with periodic boundaries is ill-defined for particles that cross boundaries.

5. The omega parameter in particle models is phenomenological, not directly calibrated
   to any specific microswimmer.

6. Phase diagrams use coarse 6x6 grids with short runs. Boundaries are indicative only.
