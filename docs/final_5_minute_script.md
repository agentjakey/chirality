# Final 5-Minute Talk Script

Total: 5 minutes. Each slide is ~1 minute.
Deliver naturally -- do not read verbatim. These are anchor points.

---

## Slide 1 (1:00) -- Can local rules generate a living star pattern?

"This is Botryllus schlosseri, a colonial tunicate that tiles hard surfaces
as a mat of radial star-shaped systems.

Each star has roughly 7 zooids arranged around a shared central atrium.
The stars maintain regular spacing from each other, and some genetic strains
show consistent rotational handedness -- biological chirality.

We asked: can we build two local rules that generate this pattern from scratch?

The answer is yes. You can see the result here.
Left is the real organism. Center is our activator field output.
Right is the agent simulation -- multiple star systems, radial arms, comparable spacing.

The question is how."

TRANSITION: "So let me explain the mechanism."

---

## Slide 2 (0:50) -- Model: centers first, stars second

"We built a two-layer model.

Layer 1 is a Gierer-Meinhardt reaction-diffusion system. Short-range activation,
long-range inhibition. When the inhibitor diffuses much faster than the activator,
you get Turing spots. Those spots are the star center positions.

This handles colony-level organization without any explicit repulsion between stars.

Layer 2 is active zooid agents. Each agent has a radial spring toward a target radius,
angular repulsion from neighboring arm groups, rotational noise, and an optional
chirality parameter omega.

The angular repulsion is the key ingredient. Without it, agents form a ring.
With it, they form discrete arms."

TRANSITION: "Here is what that looks like in motion."

---

## Slide 3 (1:00) -- Simulation: from noise to star systems

"These four frames show the time evolution.

At t=0, agents are initialized in arm groups with random offsets.
Over 400 steps, they settle into radial lobes.

The radial spring confines them at r_target.
Angular repulsion pushes arms apart.
Noise keeps it looking biological.

With omega=0, the pattern is radial.
With omega=2.5, the arms slowly rotate.

We measure this with a swirl score -- net tangential velocity normalized by total speed.
It goes from about 0.01 at omega=0 to about 0.3 at omega=2.5.
The arm structure is preserved.

[If app is running: switch to Movie Gallery and play star_formation_clean.gif]"

TRANSITION: "Let me show you the parameter space."

---

## Slide 4 (1:00) -- Creative exploration: phases of living geometry

"This is the phase diagram for radial spring strength versus chirality rate.

On the left, star-likeness: the brighter the region, the more the simulation
looks like a colony. The hotspot at moderate k_radial and low omega is the
clean star regime -- the parameters we demo by default.

On the right, swirl score: rises with omega, roughly independent of k_radial
up to a point.

This is the key finding: you can tune chirality without destroying arm structure,
up to about omega equal to 2.

The regimes here correspond to biological states.
High noise: fragmented arms.
High omega: twisted stars.
Overcrowded: stars merge.
Weak inhibition: no center selection, uniform mat.

Each regime was verified in the simulation."

TRANSITION: "I want to be honest about what this model does and does not do."

---

## Slide 5 (1:10) -- Insight, limits, and LLM use

"What the model reproduces: center spacing, radial confinement, discrete arm structure,
and measurable chirality rotation. Radial order is 1.0 at our default parameters.
Swirl score separates chiral from non-chiral.

What it does not reproduce: arm count is a parameter, not emergent.
The model has no Botryllus biochemistry, no blastogenic developmental staging,
no 3D geometry, no colonial immune recognition.

We are clear about this throughout the app and the docs.

On LLM use: Claude proposed the two-layer decomposition. That was not our initial idea.
We started with a single-layer model. Claude suggested separating center selection --
which is a colony-level Turing mechanism -- from arm formation -- which is a local
agent process. That decomposition is physically principled and biologically motivated.

Claude also designed the metric hierarchy: radial order, arm count, angular uniformity,
swirl, fragmentation. Each metric catches a specific failure mode that looks fine visually.

Both contributions were verified, not accepted blindly.

The takeaway: a Turing field and angular repulsion are sufficient to generate
star-shaped colonial geometry from local rules.
That is a clean result."

---

## Backup lines for tough questions

**"Arm count reads 1.25, not 7."**
"That is the peak detection limit at 3 agents per arm. The visual output shows 7 arms.
Use n_per_arm=5 or higher in the Model Builder slider and the metric reads correctly.
The detection algorithm is the limitation, not the model."

**"Your phase diagram is 5 by 5."**
"Yes. Each point takes about 15 seconds so 25 points takes 6 minutes.
Qualitative trends are robust. The boundary shifts by roughly one grid cell
at higher resolution."

**"This is not really Botryllus."**
"Correct, and we say so on slide 5 and in every tab of the app.
The model reproduces the spatial geometry. It makes no claim about biochemistry
or developmental biology. That honesty is a feature, not a weakness."

**"Where is the novelty?"**
"The combination is novel: using a Turing field for center placement removes
the need for explicit center-repulsion rules. And angular repulsion between arm groups
is not a standard ingredient in active particle models. Standard ABP gives a ring.
Our version gives discrete arms. That distinction matters for biological modeling."
