# Final 2-Minute Live Demo Script

Demo order: Target Pattern -> Movie Gallery -> Phase Explorer -> LLM Lab Notebook -> Presentation Mode

---

## Step 1 (20 sec): Target Pattern tab

Open the app. Tab 1 is already showing.

Say: "This is the real organism -- Botryllus schlosseri. You can see the radial star systems.
The feature checklist on the right shows what the model reproduces and what it does not."

Point to the reference image.
Point to the checklist: green items are reproduced, red items are acknowledged limitations.

---

## Step 2 (30 sec): Movie Gallery tab

Click Movie Gallery (Tab 4).

Point to the first GIF (star_formation_clean.gif):
"Here are the arms forming in real time from a random initialization.
No template. Radial spring drives them outward, angular repulsion separates them."

Wait a moment for the GIF to cycle.

Point to the second GIF (chiral_twist_emergence.gif):
"Same initialization, but with a chirality parameter omega=2.5.
The arms rotate. That is the biological chirality signature."

---

## Step 3 (20 sec): Phase Explorer tab

Click Phase Explorer (Tab 3).

Select "Sweep A -- Radial attraction vs chirality."
Click "Load pregenerated."

Point to the heatmap:
"Best star-likeness is at moderate k_radial, low omega -- the top-left region.
High chirality degrades arm structure at the right edge.
The two metrics are not correlated."

---

## Step 4 (20 sec): LLM Lab Notebook tab

Click LLM Lab Notebook (Tab 6).

Point to "Two Best Prompts."
Say: "This shows how Claude was actually used -- specific prompts, specific outcomes.
Not vibe coding. Every function was verified with at least three checks."

Point to the failure gallery:
"This is where it went wrong. Broadcast error in the swirl metric. Caught before any
figure was produced, because every function was tested against expected behavior."

---

## Step 5 (20 sec): Model Builder tab (optional, if time)

Click Model Builder (Tab 2).

Say: "You can run a simulation live. Leave defaults -- N=32, 1200 field steps -- and click
Run Simulation. Takes 45-90 seconds. Radial order near 1.0 is the quality signal.
Arm count reads low due to the detection limit at 3 agents per arm -- we say so in the tooltip."

[Do not wait for the run during a 2-minute demo. Just show the controls.]

---

## Step 6 (10 sec): Presentation Mode tab

Click Presentation Mode (Tab 7).

Say: "This is the full 5-slide deck order with exact speaker notes.
Slide 5 has the honest limitations and the LLM contribution summary."

---

## Cut-down order if under 90 seconds

1. Target Pattern tab (10 sec): show reference image
2. Movie Gallery tab (20 sec): play star_formation_clean.gif, point to chirality
3. Phase Explorer tab (10 sec): load pregenerated Sweep A
4. Say the core result: "Turing field plus angular repulsion generates star colonial geometry from local rules."

---

## Core result to say in any context

"A Turing activator-inhibitor field places star centers at regular spacing.
Active agents with angular repulsion form discrete arms around those centers.
Chirality measurably rotates the arms. Swirl score distinguishes chiral from radial.
All from local rules, no global template, no organism-specific biochemistry."
