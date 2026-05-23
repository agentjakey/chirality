"""
Slide-ready panel figures for the 5-minute hackathon presentation.

All panels are 12 x 6.75 inches (16:9) at 120 dpi = 1440 x 810 px.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.patches import FancyArrowPatch

from .style import (
    BG, INK, ACCENT, GREEN, NEUTRAL, BORDER, PANEL_BG,
    FIELD_CMAP, CHIRALITY_CMAP,
    TITLE_FS, LABEL_FS, TICK_FS,
)
from ..model_library import ensure_dir

SLIDE_W = 12.0
SLIDE_H = 6.75
SLIDE_DPI = 120

_PALETTE = [ACCENT, GREEN, "#7B6B8B", "#8B7355", "#4A7B8B", "#8B4A6B", "#6B8B4A"]


def _slide_fig(ncols=1, nrows=1, width_ratios=None, height_ratios=None):
    fig, axes = plt.subplots(
        nrows, ncols, figsize=(SLIDE_W, SLIDE_H), facecolor=BG,
        gridspec_kw={
            k: v for k, v in
            [("width_ratios", width_ratios), ("height_ratios", height_ratios)]
            if v is not None
        },
    )
    return fig, axes


def _style_ax(ax, title=None):
    ax.set_facecolor(PANEL_BG)
    ax.tick_params(colors=INK, labelsize=TICK_FS)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)
    if title:
        ax.set_title(title, fontsize=LABEL_FS, color=INK, pad=5)


def _draw_schematic_star(ax, cx, cy, r_inner, r_outer, n_arms,
                         arm_deg=18, center_color=ACCENT, lobe_color=GREEN):
    """Draw a stylized star ascidian on ax in data coordinates."""
    disk = plt.Circle((cx, cy), r_inner, color=center_color, alpha=0.8, zorder=3)
    ax.add_patch(disk)

    arm_angles = np.linspace(0, 2.0 * np.pi, n_arms, endpoint=False)
    hw = np.deg2rad(arm_deg / 2.0)

    for ang in arm_angles:
        arc = np.linspace(ang - hw, ang + hw, 14)
        outer_x = r_outer * np.cos(arc) + cx
        outer_y = r_outer * np.sin(arc) + cy
        inner_x = r_inner * np.cos(arc) + cx
        inner_y = r_inner * np.sin(arc) + cy
        lobe_x = np.concatenate([inner_x, outer_x[::-1]])
        lobe_y = np.concatenate([inner_y, outer_y[::-1]])
        ax.add_patch(plt.Polygon(
            np.column_stack([lobe_x, lobe_y]),
            color=lobe_color, alpha=0.75, zorder=2,
        ))


def make_slide1_target_and_simulation(zooid_result, field_result, output_path):
    """Slide 1: Target schematic vs simulation snapshot side by side.

    zooid_result: ZooidResult from clean_star_systems preset
    field_result: dict from generate_star_centers (has 'field', 'centers')
    """
    ensure_dir(output_path.rsplit("/", 1)[0] if "/" in output_path else
               output_path.rsplit("\\", 1)[0] if "\\" in output_path else ".")

    fig, axes = plt.subplots(1, 3, figsize=(SLIDE_W, SLIDE_H), facecolor=BG,
                             gridspec_kw={"width_ratios": [1, 1, 1]})
    fig.suptitle("Star Ascidian Colony: Target vs Model", fontsize=TITLE_FS + 1,
                 color=INK, y=0.97)

    # Left: biological target schematic
    ax = axes[0]
    ax.set_facecolor(PANEL_BG)
    _draw_schematic_star(ax, 0.5, 0.5, 0.10, 0.40, 7)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Target: Botryllus schlosseri", fontsize=LABEL_FS, color=INK, pad=5)
    ax.text(0.5, 0.04, "7 radial arms, shared atrium",
            ha="center", va="bottom", fontsize=TICK_FS, color=NEUTRAL,
            transform=ax.transAxes)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)

    # Center: GM activator field
    ax = axes[1]
    ax.set_facecolor(PANEL_BG)
    fd = field_result
    L = fd.get("field_params", {}).get("L", 10.0)
    if L is None or L == 0:
        L = 10.0
    im = ax.imshow(fd["field"], origin="lower", extent=[0, L, 0, L],
                   cmap=FIELD_CMAP, interpolation="nearest")
    centers = fd["centers"]
    if len(centers) > 0:
        ax.scatter(centers[:, 0], centers[:, 1], s=35, color=INK,
                   marker="+", linewidths=1.4, zorder=4)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04).ax.tick_params(
        labelsize=TICK_FS, colors=INK)
    ax.set_title("Layer 1: GM Field (activator)", fontsize=LABEL_FS, color=INK, pad=5)
    ax.set_xlabel("x", fontsize=TICK_FS, color=INK)
    ax.set_ylabel("y", fontsize=TICK_FS, color=INK)
    ax.tick_params(colors=INK, labelsize=TICK_FS)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)

    # Right: agent snapshot
    ax = axes[2]
    ax.set_facecolor(PANEL_BG)
    pos = zooid_result.positions[-1]
    K = zooid_result.K
    L_z = zooid_result.L
    for k in range(K):
        mask = zooid_result.assignments == k
        ax.scatter(pos[mask, 0], pos[mask, 1], s=8,
                   color=_PALETTE[k % len(_PALETTE)], alpha=0.80,
                   linewidths=0, zorder=2)
    ax.scatter(zooid_result.centers[:, 0], zooid_result.centers[:, 1],
               s=40, color=INK, marker="+", linewidths=1.4, zorder=4)
    ax.set_xlim(0, L_z)
    ax.set_ylim(0, L_z)
    ax.set_title(f"Layer 2: Zooid Agents (K={K})", fontsize=LABEL_FS, color=INK, pad=5)
    ax.set_xlabel("x", fontsize=TICK_FS, color=INK)
    ax.set_ylabel("y", fontsize=TICK_FS, color=INK)
    ax.tick_params(colors=INK, labelsize=TICK_FS)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)

    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(output_path, dpi=SLIDE_DPI, bbox_inches="tight")
    plt.close(fig)


def make_slide2_model_schematic(output_path, n_arms=7):
    """Slide 2: Model architecture diagram with equations."""
    ensure_dir(output_path.rsplit("/", 1)[0] if "/" in output_path else
               output_path.rsplit("\\", 1)[0] if "\\" in output_path else ".")

    fig = plt.figure(figsize=(SLIDE_W, SLIDE_H), facecolor=BG)
    fig.suptitle("Two-Layer Generative Model", fontsize=TITLE_FS + 1,
                 color=INK, y=0.97)

    ax = fig.add_axes([0, 0, 1, 0.92])
    ax.set_facecolor(BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    box_kw = dict(boxstyle="round,pad=0.5", facecolor=PANEL_BG,
                  edgecolor=BORDER, linewidth=1.5)

    # Layer 1 box
    ax.text(2.0, 3.9, "Layer 1", fontsize=LABEL_FS + 1,
            ha="center", va="top", color=ACCENT, fontweight="bold")
    ax.text(2.0, 3.5, "Gierer-Meinhardt Field",
            ha="center", va="top", fontsize=LABEL_FS, color=INK)
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.2, 1.5), 3.6, 2.2, **box_kw))
    ax.text(2.0, 3.1,
            r"$\partial_t a = D_a \nabla^2 a + \rho a^2/h - \mu_a a$",
            ha="center", va="top", fontsize=TICK_FS + 1, color=INK)
    ax.text(2.0, 2.65,
            r"$\partial_t h = D_h \nabla^2 h + \rho a^2 - \mu_h h$",
            ha="center", va="top", fontsize=TICK_FS + 1, color=INK)
    ax.text(2.0, 2.1, "Turing spots -> star center positions",
            ha="center", va="top", fontsize=TICK_FS, color=NEUTRAL)
    ax.text(2.0, 1.75, r"$D_h / D_a \gg 1$  (short-range act., long-range inh.)",
            ha="center", va="top", fontsize=TICK_FS, color=NEUTRAL)

    # Arrow
    ax.annotate("", xy=(6.3, 2.5), xytext=(3.8, 2.5),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.8))
    ax.text(5.05, 2.75, "centers", ha="center", va="bottom",
            fontsize=TICK_FS, color=INK)

    # Layer 2 box
    ax.text(8.0, 3.9, "Layer 2", fontsize=LABEL_FS + 1,
            ha="center", va="top", color=GREEN, fontweight="bold")
    ax.text(8.0, 3.5, "Active Zooid Agents",
            ha="center", va="top", fontsize=LABEL_FS, color=INK)
    ax.add_patch(mpatches.FancyBboxPatch(
        (6.2, 1.5), 3.6, 2.2, **box_kw))
    ax.text(8.0, 3.1,
            r"$F = k_r (r_{tgt} - r)\hat{r} - k_a \vec{r} + F_{ang} + F_{ev}$",
            ha="center", va="top", fontsize=TICK_FS + 1, color=INK)
    ax.text(8.0, 2.65,
            r"$\dot\theta_i = \omega_i + \sqrt{2 D_r}\,\xi_i(t)$",
            ha="center", va="top", fontsize=TICK_FS + 1, color=INK)
    ax.text(8.0, 2.1, "Arms form via angular repulsion between groups",
            ha="center", va="top", fontsize=TICK_FS, color=NEUTRAL)
    ax.text(8.0, 1.75, r"$\omega > 0$ : chiral twist   |   $\omega = 0$ : radial",
            ha="center", va="top", fontsize=TICK_FS, color=NEUTRAL)

    # Parameter summary at bottom
    ax.text(5.0, 1.2,
            "Key parameters:  "
            r"$k_{radial}$ (arm tightness)   "
            r"$\omega$ (chirality)   "
            r"$D_r$ (noise)   "
            r"$k_{angular}$ (arm repulsion)   "
            r"$D_h/D_a$ (# centers)",
            ha="center", va="top", fontsize=TICK_FS, color=INK,
            bbox=dict(boxstyle="round,pad=0.3", facecolor=PANEL_BG,
                      edgecolor=BORDER, alpha=0.8))

    # Mini schematic star in lower-right
    mini_ax = fig.add_axes([0.75, 0.04, 0.22, 0.28])
    mini_ax.set_facecolor(BG)
    mini_ax.set_aspect("equal")
    _draw_schematic_star(mini_ax, 0.5, 0.5, 0.10, 0.42, n_arms)
    mini_ax.set_xlim(0, 1)
    mini_ax.set_ylim(0, 1)
    mini_ax.set_xticks([])
    mini_ax.set_yticks([])
    mini_ax.set_title("target morphology", fontsize=TICK_FS - 1, color=NEUTRAL, pad=2)
    for sp in mini_ax.spines.values():
        sp.set_edgecolor(BORDER)

    fig.savefig(output_path, dpi=SLIDE_DPI, bbox_inches="tight")
    plt.close(fig)


def make_slide3_simulation_sequence(zooid_result, output_path):
    """Slide 3: Time evolution of agent dynamics (4 snapshots)."""
    ensure_dir(output_path.rsplit("/", 1)[0] if "/" in output_path else
               output_path.rsplit("\\", 1)[0] if "\\" in output_path else ".")

    n_snaps = zooid_result.positions.shape[0]
    if n_snaps < 4:
        indices = list(range(n_snaps))
        while len(indices) < 4:
            indices.append(indices[-1])
    else:
        step = (n_snaps - 1) / 3.0
        indices = [int(round(i * step)) for i in range(4)]

    labels = ["t = 0  (init)", "t = early", "t = mid", "t = final"]
    K = zooid_result.K
    L = zooid_result.L
    assignments = zooid_result.assignments
    centers = zooid_result.centers

    fig, axes = plt.subplots(1, 4, figsize=(SLIDE_W, SLIDE_H), facecolor=BG)
    fig.suptitle("Star Arm Formation: Time Sequence", fontsize=TITLE_FS + 1,
                 color=INK, y=0.97)

    for col, (idx, label) in enumerate(zip(indices, labels)):
        ax = axes[col]
        ax.set_facecolor(PANEL_BG)
        pos = zooid_result.positions[idx]
        for k in range(K):
            mask = assignments == k
            ax.scatter(pos[mask, 0], pos[mask, 1], s=9,
                       color=_PALETTE[k % len(_PALETTE)],
                       alpha=0.80, linewidths=0, zorder=2)
        ax.scatter(centers[:, 0], centers[:, 1], s=40, color=INK,
                   marker="+", linewidths=1.4, zorder=4)
        ax.set_xlim(0, L)
        ax.set_ylim(0, L)
        ax.set_aspect("equal")
        ax.set_title(label, fontsize=LABEL_FS, color=INK, pad=4)
        ax.set_xlabel("x", fontsize=TICK_FS, color=INK)
        ax.tick_params(colors=INK, labelsize=TICK_FS)
        if col > 0:
            ax.set_yticklabels([])
        for sp in ax.spines.values():
            sp.set_edgecolor(BORDER)

    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(output_path, dpi=SLIDE_DPI, bbox_inches="tight")
    plt.close(fig)


def make_slide4_phase_diagram(x_vals, y_vals, sl_grid, swirl_grid, output_path):
    """Slide 4: Phase diagram highlighting star_likeness and swirl regions.

    x_vals: k_radial values
    y_vals: omega values
    sl_grid: star_likeness grid (ny x nx)
    swirl_grid: swirl grid (ny x nx)
    """
    ensure_dir(output_path.rsplit("/", 1)[0] if "/" in output_path else
               output_path.rsplit("\\", 1)[0] if "\\" in output_path else ".")

    fig, axes = plt.subplots(1, 2, figsize=(SLIDE_W, SLIDE_H), facecolor=BG)
    fig.suptitle("Phase Diagram: Radial Attraction vs Chirality",
                 fontsize=TITLE_FS + 1, color=INK, y=0.97)

    for ax, grid, title, cmap in [
        (axes[0], sl_grid, "Star-likeness score", "YlOrBr"),
        (axes[1], swirl_grid, "Swirl magnitude", "PRGn"),
    ]:
        ax.set_facecolor(PANEL_BG)
        im = ax.pcolormesh(x_vals, y_vals, grid, cmap=cmap,
                           vmin=0, vmax=1, shading="nearest")
        cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cb.ax.tick_params(labelsize=TICK_FS, colors=INK)
        cb.outline.set_edgecolor(INK)
        ax.set_xlabel(r"$k_{radial}$", fontsize=LABEL_FS, color=INK)
        ax.set_ylabel(r"$\omega$ (chirality)", fontsize=LABEL_FS, color=INK)
        ax.set_title(title, fontsize=LABEL_FS, color=INK, pad=5)
        ax.tick_params(colors=INK, labelsize=TICK_FS)
        for sp in ax.spines.values():
            sp.set_edgecolor(BORDER)

    # Annotate best region
    best_ix = int(np.argmax(sl_grid[0]))
    axes[0].axvline(x_vals[best_ix], color=ACCENT, linewidth=1.5,
                    linestyle="--", alpha=0.8)
    axes[0].text(x_vals[best_ix] + 0.05, y_vals[-1] * 0.9,
                 "optimal\nattraction", fontsize=TICK_FS - 1,
                 color=ACCENT, va="top")

    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(output_path, dpi=SLIDE_DPI, bbox_inches="tight")
    plt.close(fig)


def make_slide5_insight_and_limits(result, output_path, target_arms=7):
    """Slide 5: What works vs what doesn't.

    result: StarColonyResult
    """
    ensure_dir(output_path.rsplit("/", 1)[0] if "/" in output_path else
               output_path.rsplit("\\", 1)[0] if "\\" in output_path else ".")

    m = result.metrics

    fig, axes = plt.subplots(1, 2, figsize=(SLIDE_W, SLIDE_H), facecolor=BG)
    fig.suptitle("Simulation Assessment", fontsize=TITLE_FS + 1, color=INK, y=0.97)

    # Left: what works
    ax = axes[0]
    ax.set_facecolor(PANEL_BG)
    ax.axis("off")
    ax.set_title("Matches target", fontsize=LABEL_FS, color=GREEN, pad=6,
                 fontweight="bold")

    matches = m.get("matches", [])
    if not matches:
        matches = ["Run simulation to populate matches"]
    for i, txt in enumerate(matches[:7]):
        ax.text(0.05, 0.88 - i * 0.12, f"+ {txt}",
                transform=ax.transAxes, fontsize=TICK_FS + 1, color=GREEN,
                va="top", wrap=True)

    # Right: failures + limits
    ax = axes[1]
    ax.set_facecolor(PANEL_BG)
    ax.axis("off")
    ax.set_title("Limitations", fontsize=LABEL_FS, color=ACCENT, pad=6,
                 fontweight="bold")

    failures = m.get("failures", [])
    limitations = [
        "No Botryllus-specific biochemistry",
        "Arm count detection sensitive to noise",
        "O(N^2) excluded volume (slow for N>500)",
        "2D only; no substrate mechanics",
    ]
    all_issues = failures[:3] + limitations[:4]
    for i, txt in enumerate(all_issues[:7]):
        prefix = "!" if i < len(failures[:3]) else "-"
        col = ACCENT if i < len(failures[:3]) else NEUTRAL
        ax.text(0.05, 0.88 - i * 0.12, f"{prefix} {txt}",
                transform=ax.transAxes, fontsize=TICK_FS + 1, color=col,
                va="top", wrap=True)

    # Bottom: suggestion
    fix = m.get("suggested_fix", "")
    if fix and fix != "Parameters look good":
        fig.text(0.5, 0.02, f"Suggestion: {fix}", ha="center", va="bottom",
                 fontsize=TICK_FS, color=NEUTRAL,
                 bbox=dict(boxstyle="round,pad=0.3", facecolor=PANEL_BG,
                           edgecolor=BORDER, alpha=0.8))

    fig.tight_layout(rect=[0, 0.06, 1, 0.94])
    fig.savefig(output_path, dpi=SLIDE_DPI, bbox_inches="tight")
    plt.close(fig)


def make_final_summary_panel(result_clean, result_chiral, field_data,
                             x_vals, y_vals, sl_grid, output_path):
    """6-panel summary: target, GM field, clean agents, chiral agents,
    phase diagram, metric table.

    result_clean:  StarColonyResult for clean_star_systems
    result_chiral: StarColonyResult for chiral_twisted_stars
    field_data:    dict from generate_star_centers (field, centers, field_params)
    x_vals, y_vals, sl_grid: from sweep_attraction_vs_chirality
    """
    ensure_dir(output_path.rsplit("/", 1)[0] if "/" in output_path else
               output_path.rsplit("\\", 1)[0] if "\\" in output_path else ".")

    fig = plt.figure(figsize=(SLIDE_W, SLIDE_H), facecolor=BG)
    fig.suptitle("Chirality Atlas: Star Ascidian Colony Model",
                 fontsize=TITLE_FS + 2, color=INK, y=0.99)

    gs = fig.add_gridspec(2, 3, hspace=0.38, wspace=0.32,
                          left=0.04, right=0.97, top=0.91, bottom=0.05)

    # [0,0] target schematic
    ax = fig.add_subplot(gs[0, 0])
    ax.set_facecolor(PANEL_BG)
    _draw_schematic_star(ax, 0.5, 0.5, 0.10, 0.42, 7)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Target organism", fontsize=LABEL_FS, color=INK, pad=4)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)

    # [0,1] GM field
    ax = fig.add_subplot(gs[0, 1])
    ax.set_facecolor(PANEL_BG)
    fd = field_data
    L = fd.get("field_params", {}).get("L", 10.0) or 10.0
    ax.imshow(fd["field"], origin="lower", extent=[0, L, 0, L],
              cmap=FIELD_CMAP, interpolation="nearest")
    ctrs = fd["centers"]
    if len(ctrs) > 0:
        ax.scatter(ctrs[:, 0], ctrs[:, 1], s=30, color=INK,
                   marker="+", linewidths=1.2, zorder=4)
    ax.set_title("GM field (Layer 1)", fontsize=LABEL_FS, color=INK, pad=4)
    ax.tick_params(colors=INK, labelsize=TICK_FS)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)

    # [0,2] clean agents
    ax = fig.add_subplot(gs[0, 2])
    _plot_zooid_snap(ax, result_clean.zooid, "Clean stars (omega=0)")

    # [1,0] chiral agents
    ax = fig.add_subplot(gs[1, 0])
    _plot_zooid_snap(ax, result_chiral.zooid, "Chiral twist (omega=2.5)")

    # [1,1] phase diagram
    ax = fig.add_subplot(gs[1, 1])
    ax.set_facecolor(PANEL_BG)
    im = ax.pcolormesh(x_vals, y_vals, sl_grid, cmap="YlOrBr",
                       vmin=0, vmax=1, shading="nearest")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04).ax.tick_params(
        labelsize=TICK_FS - 1, colors=INK)
    ax.set_xlabel(r"$k_{radial}$", fontsize=TICK_FS, color=INK)
    ax.set_ylabel(r"$\omega$", fontsize=TICK_FS, color=INK)
    ax.set_title("Phase: star-likeness", fontsize=LABEL_FS, color=INK, pad=4)
    ax.tick_params(colors=INK, labelsize=TICK_FS - 1)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)

    # [1,2] metric bars
    ax = fig.add_subplot(gs[1, 2])
    ax.set_facecolor(PANEL_BG)
    m = result_clean.metrics
    names = ["star_like", "radial", "uniformity", "1-frag", "1-merge"]
    vals = [
        m["star_likeness_score"],
        m["radial_order"],
        m["angular_uniformity"],
        max(0.0, 1.0 - m["fragmentation"]),
        max(0.0, 1.0 - m["merge_score"]),
    ]
    y_pos = np.arange(len(names))
    colors = [GREEN if v >= 0.5 else ACCENT for v in vals]
    ax.barh(y_pos, vals, color=colors, height=0.55, alpha=0.85)
    ax.axvline(0.5, color=BORDER, linewidth=1.0, linestyle="--")
    ax.set_xlim(0, 1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=TICK_FS - 1, color=INK)
    ax.set_xlabel("score", fontsize=TICK_FS, color=INK)
    ax.set_title("Metrics (clean preset)", fontsize=LABEL_FS, color=INK, pad=4)
    ax.tick_params(colors=INK, labelsize=TICK_FS - 1)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)

    fig.savefig(output_path, dpi=SLIDE_DPI, bbox_inches="tight")
    plt.close(fig)


def _plot_zooid_snap(ax, zooid_result, title):
    """Shared helper: plot final agent snapshot on ax."""
    ax.set_facecolor(PANEL_BG)
    pos = zooid_result.positions[-1]
    K = zooid_result.K
    L = zooid_result.L
    for k in range(K):
        mask = zooid_result.assignments == k
        ax.scatter(pos[mask, 0], pos[mask, 1], s=6,
                   color=_PALETTE[k % len(_PALETTE)],
                   alpha=0.80, linewidths=0, zorder=2)
    ax.scatter(zooid_result.centers[:, 0], zooid_result.centers[:, 1],
               s=30, color=INK, marker="+", linewidths=1.2, zorder=4)
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)
    ax.set_title(title, fontsize=LABEL_FS, color=INK, pad=4)
    ax.tick_params(colors=INK, labelsize=TICK_FS - 1)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)
