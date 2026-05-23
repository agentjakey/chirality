"""
Generate all final presentation assets for Chirality Atlas.

Runs in order:
  1. Reference model outputs (correct filenames)
  2. Star ascidian demo outputs
  3. Phase diagram outputs (correct filenames)
  4. Movie GIFs
  5. Presentation panels
  6. Data exports (CSV, JSON)

Run from repo root: python scripts/05_make_all_assets.py
"""

import sys
import os
import json
import csv
import importlib.util

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from chirality.model_library import ensure_dir
from chirality.model_library.fisher_kpp import simulate_fisher_kpp, front_radius
from chirality.model_library.fitzhugh_nagumo import simulate_fitzhugh_nagumo
from chirality.model_library.gierer_meinhardt import (
    simulate_gierer_meinhardt, find_activator_centers, pattern_strength
)
from chirality.model_library.cahn_hilliard import simulate_cahn_hilliard, domain_size_proxy
from chirality.model_library.gray_scott import simulate_gray_scott
from chirality.model_library.active_particles import simulate_chiral_abp, swirl_index
from chirality.star_ascidian.hybrid_model import simulate_star_ascidian_colony, PRESETS
from chirality.star_ascidian.center_field import generate_star_centers
from chirality.star_ascidian.phase_diagram import (
    sweep_attraction_vs_chirality,
    sweep_noise_vs_repulsion,
    sweep_inhibition_ratio,
    sweep_chirality_vs_occupancy,
    save_phase_diagram_csv,
)
from chirality.star_ascidian import compare as star_compare
from chirality.visualization.style import (
    BG, INK, ACCENT, GREEN, NEUTRAL, BORDER, FIELD_CMAP, CHIRALITY_CMAP,
    TITLE_FS, LABEL_FS, TICK_FS, apply_notebook_style,
)
from chirality.visualization.panels import (
    make_slide1_target_and_simulation,
    make_slide2_model_schematic,
    make_slide3_simulation_sequence,
    make_slide4_phase_diagram,
    make_slide5_insight_and_limits,
    make_final_summary_panel,
)

apply_notebook_style()

REF    = os.path.join("outputs", "reference")
STAR   = os.path.join("outputs", "star_ascidian")
PHASE  = os.path.join("outputs", "phase_diagrams")
MOVIES = os.path.join("outputs", "movies")
PANELS = os.path.join("outputs", "panels")
DATA   = os.path.join("outputs", "data")

for _d in [REF, STAR, PHASE, MOVIES, PANELS, DATA]:
    ensure_dir(_d)

_PALETTE = [ACCENT, GREEN, NEUTRAL, "#7B6B8B"]


def _save(fig, path):
    fig.savefig(path, dpi=120, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  Saved: {path}")


def _style(ax):
    ax.tick_params(colors=INK, labelsize=TICK_FS)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)


# ─────────────────────────────────────────────────────────────────
# 1. REFERENCE MODELS
# ─────────────────────────────────────────────────────────────────

def run_reference_models():
    print("\n[1/6] Reference model outputs ...")

    # Fisher-KPP
    r = simulate_fisher_kpp(N=64, L=10.0, D=0.5, r=1.0, dt=0.05,
                            n_steps=400, n_snapshots=6, seed=42)
    fr = front_radius(r)
    fig, ax = plt.subplots(figsize=(5, 4.5), facecolor=BG)
    ax.set_facecolor("#FFFFFF")
    im = ax.imshow(r.u_final, origin="lower", extent=[0, 10, 0, 10],
                   cmap=FIELD_CMAP, interpolation="nearest")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04).ax.tick_params(
        labelsize=TICK_FS, colors=INK)
    ax.set_title(f"Fisher-KPP: Invasion Front (radius={fr:.2f})",
                 fontsize=LABEL_FS, color=INK)
    ax.set_xlabel("x", fontsize=TICK_FS, color=INK)
    ax.set_ylabel("y", fontsize=TICK_FS, color=INK)
    _style(ax)
    fig.tight_layout()
    _save(fig, os.path.join(REF, "fisher_kpp_front.png"))

    # FitzHugh-Nagumo
    r = simulate_fitzhugh_nagumo(N=64, Du=1.0, epsilon=0.08, a=0.7, b=0.8,
                                  dt=0.1, n_steps=200, n_snapshots=6,
                                  seed=42, init="spiral")
    mid = len(r.snapshots_u) // 2
    fig, axes = plt.subplots(1, 2, figsize=(9, 4), facecolor=BG)
    for ax, idx, lbl in [(axes[0], 0, "t=0 (spiral init)"),
                          (axes[1], mid, f"t={r.times[mid]:.1f}")]:
        ax.imshow(r.snapshots_u[idx], origin="lower", cmap="RdBu_r",
                  vmin=-2, vmax=2, interpolation="nearest")
        ax.set_title(lbl, fontsize=LABEL_FS, color=INK)
        ax.axis("off")
    fig.suptitle("FitzHugh-Nagumo: Spiral Wave", fontsize=TITLE_FS, color=INK)
    fig.tight_layout()
    _save(fig, os.path.join(REF, "fitzhugh_nagumo_spiral.png"))

    # Gierer-Meinhardt
    r = simulate_gierer_meinhardt(N=64, Da=0.05, Dh=5.0, mu_a=0.05, mu_h=0.05,
                                   rho=0.1, rho_0=0.001, kappa=0.1,
                                   dt=0.5, n_steps=3000, n_snapshots=4, seed=42)
    ps = pattern_strength(r)
    centers = find_activator_centers(r)
    dx = 10.0 / 64
    fig, ax = plt.subplots(figsize=(5, 4.5), facecolor=BG)
    ax.set_facecolor("#FFFFFF")
    im = ax.imshow(r.u_final, origin="lower", extent=[0, 10, 0, 10],
                   cmap=FIELD_CMAP, interpolation="nearest")
    if len(centers) > 0:
        ax.scatter(centers[:, 1] * dx, centers[:, 0] * dx,
                   marker="+", c=ACCENT, s=60, linewidths=1.5, zorder=5)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04).ax.tick_params(
        labelsize=TICK_FS, colors=INK)
    ax.set_title(f"Gierer-Meinhardt: Turing Spots (n={len(centers)}, ps={ps:.2f})",
                 fontsize=LABEL_FS, color=INK)
    ax.set_xlabel("x", fontsize=TICK_FS, color=INK)
    ax.set_ylabel("y", fontsize=TICK_FS, color=INK)
    _style(ax)
    fig.tight_layout()
    _save(fig, os.path.join(REF, "gierer_meinhardt_spots.png"))

    # Cahn-Hilliard
    r = simulate_cahn_hilliard(N=64, A=1.0, B=1.0, M=1.0, kappa=0.5,
                                dt=0.05, n_steps=2000, n_snapshots=4, seed=42)
    dsp = domain_size_proxy(r)
    fig, axes = plt.subplots(1, 2, figsize=(9, 4), facecolor=BG)
    for ax, idx, lbl in [(axes[0], 0, "t=0"),
                          (axes[1], -1, f"t={r.times[-1]:.0f} (separated)")]:
        ax.imshow(r.snapshots_u[idx], origin="lower", cmap="coolwarm",
                  vmin=-1, vmax=1, interpolation="nearest")
        ax.set_title(lbl, fontsize=LABEL_FS, color=INK)
        ax.axis("off")
    fig.suptitle(f"Cahn-Hilliard: Phase Separation (proxy={dsp:.3f})",
                 fontsize=TITLE_FS, color=INK)
    fig.tight_layout()
    _save(fig, os.path.join(REF, "cahn_hilliard_domains.png"))

    # Gray-Scott
    r = simulate_gray_scott(N=64, Du=0.16, Dv=0.08, F=0.035, k=0.065,
                             dt=1.0, n_steps=3000, n_snapshots=4, seed=42)
    fig, ax = plt.subplots(figsize=(5, 4.5), facecolor=BG)
    ax.set_facecolor("#FFFFFF")
    im = ax.imshow(r.v_final, origin="lower", extent=[0, 10, 0, 10],
                   cmap="YlGnBu", interpolation="nearest")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04).ax.tick_params(
        labelsize=TICK_FS, colors=INK)
    ax.set_title("Gray-Scott: Spot Pattern (F=0.035, k=0.065)",
                 fontsize=LABEL_FS, color=INK)
    ax.set_xlabel("x", fontsize=TICK_FS, color=INK)
    ax.set_ylabel("y", fontsize=TICK_FS, color=INK)
    _style(ax)
    fig.tight_layout()
    _save(fig, os.path.join(REF, "gray_scott_pattern.png"))

    # Chiral active particles
    r = simulate_chiral_abp(N=200, L=10.0, v0=0.5, Dr=0.3, omega=2.0,
                             mode="racemic", dt=0.01, n_steps=500,
                             n_snapshots=4, seed=42)
    si = swirl_index(r)
    fig, ax = plt.subplots(figsize=(5, 4.5), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    pos = r.positions[-1]
    omegas = r.omegas
    norm_o = plt.Normalize(-float(np.abs(omegas).max()), float(np.abs(omegas).max()))
    c = CHIRALITY_CMAP(norm_o(omegas))
    ax.scatter(pos[:, 0], pos[:, 1], c=c, s=8, alpha=0.8, linewidths=0)
    ax.set_title(f"Chiral Active Particles: Racemic (swirl={si:.2f})",
                 fontsize=LABEL_FS, color=INK)
    ax.set_xlabel("x", fontsize=TICK_FS, color=INK)
    ax.set_ylabel("y", fontsize=TICK_FS, color=INK)
    _style(ax)
    fig.tight_layout()
    _save(fig, os.path.join(REF, "chiral_active_particles.png"))


# ─────────────────────────────────────────────────────────────────
# 2. STAR ASCIDIAN DEMOS
# ─────────────────────────────────────────────────────────────────

def run_star_ascidian_demos():
    print("\n[2/6] Star ascidian demos ...")

    demo_presets = [
        "clean_star_systems",
        "chiral_twisted_stars",
        "overcrowded_merged_systems",
        "noisy_fragmented_systems",
        "boundary_pinned_stars",
    ]

    results = {}
    for preset in demo_presets:
        print(f"  {preset}...")
        result = simulate_star_ascidian_colony(preset=preset, seed=42)
        results[preset] = result
        m = result.metrics
        L = result.params["L"]

        fig, axes = plt.subplots(1, 3, figsize=(13, 4.5), facecolor=BG)
        fig.suptitle(preset.replace("_", " ").title(), fontsize=TITLE_FS, color=INK)

        ax = axes[0]
        ax.set_facecolor("#FFFFFF")
        ax.imshow(result.field, origin="lower", extent=[0, L, 0, L],
                  cmap=FIELD_CMAP, interpolation="nearest")
        ax.scatter(result.centers[:, 0], result.centers[:, 1], s=30,
                   color=INK, marker="+", linewidths=1.2, zorder=4)
        ax.set_title("Activator field", fontsize=LABEL_FS, color=INK)
        ax.set_xlabel("x", fontsize=TICK_FS, color=INK)
        ax.set_ylabel("y", fontsize=TICK_FS, color=INK)
        _style(ax)

        ax = axes[1]
        ax.set_facecolor(BG)
        pos = result.zooid.positions[-1]
        K = result.zooid.K
        for k in range(K):
            mask = result.zooid.assignments == k
            ax.scatter(pos[mask, 0], pos[mask, 1], s=7,
                       color=_PALETTE[k % len(_PALETTE)],
                       alpha=0.80, linewidths=0)
        ax.scatter(result.centers[:, 0], result.centers[:, 1], s=35,
                   color=INK, marker="+", linewidths=1.2, zorder=4)
        ax.set_xlim(0, L)
        ax.set_ylim(0, L)
        ax.set_title(f"Agents (K={K}, N={result.zooid.N})",
                     fontsize=LABEL_FS, color=INK)
        ax.set_xlabel("x", fontsize=TICK_FS, color=INK)
        ax.set_ylabel("y", fontsize=TICK_FS, color=INK)
        _style(ax)

        ax = axes[2]
        ax.set_facecolor("#FFFFFF")
        names = ["star_like", "radial", "uniform", "1-frag", "1-merge"]
        vals = [
            m["star_likeness_score"], m["radial_order"], m["angular_uniformity"],
            max(0.0, 1.0 - m["fragmentation"]), max(0.0, 1.0 - m["merge_score"]),
        ]
        y_pos = np.arange(len(names))
        colors = [ACCENT if v >= 0.5 else NEUTRAL for v in vals]
        ax.barh(y_pos, vals, color=colors, height=0.55, alpha=0.85)
        ax.axvline(0.5, color=BORDER, linewidth=1.0, linestyle="--")
        ax.set_xlim(0, 1)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(names, fontsize=TICK_FS, color=INK)
        ax.set_xlabel("score", fontsize=TICK_FS, color=INK)
        ax.set_title("Metrics", fontsize=LABEL_FS, color=INK)
        _style(ax)

        fig.tight_layout()
        _save(fig, os.path.join(STAR, f"{preset}.png"))

    clean = results["clean_star_systems"]
    fig = star_compare.compare_to_target(
        clean.zooid, target_arms=clean.params["n_arms"],
        title="Star Ascidian: Simulation vs Target",
    )
    _save(fig, os.path.join(STAR, "simulation_vs_target_features.png"))

    return results


# ─────────────────────────────────────────────────────────────────
# 3. PHASE DIAGRAMS
# ─────────────────────────────────────────────────────────────────

def run_phase_diagrams():
    print("\n[3/6] Phase diagrams ...")

    def _heatmap(x_vals, y_vals, grid, xlabel, ylabel, title,
                 cmap="viridis", vmin=0, vmax=1):
        fig, ax = plt.subplots(figsize=(6, 5), facecolor=BG)
        ax.set_facecolor("#FFFFFF")
        im = ax.pcolormesh(x_vals, y_vals, grid, cmap=cmap,
                           vmin=vmin, vmax=vmax, shading="nearest")
        cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cb.ax.tick_params(labelsize=TICK_FS, colors=INK)
        cb.outline.set_edgecolor(INK)
        ax.set_xlabel(xlabel, fontsize=LABEL_FS, color=INK)
        ax.set_ylabel(ylabel, fontsize=LABEL_FS, color=INK)
        ax.set_title(title, fontsize=LABEL_FS, color=INK)
        _style(ax)
        fig.tight_layout()
        return fig

    # Sweep A: k_radial vs omega
    kv = np.array([0.5, 1.0, 2.0, 3.5, 5.0])
    ov = np.array([0.0, 0.5, 1.5, 3.0, 5.0])
    x_A, y_A, grids_A = sweep_attraction_vs_chirality(
        k_radial_vals=kv, omega_vals=ov, seed=42)
    fig = _heatmap(x_A, y_A, grids_A["star_likeness"],
                   r"$k_{radial}$", r"$\omega$ (chirality)",
                   "Star-likeness: Attraction vs Chirality", cmap="YlOrBr")
    _save(fig, os.path.join(PHASE, "star_likeness_attraction_vs_chirality.png"))
    save_phase_diagram_csv(grids_A, x_A, y_A, "k_radial", "omega",
                           os.path.join(DATA, "sweep_A.csv"))

    # Sweep B: Dr vs k_angular
    dv = np.array([0.01, 0.1, 0.3, 0.7, 1.5])
    kav = np.array([0.1, 0.3, 0.6, 1.0, 1.5])
    x_B, y_B, grids_B = sweep_noise_vs_repulsion(
        Dr_vals=dv, k_angular_vals=kav, seed=42)
    fig = _heatmap(x_B, y_B, grids_B["fragmentation"],
                   r"$D_r$ (noise)", r"$k_{angular}$",
                   "Fragmentation: Noise vs Angular Repulsion",
                   cmap="RdYlGn_r")
    _save(fig, os.path.join(PHASE, "fragmentation_noise_vs_repulsion.png"))
    save_phase_diagram_csv(grids_B, x_B, y_B, "Dr", "k_angular",
                           os.path.join(DATA, "sweep_B.csv"))

    # Sweep C: Dh/Da vs mu_h
    dhv = np.array([0.5, 1.0, 2.0, 5.0, 10.0])
    mhv = np.array([0.02, 0.05, 0.10, 0.20, 0.40])
    ratio_vals, y_C, grids_C = sweep_inhibition_ratio(
        Dh_vals=dhv, mu_h_vals=mhv, seed=42)
    fig = _heatmap(ratio_vals, y_C, grids_C["spacing_quality"],
                   r"$D_h / D_a$", r"$\mu_h$",
                   "Center Spacing Quality: Inhibition Ratio",
                   cmap="YlOrBr")
    _save(fig, os.path.join(PHASE, "center_spacing_inhibition_ratio.png"))
    save_phase_diagram_csv(grids_C, ratio_vals, y_C, "Dh_over_Da", "mu_h",
                           os.path.join(DATA, "sweep_C.csv"))

    # Sweep D: omega vs n_per_arm
    omv = np.array([0.0, 0.5, 1.5, 3.0, 5.0])
    npav = np.array([1, 2, 3, 5, 8])
    x_D, y_D, grids_D = sweep_chirality_vs_occupancy(
        omega_vals=omv, n_per_arm_vals=npav, seed=42)
    fig = _heatmap(x_D, y_D, grids_D["swirl"],
                   r"$\omega$ (chirality)", "agents per arm",
                   "Swirl Magnitude: Chirality vs Arm Occupancy",
                   cmap="PRGn", vmin=0, vmax=1)
    _save(fig, os.path.join(PHASE, "swirl_chirality_vs_boundary.png"))
    save_phase_diagram_csv(grids_D, x_D, y_D, "omega", "n_per_arm",
                           os.path.join(DATA, "sweep_D.csv"))

    # Return sweep A x/y + grids for panel use
    return x_A, y_A, grids_A["star_likeness"], grids_A["swirl"]


# ─────────────────────────────────────────────────────────────────
# 4. MOVIES
# ─────────────────────────────────────────────────────────────────

def run_movies():
    print("\n[4/6] Movies ...")
    script_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "04_make_movies.py"
    )
    spec = importlib.util.spec_from_file_location("make_movies_04", script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.make_star_formation_clean(seed=42)
    mod.make_chiral_twist_emergence(seed=42)
    mod.make_phase_transition_sweep(seed=42)
    mod.make_active_zooid_dynamics(seed=42)


# ─────────────────────────────────────────────────────────────────
# 5. PRESENTATION PANELS
# ─────────────────────────────────────────────────────────────────

def run_panels(star_results, phase_x, phase_y, sl_grid, swirl_grid):
    print("\n[5/6] Presentation panels ...")

    clean = star_results["clean_star_systems"]
    chiral = star_results.get("chiral_twisted_stars", clean)

    print("  Generating GM field data for slide 1 ...")
    fd = generate_star_centers(
        grid_size=64, L=10.0, Da=0.05, Dh=5.0,
        mu_a=0.05, mu_h=0.05, rho=0.1, rho_0=0.001, kappa=0.1,
        dt=0.5, n_steps=3000, n_snapshots=2, min_distance=2.5, seed=42,
    )

    for fn, args, name in [
        (make_slide1_target_and_simulation,
         (clean.zooid, fd, os.path.join(PANELS, "slide1_target_and_simulation.png")),
         "slide1"),
        (make_slide2_model_schematic,
         (os.path.join(PANELS, "slide2_model_schematic.png"),),
         "slide2"),
        (make_slide3_simulation_sequence,
         (clean.zooid, os.path.join(PANELS, "slide3_simulation_sequence.png")),
         "slide3"),
        (make_slide4_phase_diagram,
         (phase_x, phase_y, sl_grid, swirl_grid,
          os.path.join(PANELS, "slide4_phase_diagram.png")),
         "slide4"),
        (make_slide5_insight_and_limits,
         (clean, os.path.join(PANELS, "slide5_insight_and_limits.png")),
         "slide5"),
        (make_final_summary_panel,
         (clean, chiral, fd, phase_x, phase_y, sl_grid,
          os.path.join(PANELS, "final_summary_panel.png")),
         "summary"),
    ]:
        fn(*args)
        print(f"  Saved: {args[-1]}")


# ─────────────────────────────────────────────────────────────────
# 6. DATA EXPORTS
# ─────────────────────────────────────────────────────────────────

def run_data_exports(star_results):
    print("\n[6/6] Data exports ...")

    # star_ascidian_metrics.csv
    metrics_path = os.path.join(DATA, "star_ascidian_metrics.csv")
    fieldnames = ["preset", "K", "N", "star_likeness_score", "arm_count_mean",
                  "radial_order", "angular_uniformity", "swirl_score",
                  "fragmentation", "merge_score"]
    rows = []
    for preset_name, result in star_results.items():
        m = result.metrics
        rows.append({
            "preset": preset_name,
            "K": result.zooid.K,
            "N": result.zooid.N,
            "star_likeness_score": round(float(m["star_likeness_score"]), 4),
            "arm_count_mean": round(float(m["arm_count_mean"]), 2),
            "radial_order": round(float(m["radial_order"]), 4),
            "angular_uniformity": round(float(m["angular_uniformity"]), 4),
            "swirl_score": round(float(m["swirl_score"]), 4),
            "fragmentation": round(float(m["fragmentation"]), 4),
            "merge_score": round(float(m["merge_score"]), 4),
        })
    with open(metrics_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"  Saved: {metrics_path}")

    # star_ascidian_phase_diagrams.csv (concatenation of 4 sweep CSVs)
    pd_path = os.path.join(DATA, "star_ascidian_phase_diagrams.csv")
    all_rows = []
    for tag in ["sweep_A", "sweep_B", "sweep_C", "sweep_D"]:
        sf = os.path.join(DATA, f"{tag}.csv")
        if os.path.exists(sf):
            with open(sf, "r", newline="") as f:
                for row in csv.DictReader(f):
                    row["sweep"] = tag
                    all_rows.append(row)
    if all_rows:
        keys = list(all_rows[0].keys())
        with open(pd_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            w.writerows(all_rows)
        print(f"  Saved: {pd_path}")

    # model_parameter_presets.json
    json_path = os.path.join(DATA, "model_parameter_presets.json")

    def _py(v):
        if isinstance(v, (np.integer,)):
            return int(v)
        if isinstance(v, (np.floating,)):
            return float(v)
        return v

    clean_presets = {
        name: {k: _py(v) for k, v in params.items()}
        for name, params in PRESETS.items()
    }
    with open(json_path, "w") as f:
        json.dump(clean_presets, f, indent=2)
    print(f"  Saved: {json_path}")


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Chirality Atlas: Full Asset Generation")
    print("=" * 60)

    run_reference_models()

    star_results = run_star_ascidian_demos()

    phase_x, phase_y, sl_grid, swirl_grid = run_phase_diagrams()

    run_movies()

    run_panels(star_results, phase_x, phase_y, sl_grid, swirl_grid)

    run_data_exports(star_results)

    print("\n" + "=" * 60)
    print("Done. Output summary:")
    for subdir in ["reference", "star_ascidian", "phase_diagrams",
                   "movies", "panels", "data"]:
        d = os.path.join("outputs", subdir)
        if os.path.isdir(d):
            files = [f for f in os.listdir(d)
                     if os.path.isfile(os.path.join(d, f))]
            print(f"  outputs/{subdir}/  ({len(files)} files)")


if __name__ == "__main__":
    main()
