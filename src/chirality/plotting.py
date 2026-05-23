"""
Visualization functions for the Chirality Atlas.

All functions return matplotlib Figure objects (not shown or saved here).
Use export.save_figure(fig, path) to write to disk.

Color conventions:
  neutral / non-chiral particles -- dark gray  #666666
  left-handed particles          -- terracotta #C15A3A
  right-handed particles         -- deep green #315C4C
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle

# ---------------------------------------------------------------------------
# Presentation-safe constants
# ---------------------------------------------------------------------------

_TITLE_FS  = 13
_LABEL_FS  = 11
_TICK_FS   = 9

_COLOR_LEFT    = "#C15A3A"   # terracotta -- left-handed
_COLOR_NEUTRAL = "#666666"   # dark gray  -- non-chiral
_COLOR_RIGHT   = "#315C4C"   # deep green -- right-handed

# Chirality colormap: terracotta -> gray -> deep green
_CHIRALITY_CMAP = LinearSegmentedColormap.from_list(
    "chirality",
    [_COLOR_LEFT, _COLOR_NEUTRAL, _COLOR_RIGHT],
)
# Legacy alias used by other modules and app.py
_PARTICLE_CMAP_CHIRAL = _CHIRALITY_CMAP

_FIELD_CMAP  = "YlOrBr"   # warm, projector-safe field colormap
_PHASE_CMAP  = "viridis"  # standard phase diagram colormap

_DARK_BG     = "#111111"   # particle plot background
_DARK_FIG    = "#1c1c1c"   # particle figure border


def _style_dark_ax(ax, title=""):
    """Apply dark-background styling to a particle axes."""
    ax.set_facecolor(_DARK_BG)
    ax.tick_params(colors="white", labelsize=_TICK_FS)
    for spine in ax.spines.values():
        spine.set_edgecolor("#444444")
    if title:
        ax.set_title(title, color="white", fontsize=_TITLE_FS, pad=6)
    ax.set_xlabel("x", color="white", fontsize=_LABEL_FS)
    ax.set_ylabel("y", color="white", fontsize=_LABEL_FS)


def _style_light_ax(ax, title=""):
    """Apply light-background styling to a field/phase axes."""
    ax.tick_params(labelsize=_TICK_FS)
    if title:
        ax.set_title(title, fontsize=_TITLE_FS, pad=6)
    ax.set_xlabel("x", fontsize=_LABEL_FS)
    ax.set_ylabel("y", fontsize=_LABEL_FS)


# ---------------------------------------------------------------------------
# Particle snapshots
# ---------------------------------------------------------------------------

def plot_particle_snapshot(
    positions,
    thetas,
    omegas,
    L,
    title="",
    show_arrows=True,
    arrow_scale=0.4,
    figsize=(6, 6),
):
    """Scatter plot of particles colored by chirality omega."""
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)
    ax.set_aspect("equal")

    omega_max = max(float(np.abs(omegas).max()), 1e-9)
    norm = mcolors.Normalize(vmin=-omega_max, vmax=omega_max)
    colors = _CHIRALITY_CMAP(norm(omegas))

    ax.scatter(
        positions[:, 0], positions[:, 1],
        c=colors, s=18, alpha=0.9, linewidths=0,
    )

    if show_arrows:
        dx = arrow_scale * np.cos(thetas)
        dy = arrow_scale * np.sin(thetas)
        ax.quiver(
            positions[:, 0], positions[:, 1], dx, dy,
            color="white", alpha=0.35, scale=1.0, scale_units="xy",
            angles="xy", headwidth=3, headlength=4, width=0.005,
        )

    sm = plt.cm.ScalarMappable(cmap=_CHIRALITY_CMAP, norm=norm)
    sm.set_array([])
    cb = plt.colorbar(sm, ax=ax, fraction=0.04, pad=0.02)
    cb.set_label("chirality omega", color="white", fontsize=_LABEL_FS)
    cb.ax.yaxis.set_tick_params(color="white", labelsize=_TICK_FS)
    plt.setp(cb.ax.yaxis.get_ticklabels(), color="white")

    _style_dark_ax(ax, title)
    fig.patch.set_facecolor(_DARK_FIG)
    fig.tight_layout()
    return fig


def plot_particle_snapshot_simple(
    positions,
    thetas,
    L,
    title="",
    color="#888888",
    figsize=(6, 6),
):
    """Simple particle snapshot without per-particle chirality color."""
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)
    ax.set_aspect("equal")
    ax.scatter(positions[:, 0], positions[:, 1], c=color, s=15, alpha=0.85, linewidths=0)
    dx = 0.35 * np.cos(thetas)
    dy = 0.35 * np.sin(thetas)
    ax.quiver(
        positions[:, 0], positions[:, 1], dx, dy,
        color="white", alpha=0.3, scale=1.0, scale_units="xy",
        angles="xy", headwidth=3, width=0.005,
    )
    _style_dark_ax(ax, title)
    fig.patch.set_facecolor(_DARK_FIG)
    fig.tight_layout()
    return fig


def plot_trajectory_trails(
    positions_history,
    thetas_history,
    omegas,
    L,
    n_trail=6,
    title="",
    figsize=(6, 6),
):
    """Particle positions with short trajectory trails.

    positions_history: (n_snapshots, N, 2)
    """
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)
    ax.set_aspect("equal")

    omega_max = max(float(np.abs(omegas).max()), 1e-9)
    norm = mcolors.Normalize(vmin=-omega_max, vmax=omega_max)

    n_snap = positions_history.shape[0]
    start = max(0, n_snap - n_trail)

    for t in range(start, n_snap - 1):
        alpha = 0.1 + 0.55 * (t - start) / max(n_trail - 1, 1)
        for p in range(positions_history.shape[1]):
            c = _CHIRALITY_CMAP(norm(omegas[p]))
            x0, y0 = positions_history[t, p]
            x1, y1 = positions_history[t + 1, p]
            if abs(x1 - x0) < L / 2 and abs(y1 - y0) < L / 2:
                ax.plot([x0, x1], [y0, y1], color=c, alpha=alpha, linewidth=0.8)

    final_pos = positions_history[-1]
    final_th  = thetas_history[-1]
    c_list = [_CHIRALITY_CMAP(norm(w)) for w in omegas]
    ax.scatter(final_pos[:, 0], final_pos[:, 1], c=c_list, s=16, zorder=5, linewidths=0)
    dx = 0.3 * np.cos(final_th)
    dy = 0.3 * np.sin(final_th)
    ax.quiver(
        final_pos[:, 0], final_pos[:, 1], dx, dy,
        color="white", alpha=0.4, scale=1.0, scale_units="xy",
        angles="xy", headwidth=3, width=0.005,
    )

    _style_dark_ax(ax, title)
    fig.patch.set_facecolor(_DARK_FIG)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Particle animation frames
# ---------------------------------------------------------------------------

def render_particle_frame(positions, thetas, omegas, L, figsize=(4, 4)):
    """Render one animation frame, return H x W x 3 uint8 array."""
    fig = plot_particle_snapshot(
        positions, thetas, omegas, L,
        show_arrows=True, arrow_scale=0.3, figsize=figsize,
    )
    fig.canvas.draw()
    buf = fig.canvas.buffer_rgba()
    frame = np.frombuffer(buf, dtype=np.uint8).reshape(
        fig.canvas.get_width_height()[::-1] + (4,)
    )[:, :, :3].copy()
    plt.close(fig)
    return frame


def make_particle_frames(history, every_n=1, figsize=(4, 4)):
    """Return list of RGB frames for all (or every_n-th) snapshots."""
    frames = []
    for i in range(0, len(history.positions), every_n):
        frame = render_particle_frame(
            history.positions[i], history.thetas[i], history.omegas, history.L,
            figsize=figsize,
        )
        frames.append(frame)
    return frames


# ---------------------------------------------------------------------------
# Field images
# ---------------------------------------------------------------------------

def plot_field(
    field,
    title="",
    cmap=_FIELD_CMAP,
    figsize=(6, 5),
    vmin=None,
    vmax=None,
):
    """Plot a single 2D field as an image with colorbar."""
    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(
        field.T, origin="lower", cmap=cmap,
        vmin=vmin, vmax=vmax, aspect="equal",
    )
    cb = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.ax.tick_params(labelsize=_TICK_FS)
    _style_light_ax(ax, title)
    fig.tight_layout()
    return fig


def plot_gray_scott_final(u, v, title="Gray-Scott", figsize=(11, 5)):
    """Side-by-side plot of u (substrate) and v (activator) fields."""
    fig, axes = plt.subplots(1, 2, figsize=figsize)

    im0 = axes[0].imshow(u.T, origin="lower", cmap="Blues_r", vmin=0, vmax=1, aspect="equal")
    axes[0].set_title("u  (substrate)", fontsize=_TITLE_FS)
    cb0 = plt.colorbar(im0, ax=axes[0], fraction=0.046)
    cb0.ax.tick_params(labelsize=_TICK_FS)

    im1 = axes[1].imshow(v.T, origin="lower", cmap=_FIELD_CMAP, vmin=0, vmax=0.5, aspect="equal")
    axes[1].set_title("v  (activator)", fontsize=_TITLE_FS)
    cb1 = plt.colorbar(im1, ax=axes[1], fraction=0.046)
    cb1.ax.tick_params(labelsize=_TICK_FS)

    for ax in axes:
        ax.tick_params(labelsize=_TICK_FS)

    fig.suptitle(title, fontsize=_TITLE_FS + 1, fontweight="bold", y=1.01)
    fig.tight_layout()
    return fig


def render_field_frame(v, figsize=(4, 4)):
    """Render one field frame as uint8 RGB array."""
    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(v.T, origin="lower", cmap=_FIELD_CMAP, vmin=0, vmax=0.5, aspect="equal")
    ax.axis("off")
    fig.tight_layout(pad=0)
    fig.canvas.draw()
    buf = fig.canvas.buffer_rgba()
    frame = np.frombuffer(buf, dtype=np.uint8).reshape(
        fig.canvas.get_width_height()[::-1] + (4,)
    )[:, :, :3].copy()
    plt.close(fig)
    return frame


def make_field_frames(snapshots_v, figsize=(4, 4)):
    """Return list of RGB frames from a list of v-field snapshots."""
    return [render_field_frame(v, figsize=figsize) for v in snapshots_v]


# ---------------------------------------------------------------------------
# Phase diagram heatmaps
# ---------------------------------------------------------------------------

def plot_phase_diagram(
    param1_values,
    param2_values,
    metric_grid,
    param1_label,
    param2_label,
    metric_label,
    title="",
    figsize=(7, 5),
    cmap=_PHASE_CMAP,
    vmin=None,
    vmax=None,
    coarse_note=True,
):
    """2D heatmap phase diagram.

    metric_grid shape: (len(param1_values), len(param2_values))
    coarse_note: append a coarse-grid warning to the title.
    """
    fig, ax = plt.subplots(figsize=figsize)
    extent = [
        param2_values[0], param2_values[-1],
        param1_values[0], param1_values[-1],
    ]
    im = ax.imshow(
        metric_grid, origin="lower", aspect="auto",
        extent=extent, cmap=cmap, vmin=vmin, vmax=vmax,
        interpolation="nearest",
    )
    cb = plt.colorbar(im, ax=ax)
    cb.set_label(metric_label, fontsize=_LABEL_FS)
    cb.ax.tick_params(labelsize=_TICK_FS)

    ax.set_xlabel(param2_label, fontsize=_LABEL_FS)
    ax.set_ylabel(param1_label, fontsize=_LABEL_FS)
    ax.tick_params(labelsize=_TICK_FS)

    full_title = title
    if coarse_note and title:
        n1 = len(param1_values)
        n2 = len(param2_values)
        full_title = f"{title}  [{n1}x{n2} grid]"
    if full_title:
        ax.set_title(full_title, fontsize=_TITLE_FS)

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Summary panels
# ---------------------------------------------------------------------------

def make_particle_summary_panel(
    hist_list,
    label_list,
    figsize=(16, 4),
):
    """Row of particle snapshots.

    hist_list: list of ParticleHistory objects
    label_list: list of title strings
    Returns a single Figure.
    """
    n = len(hist_list)
    fig, axes = plt.subplots(1, n, figsize=figsize)
    if n == 1:
        axes = [axes]
    fig.patch.set_facecolor(_DARK_FIG)

    for ax, hist, label in zip(axes, hist_list, label_list):
        pos = hist.positions[-1]
        th  = hist.thetas[-1]
        om  = hist.omegas
        L   = hist.L

        omega_max = max(float(np.abs(om).max()), 1e-9)
        norm = mcolors.Normalize(vmin=-omega_max, vmax=omega_max)
        colors = _CHIRALITY_CMAP(norm(om))

        ax.scatter(pos[:, 0], pos[:, 1], c=colors, s=12, alpha=0.9, linewidths=0)
        ax.set_xlim(0, L)
        ax.set_ylim(0, L)
        ax.set_aspect("equal")
        _style_dark_ax(ax, label)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_xticks([])
        ax.set_yticks([])

    fig.suptitle(
        "Particle track: ABP, Vicsek, and chiral extensions",
        color="white", fontsize=_TITLE_FS + 1, fontweight="bold", y=1.01,
    )
    fig.tight_layout()
    return fig


def make_pattern_summary_panel(
    hist_list,
    label_list,
    figsize=(16, 4),
):
    """Row of pattern v-field snapshots.

    hist_list: list of FieldHistory objects
    label_list: list of title strings
    Returns a single Figure.
    """
    n = len(hist_list)
    fig, axes = plt.subplots(1, n, figsize=figsize)
    if n == 1:
        axes = [axes]

    for ax, hist, label in zip(axes, hist_list, label_list):
        im = ax.imshow(
            hist.v_final.T, origin="lower",
            cmap=_FIELD_CMAP, vmin=0, vmax=0.5, aspect="equal",
        )
        ax.set_title(label, fontsize=_TICK_FS + 1)
        ax.set_xticks([])
        ax.set_yticks([])
        plt.colorbar(im, ax=ax, fraction=0.046)

    fig.suptitle(
        "Pattern track: Gray-Scott with gradient, obstacle, and chiral source",
        fontsize=_TITLE_FS + 1, fontweight="bold", y=1.01,
    )
    fig.tight_layout()
    return fig


def make_bridge_panel(
    particle_hists,
    particle_labels,
    field_hists,
    field_labels,
    figsize=(14, 8),
):
    """2x2 comparison of particle and field examples with a shared-principles note.

    particle_hists: list of 2 ParticleHistory objects (baseline, chiral)
    field_hists:    list of 2 FieldHistory objects  (baseline, chiral)
    """
    fig = plt.figure(figsize=figsize)
    fig.patch.set_facecolor("white")

    axes = []
    for idx in range(4):
        ax = fig.add_subplot(2, 3, idx + 1 if idx < 2 else idx + 2)
        axes.append(ax)
    ax_text = fig.add_subplot(2, 3, 3)
    ax_text2 = fig.add_subplot(2, 3, 6)

    # Particle row
    for col, (hist, label) in enumerate(zip(particle_hists, particle_labels)):
        ax = axes[col]
        pos = hist.positions[-1]
        om  = hist.omegas
        L   = hist.L
        omega_max = max(float(np.abs(om).max()), 1e-9)
        norm = mcolors.Normalize(vmin=-omega_max, vmax=omega_max)
        colors = _CHIRALITY_CMAP(norm(om))
        ax.scatter(pos[:, 0], pos[:, 1], c=colors, s=10, alpha=0.9, linewidths=0)
        ax.set_xlim(0, L)
        ax.set_ylim(0, L)
        ax.set_aspect("equal")
        ax.set_facecolor(_DARK_BG)
        ax.set_title(label, color="white", fontsize=_TICK_FS + 1)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_edgecolor("#444444")

    # Pattern row
    for col, (hist, label) in enumerate(zip(field_hists, field_labels)):
        ax = axes[2 + col]
        im = ax.imshow(
            hist.v_final.T, origin="lower",
            cmap=_FIELD_CMAP, vmin=0, vmax=0.5, aspect="equal",
        )
        ax.set_title(label, fontsize=_TICK_FS + 1)
        ax.set_xticks([])
        ax.set_yticks([])
        plt.colorbar(im, ax=ax, fraction=0.046)

    # Text panels
    ax_text.axis("off")
    ax_text.text(
        0.5, 0.5,
        "Particle track:\nABP + Vicsek models\nself-propelled agents\n\n"
        "Metric: polar order phi,\nswirl index, boundary\naccumulation",
        ha="center", va="center", fontsize=10, transform=ax_text.transAxes,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#EFE8DC", edgecolor="#DDD5C8"),
    )

    ax_text2.axis("off")
    ax_text2.text(
        0.5, 0.5,
        "Pattern track:\nGray-Scott reaction-diffusion\nself-organized fields\n\n"
        "Metric: pattern strength,\ncluster count,\nL-R asymmetry",
        ha="center", va="center", fontsize=10, transform=ax_text2.transAxes,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#EFE8DC", edgecolor="#DDD5C8"),
    )

    fig.suptitle(
        "Bridge: two models, one idea -- local handedness -> global structure",
        fontsize=_TITLE_FS + 1, fontweight="bold",
    )
    fig.tight_layout()
    return fig


def make_final_panel(
    particle_hist,
    field_hist,
    particle_label,
    field_label,
    particle_metric_str="",
    field_metric_str="",
    figsize=(14, 6),
):
    """Hero figure: best particle result side-by-side with best pattern result."""
    fig, axes = plt.subplots(1, 3, figsize=figsize,
                             gridspec_kw={"width_ratios": [5, 2, 5]})
    fig.patch.set_facecolor("white")

    # Left: particle
    ax_p = axes[0]
    pos = particle_hist.positions[-1]
    om  = particle_hist.omegas
    L   = particle_hist.L
    omega_max = max(float(np.abs(om).max()), 1e-9)
    norm = mcolors.Normalize(vmin=-omega_max, vmax=omega_max)
    colors = _CHIRALITY_CMAP(norm(om))
    ax_p.scatter(pos[:, 0], pos[:, 1], c=colors, s=14, alpha=0.9, linewidths=0)
    ax_p.set_xlim(0, L)
    ax_p.set_ylim(0, L)
    ax_p.set_aspect("equal")
    ax_p.set_facecolor(_DARK_BG)
    ax_p.set_title(particle_label, color="white", fontsize=_TITLE_FS)
    ax_p.set_xticks([])
    ax_p.set_yticks([])
    for spine in ax_p.spines.values():
        spine.set_edgecolor("#444444")

    # Center: key takeaway text
    ax_c = axes[1]
    ax_c.axis("off")
    msg = (
        "Chirality Atlas\n\n"
        "Can microscopic\nhandedness reshape\nliving matter?\n\n"
        "Particle result:\n" + (particle_metric_str or "swirl increases\nwith omega") + "\n\n"
        "Pattern result:\n" + (field_metric_str or "L-R asymmetry\ndetectable at\nomega > 0")
    )
    ax_c.text(
        0.5, 0.5, msg,
        ha="center", va="center", fontsize=9, transform=ax_c.transAxes,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#F7F3EA", edgecolor="#C15A3A", linewidth=2),
    )

    # Right: pattern
    ax_f = axes[2]
    im = ax_f.imshow(
        field_hist.v_final.T, origin="lower",
        cmap=_FIELD_CMAP, vmin=0, vmax=0.5, aspect="equal",
    )
    ax_f.set_title(field_label, fontsize=_TITLE_FS)
    ax_f.set_xticks([])
    ax_f.set_yticks([])
    plt.colorbar(im, ax=ax_f, fraction=0.046, label="v field")

    fig.suptitle(
        "Handedness as a control knob in active matter",
        fontsize=_TITLE_FS + 2, fontweight="bold",
    )
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Legacy combined summary (kept for app.py compatibility)
# ---------------------------------------------------------------------------

def plot_combined_summary(
    particle_histories,
    field_histories,
    particle_labels,
    field_labels,
    figsize=(16, 10),
):
    """Multi-panel summary: particle row on top, field row on bottom."""
    n_particle = len(particle_histories)
    n_field    = len(field_histories)
    n_cols     = max(n_particle, n_field)

    fig, axes = plt.subplots(2, n_cols, figsize=figsize)
    if n_cols == 1:
        axes = axes[:, np.newaxis]
    fig.patch.set_facecolor("white")

    for j, (hist, label) in enumerate(zip(particle_histories, particle_labels)):
        ax  = axes[0, j]
        pos = hist.positions[-1]
        om  = hist.omegas
        L   = hist.L
        omega_max = max(float(np.abs(om).max()), 1e-9)
        norm = mcolors.Normalize(vmin=-omega_max, vmax=omega_max)
        colors = _CHIRALITY_CMAP(norm(om))
        ax.scatter(pos[:, 0], pos[:, 1], c=colors, s=10, alpha=0.85, linewidths=0)
        ax.set_xlim(0, L)
        ax.set_ylim(0, L)
        ax.set_aspect("equal")
        ax.set_facecolor(_DARK_BG)
        ax.set_title(label, color="white", fontsize=_TICK_FS + 1)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_edgecolor("#444444")

    for j in range(n_particle, n_cols):
        axes[0, j].axis("off")

    for j, (fhist, label) in enumerate(zip(field_histories, field_labels)):
        ax = axes[1, j]
        im = ax.imshow(
            fhist.v_final.T, origin="lower", cmap=_FIELD_CMAP,
            vmin=0, vmax=0.5, aspect="equal",
        )
        plt.colorbar(im, ax=ax, fraction=0.046)
        ax.set_title(label, fontsize=_TICK_FS + 1)
        ax.set_xticks([])
        ax.set_yticks([])

    for j in range(n_field, n_cols):
        axes[1, j].axis("off")

    fig.suptitle(
        "Chirality Atlas: particle and pattern track overview",
        fontsize=_TITLE_FS + 1, fontweight="bold",
    )
    fig.tight_layout()
    return fig
