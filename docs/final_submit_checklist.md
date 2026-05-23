# Final Submit Checklist

## Pre-submission verification commands

```
python healthcheck.py
# Expected: 8/8 PASS

python scripts/06_final_smoke_test.py
# Expected: 53/53 PASS

python -m pytest tests/ -q
# Expected: 42 passed

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
# Expected: slide1 through slide5, final_summary_panel.png (6 files)

ls outputs/movies/
# Expected: 4 GIF files

ls outputs/slides/
# Expected: Chirality_Atlas_Star_Ascidian_Edition.pptx

ls outputs/submission/
# Expected: SUBMISSION_README.md, key assets
```

## Slide deck

- [ ] `outputs/slides/Chirality_Atlas_Star_Ascidian_Edition.pptx` opens and shows 5 slides
- [ ] Reference image appears in Slide 1 left panel
- [ ] All panel images embedded correctly (not broken)
- [ ] PDF export done (manually: File > Export in PowerPoint)

## App checks

- [ ] Tab 1 (Target Pattern): reference image shows, feature checklist correct
- [ ] Tab 2 (Model Builder): Run Simulation works, agent plot uses dark substrate
- [ ] Tab 3 (Phase Explorer): Load pregenerated shows heatmap
- [ ] Tab 4 (Movie Gallery): Two hero GIFs visible with captions
- [ ] Tab 5 (Model Library): All 6 models expand without error
- [ ] Tab 6 (LLM Notebook): Two prompts visible as code blocks
- [ ] Tab 7 (Presentation Mode): Slide 1 expanded by default, images load

## What to show first when presenting

1. **Tab 1 (Target Pattern)**: reference image + model hypothesis (30 sec)
2. **Tab 2 (Model Builder)**: run simulation, point to radial order (60-90 sec)
3. **Tab 4 (Movie Gallery)**: star_formation_clean.gif hero (20 sec)
4. **Tab 3 (Phase Explorer)**: load pregenerated sweep A (20 sec)
5. **PPTX**: for structured 5-slide presentation to judges

## Known acceptable limitations to state

- arm_count metric reads ~1.25 at default density (3 agents/arm below detection limit)
- Phase diagram is 5x5 at reduced resolution (qualitative trends robust)
- n_arms=7 is a parameter, not emergent
- No Botryllus biochemistry modeled

## Do NOT say

- "arm count = 7" (metric reads 1.25)
- "matches Botryllus exactly" (spatial geometry only)
- "phase boundary is precisely at k_radial = X" (grid too coarse)
- "we discovered a new principle" (both Turing and ABP are well-known separately)
