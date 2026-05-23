# Speaker Script: Chirality Atlas

Total time: 4 minutes (hard cap at 5)

---

## Slide 1 (45 sec)

"The core question is simple: if every particle in a system has a slight left or right bias in how it moves, does the whole system behave differently?

The answer from biology seems to be yes -- bacteria circle near surfaces, embryos reliably pick a left-right axis, and rotating cytoskeletal structures drive asymmetric tissue folding. But the mechanism in each case is different. What we want is a minimal model.

This project takes two computational tutorials you already know -- active particle models and reaction-diffusion -- and adds one control knob: omega, a chirality parameter."

[Transition: "Let me show you the two models."]

---

## Slide 2 (45 sec)

"The particle track extends the active Brownian particle model from Tutorial 1. We add a rotation rate omega to each particle's orientation update. Small omega: particles trace large lazy circles. Large omega: tight circles. We can also assign different omega to different particles -- left-handed, right-handed, or a mix.

The pattern track extends the Gray-Scott model from Tutorial 2. We add three modifications: a linear feed gradient, a circular obstacle, and a rotating injection point that we call the chiral source. The chiral source is a toy model -- it is not meant to represent any specific organism.

Both models are direct line-for-line extensions of the tutorial code."

[Transition: "Let us see what the baseline looks like."]

---

## Slide 3 (45 sec)

"Before adding chirality, we check that the baselines reproduce expected behavior. Vicsek flocking at low noise gives polar order near 0.95 -- highly ordered. Gray-Scott at F=0.035 and k=0.065 gives self-organized spots, pattern strength around 0.10.

These phase diagrams show how polar order and pattern strength vary across the parameter space. The grids are coarse -- 6x6 -- because we are working on a laptop. The qualitative shapes match what the tutorials predict."

[Transition: "Now the creative part."]

---

## Slide 4 (60 sec)

"When we turn on chirality in the particle model, something interesting happens. Polar order goes down -- individual particles curve in circles instead of aligning with neighbors. But a different kind of order appears: swirl. With a circular boundary, particles orbit the wall. That is the edge current you see on the right.

The racemic case -- 50% left, 50% right -- is the control. The two populations compete and cancel out. Swirl index stays near zero.

In the pattern model, the chiral source introduces a small but detectable left-right asymmetry. Without the source, the L-R asymmetry is less than 0.0001 -- essentially zero. With omega=0.1, it rises to around 0.002. That is small, but it is real and reproducible with fixed seeds.

The key insight: chirality and noise are competing control knobs. Chirality suppresses polar order but creates a different structural order. You need the right metric to see it."

[Transition: "What does this mean biologically?"]

---

## Slide 5 (45 sec)

"The boundary edge current is a known phenomenon in bacterial motility near surfaces. Right-handed bacteria tend to orbit clockwise when near a wall. Our model reproduces that qualitatively.

The chiral source is more speculative. It is a proof of concept that a rotating signal source can break left-right symmetry in a pattern-forming system. The biological analogy would be a rotating cilium or cytoskeletal structure biasing morphogen distribution -- but we are not claiming this is a model of any real pathway.

The limitations are real: coarse phase diagrams, Euler integration, toy chiral source. We describe them in the docs.

The takeaway: handedness is not just a curiosity. It can reshape which order parameters matter and what structures form."

---

## If a judge asks "what did you actually add?"

"We added three things. First, a chirality parameter omega to both tutorial models -- one line of code in the orientation update for particles, a rotating injection function for the pattern model. Second, new metrics to detect the order that chirality creates -- swirl index for particles, L-R asymmetry for fields. Without these metrics, you would look at chirality and see only disorder. Third, a Streamlit app and systematic phase diagrams connecting the two tracks under one question.

The scientific claim is modest and we believe it is defensible: omega is a control knob, and the effects are measurable."

---

## If a judge asks "is the chiral source realistic?"

"No, not directly. It is a toy model. A real symmetry-breaking mechanism in development involves specific signaling molecules and directional transport. What we show is that even a simple rotating source can introduce a measurable left-right bias. That is a proof of concept, not a biological claim."

---

## If a judge asks "why are the swirl index values so small?"

"The swirl index is a noisy quantity in a small, short simulation. With N=200 particles and 800 steps, you would not expect large values. The point is that it is systematically larger with chirality than without, and it scales with omega in the phase diagram. It is a relative measurement, not an absolute one."
