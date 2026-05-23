# UI Design Notes: Chirality Atlas Streamlit App

## Design concept

The app is meant to feel like three things simultaneously:
a scientific field notebook, a live simulation instrument, and a teaching tool.

It avoids AI-dashboard cliches (dark mode, neon, card grids, gradient blobs).
The aesthetic is warm, print-like, and deliberately analog in character.

---

## Color palette

| Role       | Hex       | Usage                                        |
|------------|-----------|----------------------------------------------|
| Background | #F7F3EA   | App background, warm off-white               |
| Ink        | #1F2421   | Primary text                                 |
| Accent     | #C15A3A   | Active tab indicator, primary buttons hover, borders |
| Green      | #315C4C   | Default button color, h3 headers, expander labels |
| Panel      | #FFFFFF   | Metric cards, expanders, sci-panel class     |
| Light panel| #EFE8DC   | Tab bar background, sidebar                  |
| Border     | #DDD5C8   | All dividers, card borders                   |

---

## Typography

Georgia serif throughout. Headers use letter-spacing and border-bottom rules.
No sans-serif except browser fallback. Metric labels are uppercased with tracking.

---

## Tab structure

| Tab | Purpose |
|-----|---------|
| Overview | Project framing, science narrative, key finding previews |
| Particle Lab | Run ABP / chiral ABP / Vicsek simulations interactively |
| Pattern Lab | Run Gray-Scott and variants interactively |
| Bridge Lab | Side-by-side comparison of both tracks, shared-principles section |
| Phase Atlas | Precomputed phase diagram heatmaps, downloadable |
| Presentation Mode | Slide-deck format for demo day / judges |
| Methods & Limits | Equations, known limitations, honest self-audit |

---

## Session state keys

| Key | Type | Description |
|-----|------|-------------|
| p_hist | ParticleHistory or None | Last particle simulation result |
| p_metrics | dict or None | Computed particle metrics |
| p_label | str | Display name of last particle run |
| pat_hist | FieldHistory or None | Last pattern simulation result |
| pat_metrics | dict or None | Computed pattern metrics |
| pat_label | str | Display name of last pattern run |
| bridge | dict or None | Bridge lab comparison data |
| pa_p_data | dict or None | Phase atlas particle sweep data |
| pa_gs_data | dict or None | Phase atlas Gray-Scott sweep data |

---

## Caching strategy

`@st.cache_data` is used for expensive preview runs that are triggered by sidebar
preset changes. These are short runs (1000 steps) for quick visual feedback.
Full runs store results in session_state so re-renders do not re-simulate.

Functions decorated with @st.cache_data:
- `_preview_particle(preset_name)` -- 1000-step quick run
- `_preview_pattern(preset_name)` -- 2000-step quick run
- `_cached_particle_sweep()` -- noise vs chirality sweep
- `_cached_pattern_sweep()` -- Gray-Scott F-k sweep

---

## Simulation runtime limits

To keep the UI responsive on a laptop, the following caps are in place:
- Particle Lab: N <= 200 particles, n_steps <= 3000
- Pattern Lab: nx/ny <= 128 for interactive runs; 256 for preset previews
- Phase Atlas: uses precomputed data or runs a 6x6 grid at N=80

---

## Download buttons

All figures are downloadable as PNG via `_download_btn()` which renders to
BytesIO and passes to `st.download_button`. No file is written to disk
during interactive use.

---

## CSS customization

Loaded from `assets/style.css` via `st.markdown(..., unsafe_allow_html=True)`.

Custom classes used in the app:
- `.sci-panel` -- white bordered container for structured content
- `.slide-block` -- presentation slide card with left accent border
- `.fig-caption` -- italic gray caption below figures

---

## Assets

| File | Description |
|------|-------------|
| `assets/style.css` | Full custom stylesheet |
| `assets/logo.svg` | 44x44 chirality orbit icon, used in Overview header |
| `assets/favicon.svg` | 32x32 simplified version for browser tab |

---

## Run command

```bash
streamlit run app.py
```

Opens at http://localhost:8501 by default.
