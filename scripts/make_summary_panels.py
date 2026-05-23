"""
Generate 4 summary panel figures for the 5-slide deck.

Runs lightweight simulations (smaller N, shorter steps) suitable for overview panels.
For publication-quality individual figures, use the dedicated demo scripts.

Outputs (outputs/summary/):
  chirality_atlas_particle_panel.png
  chirality_atlas_pattern_panel.png
  chirality_atlas_bridge_panel.png
  chirality_atlas_final_panel.png

Run from repo root: python scripts/make_summary_panels.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import matplotlib
matplotlib.use("Agg")
import numpy as np

from chirality.particle_sim import simulate_abp, simulate_chiral_abp, simulate_vicsek_chiral
from chirality.pattern_sim import (
    simulate_gray_scott,
    simulate_feed_gradient,
    simulate_obstacle,
    simulate_chiral_source_gray_scott,
)
from chirality.particle_metrics import swirl_index
from chirality.pattern_metrics import field_asymmetry
from chirality.plotting import (
    make_particle_summary_panel,
    make_pattern_summary_panel,
    make_bridge_panel,
    make_final_panel,
)
from chirality.export import save_figure, ensure_dir

OUT = "outputs/summary"
ensure_dir(OUT)

# Simulation parameters scaled for speed (not max quality)
_PARTICLE_N     = 150
_PARTICLE_STEPS = 600
_PARTICLE_L     = 10.0
_PARTICLE_DT    = 0.01

_PATTERN_NX    = 128
_PATTERN_NY    = 128
_PATTERN_STEPS = 4000
_PATTERN_DT    = 1.0
_PATTERN_SEEDS = 8


# ---------------------------------------------------------------------------
print("[1] Running particle simulations for panel...")

print("    baseline ABP")
hist_abp = simulate_abp(
    N=_PARTICLE_N, L=_PARTICLE_L, v0=0.5, Dr=0.5,
    dt=_PARTICLE_DT, n_steps=_PARTICLE_STEPS, seed=42,
    boundary_mode="periodic", save_every=_PARTICLE_STEPS,
)
hist_abp.omegas = np.zeros(hist_abp.N)

print("    vicsek flocking")
hist_vik = simulate_vicsek_chiral(
    N=_PARTICLE_N, L=_PARTICLE_L, v0=0.5, R=1.0,
    eta=0.15, omega=0.0, dt=0.1, n_steps=600, seed=42,
    boundary_mode="periodic", save_every=600,
)

print("    chiral vortex")
hist_cvx = simulate_chiral_abp(
    N=_PARTICLE_N, L=_PARTICLE_L, v0=0.5, Dr=0.2, omega=2.0,
    chirality_mode="right", dt=_PARTICLE_DT,
    n_steps=_PARTICLE_STEPS, seed=42, boundary_mode="periodic",
    repulsion=False, save_every=_PARTICLE_STEPS,
)

print("    boundary edge current")
hist_bnd = simulate_chiral_abp(
    N=_PARTICLE_N, L=_PARTICLE_L, v0=0.5, Dr=0.3, omega=3.0,
    chirality_mode="right", dt=_PARTICLE_DT,
    n_steps=_PARTICLE_STEPS, seed=42, boundary_mode="circular_trap",
    repulsion=False, save_every=_PARTICLE_STEPS,
)

print("    racemic competition")
hist_rac = simulate_chiral_abp(
    N=_PARTICLE_N, L=_PARTICLE_L, v0=0.5, Dr=0.3, omega=2.0,
    chirality_mode="racemic", dt=_PARTICLE_DT,
    n_steps=_PARTICLE_STEPS, seed=42, boundary_mode="periodic",
    repulsion=True, repulsion_strength=2.0, repulsion_range=0.4,
    save_every=_PARTICLE_STEPS,
)

particle_hists  = [hist_abp, hist_vik, hist_cvx, hist_bnd, hist_rac]
particle_labels = [
    "Baseline ABP",
    "Vicsek Flocking",
    "Chiral Vortex",
    "Boundary Edge Current",
    "Racemic Competition",
]

fig = make_particle_summary_panel(particle_hists, particle_labels, figsize=(18, 4))
save_figure(fig, f"{OUT}/chirality_atlas_particle_panel.png", dpi=150)
print(f"  -> {OUT}/chirality_atlas_particle_panel.png")
print()

# ---------------------------------------------------------------------------
print("[2] Running pattern simulations for panel...")

print("    Gray-Scott spots")
hist_spt = simulate_gray_scott(
    nx=_PATTERN_NX, ny=_PATTERN_NY, Du=0.16, Dv=0.08,
    F=0.035, k=0.065, dt=_PATTERN_DT, n_steps=_PATTERN_STEPS,
    seed=42, save_every=_PATTERN_STEPS, perturbation_size=4, n_seeds=_PATTERN_SEEDS,
)

print("    Gray-Scott labyrinth")
hist_lab = simulate_gray_scott(
    nx=_PATTERN_NX, ny=_PATTERN_NY, Du=0.16, Dv=0.08,
    F=0.04, k=0.06, dt=_PATTERN_DT, n_steps=_PATTERN_STEPS,
    seed=42, save_every=_PATTERN_STEPS, perturbation_size=5, n_seeds=_PATTERN_SEEDS,
)

print("    feed gradient")
hist_fgr = simulate_feed_gradient(
    nx=_PATTERN_NX, ny=_PATTERN_NY, Du=0.16, Dv=0.08,
    F_left=0.02, F_right=0.055, k=0.063, dt=_PATTERN_DT,
    n_steps=_PATTERN_STEPS, seed=42, save_every=_PATTERN_STEPS,
    perturbation_size=4, n_seeds=_PATTERN_SEEDS,
)

print("    obstacle disrupted")
hist_obs = simulate_obstacle(
    nx=_PATTERN_NX, ny=_PATTERN_NY, Du=0.16, Dv=0.08,
    F=0.035, k=0.065, dt=_PATTERN_DT, n_steps=_PATTERN_STEPS,
    seed=42, obstacle_cx=0.5, obstacle_cy=0.5, obstacle_r=0.12,
    save_every=_PATTERN_STEPS, perturbation_size=4, n_seeds=_PATTERN_SEEDS,
)

print("    chiral source")
hist_chi = simulate_chiral_source_gray_scott(
    nx=_PATTERN_NX, ny=_PATTERN_NY, Du=0.16, Dv=0.08,
    F=0.035, k=0.065, dt=_PATTERN_DT, n_steps=_PATTERN_STEPS,
    seed=42, source_strength=0.02, source_omega=0.1,
    source_r_orbit=0.2, source_sigma=0.05,
    save_every=_PATTERN_STEPS, perturbation_size=5, n_seeds=None,
)

field_hists  = [hist_spt, hist_lab, hist_fgr, hist_obs, hist_chi]
field_labels = [
    "GS Spots",
    "Labyrinth",
    "Feed Gradient",
    "Obstacle",
    "Chiral Source",
]

fig = make_pattern_summary_panel(field_hists, field_labels, figsize=(18, 4))
save_figure(fig, f"{OUT}/chirality_atlas_pattern_panel.png", dpi=150)
print(f"  -> {OUT}/chirality_atlas_pattern_panel.png")
print()

# ---------------------------------------------------------------------------
print("[3] Bridge panel (2x2 comparison)")
fig = make_bridge_panel(
    particle_hists=[hist_vik, hist_cvx],
    particle_labels=["Vicsek Flocking  (baseline)", "Chiral Vortex  (extended)"],
    field_hists=[hist_spt, hist_chi],
    field_labels=["GS Spots  (baseline)", "Chiral Source  (extended)"],
    figsize=(13, 8),
)
save_figure(fig, f"{OUT}/chirality_atlas_bridge_panel.png", dpi=150)
print(f"  -> {OUT}/chirality_atlas_bridge_panel.png")
print()

# ---------------------------------------------------------------------------
print("[4] Final hero panel")
swirl = swirl_index(hist_cvx.positions[-1], hist_cvx.thetas[-1], hist_cvx.L)
asym  = field_asymmetry(hist_chi.v_final)

p_metric_str = f"swirl index = {swirl:.3f}\n(omega=2, right-handed)"
f_metric_str = f"L-R asymmetry = {asym:.4f}\n(omega=0.1 source)"

fig = make_final_panel(
    particle_hist=hist_bnd,
    field_hist=hist_chi,
    particle_label="Boundary Edge Current  (omega=3, circular trap)",
    field_label="Chiral Source  (omega=0.1)",
    particle_metric_str=p_metric_str,
    field_metric_str=f_metric_str,
    figsize=(14, 6),
)
save_figure(fig, f"{OUT}/chirality_atlas_final_panel.png", dpi=150)
print(f"  -> {OUT}/chirality_atlas_final_panel.png")
print()

print("Done. Summary panels written to outputs/summary/")
