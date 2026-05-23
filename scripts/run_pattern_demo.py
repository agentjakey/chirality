"""
Generate pattern formation demo figures for the Chirality Atlas.

Outputs (outputs/demo/):
  pattern_gray_scott_spots.png
  pattern_gray_scott_labyrinth.png
  pattern_feed_gradient.png
  pattern_obstacle_disrupted.png
  pattern_chiral_source.png

Run from repo root: python scripts/run_pattern_demo.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import matplotlib
matplotlib.use("Agg")

from chirality.pattern_sim import (
    simulate_gray_scott,
    simulate_feed_gradient,
    simulate_obstacle,
    simulate_chiral_source_gray_scott,
)
from chirality.pattern_metrics import compute_all_pattern_metrics
from chirality.plotting import plot_field
from chirality.export import save_figure, ensure_dir
from chirality.storytelling import summarize_pattern_metrics
from chirality.presets import (
    GRAY_SCOTT_SPOTS,
    GRAY_SCOTT_LABYRINTH,
    FEED_GRADIENT_PATTERN,
    OBSTACLE_DISRUPTED_PATTERN,
    CHIRAL_SOURCE_PATTERN,
)

OUT = "outputs/demo"
ensure_dir(OUT)

FIGSIZE = (6, 5)


def run_and_save(label, display_title, hist, out_path):
    metrics = compute_all_pattern_metrics(hist)
    summary = summarize_pattern_metrics(metrics, label)
    print(f"  {label}:")
    for line in summary.split("\n"):
        print(f"    {line}")

    fig = plot_field(
        hist.v_final,
        title=display_title,
        cmap="YlOrBr",
        vmin=0,
        vmax=0.5,
        figsize=FIGSIZE,
    )
    save_figure(fig, out_path, dpi=150)
    print(f"  -> {out_path}")
    return metrics


print("=== Pattern Demo ===")
print()

print("[1] Gray-Scott Spots (F=0.035, k=0.065)")
hist = simulate_gray_scott(**GRAY_SCOTT_SPOTS)
run_and_save(
    "gray_scott_spots",
    "Gray-Scott Spots  (F=0.035, k=0.065)",
    hist,
    f"{OUT}/pattern_gray_scott_spots.png",
)
print()

print("[2] Gray-Scott Labyrinth (F=0.04, k=0.06)")
hist = simulate_gray_scott(**GRAY_SCOTT_LABYRINTH)
run_and_save(
    "gray_scott_labyrinth",
    "Gray-Scott Labyrinth  (F=0.04, k=0.06)",
    hist,
    f"{OUT}/pattern_gray_scott_labyrinth.png",
)
print()

print("[3] Feed Gradient Pattern")
hist = simulate_feed_gradient(**FEED_GRADIENT_PATTERN)
run_and_save(
    "feed_gradient",
    "Feed Gradient  (F: 0.02 left -> 0.055 right)",
    hist,
    f"{OUT}/pattern_feed_gradient.png",
)
print()

print("[4] Obstacle Disrupted Pattern")
hist = simulate_obstacle(**OBSTACLE_DISRUPTED_PATTERN)
run_and_save(
    "obstacle_disrupted",
    "Obstacle Disrupted  (r=0.12, center)",
    hist,
    f"{OUT}/pattern_obstacle_disrupted.png",
)
print()

print("[5] Chiral Source Pattern (toy model)")
hist = simulate_chiral_source_gray_scott(**CHIRAL_SOURCE_PATTERN)
run_and_save(
    "chiral_source",
    "Chiral Source  (omega=0.1, single center seed)",
    hist,
    f"{OUT}/pattern_chiral_source.png",
)
print()

print("Done. Pattern figures written to outputs/demo/")
