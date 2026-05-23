"""
Run parameter sweeps and generate phase diagram figures.

All sweeps use small grids (6x6 or 5x5) for laptop speed.
Labels on each figure note the grid size.

Outputs (outputs/phase_sweeps/):
  particle_noise_vs_chirality_polar_order.png
  particle_noise_vs_chirality_swirl_index.png
  particle_noise_vs_chirality_clustering.png
  particle_noise_vs_chirality_boundary_accumulation.png
  pattern_F_vs_k_pattern_strength.png
  pattern_F_vs_k_cluster_count.png
  pattern_chiral_source_asymmetry.png

Outputs (outputs/data/):
  particle_phase_sweep.csv
  pattern_phase_sweep.csv
  chiral_pattern_sweep.csv

Outputs (outputs/phase_sweeps/):
  sanity_check.txt

Run from repo root: python scripts/run_phase_sweeps.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import matplotlib
matplotlib.use("Agg")

import numpy as np
from chirality.phase_sweeps import (
    sweep_noise_vs_chirality,
    sweep_gray_scott_F_k,
    sweep_chiral_source,
)
from chirality.plotting import plot_phase_diagram
from chirality.export import (
    save_figure,
    ensure_dir,
    save_phase_diagram_data,
    save_sweep_csv,
    save_sanity_report,
)

SWEEP_OUT = "outputs/phase_sweeps"
DATA_OUT  = "outputs/data"
ensure_dir(SWEEP_OUT)
ensure_dir(DATA_OUT)

# Sanity-check registry: accumulate all metric grids for final report
_sanity = {}

# ---------------------------------------------------------------------------
print("[1] Particle: noise (Dr) vs chirality (omega)  -- 6x6 grid, 250 steps/pt")
print("    Metrics: polar order, swirl index, avg neighbors, boundary accumulation")
results_p = sweep_noise_vs_chirality(
    noise_values=np.linspace(0.1, 3.0, 6),
    chirality_values=np.linspace(0.0, 4.0, 6),
    N=80,
    L=10.0,
    v0=0.5,
    dt=0.01,
    n_steps=250,
    seed=0,
    verbose=True,
)
save_phase_diagram_data(results_p, f"{SWEEP_OUT}/particle_sweep_data.npz")
save_sweep_csv(
    results_p,
    param_keys=["noise_values", "chirality_values"],
    metric_keys=["polar_order", "swirl_index", "boundary_accumulation", "avg_neighbors"],
    path=f"{DATA_OUT}/particle_phase_sweep.csv",
)
_sanity["particle_polar_order"]         = results_p["polar_order"]
_sanity["particle_swirl_index"]         = results_p["swirl_index"]
_sanity["particle_boundary_accum"]      = results_p["boundary_accumulation"]
_sanity["particle_avg_neighbors"]       = results_p["avg_neighbors"]

fig = plot_phase_diagram(
    results_p["noise_values"],
    results_p["chirality_values"],
    results_p["polar_order"],
    param1_label="Rotational noise  Dr",
    param2_label="Chirality  omega",
    metric_label="Polar order",
    title="Chiral ABP: Polar Order",
    vmin=0, vmax=1,
)
save_figure(fig, f"{SWEEP_OUT}/particle_noise_vs_chirality_polar_order.png")
print(f"  -> {SWEEP_OUT}/particle_noise_vs_chirality_polar_order.png")

fig = plot_phase_diagram(
    results_p["noise_values"],
    results_p["chirality_values"],
    results_p["swirl_index"],
    param1_label="Rotational noise  Dr",
    param2_label="Chirality  omega",
    metric_label="Swirl index",
    title="Chiral ABP: Swirl Index",
    vmin=-1, vmax=1,
    cmap="RdBu_r",
)
save_figure(fig, f"{SWEEP_OUT}/particle_noise_vs_chirality_swirl_index.png")
print(f"  -> {SWEEP_OUT}/particle_noise_vs_chirality_swirl_index.png")

fig = plot_phase_diagram(
    results_p["noise_values"],
    results_p["chirality_values"],
    results_p["avg_neighbors"],
    param1_label="Rotational noise  Dr",
    param2_label="Chirality  omega",
    metric_label="Avg neighbors (R=1)",
    title="Chiral ABP: Local Clustering",
    vmin=0,
    cmap="plasma",
)
save_figure(fig, f"{SWEEP_OUT}/particle_noise_vs_chirality_clustering.png")
print(f"  -> {SWEEP_OUT}/particle_noise_vs_chirality_clustering.png")

fig = plot_phase_diagram(
    results_p["noise_values"],
    results_p["chirality_values"],
    results_p["boundary_accumulation"],
    param1_label="Rotational noise  Dr",
    param2_label="Chirality  omega",
    metric_label="Boundary accumulation",
    title="Chiral ABP: Boundary Accumulation",
    vmin=0, vmax=1,
    cmap="hot",
)
save_figure(fig, f"{SWEEP_OUT}/particle_noise_vs_chirality_boundary_accumulation.png")
print(f"  -> {SWEEP_OUT}/particle_noise_vs_chirality_boundary_accumulation.png")
print()

# ---------------------------------------------------------------------------
print("[2] Gray-Scott: F vs k phase diagram  -- 6x6 grid, 64x64, 2000 steps/pt")
results_gs = sweep_gray_scott_F_k(
    F_values=np.linspace(0.01, 0.07, 6),
    k_values=np.linspace(0.04, 0.07, 6),
    nx=64, ny=64,
    dt=1.0,
    n_steps=2000,
    seed=42,
    verbose=True,
)
save_phase_diagram_data(results_gs, f"{SWEEP_OUT}/gray_scott_sweep_data.npz")
save_sweep_csv(
    results_gs,
    param_keys=["F_values", "k_values"],
    metric_keys=["pattern_strength", "n_clusters"],
    path=f"{DATA_OUT}/pattern_phase_sweep.csv",
)
_sanity["gs_pattern_strength"] = results_gs["pattern_strength"]
_sanity["gs_cluster_count"]    = results_gs["n_clusters"]

fig = plot_phase_diagram(
    results_gs["F_values"],
    results_gs["k_values"],
    results_gs["pattern_strength"],
    param1_label="Feed rate  F",
    param2_label="Kill rate  k",
    metric_label="Pattern strength  (std v)",
    title="Gray-Scott: Pattern Strength",
)
save_figure(fig, f"{SWEEP_OUT}/pattern_F_vs_k_pattern_strength.png")
print(f"  -> {SWEEP_OUT}/pattern_F_vs_k_pattern_strength.png")

fig = plot_phase_diagram(
    results_gs["F_values"],
    results_gs["k_values"],
    results_gs["n_clusters"],
    param1_label="Feed rate  F",
    param2_label="Kill rate  k",
    metric_label="Cluster count",
    title="Gray-Scott: Cluster Count",
    cmap="plasma",
)
save_figure(fig, f"{SWEEP_OUT}/pattern_F_vs_k_cluster_count.png")
print(f"  -> {SWEEP_OUT}/pattern_F_vs_k_cluster_count.png")
print()

# ---------------------------------------------------------------------------
print("[3] Chiral source: source_omega vs F  -- 5x5 grid, 64x64, 2000 steps/pt")
results_cs = sweep_chiral_source(
    source_omega_values=np.linspace(0.0, 0.2, 5),
    F_values=np.linspace(0.025, 0.055, 5),
    nx=64, ny=64,
    k=0.065,
    dt=1.0,
    n_steps=2000,
    seed=42,
    verbose=True,
)
save_phase_diagram_data(results_cs, f"{SWEEP_OUT}/chiral_source_sweep_data.npz")
save_sweep_csv(
    results_cs,
    param_keys=["source_omega_values", "F_values"],
    metric_keys=["pattern_strength", "field_asymmetry"],
    path=f"{DATA_OUT}/chiral_pattern_sweep.csv",
)
_sanity["cs_pattern_strength"] = results_cs["pattern_strength"]
_sanity["cs_field_asymmetry"]  = results_cs["field_asymmetry"]

fig = plot_phase_diagram(
    results_cs["source_omega_values"],
    results_cs["F_values"],
    results_cs["field_asymmetry"],
    param1_label="Source rotation speed  omega",
    param2_label="Feed rate  F",
    metric_label="|L-R asymmetry|",
    title="Chiral Source: L-R Asymmetry  (toy model)",
    cmap="inferno",
)
save_figure(fig, f"{SWEEP_OUT}/pattern_chiral_source_asymmetry.png")
print(f"  -> {SWEEP_OUT}/pattern_chiral_source_asymmetry.png")
print()

# ---------------------------------------------------------------------------
print("[4] Sanity check: validate all metric grids")
ok = save_sanity_report(_sanity, f"{SWEEP_OUT}/sanity_check.txt")
if not ok:
    print("  WARNING: sanity check failed -- inspect sanity_check.txt")
print()

print("Done. Phase diagrams and data written to outputs/")
