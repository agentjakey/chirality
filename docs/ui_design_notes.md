# UI Design Notes: Chirality Atlas Demo App

## Design Intent

The app is a scientific field notebook and live modeling instrument. It should feel like something a biophysicist would use at a bench, not a generic AI dashboard. Warm colors, serif type, compact panels, no decorative chrome.

---

## Palette

| Role | Hex | Used for |
|---|---|---|
| Background | #F7F3EA | Page background, sidebar |
| Ink | #1F2421 | Body text, h1/h2 |
| Accent | #C15A3A | Active tab, primary button hover, left-border callouts |
| Green | #315C4C | h3, buttons, info boxes, notice callouts |
| Panel | #FFFFFF | Metric cards, expanders, model cards |
| Muted panel | #EFE8DC | Tab bar background, code background |
| Border | #DDD5C8 | All borders, dividers |

## Typography

Georgia serif throughout. Sans-serif is avoided. Input labels uppercase at 0.85rem. Body text 0.9rem-1rem range.

---

## Tab Structure

| Tab | Purpose | Key interaction |
|---|---|---|
| 1 - Target | Biology intro, what we're modeling | Static images, no interaction |
| 2 - Model Builder | Full parameter control + live run | Sliders + Run button |
| 3 - Phase Explorer | Parameter sweep heatmaps | Preset selector + pregenerated vs live |
| 4 - Movie Gallery | GIF animations of dynamics | Passive viewing |
| 5 - Model Library | 6 reference PDE models with equations | Expanders |
| 6 - LLM Notebook | How Claude was used in the build | Static doc |
| 7 - Presentation | Speaker notes and slide deck structure | Static reference |

---

## State Management

Tab 2 (Model Builder) stores run output in `st.session_state["mb_result"]`. This persists across re-renders so the result is not lost when the user switches tabs and returns.

Tab 3 (Phase Explorer) stores each sweep result in `st.session_state[f"phase_result_{name}"]` keyed by sweep letter. Live sweeps are slow (5x5 = 25 simulations at grid_size=24); the UI warns before running.

All expensive simulations go through `@st.cache_data` with parameter-based cache keys. Max entries = 6 for colony runs, 3 for sweeps.

---

## Image and Asset Loading

`_show_image_safe(path)` and `_show_gif_safe(path)` never crash on missing files. They fall back to a `st.info()` message explaining the asset is missing and how to generate it. This means the app is usable even if `05_make_all_assets.py` has not been run.

GIF display uses `st.image(bytes_data, ...)` after reading raw bytes. This avoids Streamlit's deprecated `use_column_width` parameter (use `use_container_width=True` instead).

---

## Custom HTML Components

Three reusable callout helpers:
- `_notice(text)` -- green left border, for "what to notice" callouts
- `_limit(text)` -- orange left border, for limitation warnings
- `_metric_row(pairs)` -- renders a horizontal row of `st.metric` cards

The `.notice-box`, `.limit-box`, `.model-card`, `.sci-panel`, `.slide-block` CSS classes are defined in `assets/style.css`.

---

## Header

`_render_header()` embeds the SVG logo inline (read from `assets/logo.svg`) next to the app title and subtitle. Uses a flex-row `div` with the `.app-header` CSS class. Falls back gracefully if the SVG file is missing.

---

## Performance Notes

- Tab 1 loads in under 1 second (static images only).
- Tab 2 shows pregenerated images immediately; Run button triggers computation on click.
- Tab 3 pregenerated path loads in under 2 seconds. Live sweep at grid_size=24 takes roughly 30-90 seconds depending on hardware.
- Tabs 4-7 are static and load immediately.

Colony simulation safety cap: if `grid_size=64` and `n_field_steps > 1500`, the UI shows a warning and suggests reducing. The cap is advisory, not enforced.

---

## What to Check Manually

Streamlit cannot be verified in this environment. Check these after running `streamlit run app.py`:

1. App opens at `http://localhost:8501` without console errors.
2. Tab 1: `outputs/panels/slide1_target_and_simulation.png` renders, or a blue info box appears (correct fallback).
3. Tab 2: Sliders respond. "Run Simulation" button triggers computation. GM field + agent snapshot appear. Metric cards render below.
4. Tab 3: Selectbox switches between sweeps A/B/C. "Load pregenerated" radio shows the correct heatmap PNG. "Run live" shows a spinner then the computed heatmap.
5. Tab 4: All four GIFs animate. If GIF files are missing, info boxes appear.
6. Tab 5: Expandable model cards show equations and a "Run quick demo" button that works.
7. Tab 6: LLM notebook text renders without broken markdown.
8. Tab 7: Slide outlines and speaker scripts are readable.
9. Sidebar: Collapsed by default. No content overflow.
10. No Unicode rendering artifacts (no em-dashes, no smart quotes, no arrows in output text).

---

## Files

| File | Role |
|---|---|
| `app.py` | Main Streamlit entry point |
| `assets/style.css` | All custom CSS |
| `assets/logo.svg` | 7-armed star ascidian SVG, embedded in header |
| `assets/favicon.svg` | Same SVG used as page icon |

## Run Command

```
streamlit run app.py
```

Opens at http://localhost:8501 by default.
