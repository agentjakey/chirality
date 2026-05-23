"""
Health check for the Chirality Atlas deployment.

Imports core modules, runs tiny simulations, and verifies all outputs are finite.
Prints PASS if everything works, FAIL with details if something is broken.

Run from repo root:
    python healthcheck.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import numpy as np

errors = []

print("=== Chirality Atlas Health Check ===")
print()

# Import check
try:
    from chirality.particle_sim import simulate_abp, simulate_chiral_abp, simulate_vicsek_chiral
    from chirality.particle_metrics import polar_order, swirl_index, boundary_accumulation
    from chirality.pattern_sim import simulate_gray_scott
    from chirality.pattern_metrics import pattern_strength
    from chirality.validation import all_finite_report
    print("  PASS  imports")
except Exception as e:
    print(f"  FAIL  imports: {e}")
    errors.append("imports")

# Tiny particle simulation
if "imports" not in errors:
    try:
        hist = simulate_chiral_abp(
            N=20, L=5.0, v0=0.5, Dr=0.5, omega=1.0,
            chirality_mode="right", dt=0.01, n_steps=50, seed=0,
            boundary_mode="periodic", repulsion=False, save_every=50,
        )
        phi = polar_order(hist.thetas[-1])
        si  = swirl_index(hist.positions[-1], hist.thetas[-1], hist.L)
        ba  = boundary_accumulation(hist.positions[-1], hist.L)
        assert np.isfinite(phi), "polar_order not finite"
        assert np.isfinite(si),  "swirl_index not finite"
        assert np.isfinite(ba),  "boundary_accumulation not finite"
        assert 0.0 <= phi <= 1.0, f"polar_order out of range: {phi}"
        assert 0.0 <= ba  <= 1.0, f"boundary_accumulation out of range: {ba}"
        print(f"  PASS  particle simulation  (phi={phi:.3f}, swirl={si:.3f}, ba={ba:.3f})")
    except Exception as e:
        print(f"  FAIL  particle simulation: {e}")
        errors.append("particle_sim")

# Tiny pattern simulation
if "imports" not in errors:
    try:
        hist = simulate_gray_scott(
            nx=32, ny=32, Du=0.16, Dv=0.08, F=0.035, k=0.065,
            dt=1.0, n_steps=100, seed=42, save_every=100,
        )
        strength = pattern_strength(hist.v_final)
        assert np.isfinite(strength), "pattern_strength not finite"
        assert np.all(np.isfinite(hist.u_final)), "u field has non-finite values"
        assert np.all(np.isfinite(hist.v_final)), "v field has non-finite values"
        assert hist.u_final.min() >= 0.0, "u field has negative values"
        assert hist.v_final.min() >= 0.0, "v field has negative values"
        print(f"  PASS  pattern simulation   (pattern_strength={strength:.5f})")
    except Exception as e:
        print(f"  FAIL  pattern simulation: {e}")
        errors.append("pattern_sim")

# Plotting import (no figure rendered)
if "imports" not in errors:
    try:
        import matplotlib
        matplotlib.use("Agg")
        from chirality.plotting import plot_particle_snapshot, plot_field
        print("  PASS  plotting module")
    except Exception as e:
        print(f"  FAIL  plotting module: {e}")
        errors.append("plotting")

# Streamlit import
try:
    import streamlit
    print(f"  PASS  streamlit {streamlit.__version__}")
except ImportError:
    print("  WARN  streamlit not installed (optional for healthcheck)")

print()
if errors:
    print(f"FAIL: {len(errors)} check(s) failed: {errors}")
    sys.exit(1)
else:
    print("PASS")
