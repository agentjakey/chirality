# Local Deployment

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
streamlit run app.py
```

The app opens at http://localhost:8501

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

The app opens at http://localhost:8501

---

## Without a virtual environment

```bash
pip install -r requirements.txt
python healthcheck.py
streamlit run app.py
```

On systems where pip is managed (e.g., Ubuntu 22.04+), you may need:
```bash
pip install --break-system-packages -r requirements.txt
```

---

## Generating all figures

Run these scripts from the repo root to generate all outputs before launching the app.
Total estimated time: 30-50 minutes.

```bash
python scripts/run_particle_demo.py
python scripts/run_pattern_demo.py
python scripts/run_phase_sweeps.py
python scripts/make_video.py
python scripts/make_summary_panels.py
```

Or run everything at once:
```bash
python scripts/make_all_assets.py
```

The Streamlit app can also generate figures on demand by clicking the Run buttons in each tab.

---

## Troubleshooting

**Streamlit version conflict**: this app requires streamlit >= 1.30. Run `pip show streamlit` to check.

**imageio not installed**: GIF generation falls back to saving frame sequences. Install with `pip install imageio Pillow`.

**Port already in use**: change the port with `streamlit run app.py --server.port=8502`.

**Import errors**: run `python scripts/smoke_test.py` to diagnose which module is failing.
