# Deployment: Hugging Face Spaces (Docker SDK)

Chirality Atlas runs on Hugging Face Spaces using the Docker SDK.
Streamlit serves on port 7860, which Spaces routes to the public URL.

No GPU required. No API keys. No external network calls at runtime.

---

## Step 1: Create a new Hugging Face Space

1. Log into https://huggingface.co
2. Click your profile -> New Space
3. Choose:
   - Space name: `chirality-atlas` (or any name)
   - SDK: **Docker**
   - Visibility: Public or Private
4. Click Create Space

---

## Step 2: Push the repo

Hugging Face Spaces use a Git remote.

```bash
# Add the HF Space as a remote (replace YOUR_USERNAME)
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/chirality-atlas

# Push
git push hf main
```

If prompted for credentials: use your Hugging Face username and a write-access token.
Create tokens at https://huggingface.co/settings/tokens.

---

## Step 3: Confirm port 7860

The Dockerfile already sets `--server.port=7860 --server.address=0.0.0.0`.
Hugging Face Spaces automatically routes port 7860 to the public URL.
No additional configuration is needed.

---

## Step 4: Wait for the build

After pushing, HF Spaces will:
1. Build the Docker image (2-5 minutes, first build; ~30 seconds for rebuilds)
2. Run `python healthcheck.py` inside the container
3. Start Streamlit on port 7860

Watch the build log in the Spaces interface. If it fails, read the log for the
failing check and fix the issue locally before pushing again.

---

## Step 5: Pre-generated assets (recommended for demo)

The Docker image does not include `outputs/` by default (it is in `.dockerignore`).
The app generates figures on demand when you click Run buttons in each tab.

For a demo where pre-computed phase diagrams appear instantly:

1. Generate assets locally: `python scripts/05_make_all_assets.py`
2. Remove or comment out the `outputs/` line in `.dockerignore`
3. Re-push to HF Spaces

The image will be ~150-300 MB larger but all figures are available without a wait.

Note: GIF files may be large (1-5 MB each). If image size is a concern,
include only `outputs/panels/` (the slide PNG panels) and omit movies.

---

## Local Docker test (before pushing)

```bash
docker build -t chirality-atlas-star .
docker run -p 7860:7860 chirality-atlas-star
```

Open http://localhost:7860 to verify before pushing to HF.

---

## Troubleshooting

**Build fails at pip install:**
Some packages require build tools in the slim image. The Dockerfile already installs
`libopenblas-dev` and `libglib2.0-0`. If you see additional missing library errors,
add them to the `apt-get install` line in the Dockerfile.

**Healthcheck fails:**
The build log shows which check failed. Most common causes:
- scipy not finding OpenBLAS: fixed by `libopenblas-dev` (already in Dockerfile)
- Wrong working directory: the CMD runs from `/app`, which is the repo root

**App starts but pages are blank:**
Check that `--server.headless=true` is set in the CMD (it is). If XSRF or CORS
errors appear in the browser console, check that `--server.enableCORS=false`
and `--server.enableXsrfProtection=false` are set (they are).

**Out of memory:**
HF free-tier Spaces have approximately 2 GB RAM.
Default GM preset uses grid_size=64 which requires about 200 MB.
If OOM occurs, reduce grid_size in the preset defaults in
`src/chirality/star_ascidian/hybrid_model.py` (change 64 to 32).

**Slow first load:**
The first run compiles matplotlib font caches and Python bytecode.
Subsequent loads in the same session are faster.

---

## Security notes

- No API keys, secrets, or credentials anywhere in the codebase.
- No outgoing network calls at runtime.
- All simulations use fixed seeds; outputs are deterministic.
- Generated figures are not persisted between container restarts.
- User inputs (sliders) only affect local simulation parameters; nothing is stored.
