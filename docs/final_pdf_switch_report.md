# Final PDF Switch Report

Generated: 2026-05-23

---

## Canonical final presentation path

```
outputs/submission/Chirality_Atlas_Star_Ascidian_FINAL.pdf
```

This is the primary judge-facing file. Open this first.

Editable backup (PPTX):
```
outputs/slides/Chirality_Atlas_Star_Ascidian_Edition.pptx
outputs/submission/Chirality_Atlas_Star_Ascidian_Edition.pptx
```

---

## Files updated

| File | Change |
|---|---|
| `docs/final_submit_checklist.md` | Slide deck section now points to PDF; PPTX listed as backup only |
| `outputs/submission/SUBMISSION_README.md` | File table updated; "Open first" section added with PDF path |
| `outputs/submission/final_submit_checklist.md` | Synced with docs version |
| `docs/final_1_hour_polish_report.md` | Final deck path section now shows PDF as canonical; PPTX as backup |
| `docs/final_slide_export_notes.md` | Primary deliverable section now points to PDF; PPTX is editable backup |
| `docs/reference_sources.md` | PPTX reference replaced with PDF path |
| `app.py` (Presentation Mode tab) | PDF path shown prominently at top; Backup Plan now references PDF |

---

## App updated

Yes. Presentation Mode tab now shows:
- Dark header box with canonical PDF path
- Backup plan references PDF directly

---

## Remaining PPTX references and why they remain

All remaining PPTX references correctly describe it as "editable backup" or appear in historical/technical context:

- `final_1_hour_polish_report.md` -- historical record of what was done to the PPTX. Appropriate.
- `final_slide_export_notes.md` -- technical documentation of the PPTX generation workflow. Appropriate.
- `final_submit_checklist.md` -- "PPTX at ... is backup only". Correctly labeled.
- `SUBMISSION_README.md` -- "Editable PowerPoint backup". Correctly labeled.
- `scripts/make_pptx.py` -- source of truth for PPTX generation. Leave unchanged.

No remaining references call the PPTX the "final deck," "main presentation," "submission deck," or "primary presentation."

---

## Validation commands passed

```
python healthcheck.py
# PASS: all checks passed (8/8)

python -m compileall src scripts
# PASS: no syntax errors

python -c "import app; print('app imports cleanly')"
# app imports cleanly
```

---

## Manual checks still needed

1. Open `outputs/submission/Chirality_Atlas_Star_Ascidian_FINAL.pdf` and verify:
   - 5 pages
   - Page 1: observe / Botryllus / two levels of order
   - Page 2: two-layer model
   - Page 3: simulation dynamics
   - Page 4: phase diagram with regime labels
   - Page 5: insight, limits, LLM use

2. Run `streamlit run app.py`, go to Presentation Mode tab, and verify the PDF path is visible at the top.

3. Confirm PDF is accessible and not corrupted (not just 0 bytes).
