"""
Health check for Chirality Atlas: Star Ascidian Edition.

Imports core modules, runs tiny simulations, verifies all outputs are finite.
Prints PASS if everything works, exits with code 1 if something is broken.

Run from repo root:
    python healthcheck.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import numpy as np

errors = []

print("=== Chirality Atlas Health Check ===")
print()

# 1. Core imports
try:
    from chirality.star_ascidian.hybrid_model import simulate_star_ascidian_colony, PRESETS
    from chirality.star_ascidian.center_field import generate_star_centers
    from chirality.star_ascidian.zooid_agents import simulate_zooid_agents
    from chirality.star_ascidian import metrics as star_metrics
    from chirality.model_library.gierer_meinhardt import simulate_gierer_meinhardt
    from chirality.model_library.active_particles import simulate_abp
    print("  PASS  core imports")
except Exception as e:
    print(f"  FAIL  core imports: {e}")
    errors.append("imports")

# 2. Tiny GM field
if "imports" not in errors:
    try:
        fd = generate_star_centers(
            grid_size=16, L=5.0,
            Da=0.05, Dh=5.0, mu_a=0.05, mu_h=0.05,
            rho=0.1, rho_0=0.001, kappa=0.1,
            dt=0.5, n_steps=200, n_snapshots=2,
            seed=42,
        )
        assert np.all(np.isfinite(fd["field"])), "GM field has non-finite values"
        assert fd["field"].shape == (16, 16), f"GM field shape wrong: {fd['field'].shape}"
        print(f"  PASS  GM field  (centers found: {len(fd['centers'])})")
    except Exception as e:
        print(f"  FAIL  GM field: {e}")
        errors.append("gm_field")

# 3. Tiny zooid simulation
if "imports" not in errors:
    try:
        centers = np.array([[2.5, 2.5], [7.5, 7.5]])
        zr = simulate_zooid_agents(
            centers=centers,
            n_per_center=14,
            n_arms=7,
            L=10.0,
            r_target=1.5,
            v0=0.05, Dr=0.04, omega=0.0,
            k_attract=0.3, k_radial=2.0, k_angular=0.6,
            k_ev=0.4, sigma_ev=0.18,
            dt=0.02, n_steps=20, n_snapshots=3,
            seed=42,
        )
        assert np.all(np.isfinite(zr.positions)), "positions have non-finite values"
        assert zr.positions.shape[2] == 2, "positions not 2D"
        print(f"  PASS  zooid agents  (N={zr.N}, K={zr.K})")
    except Exception as e:
        print(f"  FAIL  zooid agents: {e}")
        errors.append("zooid")

# 4. star_likeness_score metric
if "imports" not in errors and "zooid" not in errors:
    try:
        sl = star_metrics.star_likeness_score(zr, target_arms=7)
        swirl = star_metrics.swirl_score(zr)
        frag = star_metrics.fragmentation_score(zr)
        assert 0.0 <= sl <= 1.0, f"star_likeness out of range: {sl}"
        assert np.isfinite(swirl), f"swirl_score not finite: {swirl}"
        assert 0.0 <= frag <= 1.0, f"fragmentation out of range: {frag}"
        print(f"  PASS  metrics  (star_likeness={sl:.3f}, swirl={swirl:.3f})")
    except Exception as e:
        print(f"  FAIL  metrics: {e}")
        errors.append("metrics")

# 5. Tiny full hybrid run
if "imports" not in errors:
    try:
        r = simulate_star_ascidian_colony(
            preset="clean_star_systems",
            seed=42,
            n_snapshots=3,
            grid_size=16,
            n_field_steps=100,
            n_steps=20,
        )
        assert np.all(np.isfinite(r.field)), "hybrid field non-finite"
        assert r.zooid.N > 0, "no agents"
        assert "star_likeness_score" in r.metrics
        print(f"  PASS  hybrid model  (K={r.zooid.K}, star_likeness={r.metrics['star_likeness_score']:.3f})")
    except Exception as e:
        print(f"  FAIL  hybrid model: {e}")
        errors.append("hybrid")

# 6. Tiny active particle baseline
if "imports" not in errors:
    try:
        abp = simulate_abp(
            N=20, L=5.0, v0=0.5, Dr=0.3,
            dt=0.05, n_steps=50, n_snapshots=3, seed=42,
        )
        assert np.all(np.isfinite(abp.positions)), "ABP positions non-finite"
        print(f"  PASS  active particles  (N={abp.N})")
    except Exception as e:
        print(f"  FAIL  active particles: {e}")
        errors.append("abp")

# 7. Visualization imports
try:
    import matplotlib
    matplotlib.use("Agg")
    from chirality.visualization import BG, ACCENT, GREEN
    assert BG.startswith("#"), "BG not a hex color"
    print("  PASS  visualization imports")
except Exception as e:
    print(f"  FAIL  visualization imports: {e}")
    errors.append("visualization")

# 8. Streamlit import
try:
    import streamlit
    print(f"  PASS  streamlit {streamlit.__version__}")
except ImportError:
    print("  WARN  streamlit not installed (required for app, optional for healthcheck)")

print()
if errors:
    print(f"FAIL: {len(errors)} check(s) failed: {errors}")
    sys.exit(1)
else:
    print("PASS: all checks passed.")
