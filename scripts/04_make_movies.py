"""
Generate GIF movies for the star ascidian presentation.

Outputs:
  outputs/movies/star_formation_clean.gif
  outputs/movies/chiral_twist_emergence.gif
  outputs/movies/phase_transition_parameter_sweep.gif
  outputs/movies/active_zooid_dynamics.gif

Pillow is required for GIF output. PNG frame fallback if unavailable.
Run from repo root: python scripts/04_make_movies.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("WARNING: Pillow not found. PNG frame fallback will be used.")

import io

from chirality.model_library import ensure_dir
from chirality.star_ascidian.hybrid_model import simulate_star_ascidian_colony
from chirality.star_ascidian.zooid_agents import simulate_zooid_agents
from chirality.star_ascidian.center_field import generate_star_centers
from chirality.visualization.style import (
    BG, INK, ACCENT, GREEN, NEUTRAL, BORDER,
    LABEL_FS, TICK_FS,
)

OUT = os.path.join("outputs", "movies")
ensure_dir(OUT)

_PALETTE = [ACCENT, GREEN, "#7B6B8B", "#8B7355", "#4A7B8B", "#8B4A6B", "#6B8B4A"]
_DPI = 72
_FIG_SIZE = (4, 4)


def _fig_to_pil(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=BG, dpi=_DPI)
    buf.seek(0)
    img = Image.open(buf).copy()
    buf.close()
    return img


def _save_frames_gif(frames, path, fps=8):
    if not frames:
        return
    duration_ms = int(1000 / max(1, fps))
    frames[0].save(
        path, save_all=True, append_images=frames[1:],
        loop=0, duration=duration_ms, optimize=False,
    )
    print(f"  Saved: {path}  ({len(frames)} frames, {fps} fps)")


def _png_fallback(figs, path):
    base = path.replace(".gif", "_frames")
    ensure_dir(base)
    for i, fig in enumerate(figs):
        fig.savefig(os.path.join(base, f"frame_{i:04d}.png"),
                    dpi=_DPI, bbox_inches="tight", facecolor=BG)
        plt.close(fig)
    print(f"  [fallback] PNG frames saved to {base}/")


def _render_zooid_frame(zooid_result, snap_idx, title="",
                         xlim=None, ylim=None):
    pos = zooid_result.positions[snap_idx]
    K = zooid_result.K
    L = zooid_result.L
    assignments = zooid_result.assignments
    centers = zooid_result.centers
    t = (zooid_result.times[snap_idx]
         if snap_idx < len(zooid_result.times) else snap_idx)

    if xlim is None:
        xlim = (0, L)
    if ylim is None:
        ylim = (0, L)

    fig, ax = plt.subplots(figsize=_FIG_SIZE, facecolor=BG, dpi=_DPI)
    ax.set_facecolor(BG)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")

    for k in range(K):
        mask = assignments == k
        ax.scatter(pos[mask, 0], pos[mask, 1], s=12,
                   color=_PALETTE[k % len(_PALETTE)],
                   alpha=0.85, linewidths=0, zorder=2)
    ax.scatter(centers[:, 0], centers[:, 1], s=35,
               color=INK, marker="+", linewidths=1.4, zorder=4)

    ax.set_xlabel("x", fontsize=LABEL_FS, color=INK)
    ax.set_ylabel("y", fontsize=LABEL_FS, color=INK)
    ax.tick_params(colors=INK, labelsize=TICK_FS)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)
    ax.set_title(f"{title}  t={t:.1f}" if title else f"t={t:.1f}",
                 fontsize=LABEL_FS, color=INK)
    fig.tight_layout()
    return fig


def make_star_formation_clean(seed=42):
    """Star arm formation animation for the clean preset."""
    path = os.path.join(OUT, "star_formation_clean.gif")
    print("\nMaking star_formation_clean.gif ...")

    result = simulate_star_ascidian_colony(
        preset="clean_star_systems", seed=seed,
        n_snapshots=20,
    )
    zr = result.zooid
    n_snaps = zr.positions.shape[0]
    indices = list(range(0, n_snaps, max(1, n_snaps // 16)))[:16]

    if HAS_PIL:
        frames = [_fig_to_pil(_render_zooid_frame(zr, i, "Clean stars"))
                  for i in indices]
        for fig in plt.get_fignums():
            plt.close(fig)
        _save_frames_gif(frames, path, fps=6)
    else:
        figs = [_render_zooid_frame(zr, i, "Clean stars") for i in indices]
        _png_fallback(figs, path)


def make_chiral_twist_emergence(seed=42):
    """Chiral arm twist animation."""
    path = os.path.join(OUT, "chiral_twist_emergence.gif")
    print("\nMaking chiral_twist_emergence.gif ...")

    result = simulate_star_ascidian_colony(
        preset="chiral_twisted_stars", seed=seed,
        n_snapshots=20,
    )
    zr = result.zooid
    n_snaps = zr.positions.shape[0]
    indices = list(range(0, n_snaps, max(1, n_snaps // 16)))[:16]

    if HAS_PIL:
        frames = [_fig_to_pil(_render_zooid_frame(zr, i, "Chiral twist"))
                  for i in indices]
        for fig in plt.get_fignums():
            plt.close(fig)
        _save_frames_gif(frames, path, fps=6)
    else:
        figs = [_render_zooid_frame(zr, i, "Chiral twist") for i in indices]
        _png_fallback(figs, path)


def make_phase_transition_sweep(seed=42):
    """Sequence of final states at increasing omega values."""
    path = os.path.join(OUT, "phase_transition_parameter_sweep.gif")
    print("\nMaking phase_transition_parameter_sweep.gif ...")

    omega_vals = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.5, 5.0]

    figs = []
    pil_frames = []

    for omega in omega_vals:
        mode = "chiral_twist" if omega > 0 else "radial_clean"
        fd = generate_star_centers(
            grid_size=32, L=10.0, Da=0.05, Dh=5.0,
            mu_a=0.05, mu_h=0.05, rho=0.1, rho_0=0.001, kappa=0.1,
            dt=0.5, n_steps=1200, n_snapshots=2, min_distance=2.0, seed=seed,
        )
        centers = fd["centers"]
        if len(centers) == 0:
            centers = np.array([[2.5, 2.5], [7.5, 7.5]])

        zr = simulate_zooid_agents(
            centers=centers, n_per_center=21, n_arms=7,
            L=10.0, r_target=1.5, v0=0.05, Dr=0.04, omega=omega,
            k_attract=0.3, k_radial=2.0, k_angular=0.6,
            k_ev=0.4, sigma_ev=0.18, dt=0.02, n_steps=200,
            n_snapshots=2, mode=mode, boundary="periodic",
            seed=seed + 1,
        )

        pos = zr.positions[-1]
        K = zr.K
        L = zr.L
        assignments = zr.assignments

        fig, ax = plt.subplots(figsize=_FIG_SIZE, facecolor=BG, dpi=_DPI)
        ax.set_facecolor(BG)
        ax.set_xlim(0, L)
        ax.set_ylim(0, L)
        ax.set_aspect("equal")

        for k in range(K):
            mask = assignments == k
            ax.scatter(pos[mask, 0], pos[mask, 1], s=12,
                       color=_PALETTE[k % len(_PALETTE)],
                       alpha=0.85, linewidths=0, zorder=2)
        ax.scatter(zr.centers[:, 0], zr.centers[:, 1], s=35,
                   color=INK, marker="+", linewidths=1.4, zorder=4)

        ax.set_title(f"omega = {omega:.1f}", fontsize=LABEL_FS, color=INK)
        ax.tick_params(colors=INK, labelsize=TICK_FS)
        for sp in ax.spines.values():
            sp.set_edgecolor(BORDER)
        ax.set_xlabel("x", fontsize=LABEL_FS, color=INK)
        ax.set_ylabel("y", fontsize=LABEL_FS, color=INK)
        fig.tight_layout()

        if HAS_PIL:
            pil_frames.append(_fig_to_pil(fig))
            plt.close(fig)
        else:
            figs.append(fig)

    if HAS_PIL:
        _save_frames_gif(pil_frames, path, fps=2)
    else:
        _png_fallback(figs, path)


def make_active_zooid_dynamics(seed=42):
    """Zoomed animation of a single center showing agent dynamics."""
    path = os.path.join(OUT, "active_zooid_dynamics.gif")
    print("\nMaking active_zooid_dynamics.gif ...")

    result = simulate_star_ascidian_colony(
        preset="clean_star_systems", seed=seed,
        n_snapshots=20,
    )
    zr = result.zooid

    # Zoom to first center
    if len(zr.centers) > 0:
        cx, cy = zr.centers[0]
    else:
        cx, cy = zr.L / 2, zr.L / 2
    zoom_r = 2.5 * zr.r_target
    xlim = (cx - zoom_r, cx + zoom_r)
    ylim = (cy - zoom_r, cy + zoom_r)

    n_snaps = zr.positions.shape[0]
    indices = list(range(0, n_snaps, max(1, n_snaps // 16)))[:16]

    if HAS_PIL:
        frames = [_fig_to_pil(
            _render_zooid_frame(zr, i, "Zooid dynamics", xlim=xlim, ylim=ylim)
        ) for i in indices]
        for fig in plt.get_fignums():
            plt.close(fig)
        _save_frames_gif(frames, path, fps=6)
    else:
        figs = [_render_zooid_frame(zr, i, "Zooid dynamics",
                                    xlim=xlim, ylim=ylim)
                for i in indices]
        _png_fallback(figs, path)


def main():
    print("=" * 60)
    print("Chirality Atlas: Movie Generation")
    print(f"Output directory: {OUT}")
    print(f"Pillow available: {HAS_PIL}")
    print("=" * 60)

    make_star_formation_clean(seed=42)
    make_chiral_twist_emergence(seed=42)
    make_phase_transition_sweep(seed=42)
    make_active_zooid_dynamics(seed=42)

    print("\n" + "=" * 60)
    print("Movie generation complete.")


if __name__ == "__main__":
    main()
