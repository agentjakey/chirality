"""
Run all 6 reference models at production parameters and save outputs.

Outputs go to outputs/reference/.
Runtime: roughly 2-5 minutes depending on machine.

Run from repo root: python scripts/01_run_reference_models.py
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from chirality.model_library import ensure_dir
from chirality.model_library.fisher_kpp import simulate_fisher_kpp, front_radius
from chirality.model_library.fitzhugh_nagumo import simulate_fitzhugh_nagumo, wave_activity
from chirality.model_library.gierer_meinhardt import (
    simulate_gierer_meinhardt, find_activator_centers, pattern_strength, cluster_count
)
from chirality.model_library.cahn_hilliard import simulate_cahn_hilliard, domain_size_proxy
from chirality.model_library.gray_scott import simulate_gray_scott, pattern_strength as gs_pattern_strength
from chirality.model_library.active_particles import (
    simulate_abp, simulate_chiral_abp, simulate_vicsek,
    polar_order, swirl_index
)
from chirality.visualization.plots import plot_field, plot_particle_snapshot, plot_trajectories
from chirality.visualization.style import apply_notebook_style

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "reference")
ensure_dir(OUT)


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=120, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved: {path}")


def run_fisher_kpp():
    print("\n[1/6] Fisher-KPP...")
    result = simulate_fisher_kpp(N=64, L=10.0, D=0.5, r=1.0, dt=0.05, n_steps=400, n_snapshots=8, seed=42)
    r_val = front_radius(result)
    print(f"      front_radius = {r_val:.2f}")

    fig, axes = plt.subplots(1, 2, figsize=(9, 4), facecolor="#F7F3EA")
    plot_field(result, title="Fisher-KPP: t=0", ax=axes[0])
    axes[0].set_title(f"t = {result.times[0]:.1f}")
    fig2, ax2 = plt.subplots(figsize=(4, 4), facecolor="#F7F3EA")
    plot_field(result, title=f"Fisher-KPP: t={result.times[-1]:.1f}", ax=ax2)
    plt.close(fig2)

    plot_field(result, field="u", title=f"Fisher-KPP final (front_radius={r_val:.2f})", ax=axes[1])
    axes[1].set_title(f"t = {result.times[-1]:.1f} | front_radius = {r_val:.2f}")
    fig.suptitle("Fisher-KPP: Invasion Front", fontsize=13, color="#1F2421")
    fig.tight_layout()
    save(fig, "01_fisher_kpp.png")


def run_fitzhugh_nagumo():
    print("\n[2/6] FitzHugh-Nagumo...")
    # Spiral init generates a persistent rotating wave in periodic domain
    result = simulate_fitzhugh_nagumo(
        N=64, Du=1.0, epsilon=0.08, a=0.7, b=0.8,
        dt=0.1, n_steps=200, n_snapshots=8, seed=42, init="spiral"
    )
    wa = wave_activity(result)
    print(f"      wave_activity (peak during run) = {float(max(float(r.mean() > 0 if hasattr(r,'mean') else 0) for r in result.snapshots_u > 0)):.3f}")
    wa_max = float(max(float((s > 0).mean()) for s in result.snapshots_u))
    print(f"      wave_activity max over run = {wa_max:.3f}")

    # Show 3 snapshots: initial, mid (wave active), final
    mid_idx = len(result.snapshots_u) // 2
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), facecolor="#F7F3EA")
    axes[0].imshow(result.snapshots_u[1], origin="lower", cmap="RdBu_r", vmin=-2, vmax=2)
    axes[0].set_title(f"u at t={result.times[1]:.1f}", fontsize=11, color="#1F2421")
    axes[0].axis("off")
    axes[1].imshow(result.snapshots_u[mid_idx], origin="lower", cmap="RdBu_r", vmin=-2, vmax=2)
    axes[1].set_title(f"u at t={result.times[mid_idx]:.1f} (wave active)", fontsize=11, color="#1F2421")
    axes[1].axis("off")
    axes[2].imshow(result.snapshots_u[-1], origin="lower", cmap="RdBu_r", vmin=-2, vmax=2)
    axes[2].set_title(f"u at t={result.times[-1]:.1f}", fontsize=11, color="#1F2421")
    axes[2].axis("off")
    fig.suptitle(f"FitzHugh-Nagumo: Spiral Wave (wa_max={wa_max:.2f})", fontsize=13, color="#1F2421")
    fig.tight_layout()
    save(fig, "02_fitzhugh_nagumo.png")


def run_gierer_meinhardt():
    print("\n[3/6] Gierer-Meinhardt...")
    result = simulate_gierer_meinhardt(
        N=64, Da=0.05, Dh=5.0, mu_a=0.05, mu_h=0.05, rho=0.1, rho_0=0.001,
        kappa=0.1, dt=0.1, n_steps=3000, n_snapshots=8, seed=42
    )
    ps = pattern_strength(result)
    cc = cluster_count(result)
    centers = find_activator_centers(result)
    n_centers = len(centers)
    print(f"      pattern_strength = {ps:.3f}, cluster_count = {cc}, centers = {n_centers}")

    fig, axes = plt.subplots(1, 2, figsize=(9, 4), facecolor="#F7F3EA")
    plot_field(result, field="u", title="GM: activator a", ax=axes[0])
    plot_field(result, field="v", title="GM: inhibitor h", ax=axes[1])

    if n_centers > 0:
        L = result.params["L"]
        N = result.params["N"]
        dx = L / N
        for ax in axes:
            ax.scatter(
                centers[:, 1] * dx, centers[:, 0] * dx,
                marker="+", c="#C15A3A", s=60, linewidths=1.5, zorder=5
            )

    fig.suptitle(
        f"Gierer-Meinhardt (spots={n_centers}, strength={ps:.2f})",
        fontsize=13, color="#1F2421"
    )
    fig.tight_layout()
    save(fig, "03_gierer_meinhardt.png")


def run_cahn_hilliard():
    print("\n[4/6] Cahn-Hilliard...")
    result = simulate_cahn_hilliard(
        N=64, A=1.0, B=1.0, M=1.0, kappa=0.5,
        dt=0.05, n_steps=2000, n_snapshots=8, seed=42
    )
    dsp = domain_size_proxy(result)
    mean_phi = float(result.u_final.mean())
    print(f"      domain_size_proxy = {dsp:.4f}, mean_phi = {mean_phi:.4f}")

    fig, axes = plt.subplots(1, 3, figsize=(12, 4), facecolor="#F7F3EA")
    for i, idx in enumerate([0, len(result.snapshots_u) // 2, -1]):
        snap = result.snapshots_u[idx]
        t = result.times[idx]
        axes[i].imshow(snap, origin="lower", cmap="coolwarm", vmin=-1, vmax=1)
        axes[i].set_title(f"t = {t:.1f}", fontsize=11, color="#1F2421")
        axes[i].axis("off")
    fig.suptitle(f"Cahn-Hilliard: Phase Separation (domain proxy = {dsp:.4f})", fontsize=13, color="#1F2421")
    fig.tight_layout()
    save(fig, "04_cahn_hilliard.png")


def run_gray_scott():
    print("\n[5/6] Gray-Scott...")
    result_spots = simulate_gray_scott(
        N=64, Du=0.16, Dv=0.08, F=0.035, k=0.065,
        dt=1.0, n_steps=3000, n_snapshots=8, seed=42
    )
    result_labs = simulate_gray_scott(
        N=64, Du=0.16, Dv=0.08, F=0.040, k=0.060,
        dt=1.0, n_steps=3000, n_snapshots=8, seed=42
    )
    ps_spots = gs_pattern_strength(result_spots)
    ps_labs = gs_pattern_strength(result_labs)
    print(f"      spots pattern_strength = {ps_spots:.3f}")
    print(f"      labyrinths pattern_strength = {ps_labs:.3f}")

    fig, axes = plt.subplots(1, 2, figsize=(9, 4), facecolor="#F7F3EA")
    plot_field(result_spots, field="v", title=f"GS Spots (F=0.035, k=0.065, ps={ps_spots:.2f})", ax=axes[0])
    plot_field(result_labs, field="v", title=f"GS Labyrinths (F=0.040, k=0.060, ps={ps_labs:.2f})", ax=axes[1])
    fig.suptitle("Gray-Scott: Spots vs Labyrinths", fontsize=13, color="#1F2421")
    fig.tight_layout()
    save(fig, "05_gray_scott.png")


def run_active_particles():
    print("\n[6/6] Active particles...")

    r_abp = simulate_abp(N=200, L=10.0, v0=0.5, Dr=0.5, dt=0.01, n_steps=500, n_snapshots=8, seed=42)
    phi_abp = polar_order(r_abp)
    print(f"      ABP polar_order = {phi_abp:.3f}")

    r_chiral = simulate_chiral_abp(
        N=200, L=10.0, v0=0.5, Dr=0.5, omega=2.0, mode="uniform",
        dt=0.01, n_steps=500, n_snapshots=8, seed=42
    )
    phi_ch = polar_order(r_chiral)
    si = swirl_index(r_chiral)
    print(f"      Chiral ABP polar_order = {phi_ch:.3f}, swirl_index = {si:.3f}")

    r_vic = simulate_vicsek(N=200, L=10.0, v0=0.5, eta=0.15, R=1.0, dt=0.1, n_steps=500, n_snapshots=8, seed=42)
    phi_vic = polar_order(r_vic)
    print(f"      Vicsek polar_order = {phi_vic:.3f}")

    fig, axes = plt.subplots(1, 3, figsize=(14, 4), facecolor="#F7F3EA")
    plot_particle_snapshot(r_abp, title=f"ABP (phi={phi_abp:.2f})", ax=axes[0], color_by="none")
    plot_particle_snapshot(r_chiral, title=f"Chiral ABP (swirl={si:.2f})", ax=axes[1], color_by="omega")
    plot_particle_snapshot(r_vic, title=f"Vicsek (phi={phi_vic:.2f})", ax=axes[2], color_by="theta")
    fig.suptitle("Active Particles: ABP, Chiral ABP, Vicsek", fontsize=13, color="#1F2421")
    fig.tight_layout()
    save(fig, "06_active_particles.png")


def main():
    apply_notebook_style()
    print("=" * 60)
    print("Chirality Atlas: Reference Model Run")
    print(f"Output directory: {OUT}")
    print("=" * 60)

    run_fisher_kpp()
    run_fitzhugh_nagumo()
    run_gierer_meinhardt()
    run_cahn_hilliard()
    run_gray_scott()
    run_active_particles()

    print("\n" + "=" * 60)
    print(f"All outputs saved to: {OUT}")
    print("Done.")


if __name__ == "__main__":
    main()
