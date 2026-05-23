"""
GIF animation utilities for field, particle, and zooid results.

Requires Pillow for GIF output. If Pillow is unavailable, falls back
to saving numbered PNG frames and prints a message.
"""

import os
import io
import numpy as np
import matplotlib.pyplot as plt

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from .style import (
    BG, INK, FIELD_CMAP, NEUTRAL, ACCENT, GREEN,
    CHIRALITY_CMAP, TITLE_FS, LABEL_FS, TICK_FS, BORDER,
    ZOOID_PALETTE,
)
from ..model_library import ensure_dir

_ZOOID_BG = "#0D1117"
_ZOOID_CENTER_COLOR = "#FFFFFF"


def _frames_to_gif(frames, output_path, fps):
    """Save list of PIL Images as GIF, or PNG sequence if Pillow unavailable."""
    if HAS_PIL and frames:
        duration_ms = int(1000 / max(1, fps))
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            loop=0,
            duration=duration_ms,
            optimize=False,
        )
        return True
    return False


def _save_png_fallback(fig_list, output_path):
    """Save PNG frames when Pillow is unavailable."""
    base = output_path.replace(".gif", "_frames")
    ensure_dir(base)
    for i, fig in enumerate(fig_list):
        frame_path = os.path.join(base, f"frame_{i:04d}.png")
        fig.savefig(frame_path, dpi=80, bbox_inches="tight", facecolor=BG)
    print(f"  [fallback] Pillow not available. Saved {len(fig_list)} PNG frames to {base}/")


def _fig_to_pil(fig, dpi=80):
    """Render a matplotlib figure to a PIL Image."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=BG, dpi=dpi)
    buf.seek(0)
    img = Image.open(buf).copy()
    buf.close()
    return img


def save_field_gif(result, output_path, field="u", cmap=None, fps=8, dpi=80, title=None):
    """Save a GIF of a scalar field evolving over snapshots.

    result: FieldResult with snapshots_u / snapshots_v
    field: "u" or "v"
    """
    ensure_dir(os.path.dirname(output_path) or ".")

    if cmap is None:
        cmap = FIELD_CMAP

    snaps = result.snapshots_u if field == "u" else result.snapshots_v
    if snaps is None or len(snaps) == 0:
        raise ValueError(f"No snapshots for field '{field}'")

    vmin, vmax = float(snaps.min()), float(snaps.max())
    L = result.params.get("L", 1.0)

    pil_frames = []
    fig_list = []

    for i, snap in enumerate(snaps):
        fig, ax = plt.subplots(figsize=(4, 4), facecolor=BG, dpi=dpi)
        ax.set_facecolor(BG)
        ax.imshow(snap, origin="lower", extent=[0, L, 0, L],
                  cmap=cmap, vmin=vmin, vmax=vmax, interpolation="nearest")
        ax.set_xlabel("x", fontsize=LABEL_FS, color=INK)
        ax.set_ylabel("y", fontsize=LABEL_FS, color=INK)
        ax.tick_params(colors=INK, labelsize=TICK_FS)
        for sp in ax.spines.values():
            sp.set_edgecolor(BORDER)
        t_label = f"t={result.times[i]:.1f}" if i < len(result.times) else f"frame {i}"
        ax.set_title(f"{title}  {t_label}" if title else t_label,
                     fontsize=TITLE_FS, color=INK)
        fig.tight_layout()

        if HAS_PIL:
            pil_frames.append(_fig_to_pil(fig, dpi))
            plt.close(fig)
        else:
            fig_list.append(fig)

    if HAS_PIL:
        _frames_to_gif(pil_frames, output_path, fps)
    else:
        _save_png_fallback(fig_list, output_path)
        for fig in fig_list:
            plt.close(fig)


def save_particle_gif(result, output_path, fps=10, dpi=80, title=None, color_by="omega"):
    """Save a GIF of particle positions over snapshots.

    result: ParticleResult
    color_by: "omega", "theta", or "none"
    """
    ensure_dir(os.path.dirname(output_path) or ".")

    L = result.L
    omegas = result.omegas
    omega_max = float(np.abs(omegas).max()) if omegas.max() != omegas.min() else 0.0

    pil_frames = []
    fig_list = []

    for i in range(len(result.times)):
        fig, ax = plt.subplots(figsize=(4, 4), facecolor=BG, dpi=dpi)
        ax.set_facecolor(BG)
        ax.set_xlim(0, L)
        ax.set_ylim(0, L)

        pos = result.positions[i]
        theta = result.thetas[i]

        if color_by == "omega" and omega_max > 0:
            norm = plt.Normalize(vmin=-omega_max, vmax=omega_max)
            c = CHIRALITY_CMAP(norm(omegas))
        elif color_by == "theta":
            c = plt.cm.hsv(plt.Normalize(-np.pi, np.pi)(theta))
        else:
            c = NEUTRAL

        ax.scatter(pos[:, 0], pos[:, 1], c=c, s=8, alpha=0.85, linewidths=0)
        scale = L / 30.0
        ax.quiver(pos[:, 0], pos[:, 1],
                  scale * np.cos(theta), scale * np.sin(theta),
                  color=INK, alpha=0.25, width=0.003,
                  headwidth=3, headlength=3, scale=1.0, scale_units="xy")
        ax.set_xlabel("x", fontsize=LABEL_FS, color=INK)
        ax.set_ylabel("y", fontsize=LABEL_FS, color=INK)
        ax.tick_params(colors=INK, labelsize=TICK_FS)
        for sp in ax.spines.values():
            sp.set_edgecolor(BORDER)
        t_label = f"t={result.times[i]:.2f}"
        ax.set_title(f"{title}  {t_label}" if title else t_label,
                     fontsize=TITLE_FS, color=INK)
        fig.tight_layout()

        if HAS_PIL:
            pil_frames.append(_fig_to_pil(fig, dpi))
            plt.close(fig)
        else:
            fig_list.append(fig)

    if HAS_PIL:
        _frames_to_gif(pil_frames, output_path, fps)
    else:
        _save_png_fallback(fig_list, output_path)
        for fig in fig_list:
            plt.close(fig)


def save_zooid_gif(
    zooid_result,
    output_path,
    fps=8,
    dpi=72,
    title=None,
    zoom_center=None,
    zoom_radius=None,
    frame_stride=1,
):
    """Save a GIF of zooid agent positions over simulation snapshots.

    zooid_result: ZooidResult from simulate_zooid_agents
    zoom_center:  (x, y) to zoom into one center; None = show full domain
    zoom_radius:  half-width of zoom window (default 2*r_target)
    frame_stride: only render every Nth snapshot (reduces file size)
    """
    ensure_dir(os.path.dirname(output_path) or ".")

    L = zooid_result.L
    centers = zooid_result.centers
    assignments = zooid_result.assignments
    K = zooid_result.K

    palette = ZOOID_PALETTE

    if zoom_center is not None:
        zc = np.array(zoom_center)
        zr = zoom_radius if zoom_radius is not None else 2.0 * zooid_result.r_target
        xlim = (zc[0] - zr, zc[0] + zr)
        ylim = (zc[1] - zr, zc[1] + zr)
    else:
        xlim = (0, L)
        ylim = (0, L)

    n_snaps = zooid_result.positions.shape[0]
    indices = list(range(0, n_snaps, max(1, frame_stride)))

    pil_frames = []
    fig_list = []

    for i in indices:
        pos = zooid_result.positions[i]
        t = zooid_result.times[i] if i < len(zooid_result.times) else i

        fig, ax = plt.subplots(figsize=(5, 5), facecolor=BG, dpi=dpi)
        ax.set_facecolor(_ZOOID_BG)
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_aspect("equal")

        for k in range(K):
            mask = assignments == k
            col = palette[k % len(palette)]
            ax.scatter(pos[mask, 0], pos[mask, 1],
                       s=14, color=col, alpha=0.85, linewidths=0, zorder=2)

        ax.scatter(centers[:, 0], centers[:, 1],
                   s=40, color=_ZOOID_CENTER_COLOR, marker="+", linewidths=1.4, zorder=4)

        ax.set_xlabel("x", fontsize=LABEL_FS, color="#AAAAAA")
        ax.set_ylabel("y", fontsize=LABEL_FS, color="#AAAAAA")
        ax.tick_params(colors="#AAAAAA", labelsize=TICK_FS)
        for sp in ax.spines.values():
            sp.set_edgecolor("#333333")
        t_label = f"t={t:.1f}"
        ax.set_title(f"{title}  {t_label}" if title else t_label,
                     fontsize=LABEL_FS, color=INK)
        fig.tight_layout()

        if HAS_PIL:
            pil_frames.append(_fig_to_pil(fig, dpi))
            plt.close(fig)
        else:
            fig_list.append(fig)

    if HAS_PIL:
        _frames_to_gif(pil_frames, output_path, fps)
    else:
        _save_png_fallback(fig_list, output_path)
        for fig in fig_list:
            plt.close(fig)
