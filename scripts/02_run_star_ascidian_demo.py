"""
Run star ascidian colony simulations for all presets and save figures.

Generates:
  outputs/star_ascidian/clean_star_systems.png
  outputs/star_ascidian/chiral_twisted_stars.png
  outputs/star_ascidian/racemic_mixed.png
  outputs/star_ascidian/overcrowded_merged_systems.png
  outputs/star_ascidian/noisy_fragmented_systems.png
  outputs/star_ascidian/boundary_pinned_stars.png
  outputs/star_ascidian/simulation_vs_target_features.png

Run from repo root: python scripts/02_run_star_ascidian_demo.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from chirality.model_library import ensure_dir
from chirality.star_ascidian.hybrid_model import simulate_star_ascidian_colony, PRESETS
from chirality.star_ascidian import compare as star_compare
from chirality.star_ascidian import metrics as star_metrics
from chirality.visualization.style import (
    BG, INK, ACCENT, GREEN, NEUTRAL, BORDER,
    FIELD_CMAP, TITLE_FS, LABEL_FS, TICK_FS,
    apply_notebook_style,
)

OUTPUT_DIR = os.path.join("outputs", "star_ascidian")
ensure_dir(OUTPUT_DIR)
apply_notebook_style()


def plot_colony_overview(result, preset_name, output_path):
    """Four-panel figure: GM field, inhibitor, agent snapshot, metric summary."""
    fig, axes = plt.subplots(1, 4, figsize=(16, 4), facecolor=BG)
    fig.suptitle(preset_name.replace("_", " ").title(), fontsize=TITLE_FS, color=INK)

    L = result.params["L"]

    # Panel 1: activator field
    ax = axes[0]
    ax.set_facecolor(BG)
    im = ax.imshow(result.field, origin="lower", extent=[0, L, 0, L],
                   cmap=FIELD_CMAP, interpolation="nearest")
    ax.scatter(result.centers[:, 0], result.centers[:, 1],
               s=30, color=INK, marker="+", linewidths=1.2, zorder=5)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=TICK_FS, colors=INK)
    ax.set_title("Activator field (GM)", fontsize=LABEL_FS, color=INK)
    ax.set_xlabel("x", fontsize=TICK_FS, color=INK)
    ax.set_ylabel("y", fontsize=TICK_FS, color=INK)
    ax.tick_params(colors=INK, labelsize=TICK_FS)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)

    # Panel 2: inhibitor field
    ax = axes[1]
    ax.set_facecolor(BG)
    im2 = ax.imshow(result.inhibitor, origin="lower", extent=[0, L, 0, L],
                    cmap="Blues", interpolation="nearest")
    ax.scatter(result.centers[:, 0], result.centers[:, 1],
               s=30, color=INK, marker="+", linewidths=1.2, zorder=5)
    cbar2 = fig.colorbar(im2, ax=ax, fraction=0.046, pad=0.04)
    cbar2.ax.tick_params(labelsize=TICK_FS, colors=INK)
    ax.set_title("Inhibitor field (GM)", fontsize=LABEL_FS, color=INK)
    ax.set_xlabel("x", fontsize=TICK_FS, color=INK)
    ax.set_ylabel("y", fontsize=TICK_FS, color=INK)
    ax.tick_params(colors=INK, labelsize=TICK_FS)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)

    # Panel 3: agent snapshot
    star_compare.plot_simulation_snapshot(
        axes[2], result.zooid,
        title=f"Agents (K={result.zooid.K}, N={result.zooid.N})"
    )
    axes[2].set_xlim(0, L)
    axes[2].set_ylim(0, L)

    # Panel 4: metric bar chart
    m = result.metrics
    metric_names = ["star_likeness", "radial_order", "ang. uniformity",
                    "1-fragmentation", "1-merge"]
    raw_values = [
        m["star_likeness_score"],
        m["radial_order"],
        m["angular_uniformity"],
        max(0.0, 1.0 - m["fragmentation"]),
        max(0.0, 1.0 - m["merge_score"]),
    ]
    ax = axes[3]
    ax.set_facecolor(BG)
    y_pos = np.arange(len(metric_names))
    bar_colors = [ACCENT if v >= 0.5 else NEUTRAL for v in raw_values]
    bars = ax.barh(y_pos, raw_values, color=bar_colors, height=0.55, alpha=0.85)
    ax.axvline(0.5, color=BORDER, linewidth=1.0, linestyle="--")
    ax.set_xlim(0, 1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(metric_names, fontsize=TICK_FS, color=INK)
    ax.set_xlabel("score", fontsize=TICK_FS, color=INK)
    ax.set_title("Metrics", fontsize=LABEL_FS, color=INK)
    ax.tick_params(colors=INK, labelsize=TICK_FS)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)
    for bar, val in zip(bars, raw_values):
        ax.text(min(val + 0.02, 0.93), bar.get_y() + bar.get_height() / 2,
                f"{val:.2f}", va="center", fontsize=TICK_FS - 1, color=INK)

    fig.tight_layout()
    fig.savefig(output_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {output_path}")


def run_preset(preset_name, seed=42):
    print(f"\nRunning preset: {preset_name}")
    result = simulate_star_ascidian_colony(preset=preset_name, seed=seed)

    m = result.metrics
    print(f"  Centers: {result.zooid.K} | N={result.zooid.N}")
    print(f"  star_likeness={m['star_likeness_score']:.3f}  "
          f"radial={m['radial_order']:.3f}  "
          f"uniformity={m['angular_uniformity']:.3f}")
    print(f"  swirl={m['swirl_score']:.3f}  "
          f"frag={m['fragmentation']:.3f}  "
          f"merge={m['merge_score']:.3f}")
    if m["failures"]:
        print(f"  Failures: {'; '.join(m['failures'])}")

    output_path = os.path.join(OUTPUT_DIR, f"{preset_name}.png")
    plot_colony_overview(result, preset_name, output_path)
    return result


def main():
    print("=" * 60)
    print("Star Ascidian Colony Demo")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR}")

    presets_to_run = [
        "clean_star_systems",
        "chiral_twisted_stars",
        "racemic_mixed",
        "overcrowded_merged_systems",
        "noisy_fragmented_systems",
        "boundary_pinned_stars",
    ]

    results = {}
    for preset_name in presets_to_run:
        results[preset_name] = run_preset(preset_name, seed=42)

    # Simulation vs target comparison for clean preset
    print("\nGenerating simulation_vs_target_features.png ...")
    clean_result = results["clean_star_systems"]
    fig = star_compare.compare_to_target(
        clean_result.zooid,
        target_arms=clean_result.params["n_arms"],
        title="Star Ascidian: Simulation vs Target",
    )
    target_path = os.path.join(OUTPUT_DIR, "simulation_vs_target_features.png")
    fig.savefig(target_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {target_path}")

    print("\n" + "=" * 60)
    print("All figures saved.")


if __name__ == "__main__":
    main()
