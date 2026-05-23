"""
Generate animation GIFs for the Chirality Atlas.

Outputs (outputs/videos/):
  particle_chiral_vortex.gif
  particle_boundary_edge_current.gif
  pattern_gray_scott_growth.gif
  pattern_chiral_source_growth.gif

Falls back to frame sequence directories if imageio is unavailable.

Run from repo root: python scripts/make_video.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import matplotlib
matplotlib.use("Agg")

from chirality.particle_sim import simulate_chiral_abp
from chirality.pattern_sim import simulate_gray_scott, simulate_chiral_source_gray_scott
from chirality.plotting import make_particle_frames, make_field_frames
from chirality.export import save_frames_as_gif, save_frame_sequence, ensure_dir

OUT = "outputs/videos"
ensure_dir(OUT)


def make_gif(frames, path, fps=12):
    """Try to write a GIF; fall back to a frame sequence directory."""
    if not frames:
        print(f"  No frames generated for {path}")
        return
    print(f"  Writing {len(frames)} frames -> {path}")
    ok = save_frames_as_gif(frames, path, fps=fps)
    if not ok:
        seq_dir = path.replace(".gif", "_frames")
        print(f"  GIF write failed. Saving frame sequence to {seq_dir}/")
        save_frame_sequence(frames, seq_dir)


# ---------------------------------------------------------------------------
print("[1] Chiral vortex gas animation")
hist = simulate_chiral_abp(
    N=200, L=10.0, v0=0.5, Dr=0.2, omega=2.0, chirality_mode="right",
    dt=0.01, n_steps=800, seed=42, boundary_mode="periodic",
    repulsion=False, save_every=8,
)
frames = make_particle_frames(hist, every_n=2, figsize=(4, 4))
make_gif(frames, f"{OUT}/particle_chiral_vortex.gif", fps=12)
print()

# ---------------------------------------------------------------------------
print("[2] Boundary edge current animation")
hist = simulate_chiral_abp(
    N=200, L=10.0, v0=0.5, Dr=0.3, omega=3.0, chirality_mode="right",
    dt=0.01, n_steps=800, seed=42, boundary_mode="circular_trap",
    repulsion=False, save_every=8,
)
frames = make_particle_frames(hist, every_n=2, figsize=(4, 4))
make_gif(frames, f"{OUT}/particle_boundary_edge_current.gif", fps=12)
print()

# ---------------------------------------------------------------------------
print("[3] Gray-Scott growth animation")
hist = simulate_gray_scott(
    nx=128, ny=128, Du=0.16, Dv=0.08, F=0.035, k=0.065,
    dt=1.0, n_steps=5000, seed=42, save_every=250, n_seeds=12,
)
frames = make_field_frames(hist.snapshots_v, figsize=(4, 4))
make_gif(frames, f"{OUT}/pattern_gray_scott_growth.gif", fps=8)
print()

# ---------------------------------------------------------------------------
print("[4] Chiral source growth animation")
hist = simulate_chiral_source_gray_scott(
    nx=128, ny=128, Du=0.16, Dv=0.08, F=0.035, k=0.065,
    dt=1.0, n_steps=5000, seed=42,
    source_strength=0.02, source_omega=0.1,
    source_r_orbit=0.2, source_sigma=0.05,
    save_every=250, perturbation_size=5, n_seeds=None,
)
frames = make_field_frames(hist.snapshots_v, figsize=(4, 4))
make_gif(frames, f"{OUT}/pattern_chiral_source_growth.gif", fps=8)
print()

print("Done. Videos written to outputs/videos/")
