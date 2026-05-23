# Self Audit: Chirality Atlas Star Ascidian Edition

Honest pre-hackathon scoring from five perspectives:
scientific reviewer, hackathon judge, skeptical teammate, deployment engineer, presentation coach.

---

## Scores (1-10)

| Category | Score | One-line verdict |
|---|---|---|
| Scientific accuracy | 8 | Equations correct; IMEX verified; limitations explicit |
| Creative insight | 8 | Memorable target; 7 distinct phases; chirality cleanly measured |
| LLM proficiency | 9 | Workflow documented; 2 prompts shown; 3 bugs caught; human judgment recorded |
| Visual impact | 7 | GIFs compelling; panels clear; arm count metric looks bad on screen |
| Demo reliability | 8 | Graceful fallbacks; backup plan in Tab 7; assets pre-generated |
| Biological relevance | 7 | Geometry modeled honestly; no biochemistry overclaimed |
| Phase diagram quality | 7 | 4 real sweeps; 5x5 at reduced resolution; boundaries are illustrative |
| Presentation clarity | 9 | 5-slide deck exact; speaker script timed; demo script step-by-step |
| Deployment readiness | 9 | healthcheck 8/8 PASS; Dockerfile valid; no secrets; HF-ready |
| Honesty and limits | 9 | Limitations in every tab; arm count failure explicit; "toy model" stated |

**Overall: 8.1 / 10**

---

## For every score below 8: exact fix

### Visual impact (7): The arm count number will confuse judges

**Problem:** When a judge runs the Model Builder and sees `arm_count_mean = 1.25` in the
metric card labeled "Arm count (mean)" next to a target of 7, they will question whether
the model works at all. The visual output clearly shows ~7 arms, but the number says 1.25.

**What was already fixed:** The feature checklist in Tab 1 now shows "Discrete arm lobes"
as partial/red (not green), with the note "metric underestimates at low density."
The metric card tooltip now says "Underestimates at n_per_arm < 5."
A `_limit()` callout was added below the metric cards.

**What remains:** A judge might still be confused by the discrepancy. The correct script:
"The arm count metric reads low because at 3 agents per arm, the angular histogram
has too few points for peak detection. Look at the visual output -- arms are there.
Increase n_per_arm to 6 in the slider and the metric will read correctly."

**To verify this yourself:**
```
python -c "
from chirality.star_ascidian.hybrid_model import simulate_star_ascidian_colony
from chirality.star_ascidian.metrics import arm_count_distribution
r = simulate_star_ascidian_colony(preset='clean_star_systems', seed=42, n_snapshots=4,
    n_field_steps=500, n_steps=200, n_per_arm=6)
ac = arm_count_distribution(r.zooid)
print('n_per_arm=6:', ac['mean'])
r2 = simulate_star_ascidian_colony(preset='clean_star_systems', seed=42, n_snapshots=4,
    n_field_steps=500, n_steps=200, n_per_arm=3)
ac2 = arm_count_distribution(r2.zooid)
print('n_per_arm=3:', ac2['mean'])
"
```

### Biological relevance (7): Geography is reproduced but "biology" claim needs care

**Problem:** The project correctly avoids overclaiming, but a judge might think
"if arm count isn't modeled, what IS modeled?" The answer is: center spacing
(from GM, quantitatively controlled) and radial confinement (radial_order=1.0 at default).
These are the two most visually salient features of Botryllus stars.

**Fix in presentation:** Be specific. "We model center-spacing geometry and radial arm
confinement, not arm count or developmental biology."

### Phase diagram quality (7): 5x5 at N=32 is coarse

**Problem:** Each sweep point uses N=32 grid and n_steps=150 for agents. The phase
boundaries are approximate. A skeptical reviewer could ask for a finer grid.

**Fix in presentation:** State the resolution explicitly in slide 4. "This is a 5x5 grid
at reduced resolution for speed. The qualitative trends are robust; boundaries shift
at higher resolution." The CSV data files in outputs/data/ are available for
reproducibility verification.

---

## Scientific accuracy audit: what the equations actually say

### GM Layer 1

Equation in code vs CLAUDE_CONTEXT spec:
- CLAUDE_CONTEXT: `da/dt = D_a * lap(a) + rho * a^2 / (h*(1+kappa*a^2)) - mu_a * a`
- Code: adds `rho_0` baseline production
- Status: CORRECT. The rho_0 term prevents total activator extinction and is standard in GM implementations.

Chirality in Layer 2:
- CLAUDE_CONTEXT: `theta_i += omega_i * dt + sqrt(2*Dr*dt) * xi_i`
- Code: identical formula
- Status: CORRECT. Chirality is a turning bias (orientation drift), not a tangential force.
  The swirl_score measures the consequence (net tangential velocity), not the input.

IMEX stability:
- Verified at dt=5.0 (10x default). Field stays finite.
- Explicit stability limit at N=64, Dh=5.0: dt < dx^2/(4*Dh) = (10/64)^2 / (4*5) = 0.0024.
  Default dt=0.5 is 200x above explicit limit. IMEX is necessary and correct.

### Active zooid Layer 2

Angular repulsion: force is zero for same-arm pairs because sign(0) = 0.
Verified: same-arm force sum == 0 in smoke test.

Radial spring singularity at r=0: protected by 1e-9 guard. Correct.

---

## What a skeptic would flag and how to answer

**"Your arm count metric reads 1.25, not 7."**
Response: "That is the detection limit of find_peaks at 3 agents per arm. The angular
histogram has 3 points per arm out of 36 bins -- the peak is one bin wide and below
the prominence threshold. Set n_per_arm=6 in the Model Builder slider and the metric
reads correctly. The visual output shows the arms; the detection algorithm is the limitation."

**"Your star_likeness score is 0.42. That's below 0.5."**
Response: "Star_likeness is a composite of arm_score, radial_order, and angular_uniformity.
Radial_order is 1.0. Angular_uniformity is ~0.7. Arm_score is ~0.1 because arm_count
reads low. The radial_order and visual output are the primary quality indicators."

**"These are toy parameters with no connection to real biology."**
Response: "Correct, and we state this explicitly. The model makes no claim about
Botryllus biochemistry. The claim is specifically: spatial geometry (center spacing,
radial arm structure) can emerge from a Turing field plus active agent forces.
That claim is supported by the simulation outputs."

**"The phase diagram is only 5x5."**
Response: "Yes. Each point takes ~15 seconds so 25 points takes ~6 minutes.
The qualitative trends are robust -- radial arm structure improves with k_radial,
degrades with high omega and high noise. The coarse grid gives the regime map;
fine-grained boundaries would require overnight runs."

---

## What to NOT say

- Do NOT say "arm count = 7" -- it's not detected correctly at default settings
- Do NOT say "matches Botryllus exactly" -- it reproduces spatial geometry, not biology
- Do NOT say "phase boundary is at k_radial = 1.5" -- the grid is too coarse for precision
- Do NOT say "chirality suppresses arm structure" -- it doesn't, up to omega~2.5
- Do NOT say "the model explains colony immune recognition" -- it does not model this at all

---

## What to say confidently

- "Radial order is 1.0 -- agents are well-confined to the target ring."
- "Adding chirality (omega=2.5) measurably rotates arm geometry -- swirl_score goes from ~0 to ~0.3."
- "The GM field provides quasi-regular star center spacing through Turing instability, without requiring explicit center-repulsion rules."
- "We used Claude for IMEX implementation and vectorized force computation. Both were correct on first try when the math was specified precisely."
- "We caught and fixed 3 code bugs before they affected any figure: a broadcast error in the swirl metric, a double-seed error, and a double-writer error."
