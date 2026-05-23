"""
Core plotting functions for field and particle results.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from .style import (
    BG, INK, NEUTRAL, ACCENT, GREEN,
    FIELD_CMAP, PHASE_CMAP, CHIRALITY_CMAP,
    TITLE_FS, LABEL_FS, TICK_FS,
)


def plot_field(result, field="u", title=None, ax=None, cmap=None, vmin=None, vmax=None):
    """Plot the final state of a scalar field result.

    field: "u" or "v" -- which field to show
    Returns: fig, ax
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(4, 4), facecolor=BG)
        own_fig = True
    else:
        fig = ax.get_figure()
        own_fig = False

    if field == "u":
        data = result.u_final
    elif field == "v":
        data = result.v_final
    else:
        raise ValueError(f"Unknown field: {field}. Use 'u' or 'v'.")

    if cmap is None:
        cmap = FIELD_CMAP

    L = result.params.get("L", 1.0)
    im = ax.imshow(
        data,
        origin="lower",
        extent=[0, L, 0, L],
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        interpolation="nearest",
    )

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=TICK_FS, colors=INK)
    cbar.outline.set_edgecolor(INK)

    ax.set_xlabel("x", fontsize=LABEL_FS, color=INK)
    ax.set_ylabel("y", fontsize=LABEL_FS, color=INK)
    ax.tick_params(colors=INK, labelsize=TICK_FS)
    for spine in ax.spines.values():
        spine.set_edgecolor(INK)

    if title is not None:
        ax.set_title(title, fontsize=TITLE_FS, color=INK)

    if own_fig:
        fig.tight_layout()
    return fig, ax


def plot_phase_diagram(
    x_vals, y_vals, z_grid, xlabel, ylabel, title=None,
    cmap=None, ax=None, vmin=None, vmax=None
):
    """Plot a 2D phase diagram heatmap.

    x_vals, y_vals: 1D arrays of parameter values
    z_grid: 2D array of shape (len(y_vals), len(x_vals))
    Returns: fig, ax
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(5, 4), facecolor=BG)
        own_fig = True
    else:
        fig = ax.get_figure()
        own_fig = False

    if cmap is None:
        cmap = PHASE_CMAP

    im = ax.pcolormesh(
        x_vals, y_vals, z_grid,
        cmap=cmap, vmin=vmin, vmax=vmax, shading="nearest"
    )

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=TICK_FS, colors=INK)
    cbar.outline.set_edgecolor(INK)

    ax.set_xlabel(xlabel, fontsize=LABEL_FS, color=INK)
    ax.set_ylabel(ylabel, fontsize=LABEL_FS, color=INK)
    ax.tick_params(colors=INK, labelsize=TICK_FS)
    for spine in ax.spines.values():
        spine.set_edgecolor(INK)

    if title is not None:
        ax.set_title(title, fontsize=TITLE_FS, color=INK)

    if own_fig:
        fig.tight_layout()
    return fig, ax


def plot_particle_snapshot(result, snapshot_idx=-1, title=None, ax=None, color_by="omega"):
    """Plot a particle snapshot.

    color_by: "omega" (uses chirality colormap), "theta" (direction), or "none" (neutral)
    Returns: fig, ax
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(4, 4), facecolor=BG)
        own_fig = True
    else:
        fig = ax.get_figure()
        own_fig = False

    pos = result.positions[snapshot_idx]
    theta = result.thetas[snapshot_idx]
    L = result.L

    ax.set_facecolor(BG)
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)

    if color_by == "omega":
        omegas = result.omegas
        if omegas.max() == omegas.min():
            colors = [NEUTRAL] * len(pos)
        else:
            norm = plt.Normalize(vmin=-abs(omegas).max(), vmax=abs(omegas).max())
            cmap_vals = CHIRALITY_CMAP(norm(omegas))
            colors = cmap_vals
    elif color_by == "theta":
        norm = plt.Normalize(vmin=-np.pi, vmax=np.pi)
        colors = plt.cm.hsv(norm(theta))
    else:
        colors = NEUTRAL

    ax.scatter(pos[:, 0], pos[:, 1], c=colors, s=8, alpha=0.8, linewidths=0)

    scale = L / 30.0
    ax.quiver(
        pos[:, 0], pos[:, 1],
        scale * np.cos(theta), scale * np.sin(theta),
        color=INK, alpha=0.3, width=0.003, headwidth=3, headlength=3,
        scale=1.0, scale_units="xy",
    )

    ax.set_xlabel("x", fontsize=LABEL_FS, color=INK)
    ax.set_ylabel("y", fontsize=LABEL_FS, color=INK)
    ax.tick_params(colors=INK, labelsize=TICK_FS)
    for spine in ax.spines.values():
        spine.set_edgecolor(INK)

    if title is not None:
        ax.set_title(title, fontsize=TITLE_FS, color=INK)

    if own_fig:
        fig.tight_layout()
    return fig, ax


def plot_trajectories(result, n_particles=20, title=None, ax=None):
    """Plot particle trajectories over all snapshots.

    Shows the first n_particles as colored traces.
    Returns: fig, ax
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(4, 4), facecolor=BG)
        own_fig = True
    else:
        fig = ax.get_figure()
        own_fig = False

    L = result.L
    ax.set_facecolor(BG)
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)

    n = min(n_particles, result.N)
    colors = plt.cm.tab20(np.linspace(0, 1, n))

    for i in range(n):
        x = result.positions[:, i, 0]
        y = result.positions[:, i, 1]
        ax.plot(x, y, color=colors[i], alpha=0.6, linewidth=0.8)
        ax.scatter(x[-1:], y[-1:], color=colors[i], s=15, zorder=3)

    ax.set_xlabel("x", fontsize=LABEL_FS, color=INK)
    ax.set_ylabel("y", fontsize=LABEL_FS, color=INK)
    ax.tick_params(colors=INK, labelsize=TICK_FS)
    for spine in ax.spines.values():
        spine.set_edgecolor(INK)

    if title is not None:
        ax.set_title(title, fontsize=TITLE_FS, color=INK)

    if own_fig:
        fig.tight_layout()
    return fig, ax
