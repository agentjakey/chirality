# Final Streamlit Deploy Report

Generated: 2026-05-23

---

## App polish changes

### Header
- Added one-line summary: "A toy geometric model of star ascidian colony morphology using Turing center selection and active zooid arm formation."
- Added scope note: "We model the visible geometry, not the full organism." in `.app-scope` CSS class
- Subtitle font size increased to 1.0rem for projector readability

### Tab headings (now match PDF language)
- Tab 1: "Biological Target" -> "Observe: Botryllus schlosseri Colony"
- Tab 2: "Mechanism: Centers First, Stars Second" -> "Hypothesize: Centers First, Stars Second"
- Tab 3: "Movie Gallery" -> "Simulate: Arms in Motion"
- Tab 4: "Phase Explorer: Parameter Space" -> "Explore: Phases of Living Geometry"
- Tab 5: "LLM Lab Notebook" -> "Explain: How LLMs Helped Without Replacing Verification"

### Tab 1 (Observe)
- Replaced single large green box with separate judge-card and scope-card using CSS classes
- Scope card clearly states: "This is a toy geometric model. It reproduces the visible spatial signature, not Botryllus biochemistry, developmental staging, or immune recognition."

### Tab 5 (Explain)
- Replaced two stacked green boxes with three side-by-side cards (model decomposition, metric design, human verification) using `.llm-card` CSS class
- Added failure case note in `.scope-card` style: visible-looking output can still fail metrics
- Removed "Two strongest contributions" heading (redundant with card titles)

### Tab 6 (Presentation Mode)
- PDF box now uses `.pdf-box` CSS class instead of inline styles
- Added 30-second pitch section above 5-slide story using `.judge-card` CSS class

### CSS (assets/style.css)
New classes added:
- `.app-scope` -- small italic scope note in header
- `.judge-card` -- green left-border takeaway card
- `.scope-card` -- terracotta left-border limitation/warning card
- `.compare-card`, `.compare-card-title` -- comparison card grid
- `.tab-section` -- top-bordered section divider
- `.mech-bar` -- mechanism summary bar
- `.gif-card`, `.gif-card-title`, `.gif-card-sub` -- GIF card styling
- `.pdf-box`, `.pdf-box-label`, `.pdf-box-path`, `.pdf-box-backup` -- presentation mode PDF block
- `.llm-card`, `.llm-card-title` -- LLM contribution cards
- Updated `.app-subtitle` font size from 0.86rem to 1.0rem

---

## Deployment files changed

| File | Change |
|---|---|
| `.streamlit/config.toml` | Created (new) -- theme, server, browser settings |
| `requirements.txt` | Verified clean -- no unnecessary packages |
| `README.md` | Added Streamlit Community Cloud deploy section |
| `outputs/submission/SUBMISSION_README.md` | Added local + cloud deploy instructions |

---

## Final PDF path (canonical presentation)

```
outputs/submission/Chirality_Atlas_Star_Ascidian_FINAL.pdf
```

---

## Streamlit tab order

1. Target Pattern (Observe)
2. Mechanism (Hypothesize)
3. Movie Gallery (Simulate)
4. Phase Explorer (Explore)
5. LLM Lab Notebook (Explain)
6. Presentation Mode
7. Model Builder

---

## Validation results

```
python healthcheck.py                            PASS 8/8
python scripts/06_final_smoke_test.py            PASS 53/53
python -m compileall src scripts                 PASS no errors
python -c "import app; print('app imports cleanly')"  PASS
```

---

## Streamlit deploy settings

Platform: Streamlit Community Cloud (share.streamlit.io)
Repo: push to GitHub first
Main file: `app.py`
Python version: 3.11 (recommended)
No system packages required (packages.txt not needed)
No secrets required for base app

`.streamlit/config.toml` configures:
- `backgroundColor = "#F7F3EA"` (warm off-white)
- `primaryColor = "#C15A3A"` (terracotta)
- `textColor = "#1F2421"` (charcoal)
- `font = "serif"` (matches scientific notebook aesthetic)
- `headless = true` (required for cloud)
- `enableCORS = false`
- `enableXsrfProtection = false`

---

## Manual checks still needed

1. Open `outputs/submission/Chirality_Atlas_Star_Ascidian_FINAL.pdf` -- confirm 5 pages, not corrupted
2. `streamlit run app.py` and verify visually:
   - Tab 1: reference image + colony match side by side
   - Tab 2: mechanism schematic panels load
   - Tab 3: GIFs display (not static)
   - Tab 4: phase diagram loads immediately (no blank state)
   - Tab 5: three LLM cards side by side
   - Tab 6: PDF path shown, 30-second pitch visible
   - Tab 7: preset selector at top, no simulation runs on load
3. Confirm `.streamlit/config.toml` theme applies (warm background, serif font)
4. Before cloud deploy: verify GitHub push includes `.streamlit/config.toml`
