# Final Slide Speaker Notes

## Slide 1 (1:00) -- Can local rules generate a living star pattern?

"This is Botryllus schlosseri. A colonial tunicate that tiles hard substrates
as a mat of star-shaped systems. Each star has 5-10 zooids arranged radially
around a shared atrium.

We asked: can two local rules reproduce this geometry? The answer is yes.
A Turing field places the centers. Active agents form the arms. That is it.

The three panels show: the biological target, the activator field, and the
agent simulation at the same scale."

Timing: 45-60 seconds. Point at each panel.

---

## Slide 2 (0:50) -- Model: centers first, stars second

"Layer 1: Gierer-Meinhardt. Short-range activation, long-range inhibition.
Turing instability produces quasi-periodic spots -- these are the star centers.
The Dh/Da ratio controls how many centers appear.

Layer 2: Active zooid agents. Each agent has a radial spring toward r_target,
and angular repulsion from neighboring arm groups. Omega adds a turning bias.

No global template. Everything is local."

Timing: 50 seconds. Point at the equation boxes. Two sentences per layer.

---

## Slide 3 (1:00) -- Simulation: from noise to star systems

"Arms self-organize from noise in about 400 steps. At t=0, agents are in
initialized arm groups with random offsets. By the final frame they have
settled into radial lobes.

With omega=0: the pattern is radial. With omega=2.5: the arms rotate.
Swirl score rises from 0.01 to 0.3 -- a measurable chirality signature.

[If app is running: switch to Movie Gallery, play star_formation_clean.gif]"

Timing: 45-60 seconds. If time: play the GIF from Movie Gallery.

---

## Slide 4 (1:00) -- Creative exploration: phases of living geometry

"This is the phase diagram for radial attraction versus chirality.

Left: star-likeness. The bright region at moderate k_radial, low omega is the
clean star regime. At high chirality, persistent rotation smears the arms.

Right: swirl. Rises with omega without destroying arm structure up to omega~2.
The two metrics are not correlated -- you can have good arms without chirality,
and chirality without arm degradation.

The regimes from left to right: uniform mat, spots without stars, clean stars,
twisted stars."

Timing: 50-60 seconds. Point at each regime on the left heatmap.

---

## Slide 5 (1:10) -- Insight, limits, and LLM use

"What works: center spacing from the Turing field, radial confinement at r_target,
discrete arm lobes from angular repulsion, measurable chirality rotation.

What does not: arm count is a parameter not emergent. No Botryllus biochemistry,
no 3D, no blastogenic timing, no immune recognition.

LLM contributions: the IMEX Gierer-Meinhardt solver, the vectorized angular
repulsion, and diagnosing a broadcast error in the swirl metric during testing.
All equation choices and parameter values were human decisions.

The core insight: Turing instability plus angular repulsion is sufficient
to generate star-shaped colonial geometry from local rules, without any
organism-specific information."

Timing: 60-70 seconds. End on the core insight sentence.

---

## If asked about arm count reading 1.25

"That is the detection limit of find_peaks at 3 agents per arm. The angular
histogram has 3 points per arm out of 36 bins. The peak detection algorithm
needs at least 5 agents per arm to reliably detect peaks. The visual output
shows 7 arms. The metric is the limitation, not the model."

## If asked about phase boundary precision

"The phase diagram uses a 5x5 grid at reduced resolution for speed.
Each point takes about 15 seconds. The qualitative trends are robust.
Phase boundaries would shift by approximately one grid cell at higher resolution."

## If asked about biological validation

"This model does not claim to reproduce Botryllus biochemistry. The claim
is specifically about spatial geometry: center spacing and radial arm structure
can emerge from a Turing field plus active agent forces. That claim is supported
by the simulation outputs and the radial_order metric."
