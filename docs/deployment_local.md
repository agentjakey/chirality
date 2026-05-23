# Local Deployment: Chirality Atlas Star Ascidian

## Prerequisites

- Python 3.10 or higher
- Git

---

## macOS / Linux

```bash
git clone https://github.com/agentjakey/chirality.git
cd chirality

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python healthcheck.py
```

If healthcheck prints `PASS: all checks passed.`, start the app:

```bash
streamlit run app.py
```

Opens at http://localhost:8501

---

## Windows (PowerShell)

```powershell
git clone https://github.com/agentjakey/chirality.git
cd chirality

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

python healthcheck.py
streamlit run app.py
```

---

## Without a virtual environment

```bash
pip install -r requirements.txt
python healthcheck.py
streamlit run app.py
```

On Ubuntu 22.04+ or similar managed environments:
```bash
pip install --break-system-packages -r requirements.txt
```

---

## Generating all presentation assets

Run from repo root. Estimated time: 15-30 minutes.

```bash
python scripts/05_make_all_assets.py
```

This generates:
- `outputs/panels/` -- 6 slide-ready PNG panels
- `outputs/movies/` -- 4 GIF animations (requires Pillow)
- `outputs/star_ascidian/` -- per-preset demo figures
- `outputs/phase_diagrams/` -- 4 parameter sweep heatmaps
- `outputs/data/` -- metrics CSV, phase diagrams CSV, presets JSON

The Streamlit app works without pre-generated assets. Missing assets show
a blue info box with instructions.

---

## Verification

```bash
python healthcheck.py             # 8 checks; prints PASS
python scripts/06_final_smoke_test.py   # 53 checks; prints PASS
python -m compileall src scripts  # syntax check
```

---

## Troubleshooting

**Streamlit version conflict:** This app requires streamlit >= 1.30.
Check with `pip show streamlit`. Upgrade with `pip install --upgrade streamlit`.

**scipy not found:** Install with `pip install scipy`.

**GIFs not generating:** Pillow is required for GIF output.
Install with `pip install Pillow`. If Pillow is unavailable, numbered PNG
frame sequences are saved instead.

**Port already in use:** Change port with:
```bash
streamlit run app.py --server.port=8502
```

**Import errors:** Run `python healthcheck.py` to identify which module is failing.
Most import errors are caused by running from a directory other than the repo root.
Always run from the `chirality/` directory (where `app.py` is).

**Slow simulation in Tab 2:** The default preset runs GM at grid_size=64 for 3000 steps.
On a slow machine, reduce these in the Model Builder sliders before clicking Run.
A warning appears if the settings will be slow.
