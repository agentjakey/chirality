# Final 5-Minute Talk Script

Total: 5 minutes. Slide timing shown. Deliver naturally.

---

## Slide 1 (0:55) -- Can local rules generate a living star pattern?

"This is Botryllus schlosseri, a colonial tunicate that tiles hard surfaces
as a mat of radial star systems.

Each star has roughly 7 zooids arranged radially around a shared central atrium.
Stars maintain regular spacing from each other.
Some genetic strains show consistent rotational handedness -- that is biological chirality.

Two things to notice: the spacing between stars, and the radial structure inside each star.
Those are two distinct levels of spatial organization.

We asked: can two simple local rules reproduce both?

The right panel is our simulation -- many star systems, radial arms, comparable spacing.
Yes for the core geometry."

TRANSITION: "Let me explain the mechanism."

---

## Slide 2 (0:55) -- Model: centers first, stars second

"We built a two-layer model to match the two biological scales.

Layer 1 is a Gierer-Meinhardt reaction-diffusion system.
Short-range activation, long-range inhibition.
When the inhibitor diffuses much faster than the activator,
the system spontaneously breaks into Turing spots.
Those spots become the star center positions.
This handles colony-level spacing without any explicit repulsion between centers.
Spacing emerges from the diffusion ratio alone.

Layer 2 is active zooid agents.
Each agent has a radial spring toward a target radius,
angular repulsion from neighboring arm groups,
rotational noise, and an optional chirality parameter omega.

The angular repulsion is the key ingredient.
Without it, agents form a ring.
With it, they separate into discrete arms.

Left inset: clean star, omega equals zero.
Right inset: chiral star, omega equals 2.5. The arms have rotated."

TRANSITION: "Here is what that looks like in motion."

---

## Slide 3 (0:55) -- Simulation: from noise to star systems

"Four frames of the time evolution.

At t equals zero, agents are initialized in arm groups with random offsets.
The radial spring confines them at r target.
Angular repulsion pushes groups apart.
Noise keeps the structure organic.

Top row: omega equals zero. Radial and stable.
Bottom row: omega equals 2.5. Arms slowly rotate.

We measure chirality with a swirl score: net tangential velocity normalized by speed.
It goes from about 0.01 at omega zero to about 0.3 at omega 2.5.
The arm structure is preserved under chirality up to a threshold.

[If the app is running: switch to Movie Gallery and play the clean formation GIF.]"

TRANSITION: "Now let me show you the full parameter space."

---

## Slide 4 (0:55) -- Creative exploration: phases of living geometry

"This is the phase diagram for radial spring strength versus chirality rate.

Left heatmap: star-likeness. Brighter means more star-like.
The hotspot at moderate k radial, low omega is the clean star regime.

Right heatmap: swirl score. Rises with omega, mostly independent of k radial.

The key finding: the two metrics are not correlated.
You can tune chirality without destroying arm structure up to about omega equals 2.

The named regimes from bottom to top:
uniform mat at low inhibition ratio -- no Turing spots, no centers;
spots without arms at low k radial;
clean stars at moderate k radial, low omega;
twisted stars at high omega;
merged stars when overcrowded;
fragmented stars at high noise.

Each regime was verified in the simulation.
One run is a demo. A phase diagram is the result."

TRANSITION: "I want to be honest about what this model does and does not do."

---

## Slide 5 (1:00) -- Insight, limits, and LLM use

"Three columns.

Green: what the model matches.
Repeated center spacing, radial arm confinement, discrete arm structure, measurable chirality.
Radial order is above 0.8 at default parameters.

Orange: what it does not.
Arm count is a parameter we set, not something that emerges.
No Botryllus biochemistry, no blastogenic developmental staging,
no 3D geometry, no colonial immune recognition.
This is a geometric model, and we say so.

Blue: what LLM changed.
Claude proposed the two-layer decomposition.
That was not our initial idea.
We started with a single-layer model.
Claude suggested separating center selection using a Turing field
from arm formation using active agents.
That separation is physically principled and biologically motivated.

Claude also designed the metric hierarchy: radial order, arm count, swirl, fragmentation.
Each metric catches a specific failure mode that looks fine on visual inspection alone.

Both contributions were verified, not accepted blindly.

Core result: a Turing activator-inhibitor field places star centers.
Active agents with angular repulsion form arms.
Chirality adds measurable swirl without immediately destroying the star geometry.
This is a toy geometric model, and we say so."

---

## Backup lines for tough questions

**"Arm count reads 1 to 2, not 7."**
"That is the angular histogram peak detection limit at 3 agents per arm.
The visual output shows 7 arms clearly. Use n per arm equal to 5 in the slider
and the metric reads correctly. The detection algorithm is the limitation, not the model."

**"Your phase diagram is only 5 by 5."**
"Yes. Each simulation point takes about 15 seconds, so 25 points takes about 6 minutes.
Qualitative trends are robust. The phase boundary shifts by roughly one grid cell at higher resolution.
The named regimes were verified with full-resolution preset runs."

**"This is not really Botryllus."**
"Correct, and we say so on slide 5 and in every tab of the app.
The model reproduces the spatial geometry.
It makes no claim about biochemistry or developmental timing.
That honesty is the point."

**"Where is the novelty?"**
"Two things.
First: using a Turing field for center placement removes the need for explicit center-repulsion rules.
Second: angular repulsion between arm groups is not a standard active particle ingredient.
Standard ABP gives a ring. Our model gives discrete arms.
That distinction matters for modeling any colonial organism with radial geometry."
