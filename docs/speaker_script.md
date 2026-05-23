# Speaker Script: Chirality Atlas -- Star Ascidian Edition

Total time: 5 minutes (hard cap). Slide times are targets, not exact.

---

## Slide 1 (45 sec): Target

"This is a star ascidian. It is a colonial animal that lives in shallow water
and arranges its individuals -- called zooids -- into star-shaped systems.
Each star has a central opening and about seven animals radiating out in discrete arms.
Multiple stars tile the colony surface without merging. And in some species,
the arms rotate -- every star in the colony twists the same direction.

Our question is simple: can two local physical rules produce this geometry
from scratch? A spacing rule for where the stars go, and a force rule for how
the arms form?"

[point to schematic, then to simulation still]

---

## Slide 2 (50 sec): Model

"We use a two-layer model. The layers run in sequence and have no feedback between them.

Layer one is a Gierer-Meinhardt reaction-diffusion system. One chemical activates itself
but also triggers a faster-diffusing inhibitor. This short-range activation,
long-range inhibition structure is why reaction-diffusion is called a Turing mechanism.
It produces spots at regular spacing, controlled by the ratio of the two diffusion rates.
Those spots become our star center positions.

Layer two is an active particle model. Each zooid is a self-propelled agent
with four forces: a pull toward its home center, a spring toward a ring at the target radius,
angular repulsion that pushes agents from different arms apart, and optional chirality --
a rotation rate omega that twists the orientation over time.

The key creative step was the angular repulsion. Standard active matter models
do not have this. It is what converts a ring of agents into discrete arms."

[point to equations on slide]

---

## Slide 3 (50 sec): Simulation

"Starting from agents scattered randomly around each center, the forces organize them
into radial arms in about 400 timesteps. You can see it in the animation.

At the end of the run, we measure three things: radial order -- how many agents
are near the target ring; arm count -- how many arms we detect per center;
and center spacing -- whether the stars maintain their distance.

With the default parameters, radial order is above 0.8, which means most agents
are well-confined to the ring. Arm count is harder to measure -- with only three
agents per arm, the angular histogram is sparse and the peak detection is noisy.
That is an honest limitation of the metric, not the model.

When we add chirality at omega equals 2.5, the arms rotate measurably. The swirl score
goes from near zero to about 0.3. The arm structure is preserved -- just twisted."

[show clean GIF, then chiral GIF]

---

## Slide 4 (50 sec): Phase diagram

"The phase diagram sweeps radial spring strength and chirality simultaneously.
Each point in the grid is a separate simulation. The left heatmap shows star-likeness.
The right shows swirl.

The green region in the top left -- high radial spring, low chirality -- is our
target regime. That is where the model produces the cleanest stars.

As we increase chirality, star-likeness stays reasonable but swirl increases.
The arms rotate without losing coherence until chirality is very high.
At the bottom -- low radial spring -- agents escape the ring and fragmentation rises.

The other phase diagram sweeps noise versus angular repulsion.
High noise fragments the stars. Strong angular repulsion partially compensates,
but only up to a point. Biology presumably operates in the moderate-noise regime."

[point to optimal region, then high-omega column]

---

## Slide 5 (45 sec): Insight and limits

"The model explains the geometric properties that follow from the two physical rules.
Center spacing follows from the Turing instability. Arm structure follows from
the radial spring and angular repulsion. Chirality-induced rotation follows from omega.

What it does not explain: arm count is a parameter, not emergent.
There is no Botryllus biochemistry, no colonial immune recognition,
no developmental timing. This is a minimal geometric model, not a developmental model.

On LLM use: we used Claude for the IMEX scheme, the vectorized force computations,
and the phase sweep loops. The code was verified against expected physical behavior
after every prompt. One bug slipped through -- a numpy broadcasting error in the
swirl metric -- and was caught by comparing output shapes to the manually-written
force code. The lesson: LLMs write fast but do not catch shape mismatches.

Takeaway: a two-stage mechanism can turn local rules into star-shaped colonial order.
Chirality adds rotation without destroying the structure."

[pause]

---

## Transitions

Slide 1 to 2: "So what are the rules? Let me show you the model."

Slide 2 to 3: "Here is what that model actually does when you run it."

Slide 3 to 4: "One run is not enough. Let us sweep the parameter space."

Slide 4 to 5: "Good. Now -- what does this tell us, and what does it not?"

---

## Backup

If the live demo fails: navigate to Tab 4 (Movie Gallery) and show the pre-generated GIFs.
If GIFs are missing: show `outputs/panels/slide3_simulation_sequence.png` from file explorer.
If the app crashes entirely: open the notebook (`notebooks/Star_Ascidian_Chirality_Atlas.ipynb`)
and scroll to Section 6 and Section 8. All figures regenerate in under 2 minutes.
