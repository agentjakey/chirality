# For Judges: Chirality Atlas -- Star Ascidian Edition

---

## What to run (60 seconds)

```
pip install -r requirements.txt
python healthcheck.py
streamlit run app.py
```

The healthcheck runs the full two-layer model in under 30 seconds and prints PASS.
The app opens at http://localhost:8501.

---

## What to inspect

**Tab 1 -- Target Pattern:**
Biology motivation. Botryllus schlosseri schematic + simulation comparison.
Pre-generated `outputs/panels/slide1_target_and_simulation.png`.

**Tab 2 -- Model Builder:**
Live simulation. Run with defaults (clean stars), then raise omega to 2.5 (twisted stars).
Watch the swirl metric change. GM field + agent snapshot appear after ~30 seconds.

**Tab 4 -- Movie Gallery:**
GIF animations of arm formation and chiral twist. Pre-generated. No wait time.

**Tab 6 -- LLM Notebook:**
How Claude was used. Two best prompts, one failure case, how outputs were verified.

**docs/llm_proficiency.md**: Full written record.
**notebooks/Star_Ascidian_Chirality_Atlas.ipynb**: Runnable notebook with all steps.

---

## Main insight

A Turing reaction-diffusion field (Gierer-Meinhardt) places star centers at regular
spacing. Active zooid agents with radial confinement and angular repulsion form
discrete arms around those centers. Chirality (omega) measurably rotates the arm
pattern -- swirl score rises from near zero to ~0.3 at omega=2.5.

The model reproduces the spatial geometry of Botryllus colonies from minimal local rules.
It is not a mechanistic developmental model. The biology it does not capture is stated
clearly in slide 5 and in docs/scientific_audit.md.

---

## What is creative

**The two-layer design:** Separating center placement (field) from arm formation (agents)
is not standard in active matter models. It allows each layer to be tuned independently
and makes the parameter space tractable.

**Angular repulsion between arm groups:** Standard active particle models do not have this.
It is the force that converts a ring of agents into discrete arms with regular angular spacing.
Without it, agents form a ring but not distinct arms.

**Chirality as a measurable signature:** The swirl score detects collective rotation
that would be invisible to standard order parameters (polar order, radial order).
This is the novel metric contribution.

---

## What is scientifically grounded

- GM equations are a standard reference model for Turing pattern formation.
- IMEX numerical scheme is standard for reaction-diffusion; unconditionally stable for diffusion.
- Active Brownian particle dynamics are from the hackathon tutorial baseline.
- All metrics verified: smoke test runs 53 checks, all passing.
- Phase diagram sweeps reproduce known regimes: fragmented (high Dr), merged (high n_per_arm),
  clean stars (moderate k_radial, low omega), twisted stars (high omega).

---

## What is honest about limitations

- Arm count (n_arms=7) is a model parameter, not emergent.
- The arm count detection metric under-counts at low agent density. We say so explicitly.
- Phase diagram boundaries are computed at reduced resolution (N=32 grid, n_steps=150 agents).
- No Botryllus biochemistry, blastogenic timing, or 3D geometry.

---

## Backup if live app fails

1. Open `outputs/panels/` in file explorer -- all slide panels are pre-generated.
2. Run notebook sections 6 and 8 -- produces key figures in under 2 minutes.
3. Run `python scripts/05_make_all_assets.py` -- regenerates all outputs (~15 minutes).

All pre-generated outputs are committed to the repo under `outputs/`.
