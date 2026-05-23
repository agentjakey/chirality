# Project Brief: Chirality Atlas -- Star Ascidian Edition

## 30-Second Summary

We built a two-layer computational model that reproduces the spatial geometry of
Botryllus schlosseri, the star ascidian. Layer 1 is a Gierer-Meinhardt Turing field
that places star centers at regular intervals. Layer 2 is a system of active zooid
agents with radial confinement, angular repulsion, and tunable chirality (omega)
that form radial arms around those centers. The model runs live in a Streamlit app,
accepts parameter inputs, and reports quantitative metrics against the biological target.

## Target Pattern

Botryllus schlosseri is a colonial tunicate. Its colonies form star-shaped systems:
each star has a shared central atrium and approximately 7 zooids radiating outward
in discrete arms. Multiple stars tile the colony surface with characteristic spacing
and do not merge. Some colonies show a consistent handedness (chirality) in arm orientation.

This is a spatial self-organization problem. We ask whether two simple physical mechanisms
-- a short-range activation / long-range inhibition field plus active agent dynamics --
are sufficient to reproduce the target geometry.

## Model Hypothesis

A two-stage mechanism produces the pattern:

1. A Gierer-Meinhardt reaction-diffusion field (Dh/Da >> 1) produces quasi-regular
   Turing spots. These become star center positions.

2. Active zooid agents initialized around those centers settle into radial arms under:
   - center attraction (prevents cross-star drift)
   - radial spring (targets a ring at r_target)
   - angular repulsion (spaces arms evenly)
   - orientation noise (Dr) and optional chirality (omega)

## Main Result

The clean_star_systems preset produces multiple star centers with radial arm structure
scoring radial_order >= 0.8 and star_likeness >= 0.6. Adding chirality (omega = 2.5)
measurably rotates arm geometry (swirl_score increases) without destroying the arm pattern.
The phase diagram (k_radial vs omega) shows a clear optimal regime.

The arm count detection metric under-counts at low agent density (3 agents per arm is near
the detection threshold). The radial_order and star_likeness metrics are more reliable
indicators of model quality.

## Why Judges Should Care

This project demonstrates two things that matter for the hackathon criteria:

**Scientific grounding:** The two-layer design is physically motivated. The GM layer
connects directly to the pattern formation tutorial. The zooid force structure connects
directly to the active matter tutorial. Both layers are verified independently before
being combined.

**LLM proficiency:** The force equations, IMEX scheme, and phase diagram sweep were all
generated through prompt-run-test-modify-critique cycles with explicit verification
against known physics. We caught and fixed one broadcast bug in the LLM-generated
swirl metric, documented in both the notebook and llm_proficiency.md.

The model is honest about its limits. Arm count is a free parameter, not emergent.
There is no biology (no blastogenesis, no immune recognition, no signaling molecules).
The geometry is 2D. These are stated clearly in slide 5 and in scientific_audit.md.
