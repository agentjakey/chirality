"""
Final smoke test: run a tiny version of each model, compute one metric,
verify the result is finite.

All grid sizes are minimal (N=16 or N=32) and step counts are short.
Run from repo root: python scripts/06_final_smoke_test.py
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

PASS = 0
FAIL = 0


def check(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        print(f"  PASS  {label}")
        PASS += 1
    else:
        print(f"  FAIL  {label}  {detail}")
        FAIL += 1


def run_test(label, fn):
    global PASS, FAIL
    try:
        fn()
    except Exception as e:
        print(f"  FAIL  {label}: {e}")
        FAIL += 1


def test_fisher_kpp():
    from chirality.model_library.fisher_kpp import simulate_fisher_kpp, front_radius
    result = simulate_fisher_kpp(N=16, n_steps=50, n_snapshots=5, seed=0)
    check("fisher_kpp: u_final shape", result.u_final.shape == (16, 16))
    check("fisher_kpp: u_final finite", np.all(np.isfinite(result.u_final)))
    check("fisher_kpp: u in [0,1]", result.u_final.min() >= 0 and result.u_final.max() <= 1.0 + 1e-6)
    r = front_radius(result)
    check("fisher_kpp: front_radius >= 0", r >= 0)
    check("fisher_kpp: n_snapshots", len(result.times) > 0)


def test_fitzhugh_nagumo():
    from chirality.model_library.fitzhugh_nagumo import simulate_fitzhugh_nagumo, wave_activity
    result = simulate_fitzhugh_nagumo(N=16, n_steps=100, n_snapshots=5, seed=0)
    check("fhn: u_final shape", result.u_final.shape == (16, 16))
    check("fhn: u_final finite", np.all(np.isfinite(result.u_final)))
    check("fhn: v_final finite", np.all(np.isfinite(result.v_final)))
    wa = wave_activity(result)
    check("fhn: wave_activity in [0,1]", 0.0 <= wa <= 1.0)


def test_gierer_meinhardt():
    from chirality.model_library.gierer_meinhardt import (
        simulate_gierer_meinhardt, find_activator_centers, pattern_strength, cluster_count
    )
    result = simulate_gierer_meinhardt(N=32, dt=0.5, n_steps=500, n_snapshots=5, seed=0)
    check("gm: a_final shape", result.u_final.shape == (32, 32))
    check("gm: a_final finite", np.all(np.isfinite(result.u_final)))
    check("gm: h_final finite", np.all(np.isfinite(result.v_final)))
    check("gm: a_final positive", result.u_final.min() > 0)
    ps = pattern_strength(result)
    check("gm: pattern_strength >= 0", ps >= 0)
    cc = cluster_count(result)
    check("gm: cluster_count >= 0", cc >= 0)
    centers = find_activator_centers(result)
    check("gm: centers shape", centers.ndim == 2 or len(centers) == 0)


def test_cahn_hilliard():
    from chirality.model_library.cahn_hilliard import simulate_cahn_hilliard, domain_size_proxy
    result = simulate_cahn_hilliard(N=32, dt=0.5, n_steps=200, n_snapshots=5, seed=0)
    check("ch: phi_final shape", result.u_final.shape == (32, 32))
    check("ch: phi_final finite", np.all(np.isfinite(result.u_final)))
    dsp = domain_size_proxy(result)
    check("ch: domain_size_proxy >= 0", dsp >= 0)
    mean0 = result.snapshots_u[0].mean()
    meanf = result.u_final.mean()
    check("ch: conservation (mean phi approx constant)", abs(mean0 - meanf) < 0.05)


def test_gray_scott():
    from chirality.model_library.gray_scott import simulate_gray_scott, pattern_strength, cluster_count
    result = simulate_gray_scott(N=32, n_steps=500, n_snapshots=5, seed=0)
    check("gs: u_final shape", result.u_final.shape == (32, 32))
    check("gs: u_final finite", np.all(np.isfinite(result.u_final)))
    check("gs: v_final finite", np.all(np.isfinite(result.v_final)))
    check("gs: u in [0,1]", result.u_final.min() >= -1e-6 and result.u_final.max() <= 1.0 + 1e-6)
    ps = pattern_strength(result)
    check("gs: pattern_strength >= 0", ps >= 0)
    cc = cluster_count(result)
    check("gs: cluster_count >= 0", cc >= 0)


def test_active_particles():
    from chirality.model_library.active_particles import (
        simulate_abp, simulate_chiral_abp, simulate_vicsek,
        polar_order, swirl_index, msd, avg_neighbors
    )

    r_abp = simulate_abp(N=50, n_steps=100, n_snapshots=5, seed=0)
    check("abp: positions finite", np.all(np.isfinite(r_abp.positions)))
    check("abp: positions in [0,L]", r_abp.positions.min() >= 0 and r_abp.positions.max() <= r_abp.L)
    phi = polar_order(r_abp)
    check("abp: polar_order in [0,1]", 0.0 <= phi <= 1.0 + 1e-6)

    r_ch = simulate_chiral_abp(N=50, omega=2.0, n_steps=100, n_snapshots=5, seed=0)
    check("chiral_abp: positions finite", np.all(np.isfinite(r_ch.positions)))
    si = swirl_index(r_ch)
    check("chiral_abp: swirl_index finite", np.isfinite(si))

    r_rac = simulate_chiral_abp(N=50, omega=2.0, mode="racemic", n_steps=50, n_snapshots=5, seed=0)
    check("racemic: omegas both signs", r_rac.omegas.min() < 0 and r_rac.omegas.max() > 0)

    r_vic = simulate_vicsek(N=50, eta=0.1, n_steps=100, n_snapshots=5, seed=0)
    check("vicsek: positions finite", np.all(np.isfinite(r_vic.positions)))
    phi_v = polar_order(r_vic)
    check("vicsek: polar_order in [0,1]", 0.0 <= phi_v <= 1.0 + 1e-6)
    check("vicsek: low noise -> high order", phi_v > 0.5)

    d = msd(r_abp)
    check("msd: finite and non-negative", np.isfinite(d) and d >= 0)

    an = avg_neighbors(r_abp)
    check("avg_neighbors: finite and non-negative", np.isfinite(an) and an >= 0)


def test_visualization_imports():
    from chirality.visualization import (
        plot_field, plot_phase_diagram, plot_particle_snapshot,
        plot_trajectories, save_field_gif, save_particle_gif,
        BG, INK, ACCENT, GREEN, NEUTRAL
    )
    check("visualization: imports succeed", True)
    check("visualization: BG is hex color", isinstance(BG, str) and BG.startswith("#"))


def test_star_ascidian():
    from chirality.star_ascidian.center_field import generate_star_centers, compute_center_quality
    from chirality.star_ascidian.zooid_agents import simulate_zooid_agents
    from chirality.star_ascidian import metrics as star_metrics
    from chirality.star_ascidian.hybrid_model import simulate_star_ascidian_colony, PRESETS

    # Layer 1: center field (tiny run)
    fd = generate_star_centers(grid_size=16, L=5.0, n_steps=200, n_snapshots=2, seed=7)
    check("star: field shape", fd["field"].shape == (16, 16))
    check("star: field finite", np.all(np.isfinite(fd["field"])))
    centers = fd["centers"]
    if len(centers) == 0:
        centers = np.array([[2.5, 2.5]])
    check("star: centers array 2D", centers.ndim == 2 and centers.shape[1] == 2)
    cq = fd["quality"]
    check("star: quality keys present", "n_centers" in cq and "spacing_cv" in cq)

    # Layer 2: zooid agents (tiny run)
    zr = simulate_zooid_agents(
        centers=centers, n_per_center=7, n_arms=7, L=5.0,
        r_target=1.0, v0=0.05, Dr=0.04, omega=0.0,
        k_attract=0.3, k_radial=2.0, k_angular=0.6, k_ev=0.4, sigma_ev=0.18,
        dt=0.02, n_steps=30, n_snapshots=3, mode="radial_clean",
        boundary="periodic", seed=9,
    )
    check("star: zooid positions shape", zr.positions.ndim == 3 and zr.positions.shape[2] == 2)
    check("star: zooid positions finite", np.all(np.isfinite(zr.positions)))
    check("star: zooid assignments shape", zr.assignments.shape[0] == zr.N)

    # Metrics
    sl = star_metrics.star_likeness_score(zr, target_arms=7)
    check("star: star_likeness in [0,1]", 0.0 <= sl <= 1.0 + 1e-6)
    swirl = star_metrics.swirl_score(zr)
    check("star: swirl_score finite", np.isfinite(swirl))
    frag = star_metrics.fragmentation_score(zr)
    check("star: fragmentation_score in [0,1]", 0.0 <= frag <= 1.0 + 1e-6)

    # Hybrid model (smallest preset params)
    check("star: PRESETS dict non-empty", len(PRESETS) >= 5)
    result = simulate_star_ascidian_colony(
        preset="clean_star_systems", seed=7,
        n_snapshots=2,
        n_field_steps=150,
        n_steps=30,
        grid_size=16,
        L=5.0,
        min_distance=1.0,
    )
    check("star: StarColonyResult has zooid", hasattr(result, "zooid"))
    check("star: StarColonyResult metrics present", "star_likeness_score" in result.metrics)
    check("star: StarColonyResult preset name", result.preset == "clean_star_systems")


def main():
    print("=" * 60)
    print("Chirality Atlas: Final Smoke Test")
    print("=" * 60)

    tests = [
        ("Fisher-KPP", test_fisher_kpp),
        ("FitzHugh-Nagumo", test_fitzhugh_nagumo),
        ("Gierer-Meinhardt", test_gierer_meinhardt),
        ("Cahn-Hilliard", test_cahn_hilliard),
        ("Gray-Scott", test_gray_scott),
        ("Active Particles", test_active_particles),
        ("Visualization imports", test_visualization_imports),
        ("Star Ascidian model", test_star_ascidian),
    ]

    for name, fn in tests:
        print(f"\n--- {name} ---")
        run_test(name, fn)

    print(f"\n{'=' * 60}")
    total = PASS + FAIL
    print(f"Results: {PASS}/{total} passed, {FAIL} failed")
    if FAIL == 0:
        print("PASS: all checks passed.")
    else:
        print("FAIL: some checks failed. See above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
