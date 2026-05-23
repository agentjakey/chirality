# Final Slide Speaker Notes

5 slides, 5 minutes. Each slide is 45-60 seconds.
These are anchor points, not a script to read verbatim.

---

## Slide 1 (0:55): Can local rules generate a living star pattern?

**Visual:** Real Botryllus schlosseri colony (left) + simulation colony scale (right)

Open by pointing to the reference image.

"This is Botryllus schlosseri, a colonial tunicate that tiles hard substrates
as a mat of star-shaped systems. Each star has roughly seven zooids arranged
radially around a shared central atrium. Stars maintain characteristic spacing
and do not merge under normal conditions.

Notice two things: the spacing between stars, and the radial structure inside each star.
Those are two distinct levels of spatial organization.

We asked whether two local rules can reproduce both of them.

The right panel is our simulation. Many star systems. Radial arms. Comparable spacing.
Yes for the core geometry."

Transition: "Let me explain how the mechanism works."

---

## Slide 2 (0:55): Model -- centers first, stars second

**Visual:** Layer 1 center selection schematic (left) + single star mechanism (right)

Walk through both panels from left to right.

"We built a two-layer model to match the two biological scales.

Left panel -- Layer 1. This is a Gierer-Meinhardt reaction-diffusion field.
Short-range activation, long-range inhibition. When the inhibitor diffuses
much faster than the activator, the system spontaneously breaks into Turing spots.
Those spots become the star center positions. No explicit repulsion between centers is needed.
Spacing emerges from the diffusion ratio alone.

Right panel -- Layer 2. Active zooid agents. Each agent has a radial spring toward r target,
angular repulsion from neighboring arm groups, rotational noise, and chirality omega.

The angular repulsion is the key ingredient.
Without it: agents form a ring. With it: discrete arms.
Clean star on the left inset. Chiral star on the right -- arms have rotated."

Transition: "Here is the time evolution."

---

## Slide 3 (0:55): Simulation -- from noise to star systems

**Visual:** 4-frame time sequence, top row clean, bottom row chiral

Point to the four frames from left to right.

"At t equals zero, agents are initialized in arm groups with random offsets.
Over 400 steps they settle into radial lobes.
The radial spring confines them at r target. Angular repulsion pushes arms apart.

Top row is omega zero -- radial and stable.
Bottom row is omega 2.5 -- arms slowly rotate.

We quantify chirality with a swirl score: net tangential velocity normalized by total speed.
It rises from about 0.01 at omega zero to about 0.3 at omega 2.5.
The arm structure is preserved under chirality up to a threshold."

If app is running: switch to Movie Gallery and show star_formation_clean.gif.

Transition: "Now let me show you the full parameter space."

---

## Slide 4 (0:55): Creative exploration -- phases of living geometry

**Visual:** Phase diagram with two heatmaps and regime labels

Point to the left heatmap first, then right.

"Phase diagram: radial spring strength versus chirality rate.

Left: star-likeness. Brighter means more star-like.
Hotspot at moderate k radial, low omega -- this is the clean star regime.

Right: swirl score. Rises with omega, mostly independent of k radial.

The key finding: the two metrics are not correlated.
You can tune chirality without destroying arm structure up to about omega two.

The regime labels correspond to what you actually see:
uniform mat at low inhibition ratio, spots without arms at low k radial,
clean stars in the center, twisted stars at high omega,
merged stars when overcrowded, fragmented stars at high noise.

Each regime was verified in a full-resolution simulation.
One run is a demo. A phase diagram is the result."

Transition: "I want to be honest about what this model does and does not do."

---

## Slide 5 (1:00): Insight, limits, and LLM use

**Visual:** Three columns -- what matched, what did not, what LLM changed

Read column by column, briefly.

"Green column: what the model matches.
Center spacing, radial confinement, discrete arm structure, measurable chirality.
Radial order stays above 0.8 at default parameters.

Orange column: what it does not.
Arm count is a parameter we set, not emergent.
No Botryllus biochemistry, no developmental staging, no 3D geometry.
This is a geometric model, and we say so.

Blue column: what LLM changed.
Claude proposed the two-layer decomposition. That was not our initial idea.
We started with a single-layer model. The suggestion to separate center selection
using a Turing field from arm formation using active agents was physically principled
and biologically motivated. It worked better than the original approach.

Claude also designed the metric hierarchy. Each metric catches a specific failure mode
that looks fine on visual inspection alone. Both contributions were verified, not accepted.

Core result: a Turing activator-inhibitor field places star centers.
Active agents with angular repulsion form arms.
Chirality adds measurable swirl without immediately destroying the star geometry.
This is a toy geometric model, and we say so."

End with the takeaway bar text.

---

## Timing guide

| Slide | Target | Transition line |
|-------|--------|----------------|
| 1 | 0:55 | "Let me explain how the mechanism works." |
| 2 | 0:55 | "Here is the time evolution." |
| 3 | 0:55 | "Now let me show you the full parameter space." |
| 4 | 0:55 | "I want to be honest about what this model does and does not do." |
| 5 | 1:00 | Takeaway line. Done. |
| Buffer | 0:20 | Questions setup |
