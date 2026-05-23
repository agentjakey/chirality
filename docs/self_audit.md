# Self Audit

## What we claim vs what we can support

| Claim | Status | Notes |
|-------|--------|-------|
| Reproduces tutorial ABP baseline | Verified | polar order ~0.05 for disordered ABP (Dr=0.5) |
| Reproduces Vicsek flocking | Verified | polar order ~0.95 at low noise (eta=0.15) |
| Reproduces Gray-Scott spots | Verified | pattern_strength ~0.10 for spots preset (F=0.035, k=0.065) |
| Reproduces Gray-Scott labyrinths | Verified | different morphology, different cluster count |
| Chiral ABP creates edge current | Observed | visible in circular trap GIF and snapshot |
| Chirality suppresses polar order | Verified | phase diagram shows polar order drops with omega |
| Chirality creates swirl | Weakly observed | swirl values ~0.07-0.19, small but systematic |
| Chiral source breaks L-R symmetry | Observed | asymmetry ~0.002-0.006 vs ~0.0001 without source |
| Racemic mix has near-zero net swirl | Observed | control case works as expected |
| All simulations use fixed seeds | Verified | seed parameter passed throughout |
| All metric outputs validated finite | Verified | sanity_check.txt in outputs/phase_sweeps/ -- PASS |

---

## Honest scoring (1-10)

| Category | Score | Honest notes |
|----------|-------|-------------|
| Tutorial alignment | 9 | Direct line-by-line extension of both tutorials; docs/tutorial_connections.md maps it |
| Scientific validity | 7 | ABP/Vicsek/GS are correct; chiral source is phenomenological toy model |
| Originality | 8 | Two-track unified framework + chiral source novel in this context |
| Visual clarity | 8 | Consistent palette, colorbars present, dark particle plots, warm field plots |
| UI polish | 8 | 7-tab Streamlit app, download buttons, progress indicators |
| Phase diagrams | 7 | 7 diagrams from real sweeps; 6x6 coarse grids, noted on all figures |
| Biological connection | 6 | Edge current well-connected to bacteria; chiral source is speculative |
| Reproducibility | 9 | Fixed seeds, smoke test, sanity report, gitignored outputs |
| Deployment readiness | 8 | Streamlit, healthcheck, Dockerfile, HF deployment docs |
| Presentation strength | 8 | 5-slide deck, speaker script, 2-min demo script, backup plan |

**Overall: 7.8 / 10**

---

## How to improve any score below 8

**Scientific validity (7 -> 8):**
Add one citation linking the edge current result to a real experiment.
Lauga et al. (2006) "Swimming in Circles: Motion of Bacteria near Solid Boundaries"
is the canonical reference. Even citing this in docs/science_notes.md would raise the score.

**Biological connection (6 -> 8):**
Either (a) cite a specific paper for the edge current and downplay chiral source as a
pure toy, or (b) cite a paper on symmetry-breaking morphogenetic gradients to justify
the chiral source framing. Current state: edge current is plausible, chiral source is
speculative without citation.

**Phase diagrams (7 -> 8):**
Run one additional sweep at 8x8 to confirm the 6x6 trends are not artifacts.
Even 2 additional points on the boundary of the phase diagram would be reassuring.

---

## What NOT to overclaim

Do NOT say: "This model explains left-right axis determination."
DO say: "This is a toy model showing that a rotating source can break L-R symmetry."

Do NOT say: "The swirl index shows strong chiral order."
DO say: "The swirl index shows a systematic trend that grows with omega."

Do NOT say: "This is a complete model of bacterial motility."
DO say: "This captures the qualitative boundary-accumulation behavior of chiral swimmers."

Do NOT say: "Gray-Scott is a realistic model."
DO say: "Gray-Scott is a well-studied toy model for pattern formation."

---

## Weaknesses a skeptic would flag

1. **Swirl values are small.** 0.07-0.19 with N=200, 800 steps. The GIF is more convincing
   than the number. If pressed: show the GIF and say the metric is noisy for these parameters.

2. **Chiral source asymmetry is tiny.** ~0.002-0.006. Reproducible with fixed seeds.
   A critic could argue this is near the noise floor. The sweep shows it grows with omega,
   which is the expected behavior of a real effect.

3. **Pattern strength labeled "weak patterning."** The storytelling module threshold is
   conservative. Pattern_strength ~0.10 shows real spots visually. This is a labeling issue,
   not a scientific issue.

4. **Polar order max 0.20 in particle phase sweep.** Correct for ABP (no alignment).
   This would confuse someone expecting Vicsek-like order from ABP. The explanation is clear
   in docs and in the app.
