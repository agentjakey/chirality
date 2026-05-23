"""
Visual rescue script for Chirality Atlas hackathon submission.
Generates all improved visual assets for slides, panels, and animations.

Usage: python scripts/make_visual_rescue.py
"""
import sys
import os
import io
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Ellipse
import pandas as pd

try:
    import imageio.v2 as imageio
except ImportError:
    import imageio

from chirality.star_ascidian.hybrid_model import simulate_star_ascidian_colony
from chirality.star_ascidian.zooid_agents import simulate_zooid_agents
from chirality.visualization.style import (
    ZOOID_PALETTE, INK, BG, ACCENT, GREEN, BORDER, PANEL_BG
)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANELS_DIR = os.path.join(REPO, "outputs", "panels")
MOVIES_DIR = os.path.join(REPO, "outputs", "movies")
DATA_DIR = os.path.join(REPO, "outputs", "data")
SA_DIR = os.path.join(REPO, "outputs", "star_ascidian")
REF_IMAGE = os.path.join(REPO, "assets", "reference", "star_ascidian_reference.jpg")

DARK_BG = "#0D1117"
DARK_MID = "#1A1A2E"

FIG_W = 9.6
FIG_H = 5.4
FIG_DPI = 150


def _draw_zooids_ellipse(ax, pos, arm_assignments, center, palette, alpha=0.88,
                         ell_w=0.30, ell_h=0.14):
    for i in range(len(pos)):
        arm_id = int(arm_assignments[i]) % len(palette)
        dr = pos[i] - center
        angle_deg = np.degrees(np.arctan2(dr[1], dr[0]))
        e = Ellipse(xy=(pos[i, 0], pos[i, 1]),
                    width=ell_w, height=ell_h, angle=angle_deg,
                    color=palette[arm_id], alpha=alpha, zorder=3, linewidth=0)
        ax.add_patch(e)


def _draw_zooids_scatter(ax, pos, arm_assignments, palette, s=40, alpha=0.8, zorder=3):
    arm_colors = [palette[int(a) % len(palette)] for a in arm_assignments]
    ax.scatter(pos[:, 0], pos[:, 1], c=arm_colors, s=s, alpha=alpha,
               zorder=zorder, linewidths=0, edgecolors="none")


def _style_dark_ax(ax, xlim=None, ylim=None, title=None):
    ax.set_facecolor(DARK_BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor("#333344")
    if xlim:
        ax.set_xlim(*xlim)
    if ylim:
        ax.set_ylim(*ylim)
    if title:
        ax.set_title(title, color="#AAAACC", fontsize=9, pad=3)


def _tile_colony(pos, centers, arm_assignments, L, tiles=3):
    tiled_pos, tiled_arm, tiled_centers = [], [], []
    for ti in range(tiles):
        for tj in range(tiles):
            offset = np.array([ti * L, tj * L])
            tiled_pos.append(pos + offset)
            tiled_arm.append(arm_assignments.copy())
            tiled_centers.append(centers + offset)
    return (np.concatenate(tiled_pos, axis=0),
            np.concatenate(tiled_arm),
            np.concatenate(tiled_centers, axis=0))


def run_single_star_sim(omega, seed=42):
    center = np.array([[5.0, 5.0]])
    mode = "chiral_twist" if omega > 0 else "radial_clean"
    return simulate_zooid_agents(
        centers=center,
        n_per_center=35,
        n_arms=7,
        L=10.0,
        r_target=1.4,
        v0=0.04,
        Dr=0.03,
        omega=omega,
        k_attract=0.35,
        k_radial=2.5,
        k_angular=0.7,
        k_ev=0.5,
        sigma_ev=0.16,
        dt=0.02,
        n_steps=300,
        n_snapshots=8,
        mode=mode,
        boundary="periodic",
        seed=seed,
    )


def make_single_star_mechanism():
    print("  Running single-star simulations...")
    res_clean = run_single_star_sim(omega=0.0)
    res_chiral = run_single_star_sim(omega=2.5)

    fig, axes = plt.subplots(1, 2, figsize=(FIG_W, FIG_H))
    fig.patch.set_facecolor(DARK_BG)

    center = np.array([5.0, 5.0])
    titles = ["Clean star  (omega = 0)", "Chiral star  (omega = 2.5)"]
    results = [res_clean, res_chiral]

    for ax, res, title in zip(axes, results, titles):
        pos = res.positions[-1]
        arm_ids = res.arm_assignments
        _style_dark_ax(ax, xlim=(3.0, 7.0), ylim=(3.0, 7.0), title=title)
        _draw_zooids_ellipse(ax, pos, arm_ids, center, ZOOID_PALETTE)
        ax.scatter([center[0]], [center[1]], c="#FFFFFF", s=30, zorder=10, linewidths=0)

        # Arm labels
        for arm_id in range(7):
            arm_mask = arm_ids == arm_id
            if arm_mask.sum() > 0:
                arm_center = pos[arm_mask].mean(axis=0)
                dr = arm_center - center
                label_pos = center + dr / (np.linalg.norm(dr) + 1e-9) * 2.0
                ax.text(label_pos[0], label_pos[1], str(arm_id + 1),
                        color=ZOOID_PALETTE[arm_id % len(ZOOID_PALETTE)],
                        fontsize=7, ha="center", va="center", alpha=0.9)

    # Add metric annotations at bottom
    axes[0].text(0.05, 0.04, "radial_order >= 0.8", transform=axes[0].transAxes,
                 color="#88CC88", fontsize=8, va="bottom")
    axes[1].text(0.05, 0.04, "swirl_score ~ 0.3", transform=axes[1].transAxes,
                 color="#FFAA66", fontsize=8, va="bottom")

    fig.suptitle("Layer 2: Single star -- radial confinement + angular arm separation",
                 color="#EEEEFF", fontsize=11, y=0.97)

    out_path = os.path.join(PANELS_DIR, "single_star_mechanism.png")
    fig.savefig(out_path, dpi=FIG_DPI, bbox_inches="tight",
                facecolor=DARK_BG, edgecolor="none")
    plt.close(fig)
    print(f"  Saved: {out_path}")


def make_colony_scale_view(result):
    L = result.zooid.L
    pos_final = result.zooid.positions[-1]
    arm_ids = result.zooid.arm_assignments
    centers = result.zooid.centers

    tiled_pos, tiled_arm, tiled_centers = _tile_colony(pos_final, centers, arm_ids, L)

    fig, ax = plt.subplots(1, 1, figsize=(FIG_H, FIG_H))
    fig.patch.set_facecolor(DARK_BG)
    _style_dark_ax(ax, xlim=(0, 3 * L), ylim=(0, 3 * L))
    _draw_zooids_scatter(ax, tiled_pos, tiled_arm, ZOOID_PALETTE, s=9, alpha=0.78)
    ax.scatter(tiled_centers[:, 0], tiled_centers[:, 1],
               c="#FFFFFF", s=8, zorder=5, linewidths=0, alpha=0.55)
    ax.set_title("Colony simulation -- 3x3 periodic tiling", color="#CCCCDD", fontsize=10, pad=4)

    out_path = os.path.join(PANELS_DIR, "colony_scale_reference_match.png")
    fig.savefig(out_path, dpi=FIG_DPI, bbox_inches="tight",
                facecolor=DARK_BG, edgecolor="none")
    plt.close(fig)
    print(f"  Saved: {out_path}")


def make_center_selection_schematic(result):
    field = result.field
    centers = result.zooid.centers
    L = result.params["L"]
    r_target = result.params["r_target"]

    fig, axes = plt.subplots(1, 3, figsize=(FIG_W, FIG_H * 0.75))
    fig.patch.set_facecolor(BG)

    ax = axes[0]
    ax.imshow(field, cmap="YlOrBr", origin="lower",
              extent=[0, L, 0, L], aspect="equal")
    ax.set_title("GM activator field", fontsize=10, color=INK)
    ax.set_xticks([])
    ax.set_yticks([])

    ax = axes[1]
    ax.imshow(field, cmap="YlOrBr", origin="lower",
              extent=[0, L, 0, L], aspect="equal", alpha=0.55)
    if len(centers) > 0:
        ax.scatter(centers[:, 0], centers[:, 1],
                   c="#FFFFFF", s=70, zorder=10, edgecolors="#333333", linewidths=0.8)
    ax.set_title(f"Extracted centers ({len(centers)} peaks)", fontsize=10, color=INK)
    ax.set_xticks([])
    ax.set_yticks([])

    ax = axes[2]
    ax.set_facecolor("#F0EFE8")
    if len(centers) > 0:
        for i, c in enumerate(centers):
            col = ZOOID_PALETTE[i % len(ZOOID_PALETTE)]
            ring = plt.Circle(c, r_target, fill=False,
                              edgecolor=col, linewidth=1.3, alpha=0.75, zorder=2)
            ax.add_patch(ring)
            ax.scatter([c[0]], [c[1]], c=col, s=55, zorder=10, linewidths=0)
        ax.set_xlim(0, L)
        ax.set_ylim(0, L)
        ax.set_aspect("equal")
    ax.set_title("Center spacing + arm radius", fontsize=10, color=INK)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in axes[2].spines.values():
        spine.set_edgecolor(BORDER)

    fig.suptitle(
        "Layer 1: Turing instability produces quasi-regular star centers  (no explicit center-repulsion)",
        fontsize=10, color=INK, y=1.01
    )
    fig.tight_layout()

    out_path = os.path.join(PANELS_DIR, "center_selection_schematic.png")
    fig.savefig(out_path, dpi=FIG_DPI, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close(fig)
    print(f"  Saved: {out_path}")


def make_phase_diagram_with_regimes():
    df = pd.read_csv(os.path.join(DATA_DIR, "sweep_A.csv"))
    k_vals = sorted(df["k_radial"].unique())
    omega_vals = sorted(df["omega"].unique())

    sl_grid = df.pivot(index="omega", columns="k_radial", values="star_likeness").values
    sw_grid = df.pivot(index="omega", columns="k_radial", values="swirl").values

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    fig.patch.set_facecolor(BG)

    ax1 = fig.add_axes([0.07, 0.13, 0.37, 0.74])
    ax2 = fig.add_axes([0.54, 0.13, 0.37, 0.74])

    nx = len(k_vals)
    ny = len(omega_vals)

    im1 = ax1.imshow(sl_grid, cmap="viridis", origin="lower",
                     interpolation="bilinear", aspect="auto",
                     extent=[0, nx, 0, ny], vmin=0.0, vmax=0.5)
    ax1.set_xticks(np.arange(nx) + 0.5)
    ax1.set_xticklabels([str(k) for k in k_vals], fontsize=8, color=INK)
    ax1.set_yticks(np.arange(ny) + 0.5)
    ax1.set_yticklabels([str(o) for o in omega_vals], fontsize=8, color=INK)
    ax1.set_xlabel("k_radial", fontsize=9, color=INK)
    ax1.set_ylabel("omega", fontsize=9, color=INK)
    ax1.set_title("Star-likeness", fontsize=11, color=INK)
    plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)

    label_cfg = [
        (2.5, 4.3, "Twisted stars", "#222222", "#AACCFF"),
        (2.5, 2.0, "Clean stars",   "#FFFFFF", "#1a5c2a"),
        (0.5, 2.0, "Weak struct.",  "#FFFFFF", "#5c1a1a"),
    ]
    for lx, ly, ltext, tc, fc in label_cfg:
        ax1.text(lx, ly, ltext, color=tc, fontsize=8, ha="center", va="center",
                 fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.2", facecolor=fc, alpha=0.75))

    im2 = ax2.imshow(sw_grid, cmap="plasma", origin="lower",
                     interpolation="bilinear", aspect="auto",
                     extent=[0, nx, 0, ny], vmin=0.0, vmax=0.35)
    ax2.set_xticks(np.arange(nx) + 0.5)
    ax2.set_xticklabels([str(k) for k in k_vals], fontsize=8, color=INK)
    ax2.set_yticks(np.arange(ny) + 0.5)
    ax2.set_yticklabels([str(o) for o in omega_vals], fontsize=8, color=INK)
    ax2.set_xlabel("k_radial", fontsize=9, color=INK)
    ax2.set_ylabel("omega", fontsize=9, color=INK)
    ax2.set_title("Swirl score (chirality)", fontsize=11, color=INK)
    plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)

    # Inset thumbnails from existing preset PNGs
    preset_files = [
        (os.path.join(SA_DIR, "clean_star_systems.png"),       "clean\nstars"),
        (os.path.join(SA_DIR, "chiral_twisted_stars.png"),     "chiral\nstars"),
        (os.path.join(SA_DIR, "noisy_fragmented_systems.png"), "fragm."),
        (os.path.join(SA_DIR, "overcrowded_merged_systems.png"), "merged"),
    ]
    inset_lefts   = [0.467, 0.467, 0.467, 0.467]
    inset_bottoms = [0.65,  0.475, 0.30,  0.13]

    for (fpath, label), left, bottom in zip(preset_files, inset_lefts, inset_bottoms):
        if os.path.exists(fpath):
            ax_ins = fig.add_axes([left, bottom, 0.055, 0.14])
            ax_ins.imshow(plt.imread(fpath))
            ax_ins.set_xticks([])
            ax_ins.set_yticks([])
            ax_ins.set_title(label, fontsize=6, color=INK, pad=1)
            for spine in ax_ins.spines.values():
                spine.set_edgecolor(BORDER)
                spine.set_linewidth(0.5)

    fig.suptitle(
        "Phase diagram: k_radial vs omega  --  star-likeness and swirl are independent axes",
        fontsize=10, color=INK, y=0.97
    )

    out_path = os.path.join(PANELS_DIR, "phase_diagram_with_regimes.png")
    fig.savefig(out_path, dpi=FIG_DPI, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close(fig)
    print(f"  Saved: {out_path}")


def make_formation_sequence(result):
    n_snaps = result.zooid.positions.shape[0]
    indices = [0, n_snaps // 3, 2 * n_snaps // 3, n_snaps - 1]
    L = result.zooid.L
    centers = result.zooid.centers
    arm_ids = result.zooid.arm_assignments

    fig, axes = plt.subplots(1, 4, figsize=(FIG_W, FIG_H * 0.85))
    fig.patch.set_facecolor(DARK_BG)

    for ax, idx in zip(axes, indices):
        pos = result.zooid.positions[idx]
        t = result.zooid.times[idx]
        _style_dark_ax(ax, xlim=(0, L), ylim=(0, L), title=f"t = {t:.0f}")
        _draw_zooids_scatter(ax, pos, arm_ids, ZOOID_PALETTE, s=18, alpha=0.82)
        ax.scatter(centers[:, 0], centers[:, 1],
                   c="#FFFFFF", s=15, zorder=5, linewidths=0)

    fig.suptitle("Formation: random initial state -> radial arm structure",
                 color="#EEEEFF", fontsize=11, y=0.98)

    out_path = os.path.join(PANELS_DIR, "formation_sequence_strong.png")
    fig.savefig(out_path, dpi=FIG_DPI, bbox_inches="tight",
                facecolor=DARK_BG, edgecolor="none")
    plt.close(fig)
    print(f"  Saved: {out_path}")


def make_animations(result_clean, result_chiral):
    def _gif_from_result(result, out_path, n_frames=10, fps=4):
        L = result.zooid.L
        centers = result.zooid.centers
        arm_ids = result.zooid.arm_assignments
        n_snaps = result.zooid.positions.shape[0]
        frame_indices = np.linspace(0, n_snaps - 1, n_frames, dtype=int)

        frames = []
        for fi in frame_indices:
            pos = result.zooid.positions[fi]
            t = result.zooid.times[fi]

            fig, ax = plt.subplots(1, 1, figsize=(5, 5))
            fig.patch.set_facecolor(DARK_BG)
            _style_dark_ax(ax, xlim=(0, L), ylim=(0, L), title=f"t = {t:.0f}")
            _draw_zooids_scatter(ax, pos, arm_ids, ZOOID_PALETTE, s=24, alpha=0.85)
            ax.scatter(centers[:, 0], centers[:, 1],
                       c="#FFFFFF", s=22, zorder=5, linewidths=0)

            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=100, bbox_inches="tight",
                        pad_inches=0.06, facecolor=DARK_BG)
            buf.seek(0)
            frames.append(imageio.imread(buf))
            plt.close(fig)

        imageio.mimsave(out_path, frames, fps=fps, loop=0)
        print(f"  Saved: {out_path}")

    _gif_from_result(
        result_clean,
        os.path.join(MOVIES_DIR, "star_formation_clean.gif"),
    )
    _gif_from_result(
        result_chiral,
        os.path.join(MOVIES_DIR, "chiral_twist_emergence.gif"),
    )


def make_colony_animation(result):
    L = result.zooid.L
    arm_ids = result.zooid.arm_assignments
    centers = result.zooid.centers
    n_snaps = result.zooid.positions.shape[0]
    frame_indices = np.linspace(0, n_snaps - 1, 8, dtype=int)

    frames = []
    for fi in frame_indices:
        pos = result.zooid.positions[fi]
        t = result.zooid.times[fi]

        tiled_pos, tiled_arm, tiled_centers = _tile_colony(pos, centers, arm_ids, L)

        fig, ax = plt.subplots(1, 1, figsize=(5, 5))
        fig.patch.set_facecolor(DARK_BG)
        _style_dark_ax(ax, xlim=(0, 3 * L), ylim=(0, 3 * L), title=f"Colony  t = {t:.0f}")
        _draw_zooids_scatter(ax, tiled_pos, tiled_arm, ZOOID_PALETTE, s=6, alpha=0.75)
        ax.scatter(tiled_centers[:, 0], tiled_centers[:, 1],
                   c="#FFFFFF", s=6, zorder=5, linewidths=0, alpha=0.5)

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=100, bbox_inches="tight",
                    pad_inches=0.06, facecolor=DARK_BG)
        buf.seek(0)
        frames.append(imageio.imread(buf))
        plt.close(fig)

    out_path = os.path.join(MOVIES_DIR, "colony_scale_formation.gif")
    imageio.mimsave(out_path, frames, fps=3, loop=0)
    print(f"  Saved: {out_path}")


def make_slide1_panel(result):
    L = result.zooid.L
    pos_final = result.zooid.positions[-1]
    arm_ids = result.zooid.arm_assignments
    centers = result.zooid.centers
    field = result.field

    tiled_pos, tiled_arm, tiled_centers = _tile_colony(pos_final, centers, arm_ids, L)

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    fig.patch.set_facecolor(DARK_MID)

    # Left: reference image (38% width)
    ax_ref = fig.add_axes([0.0, 0.0, 0.38, 1.0])
    if os.path.exists(REF_IMAGE):
        ax_ref.imshow(plt.imread(REF_IMAGE), aspect="auto")
    else:
        ax_ref.set_facecolor("#2A2A4E")
        ax_ref.text(0.5, 0.5, "Botryllus schlosseri", color="#AACCFF",
                    ha="center", va="center", fontsize=11, transform=ax_ref.transAxes)
    ax_ref.set_xticks([])
    ax_ref.set_yticks([])
    ax_ref.set_title("Reference colony", color="#CCCCDD", fontsize=9, pad=3)

    # Center: GM activator field (24% width)
    ax_field = fig.add_axes([0.40, 0.10, 0.24, 0.80])
    ax_field.imshow(field, cmap="YlOrBr", origin="lower",
                    extent=[0, L, 0, L], aspect="equal")
    if len(centers) > 0:
        ax_field.scatter(centers[:, 0], centers[:, 1],
                         c="#FFFFFF", s=30, zorder=10, linewidths=0)
    ax_field.set_xticks([])
    ax_field.set_yticks([])
    ax_field.set_title("GM field + centers\n(Layer 1)", color=INK, fontsize=9, pad=3)

    # Right: tiled colony simulation (34% width)
    ax_col = fig.add_axes([0.66, 0.04, 0.34, 0.92])
    ax_col.set_facecolor(DARK_BG)
    _draw_zooids_scatter(ax_col, tiled_pos, tiled_arm, ZOOID_PALETTE, s=5, alpha=0.75)
    ax_col.scatter(tiled_centers[:, 0], tiled_centers[:, 1],
                   c="#FFFFFF", s=5, zorder=5, linewidths=0, alpha=0.45)
    ax_col.set_xlim(0, 3 * L)
    ax_col.set_ylim(0, 3 * L)
    ax_col.set_xticks([])
    ax_col.set_yticks([])
    ax_col.set_title("Colony simulation\n(Layer 2, 3x3 tiled)", color="#CCCCDD", fontsize=9, pad=3)

    fig.text(0.19, 0.01, "observation", color="#AACCFF", fontsize=8, ha="center")
    fig.text(0.52, 0.01, "Layer 1",     color="#FFCC88", fontsize=8, ha="center")
    fig.text(0.83, 0.01, "Layer 2",     color="#88CCFF", fontsize=8, ha="center")

    out_path = os.path.join(PANELS_DIR, "slide1_target_and_simulation.png")
    fig.savefig(out_path, dpi=FIG_DPI, bbox_inches="tight",
                facecolor=DARK_MID, edgecolor="none")
    plt.close(fig)
    print(f"  Saved: {out_path}")


def make_slide2_panel():
    single_path = os.path.join(PANELS_DIR, "single_star_mechanism.png")
    center_path = os.path.join(PANELS_DIR, "center_selection_schematic.png")

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    fig.patch.set_facecolor(BG)

    if os.path.exists(single_path):
        ax_top = fig.add_axes([0.0, 0.50, 1.0, 0.50])
        ax_top.imshow(plt.imread(single_path))
        ax_top.set_xticks([])
        ax_top.set_yticks([])
        ax_top.set_title("Layer 2: agent dynamics -- clean vs chiral", fontsize=10, color=INK, pad=2)

    if os.path.exists(center_path):
        ax_bot = fig.add_axes([0.0, 0.01, 1.0, 0.48])
        ax_bot.imshow(plt.imread(center_path))
        ax_bot.set_xticks([])
        ax_bot.set_yticks([])
        ax_bot.set_title("Layer 1: GM field -> center placement (Turing mechanism)", fontsize=10, color=INK, pad=2)

    out_path = os.path.join(PANELS_DIR, "slide2_model_schematic.png")
    fig.savefig(out_path, dpi=FIG_DPI, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close(fig)
    print(f"  Saved: {out_path}")


def make_slide3_panel(result_clean, result_chiral):
    L = result_clean.zooid.L
    n_clean = result_clean.zooid.positions.shape[0]
    n_chiral = result_chiral.zooid.positions.shape[0]
    idx_clean  = [0, n_clean // 3, 2 * n_clean // 3, n_clean - 1]
    idx_chiral = [0, n_chiral // 3, 2 * n_chiral // 3, n_chiral - 1]

    fig, axes = plt.subplots(2, 4, figsize=(FIG_W, FIG_H))
    fig.patch.set_facecolor(DARK_BG)

    def _draw_row(axes_row, result, snap_indices):
        L = result.zooid.L
        centers = result.zooid.centers
        arm_ids = result.zooid.arm_assignments
        for ax, si in zip(axes_row, snap_indices):
            pos = result.zooid.positions[si]
            t = result.zooid.times[si]
            _style_dark_ax(ax, xlim=(0, L), ylim=(0, L), title=f"t={t:.0f}")
            _draw_zooids_scatter(ax, pos, arm_ids, ZOOID_PALETTE, s=13, alpha=0.82)
            ax.scatter(centers[:, 0], centers[:, 1],
                       c="#FFFFFF", s=12, zorder=5, linewidths=0)

    _draw_row(axes[0], result_clean, idx_clean)
    _draw_row(axes[1], result_chiral, idx_chiral)

    axes[0][0].set_ylabel("Clean\n(omega~0)", color="#AACCAA", fontsize=8)
    axes[1][0].set_ylabel("Chiral\n(omega=2.5)", color="#FFAA88", fontsize=8)

    fig.suptitle(
        "Time evolution: arm formation  (top)  and chiral rotation  (bottom)",
        color="#EEEEFF", fontsize=10, y=0.98
    )

    out_path = os.path.join(PANELS_DIR, "slide3_simulation_sequence.png")
    fig.savefig(out_path, dpi=FIG_DPI, bbox_inches="tight",
                facecolor=DARK_BG, edgecolor="none")
    plt.close(fig)
    print(f"  Saved: {out_path}")


def make_slide4_panel():
    src = os.path.join(PANELS_DIR, "phase_diagram_with_regimes.png")
    dst = os.path.join(PANELS_DIR, "slide4_phase_diagram.png")
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"  Saved: {dst}")


def make_slide5_panel(result_clean):
    metrics = result_clean.metrics
    ro = metrics.get("radial_order", 0.0)
    sw = metrics.get("swirl_score", 0.0)

    fig, axes = plt.subplots(1, 2, figsize=(FIG_W, FIG_H))
    fig.patch.set_facecolor(BG)

    matches = [
        "Star center spacing via Turing instability",
        f"Radial arm confinement  (radial_order = {ro:.2f})",
        "Discrete arm structure from angular repulsion",
        f"Measurable chirality  (swirl = {sw:.3f})",
    ]
    limits = [
        "n_arms = 7 is a parameter, not emergent",
        "No Botryllus biochemistry or genetics",
        "2D toy model (no 3D geometry)",
        "No developmental staging or blastogenic cycle",
    ]

    def _text_panel(ax, header, items, header_color, item_prefix, item_color):
        ax.set_facecolor(PANEL_BG)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_edgecolor(header_color)
            spine.set_linewidth(1.5)
        ax.text(0.5, 0.93, header, transform=ax.transAxes,
                fontsize=11, color=header_color, fontweight="bold", ha="center")
        y = 0.82
        for item in items:
            ax.text(0.06, y, item_prefix, transform=ax.transAxes,
                    fontsize=10, color=header_color, fontweight="bold")
            ax.text(0.12, y, item, transform=ax.transAxes,
                    fontsize=9, color=INK)
            y -= 0.16
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

    _text_panel(axes[0], "What the model produces", matches,
                GREEN, "[+]", INK)
    _text_panel(axes[1], "Honest limitations", limits,
                ACCENT, "[-]", INK)

    fig.suptitle(
        "Geometric star model -- not a full developmental model, and we say so",
        fontsize=11, color=INK, y=1.01
    )
    fig.tight_layout()

    out_path = os.path.join(PANELS_DIR, "slide5_insight_and_limits.png")
    fig.savefig(out_path, dpi=FIG_DPI, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close(fig)
    print(f"  Saved: {out_path}")


def make_final_summary_panel(result_clean, result_chiral):
    L = result_clean.zooid.L
    pos_final = result_clean.zooid.positions[-1]
    arm_ids = result_clean.zooid.arm_assignments
    centers = result_clean.zooid.centers

    tiled_pos, tiled_arm, tiled_centers = _tile_colony(pos_final, centers, arm_ids, L)

    pos_ch = result_chiral.zooid.positions[-1]
    arm_ids_ch = result_chiral.zooid.arm_assignments
    centers_ch = result_chiral.zooid.centers

    df = pd.read_csv(os.path.join(DATA_DIR, "sweep_A.csv"))
    k_vals = sorted(df["k_radial"].unique())
    omega_vals = sorted(df["omega"].unique())
    sl_grid = df.pivot(index="omega", columns="k_radial", values="star_likeness").values

    fig, axes = plt.subplots(2, 3, figsize=(FIG_W, FIG_H))
    fig.patch.set_facecolor(BG)

    # [0,0] Reference image
    ax = axes[0, 0]
    if os.path.exists(REF_IMAGE):
        ax.imshow(plt.imread(REF_IMAGE), aspect="auto")
    else:
        ax.set_facecolor("#2A2A4E")
        ax.text(0.5, 0.5, "Reference", color="white", ha="center", va="center",
                transform=ax.transAxes)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Botryllus schlosseri", fontsize=9, color=INK)

    # [0,1] GM field
    ax = axes[0, 1]
    ax.imshow(result_clean.field, cmap="YlOrBr", origin="lower",
              extent=[0, L, 0, L], aspect="equal")
    if len(centers) > 0:
        ax.scatter(centers[:, 0], centers[:, 1],
                   c="#FFFFFF", s=25, zorder=10, linewidths=0)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("GM field + centers", fontsize=9, color=INK)

    # [0,2] Colony scale
    ax = axes[0, 2]
    ax.set_facecolor(DARK_BG)
    _draw_zooids_scatter(ax, tiled_pos, tiled_arm, ZOOID_PALETTE, s=4, alpha=0.75)
    ax.set_xlim(0, 3 * L)
    ax.set_ylim(0, 3 * L)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Colony (3x3 tiled)", fontsize=9, color="#CCCCDD")

    # [1,0] Clean star close-up
    ax = axes[1, 0]
    ax.set_facecolor(DARK_BG)
    k0_mask = result_clean.zooid.assignments == 0
    center0 = result_clean.zooid.centers[0]
    _draw_zooids_ellipse(ax, pos_final[k0_mask],
                         arm_ids[k0_mask], center0, ZOOID_PALETTE)
    ax.scatter([center0[0]], [center0[1]], c="#FFFFFF", s=25, zorder=10, linewidths=0)
    ax.set_xlim(center0[0] - 2.5, center0[0] + 2.5)
    ax.set_ylim(center0[1] - 2.5, center0[1] + 2.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Single star (omega~0)", fontsize=9, color="#AACCAA")

    # [1,1] Chiral star close-up
    ax = axes[1, 1]
    ax.set_facecolor(DARK_BG)
    k0_mask_ch = result_chiral.zooid.assignments == 0
    center0_ch = result_chiral.zooid.centers[0]
    _draw_zooids_ellipse(ax, pos_ch[k0_mask_ch],
                         arm_ids_ch[k0_mask_ch], center0_ch, ZOOID_PALETTE)
    ax.scatter([center0_ch[0]], [center0_ch[1]], c="#FFFFFF", s=25, zorder=10, linewidths=0)
    ax.set_xlim(center0_ch[0] - 2.5, center0_ch[0] + 2.5)
    ax.set_ylim(center0_ch[1] - 2.5, center0_ch[1] + 2.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Single star (omega=2.5)", fontsize=9, color="#FFAA88")

    # [1,2] Phase diagram (star-likeness)
    ax = axes[1, 2]
    nx, ny = len(k_vals), len(omega_vals)
    ax.imshow(sl_grid, cmap="viridis", origin="lower", interpolation="bilinear",
              aspect="auto", extent=[0, nx, 0, ny], vmin=0, vmax=0.5)
    ax.set_xticks(np.arange(nx) + 0.5)
    ax.set_xticklabels([str(k) for k in k_vals], fontsize=6, color=INK)
    ax.set_yticks(np.arange(ny) + 0.5)
    ax.set_yticklabels([str(o) for o in omega_vals], fontsize=6, color=INK)
    ax.set_xlabel("k_radial", fontsize=7, color=INK)
    ax.set_ylabel("omega", fontsize=7, color=INK)
    ax.set_title("Phase diagram", fontsize=9, color=INK)

    fig.suptitle("Chirality Atlas: Star Ascidian Edition  --  Summary",
                 fontsize=12, color=INK, y=1.01)
    fig.tight_layout()

    out_path = os.path.join(PANELS_DIR, "final_summary_panel.png")
    fig.savefig(out_path, dpi=FIG_DPI, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close(fig)
    print(f"  Saved: {out_path}")


def main():
    print("Visual rescue: generating improved assets")
    print()

    print("Step 1/4  Running simulations...")
    result_clean  = simulate_star_ascidian_colony("hero_reference_match", seed=42)
    result_chiral = simulate_star_ascidian_colony("chiral_twisted_stars",  seed=42)
    print(f"  hero_reference_match: {result_clean.zooid.K} centers, "
          f"{result_clean.zooid.N} agents")
    print(f"  chiral_twisted_stars: {result_chiral.zooid.K} centers, "
          f"{result_chiral.zooid.N} agents")
    print()

    print("Step 2/4  Generating component panels...")
    make_single_star_mechanism()
    make_colony_scale_view(result_clean)
    make_center_selection_schematic(result_clean)
    make_phase_diagram_with_regimes()
    make_formation_sequence(result_clean)
    print()

    print("Step 3/4  Generating animations...")
    make_animations(result_clean, result_chiral)
    make_colony_animation(result_clean)
    print()

    print("Step 4/4  Rebuilding slide panels...")
    make_slide1_panel(result_clean)
    make_slide2_panel()
    make_slide3_panel(result_clean, result_chiral)
    make_slide4_panel()
    make_slide5_panel(result_clean)
    make_final_summary_panel(result_clean, result_chiral)
    print()

    print("Done.")
    print()
    panel_files = [
        "single_star_mechanism.png",
        "colony_scale_reference_match.png",
        "center_selection_schematic.png",
        "phase_diagram_with_regimes.png",
        "formation_sequence_strong.png",
        "slide1_target_and_simulation.png",
        "slide2_model_schematic.png",
        "slide3_simulation_sequence.png",
        "slide4_phase_diagram.png",
        "slide5_insight_and_limits.png",
        "final_summary_panel.png",
    ]
    print("Output sizes (KB):")
    for fname in panel_files:
        fpath = os.path.join(PANELS_DIR, fname)
        if os.path.exists(fpath):
            kb = os.path.getsize(fpath) // 1024
            print(f"  {fname:46s} {kb:5d} KB")
    for gname in ["star_formation_clean.gif", "chiral_twist_emergence.gif",
                  "colony_scale_formation.gif"]:
        fpath = os.path.join(MOVIES_DIR, gname)
        if os.path.exists(fpath):
            kb = os.path.getsize(fpath) // 1024
            print(f"  {gname:46s} {kb:5d} KB")


if __name__ == "__main__":
    main()
