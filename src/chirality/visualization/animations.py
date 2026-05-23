"""
GIF animation utilities for field and particle results.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from PIL import Image
import io

from .style import BG, INK, FIELD_CMAP, NEUTRAL, ACCENT, GREEN, CHIRALITY_CMAP, TITLE_FS, LABEL_FS
from ..model_library import ensure_dir


def save_field_gif(result, output_path, field="u", cmap=None, fps=8, dpi=80, title=None):
    """Save a GIF of the field evolving over snapshots.

    result: FieldResult
    field: "u" or "v"
    fps: frames per second
    """
    ensure_dir(os.path.dirname(output_path))

    if cmap is None:
        cmap = FIELD_CMAP

    if field == "u":
        snaps = result.snapshots_u
    else:
        snaps = result.snapshots_v

    if snaps is None or len(snaps) == 0:
        raise ValueError(f"No snapshots for field '{field}'")

    vmin = snaps.min()
    vmax = snaps.max()

    frames = []
    for i, snap in enumerate(snaps):
        fig, ax = plt.subplots(figsize=(4, 4), facecolor=BG, dpi=dpi)
        ax.set_facecolor(BG)

        L = result.params.get("L", 1.0)
        im = ax.imshow(
            snap, origin="lower", extent=[0, L, 0, L],
            cmap=cmap, vmin=vmin, vmax=vmax, interpolation="nearest"
        )
        ax.set_xlabel("x", fontsize=LABEL_FS, color=INK)
        ax.set_ylabel("y", fontsize=LABEL_FS, color=INK)
        ax.tick_params(colors=INK)

        if title is not None:
            ax.set_title(f"{title} (t={result.times[i]:.1f})", fontsize=TITLE_FS, color=INK)

        for spine in ax.spines.values():
            spine.set_edgecolor(INK)

        fig.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", facecolor=BG, dpi=dpi)
        buf.seek(0)
        frames.append(Image.open(buf).copy())
        plt.close(fig)

    duration_ms = int(1000 / fps)
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=duration_ms,
    )


def save_particle_gif(result, output_path, fps=10, dpi=80, title=None, color_by="omega"):
    """Save a GIF of particle positions over snapshots.

    result: ParticleResult
    color_by: "omega" or "theta" or "none"
    """
    ensure_dir(os.path.dirname(output_path))

    L = result.L
    omegas = result.omegas

    if color_by == "omega" and omegas.max() != omegas.min():
        norm = plt.Normalize(vmin=-abs(omegas).max(), vmax=abs(omegas).max())
        colors_arr = CHIRALITY_CMAP(norm(omegas))
    else:
        colors_arr = None

    frames = []
    for i in range(len(result.times)):
        fig, ax = plt.subplots(figsize=(4, 4), facecolor=BG, dpi=dpi)
        ax.set_facecolor(BG)
        ax.set_xlim(0, L)
        ax.set_ylim(0, L)

        pos = result.positions[i]
        theta = result.thetas[i]

        if colors_arr is not None:
            c = colors_arr
        elif color_by == "theta":
            norm_t = plt.Normalize(vmin=-np.pi, vmax=np.pi)
            c = plt.cm.hsv(norm_t(theta))
        else:
            c = NEUTRAL

        ax.scatter(pos[:, 0], pos[:, 1], c=c, s=8, alpha=0.85, linewidths=0)

        scale = L / 30.0
        ax.quiver(
            pos[:, 0], pos[:, 1],
            scale * np.cos(theta), scale * np.sin(theta),
            color=INK, alpha=0.25, width=0.003, headwidth=3, headlength=3,
            scale=1.0, scale_units="xy",
        )

        ax.set_xlabel("x", fontsize=LABEL_FS, color=INK)
        ax.set_ylabel("y", fontsize=LABEL_FS, color=INK)
        ax.tick_params(colors=INK)
        for spine in ax.spines.values():
            spine.set_edgecolor(INK)

        if title is not None:
            ax.set_title(f"{title} (t={result.times[i]:.2f})", fontsize=TITLE_FS, color=INK)

        fig.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", facecolor=BG, dpi=dpi)
        buf.seek(0)
        frames.append(Image.open(buf).copy())
        plt.close(fig)

    duration_ms = int(1000 / fps)
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=duration_ms,
    )
