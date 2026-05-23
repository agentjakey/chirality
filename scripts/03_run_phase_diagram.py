"""
Run four phase diagram sweeps for the star ascidian model.

Saves figures and CSVs to:
  outputs/phase_diagrams/sweep_A_attraction_vs_chirality.png
  outputs/phase_diagrams/sweep_B_noise_vs_repulsion.png
  outputs/phase_diagrams/sweep_C_inhibition_ratio.png
  outputs/phase_diagrams/sweep_D_chirality_vs_occupancy.png
  outputs/data/sweep_A.csv
  outputs/data/sweep_B.csv
  outputs/data/sweep_C.csv
  outputs/data/sweep_D.csv

Run from repo root: python scripts/03_run_phase_diagram.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from chirality.model_library import ensure_dir
from chirality.star_ascidian.phase_diagram import (
    sweep_attraction_vs_chirality,
    sweep_noise_vs_repulsion,
    sweep_inhibition_ratio,
    sweep_chirality_vs_occupancy,
    save_phase_diagram_csv,
)
from chirality.visualization.style import (
    BG, INK, BORDER, ACCENT, GREEN, NEUTRAL,
    PHASE_CMAP, TITLE_FS, LABEL_FS, TICK_FS,
    apply_notebook_style,
)

OUTPUT_FIGS = os.path.join("outputs", "phase_diagrams")
OUTPUT_DATA = os.path.join("outputs", "data")
ensure_dir(OUTPUT_FIGS)
ensure_dir(OUTPUT_DATA)
apply_notebook_style()


def _pcolor_panel(ax, x_vals, y_vals, z_grid, xlabel, ylabel, title, cmap=PHASE_CMAP,
                  vmin=None, vmax=None):
    """Draw one pcolormesh panel with shared style."""
    ax.set_facecolor(BG)
    im = ax.pcolormesh(x_vals, y_vals, z_grid, cmap=cmap,
                       vmin=vmin, vmax=vmax, shading="nearest")
    cbar = ax.get_figure().colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=TICK_FS, colors=INK)
    cbar.outline.set_edgecolor(INK)
    ax.set_xlabel(xlabel, fontsize=LABEL_FS, color=INK)
    ax.set_ylabel(ylabel, fontsize=LABEL_FS, color=INK)
    ax.tick_params(colors=INK, labelsize=TICK_FS)
    ax.set_title(title, fontsize=LABEL_FS, color=INK)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)
    return im


def run_sweep_A(seed=42):
    print("Sweep A: k_radial vs omega -> star_likeness, swirl")
    k_radial_vals = np.array([0.5, 1.0, 2.0, 3.5, 5.0])
    omega_vals = np.array([0.0, 0.5, 1.5, 3.0, 5.0])
    x_vals, y_vals, grids = sweep_attraction_vs_chirality(
        k_radial_vals=k_radial_vals, omega_vals=omega_vals, seed=seed
    )

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), facecolor=BG)
    fig.suptitle("Sweep A: Radial attraction vs Chirality", fontsize=TITLE_FS, color=INK)
    _pcolor_panel(axes[0], x_vals, y_vals, grids["star_likeness"],
                  "k_radial", "omega", "Star-likeness score", vmin=0, vmax=1)
    _pcolor_panel(axes[1], x_vals, y_vals, grids["swirl"],
                  "k_radial", "omega", "Swirl magnitude", vmin=0, vmax=1)
    fig.tight_layout()
    path = os.path.join(OUTPUT_FIGS, "sweep_A_attraction_vs_chirality.png")
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")

    csv_path = os.path.join(OUTPUT_DATA, "sweep_A.csv")
    save_phase_diagram_csv(grids, x_vals, y_vals, "k_radial", "omega", csv_path)
    print(f"  Saved: {csv_path}")


def run_sweep_B(seed=42):
    print("Sweep B: Dr vs k_angular -> fragmentation, star_likeness")
    Dr_vals = np.array([0.01, 0.1, 0.3, 0.7, 1.5])
    k_angular_vals = np.array([0.1, 0.3, 0.6, 1.0, 1.5])
    x_vals, y_vals, grids = sweep_noise_vs_repulsion(
        Dr_vals=Dr_vals, k_angular_vals=k_angular_vals, seed=seed
    )

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), facecolor=BG)
    fig.suptitle("Sweep B: Noise vs Angular Repulsion", fontsize=TITLE_FS, color=INK)
    _pcolor_panel(axes[0], x_vals, y_vals, grids["fragmentation"],
                  "Dr (noise)", "k_angular", "Fragmentation score",
                  cmap="RdYlGn_r", vmin=0, vmax=1)
    _pcolor_panel(axes[1], x_vals, y_vals, grids["star_likeness"],
                  "Dr (noise)", "k_angular", "Star-likeness score", vmin=0, vmax=1)
    fig.tight_layout()
    path = os.path.join(OUTPUT_FIGS, "sweep_B_noise_vs_repulsion.png")
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")

    csv_path = os.path.join(OUTPUT_DATA, "sweep_B.csv")
    save_phase_diagram_csv(grids, x_vals, y_vals, "Dr", "k_angular", csv_path)
    print(f"  Saved: {csv_path}")


def run_sweep_C(seed=42):
    print("Sweep C: Dh/Da ratio vs mu_h -> center count, spacing quality")
    Dh_vals = np.array([0.5, 1.0, 2.0, 5.0, 10.0])
    mu_h_vals = np.array([0.02, 0.05, 0.10, 0.20, 0.40])
    ratio_vals, y_vals, grids = sweep_inhibition_ratio(
        Dh_vals=Dh_vals, mu_h_vals=mu_h_vals, seed=seed
    )

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2), facecolor=BG)
    fig.suptitle("Sweep C: Inhibition Ratio vs Decay Rate", fontsize=TITLE_FS, color=INK)
    _pcolor_panel(axes[0], ratio_vals, y_vals, grids["n_centers"],
                  "Dh/Da", "mu_h", "Number of centers", cmap="Blues")
    _pcolor_panel(axes[1], ratio_vals, y_vals, grids["spacing_cv"],
                  "Dh/Da", "mu_h", "Spacing CV (lower = more regular)",
                  cmap="RdYlGn_r", vmin=0, vmax=1)
    _pcolor_panel(axes[2], ratio_vals, y_vals, grids["spacing_quality"],
                  "Dh/Da", "mu_h", "Spacing quality (1 - CV)", vmin=0, vmax=1)
    fig.tight_layout()
    path = os.path.join(OUTPUT_FIGS, "sweep_C_inhibition_ratio.png")
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")

    csv_path = os.path.join(OUTPUT_DATA, "sweep_C.csv")
    save_phase_diagram_csv(grids, ratio_vals, y_vals, "Dh_over_Da", "mu_h", csv_path)
    print(f"  Saved: {csv_path}")


def run_sweep_D(seed=42):
    print("Sweep D: omega vs n_per_arm -> swirl, star_likeness")
    omega_vals = np.array([0.0, 0.5, 1.5, 3.0, 5.0])
    n_per_arm_vals = np.array([1, 2, 3, 5, 8])
    x_vals, y_vals, grids = sweep_chirality_vs_occupancy(
        omega_vals=omega_vals, n_per_arm_vals=n_per_arm_vals, seed=seed
    )

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), facecolor=BG)
    fig.suptitle("Sweep D: Chirality vs Arm Occupancy", fontsize=TITLE_FS, color=INK)
    _pcolor_panel(axes[0], x_vals, y_vals, grids["swirl"],
                  "omega", "n_per_arm", "Swirl magnitude", vmin=0, vmax=1)
    _pcolor_panel(axes[1], x_vals, y_vals, grids["star_likeness"],
                  "omega", "n_per_arm", "Star-likeness score", vmin=0, vmax=1)
    fig.tight_layout()
    path = os.path.join(OUTPUT_FIGS, "sweep_D_chirality_vs_occupancy.png")
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")

    csv_path = os.path.join(OUTPUT_DATA, "sweep_D.csv")
    save_phase_diagram_csv(grids, x_vals, y_vals, "omega", "n_per_arm", csv_path)
    print(f"  Saved: {csv_path}")


def main():
    print("=" * 60)
    print("Star Ascidian Phase Diagram Sweeps")
    print("=" * 60)
    print(f"Figures -> {OUTPUT_FIGS}")
    print(f"CSVs    -> {OUTPUT_DATA}")
    print()

    run_sweep_A(seed=42)
    print()
    run_sweep_B(seed=42)
    print()
    run_sweep_C(seed=42)
    print()
    run_sweep_D(seed=42)

    print("\n" + "=" * 60)
    print("All phase diagrams saved.")


if __name__ == "__main__":
    main()
