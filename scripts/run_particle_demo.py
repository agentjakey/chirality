"""
Generate particle demo figures for the Chirality Atlas.

Outputs (outputs/demo/):
  particle_baseline_abp.png
  particle_vicsek_flocking.png
  particle_chiral_vortex.png
  particle_boundary_edge_current.png
  particle_racemic_competition.png

Run from repo root: python scripts/run_particle_demo.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import matplotlib
matplotlib.use("Agg")
import numpy as np

from chirality.particle_sim import simulate_abp, simulate_chiral_abp, simulate_vicsek_chiral
from chirality.particle_metrics import compute_all_particle_metrics
from chirality.plotting import plot_particle_snapshot, plot_trajectory_trails
from chirality.export import save_figure, ensure_dir
from chirality.storytelling import summarize_particle_metrics
from chirality.presets import (
    BASELINE_ACTIVE_BROWNIAN,
    VICSEK_FLOCKING,
    CHIRAL_VORTEX_GAS,
    BOUNDARY_EDGE_CURRENT,
    RACEMIC_LEFT_RIGHT_COMPETITION,
)

OUT = "outputs/demo"
ensure_dir(OUT)

FIGSIZE = (6, 6)


def run_and_save(label, display_title, hist, out_path):
    metrics = compute_all_particle_metrics(hist, R_neighbor=1.0)
    summary = summarize_particle_metrics(metrics, label)
    print(f"  {label}:")
    for line in summary.split("\n"):
        print(f"    {line}")

    fig = plot_particle_snapshot(
        hist.positions[-1],
        hist.thetas[-1],
        hist.omegas,
        hist.L,
        title=display_title,
        show_arrows=True,
        figsize=FIGSIZE,
    )
    save_figure(fig, out_path, dpi=150)
    print(f"  -> {out_path}")
    return metrics


print("=== Particle Demo ===")
print()

# 1. Baseline ABP
print("[1] Baseline Active Brownian Particles (no chirality)")
hist = simulate_abp(**BASELINE_ACTIVE_BROWNIAN)
hist.omegas = np.zeros(hist.N)
run_and_save(
    "baseline_abp",
    "Baseline ABP  (Dr=0.5, omega=0)",
    hist,
    f"{OUT}/particle_baseline_abp.png",
)
print()

# 2. Vicsek flocking
print("[2] Vicsek Flocking (alignment + low noise)")
hist = simulate_vicsek_chiral(**VICSEK_FLOCKING)
run_and_save(
    "vicsek_flocking",
    "Vicsek Flocking  (eta=0.15, omega=0)",
    hist,
    f"{OUT}/particle_vicsek_flocking.png",
)
print()

# 3. Chiral vortex gas
print("[3] Chiral Vortex Gas (all right-handed)")
hist = simulate_chiral_abp(**CHIRAL_VORTEX_GAS)
run_and_save(
    "chiral_vortex",
    "Chiral Vortex Gas  (omega=2, right)",
    hist,
    f"{OUT}/particle_chiral_vortex.png",
)
print()

# 4. Boundary edge current
print("[4] Boundary Edge Current (circular trap + chirality)")
hist = simulate_chiral_abp(**BOUNDARY_EDGE_CURRENT)
run_and_save(
    "boundary_edge_current",
    "Boundary Edge Current  (omega=3, circular trap)",
    hist,
    f"{OUT}/particle_boundary_edge_current.png",
)
print()

# 5. Racemic competition
print("[5] Racemic Competition (equal left/right with repulsion)")
hist = simulate_chiral_abp(**RACEMIC_LEFT_RIGHT_COMPETITION)
run_and_save(
    "racemic_competition",
    "Racemic Competition  (50% left / 50% right)",
    hist,
    f"{OUT}/particle_racemic_competition.png",
)
print()

print("Done. Particle figures written to outputs/demo/")
