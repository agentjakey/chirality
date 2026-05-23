# Final Submit Checklist

## Pre-submission verification commands

```
python healthcheck.py
# Expected: 8/8 PASS

python scripts/06_final_smoke_test.py
# Expected: 53/53 PASS

python -m compileall src scripts
# Expected: no syntax errors

python -c "import app; print('app imports cleanly')"
# Expected: app imports cleanly

streamlit run app.py
# Expected: opens at localhost:8501
```

## Assets to verify exist

```
ls outputs/panels/
# Expected: 11 panels including single_star_mechanism.png, colony_scale_reference_match.png,
#           center_selection_schematic.png, phase_diagram_with_regimes.png, formation_sequence_strong.png

ls outputs/movies/
# Expected: star_formation_clean.gif, chiral_twist_emergence.gif, colony_scale_formation.gif

ls outputs/slides/
# Expected: Chirality_Atlas_Star_Ascidian_Edition.pptx (477 KB, 5 slides)

ls outputs/submission/
# Expected: SUBMISSION_README.md, PPTX, hero panels, GIFs, scripts
```

## Slide deck (session 6 rebuild)

- [ ] `outputs/slides/Chirality_Atlas_Star_Ascidian_Edition.pptx` opens and shows exactly 5 slides
- [ ] Slide 1: real reference image (left) + colony_scale_reference_match (right, 36 stars)
- [ ] Slide 2: center_selection_schematic (left) + single_star_mechanism (right)
- [ ] Slide 3: formation sequence (4 frames, clean + chiral rows)
- [ ] Slide 4: phase_diagram_with_regimes (6 named regimes visible)
- [ ] Slide 5: 3-column layout (matched / did not / LLM use)
- [ ] Footer on every slide: "Chirality Atlas: Star Ascidian Edition" + slide number
- [ ] PDF export done (manually: File > Save as PDF in PowerPoint)

## App checks (session 6 tab order)

Tab bar order: Target Pattern | Mechanism | Movie Gallery | Phase Explorer | LLM Lab Notebook | Presentation Mode | Model Builder

- [ ] Tab 1 (Target Pattern): reference image + colony_scale_reference_match side by side
- [ ] Tab 2 (Mechanism): center_selection_schematic + single_star_mechanism visible
- [ ] Tab 3 (Movie Gallery): star_formation_clean.gif + chiral_twist_emergence.gif as hero row
- [ ] Tab 4 (Phase Explorer): phase_diagram_with_regimes shown by default for Sweep A
- [ ] Tab 5 (LLM Lab Notebook): two strongest contributions at top, two prompts as expanders
- [ ] Tab 6 (Presentation Mode): demo order reads Target -> Mechanism -> Movies -> Phase
- [ ] Tab 7 (Model Builder): Run Simulation button works

## Live demo script (2 min)

1. Tab 1 (Target Pattern): show reference image + colony match (20 sec)
2. Tab 2 (Mechanism): point to center schematic + single star panels (25 sec)
3. Tab 3 (Movie Gallery): play star_formation_clean.gif then chiral_twist_emergence.gif (30 sec)
4. Tab 4 (Phase Explorer): point to clean-star regime in phase diagram (20 sec)
5. Core result: "Turing field plus angular repulsion generates star geometry from local rules."

## Known acceptable limitations to state

- arm_count metric reads ~1.25 at default density (3 agents/arm below detection limit)
- Phase diagram is 5x5 at reduced resolution (qualitative trends robust, boundaries qualitative)
- n_arms=7 is a parameter, not emergent
- No Botryllus biochemistry, developmental staging, 3D, or immune recognition
- Colony simulation uses seed=0 which gives 4 centers (best available)

## Do NOT say

- "arm count = 7" (metric reads 1.25 at default density)
- "matches Botryllus exactly" (spatial geometry only)
- "phase boundary is precisely at k_radial = X" (grid too coarse)
- "we discovered a new principle" (Turing + ABP are known, combination is the contribution)
