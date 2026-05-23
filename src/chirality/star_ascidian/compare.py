"""
Visual comparison tools for star ascidian simulation vs biological target.

compare_to_target: generates a side-by-side panel with
  left:  schematic drawing of target star ascidian morphology
  right: simulation snapshot with metric overlay

feature_table_figure: bar chart comparing target feature requirements
  against simulation scores.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

from chirality.visualization.style import (
    BG, INK, ACCENT, GREEN, NEUTRAL, BORDER,
    TITLE_FS, LABEL_FS, TICK_FS,
    CHIRALITY_CMAP,
)
from . import metrics as star_metrics


def draw_schematic_star(ax, center, r_inner, r_outer, n_arms, arm_width_deg=18,
                        color=ACCENT, lobe_color=GREEN, alpha=0.75):
    """Draw a schematic star ascidian on ax.

    Draws a central disk + n_arms radial lobes.
    All coordinates are in the axes data space.
    """
    cx, cy = center

    disk = plt.Circle((cx, cy), r_inner, color=color, alpha=alpha, zorder=3)
    ax.add_patch(disk)

    arm_angles = np.linspace(0, 2.0 * np.pi, n_arms, endpoint=False)
    half_w = np.deg2rad(arm_width_deg / 2.0)

    for ang in arm_angles:
        left_ang = ang - half_w
        right_ang = ang + half_w
        tip_x = cx + r_outer * np.cos(ang)
        tip_y = cy + r_outer * np.sin(ang)

        theta_arc = np.linspace(left_ang, right_ang, 12)
        xs = np.concatenate([[cx], r_inner * np.cos(theta_arc) + cx, [cx]])
        ys = np.concatenate([[cy], r_inner * np.sin(theta_arc) + cy, [cy]])

        inner_xs = xs
        inner_ys = ys

        outer_arc_xs = r_outer * np.cos(theta_arc) + cx
        outer_arc_ys = r_outer * np.sin(theta_arc) + cy

        lobe_xs = np.concatenate([r_inner * np.cos(theta_arc) + cx,
                                   outer_arc_xs[::-1]])
        lobe_ys = np.concatenate([r_inner * np.sin(theta_arc) + cy,
                                   outer_arc_ys[::-1]])

        lobe = plt.Polygon(
            np.column_stack([lobe_xs, lobe_ys]),
            color=lobe_color, alpha=alpha, zorder=2
        )
        ax.add_patch(lobe)

    ax.set_aspect("equal")


def plot_target_schematic(ax, n_arms=7, label="Botryllus schlosseri\n(target morphology)"):
    """Draw the target star ascidian schematic on the given axes."""
    ax.set_facecolor(BG)
    cx, cy = 0.5, 0.5
    r_inner = 0.10
    r_outer = 0.38

    draw_schematic_star(ax, (cx, cy), r_inner, r_outer, n_arms)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(label, fontsize=LABEL_FS, color=INK, pad=6)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)


def plot_simulation_snapshot(ax, result, title="Simulation"):
    """Plot the final agent snapshot with center markers."""
    pos = result.positions[-1]
    centers = result.centers
    assignments = result.assignments
    L = result.L

    ax.set_facecolor(BG)
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)

    palette = [ACCENT, GREEN, "#7B6B8B", "#8B7355", "#4A7B8B", "#8B4A6B", "#6B8B4A"]
    K = len(centers)

    for k in range(K):
        mask = assignments == k
        col = palette[k % len(palette)]
        ax.scatter(pos[mask, 0], pos[mask, 1], s=6, color=col, alpha=0.7,
                   linewidths=0, zorder=2)

    ax.scatter(centers[:, 0], centers[:, 1], s=40, color=INK, marker="+",
               linewidths=1.2, zorder=4)

    ax.set_xlabel("x", fontsize=TICK_FS, color=INK)
    ax.set_ylabel("y", fontsize=TICK_FS, color=INK)
    ax.tick_params(colors=INK, labelsize=TICK_FS)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
    ax.set_title(title, fontsize=LABEL_FS, color=INK, pad=6)


def compare_to_target(result, target_arms=7, title="Star Ascidian: Simulation vs Target",
                      figsize=(10, 4.5)):
    """Generate a three-panel comparison figure.

    Left:   schematic of biological target
    Center: simulation snapshot
    Right:  metric bar chart

    Returns: fig
    """
    m = star_metrics.visual_similarity_report(result, target_arms=target_arms)

    fig, axes = plt.subplots(1, 3, figsize=figsize, facecolor=BG)
    fig.suptitle(title, fontsize=TITLE_FS, color=INK, y=1.01)

    plot_target_schematic(axes[0], n_arms=target_arms)
    plot_simulation_snapshot(axes[1], result, title="Simulation (final)")

    metric_names = ["star_likeness", "radial_order", "angular_uniformity",
                    "fragmentation (inv)", "merge (inv)"]
    raw_values = [
        m["star_likeness_score"],
        m["radial_order"],
        m["angular_uniformity"],
        1.0 - min(1.0, m["fragmentation"]),
        1.0 - min(1.0, m["merge_score"]),
    ]

    ax = axes[2]
    ax.set_facecolor(BG)
    y_pos = np.arange(len(metric_names))
    bar_colors = [ACCENT if v >= 0.5 else NEUTRAL for v in raw_values]
    bars = ax.barh(y_pos, raw_values, color=bar_colors, height=0.55, alpha=0.85)
    ax.axvline(0.5, color=BORDER, linewidth=1.0, linestyle="--")
    ax.set_xlim(0, 1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(metric_names, fontsize=TICK_FS, color=INK)
    ax.set_xlabel("score", fontsize=LABEL_FS, color=INK)
    ax.set_title("Metric scores", fontsize=LABEL_FS, color=INK, pad=6)
    ax.tick_params(colors=INK, labelsize=TICK_FS)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)

    for bar, val in zip(bars, raw_values):
        ax.text(min(val + 0.02, 0.95), bar.get_y() + bar.get_height() / 2,
                f"{val:.2f}", va="center", fontsize=TICK_FS, color=INK)

    fig.tight_layout()
    return fig


def feature_table_figure(result, target_arms=7, preset_name="",
                         figsize=(7, 4)):
    """Generate a feature checklist figure.

    Shows each biological target feature and whether the simulation matches it.
    Returns: fig
    """
    m = star_metrics.visual_similarity_report(result, target_arms=target_arms)

    # Ordered to match get_target_feature_checklist() positions
    feature_labels = [
        "Repeated star centers",
        "Correct center spacing",
        "Radial arm structure",
        "Discrete arms",
        "Arm regularity",
        "Star-like overall shape",
        "Chirality sensitivity",
    ]

    arm_count_score = max(0.0, 1.0 - abs(m["arm_count_mean"] - target_arms) / float(target_arms))
    scores = [
        1.0 if result.K >= 2 else 0.3,
        1.0 - min(1.0, m["merge_score"]),
        m["radial_order"],
        arm_count_score,
        m["angular_uniformity"],
        m["star_likeness_score"],
        min(1.0, abs(m["swirl_score"])),
    ]
    target_threshold = 0.5

    fig, ax = plt.subplots(figsize=figsize, facecolor=BG)
    ax.set_facecolor(BG)

    y_pos = np.arange(len(feature_keys))
    bar_colors = [GREEN if s >= target_threshold else ACCENT for s in scores]
    bars = ax.barh(y_pos, scores, color=bar_colors, height=0.6, alpha=0.82)
    ax.axvline(target_threshold, color=INK, linewidth=1.0, linestyle="--", alpha=0.6)
    ax.set_xlim(0, 1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(feature_labels, fontsize=TICK_FS, color=INK)
    ax.set_xlabel("match score", fontsize=LABEL_FS, color=INK)
    title = "Simulation vs Target Features"
    if preset_name:
        title += f"  [{preset_name}]"
    ax.set_title(title, fontsize=TITLE_FS, color=INK, pad=6)
    ax.tick_params(colors=INK, labelsize=TICK_FS)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)

    pass_patch = mpatches.Patch(color=GREEN, label="meets target", alpha=0.82)
    fail_patch = mpatches.Patch(color=ACCENT, label="below target", alpha=0.82)
    ax.legend(handles=[pass_patch, fail_patch], loc="lower right",
              fontsize=TICK_FS, framealpha=0.7,
              facecolor=BG, edgecolor=BORDER)

    fig.tight_layout()
    return fig
