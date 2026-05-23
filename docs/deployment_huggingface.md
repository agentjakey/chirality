# Deployment: Hugging Face Spaces (Docker SDK)

This app is deployed using the Docker SDK on Hugging Face Spaces.
It runs Streamlit on port 7860, which Spaces routes to the public URL.

No GPU is required. No API keys. No external network calls at runtime.

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

## Step 2: Push the repo to the Space

Hugging Face Spaces use a Git remote. Replace `YOUR_USERNAME` below.

```bash
# Add the HF Space as a remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/chirality-atlas

# Push
git push hf main
```

If prompted for credentials, use your Hugging Face username and an access token
(not your password). Tokens are created at https://huggingface.co/settings/tokens

---

## Step 3: Confirm port 7860

The Dockerfile already uses `--server.port=7860 --server.address=0.0.0.0`.
Hugging Face Spaces automatically maps port 7860 to the public URL.

No additional configuration is needed.

---

## Step 4: Wait for the build

After pushing, HF Spaces will:
1. Build the Docker image (2-5 minutes, first build)
2. Run `python healthcheck.py` to verify the environment
3. Start Streamlit on port 7860

Watch the build log in the Spaces interface. If it fails, read the log for errors.

---

## Step 5: Use pre-generated outputs for demo

The Docker image does not include `outputs/` (it is in `.dockerignore`).
The app generates figures on demand when you click Run buttons in each tab.

For a demo where you want pre-computed phase diagrams to appear instantly:
1. Run `python scripts/make_all_assets.py` locally
2. Remove `outputs/` from `.dockerignore` temporarily
3. Push to HF Spaces

This makes the image larger (~100-200 MB for figures + GIFs) but avoids wait times
during live demo.

---

## Troubleshooting

**Build fails at pip install**: check that all packages in requirements.txt are
available on PyPI and have no platform-specific constraints.

**Healthcheck fails**: the build log will show which check failed.
Common cause: scipy or imageio not installed correctly in the slim image.
Fix: add `RUN apt-get update && apt-get install -y libopenblas-dev` before pip install.

**App starts but pages are blank**: Streamlit needs `--server.headless=true` (already set).
If you see XSRF or CORS errors, check that `--server.enableCORS=false` is set.

**Slow first load**: the first run generates matplotlib caches and compiles imports.
Subsequent loads are faster.

**Out of memory**: Hugging Face free-tier Spaces have limited RAM.
Reduce pattern grid size in `src/chirality/presets.py` (e.g., nx=ny=128 instead of 256).

---

## Security notes

- No API keys, secrets, or user data.
- No outgoing network calls at runtime.
- All simulations use fixed seeds; outputs are deterministic.
- Generated figures are not persisted between restarts (unless you mount a volume).

---

## Local Docker test

```bash
docker build -t chirality-atlas .
docker run -p 7860:7860 chirality-atlas
```

Open http://localhost:7860 to test locally before pushing to HF.
