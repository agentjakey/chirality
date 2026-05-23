"""
Smoke test: verifies all modules import and run on small inputs.
Run from repo root: python scripts/smoke_test.py

Prints PASS or FAIL for each check.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np

failures = []


def check(label, fn):
    try:
        fn()
        print(f"  PASS  {label}")
    except Exception as e:
        print(f"  FAIL  {label}: {e}")
        failures.append(label)


print("=== Chirality Atlas Smoke Test ===")
print()

# ------------------------------------------------------------------
print("[1] Import checks")
check("import chirality", lambda: __import__("chirality"))
check("import chirality.particle_sim", lambda: __import__("chirality.particle_sim"))
check("import chirality.particle_metrics", lambda: __import__("chirality.particle_metrics"))
check("import chirality.pattern_sim", lambda: __import__("chirality.pattern_sim"))
check("import chirality.pattern_metrics", lambda: __import__("chirality.pattern_metrics"))
check("import chirality.phase_sweeps", lambda: __import__("chirality.phase_sweeps"))
check("import chirality.plotting", lambda: __import__("chirality.plotting"))
check("import chirality.presets", lambda: __import__("chirality.presets"))
check("import chirality.export", lambda: __import__("chirality.export"))
check("import chirality.validation", lambda: __import__("chirality.validation"))
check("import chirality.storytelling", lambda: __import__("chirality.storytelling"))
check("import chirality.config", lambda: __import__("chirality.config"))
print()

# ------------------------------------------------------------------
print("[2] Particle simulations (N=20, 50 steps)")

from chirality.particle_sim import simulate_abp, simulate_chiral_abp, simulate_vicsek_chiral
from chirality.particle_metrics import compute_all_particle_metrics
from chirality.validation import all_finite_report

def _run_abp():
    hist = simulate_abp(N=20, L=5.0, v0=0.5, Dr=0.5, dt=0.01, n_steps=50, seed=1, save_every=10)
    assert hist.positions.shape[1] == 20
    assert hist.positions.shape[2] == 2
    ok, msgs = all_finite_report({"positions": hist.positions, "thetas": hist.thetas})
    assert ok, str(msgs)

def _run_chiral_abp():
    for mode in ("none", "left", "right", "racemic", "random"):
        hist = simulate_chiral_abp(
            N=20, L=5.0, v0=0.5, Dr=0.5, omega=1.0, chirality_mode=mode,
            dt=0.01, n_steps=50, seed=2, save_every=10
        )
        ok, msgs = all_finite_report({"positions": hist.positions, "thetas": hist.thetas})
        assert ok, f"mode={mode}: {msgs}"

def _run_vicsek():
    hist = simulate_vicsek_chiral(
        N=20, L=5.0, v0=0.5, R=1.0, eta=0.2, omega=0.5,
        dt=0.1, n_steps=50, seed=3, save_every=10
    )
    ok, msgs = all_finite_report({"positions": hist.positions, "thetas": hist.thetas})
    assert ok, str(msgs)

def _run_boundary_modes():
    for mode in ("periodic", "reflective", "circular_trap"):
        hist = simulate_chiral_abp(
            N=20, L=5.0, v0=0.5, Dr=0.5, omega=1.0, chirality_mode="right",
            dt=0.01, n_steps=30, seed=4, boundary_mode=mode, save_every=10
        )
        ok, msgs = all_finite_report({"positions": hist.positions})
        assert ok, f"boundary={mode}: {msgs}"

def _run_particle_metrics():
    hist = simulate_chiral_abp(
        N=50, L=10.0, v0=0.5, Dr=0.3, omega=2.0, chirality_mode="right",
        dt=0.01, n_steps=100, seed=5, save_every=10
    )
    metrics = compute_all_particle_metrics(hist, R_neighbor=1.0)
    for k, v in metrics.items():
        assert np.isfinite(v), f"metric {k} is not finite: {v}"

check("simulate_abp", _run_abp)
check("simulate_chiral_abp all modes", _run_chiral_abp)
check("simulate_vicsek_chiral", _run_vicsek)
check("boundary modes", _run_boundary_modes)
check("particle metrics", _run_particle_metrics)
print()

# ------------------------------------------------------------------
print("[3] Pattern simulations (64x64, 300 steps)")

from chirality.pattern_sim import (
    laplacian, run_diffusion, run_logistic_growth,
    run_reaction_diffusion_one_field, simulate_gray_scott,
    simulate_feed_gradient, simulate_obstacle,
    simulate_chiral_source_gray_scott, initialize_gray_scott,
)
from chirality.pattern_metrics import compute_all_pattern_metrics

def _run_laplacian():
    f = np.random.default_rng(10).random((32, 32))
    lap = laplacian(f)
    assert lap.shape == f.shape
    assert np.all(np.isfinite(lap))

def _run_diffusion():
    f = np.random.default_rng(11).random((32, 32))
    f2 = run_diffusion(f, D=0.05, dt=0.5, n_steps=20)
    assert np.all(np.isfinite(f2))
    assert f2.shape == f.shape

def _run_logistic():
    f = np.random.default_rng(12).random((32, 32)) * 0.5
    f2 = run_logistic_growth(f, r=0.1, K=1.0, dt=0.5, n_steps=20)
    assert np.all(np.isfinite(f2))

def _run_one_field():
    f = np.random.default_rng(13).random((32, 32)) * 0.1
    f2 = run_reaction_diffusion_one_field(f, D=0.05, r=0.1, K=1.0, dt=0.5, n_steps=20)
    assert np.all(np.isfinite(f2))

def _run_gray_scott():
    hist = simulate_gray_scott(
        nx=64, ny=64, Du=0.16, Dv=0.08, F=0.035, k=0.065,
        dt=1.0, n_steps=300, seed=42, save_every=100
    )
    assert np.all(np.isfinite(hist.u_final))
    assert np.all(np.isfinite(hist.v_final))
    assert hist.u_final.shape == (64, 64)

def _run_feed_gradient():
    hist = simulate_feed_gradient(
        nx=64, ny=64, F_left=0.02, F_right=0.05, k=0.065,
        dt=1.0, n_steps=200, seed=42, save_every=200
    )
    assert np.all(np.isfinite(hist.v_final))

def _run_obstacle():
    hist = simulate_obstacle(
        nx=64, ny=64, F=0.035, k=0.065,
        dt=1.0, n_steps=200, seed=42, save_every=200
    )
    assert np.all(np.isfinite(hist.v_final))

def _run_chiral_source():
    hist = simulate_chiral_source_gray_scott(
        nx=64, ny=64, F=0.035, k=0.065,
        dt=1.0, n_steps=200, seed=42,
        source_strength=0.01, source_omega=0.05,
        save_every=200
    )
    assert np.all(np.isfinite(hist.v_final))

def _run_pattern_metrics():
    hist = simulate_gray_scott(
        nx=64, ny=64, F=0.035, k=0.065,
        dt=1.0, n_steps=500, seed=42, save_every=500
    )
    metrics = compute_all_pattern_metrics(hist)
    for k, v in metrics.items():
        if isinstance(v, float):
            assert np.isfinite(v), f"metric {k} is not finite: {v}"

check("laplacian", _run_laplacian)
check("run_diffusion", _run_diffusion)
check("run_logistic_growth", _run_logistic)
check("run_reaction_diffusion_one_field", _run_one_field)
check("simulate_gray_scott", _run_gray_scott)
check("simulate_feed_gradient", _run_feed_gradient)
check("simulate_obstacle", _run_obstacle)
check("simulate_chiral_source_gray_scott", _run_chiral_source)
check("pattern metrics", _run_pattern_metrics)
print()

# ------------------------------------------------------------------
print("[4] Presets")
from chirality.presets import PRESETS

def _check_presets():
    expected = [
        "baseline_active_brownian",
        "vicsek_flocking",
        "chiral_vortex_gas",
        "boundary_edge_current",
        "racemic_left_right_competition",
        "gray_scott_spots",
        "gray_scott_labyrinth",
        "feed_gradient_pattern",
        "obstacle_disrupted_pattern",
        "chiral_source_pattern",
    ]
    for name in expected:
        assert name in PRESETS, f"Missing preset: {name}"

check("all 10 presets defined", _check_presets)
print()

# ------------------------------------------------------------------
print("[5] Validation module")
from chirality.validation import all_finite_report, check_finite, check_range

def _validation():
    good = np.array([1.0, 2.0, 3.0])
    ok, msgs = all_finite_report({"good": good})
    assert ok

    bad = np.array([1.0, np.nan, 3.0])
    ok, msgs = all_finite_report({"bad": bad})
    assert not ok

check("validation checks", _validation)
print()

# ------------------------------------------------------------------
print("[6] Storytelling module")
from chirality.storytelling import summarize_particle_metrics, summarize_pattern_metrics

def _storytelling():
    m = {
        "polar_order_final": 0.8,
        "polar_order_avg": 0.75,
        "swirl_index": -0.5,
        "boundary_accumulation": 0.6,
        "n_clusters": 3,
    }
    s = summarize_particle_metrics(m, "test")
    assert "polar" in s.lower()

    m2 = {
        "pattern_strength": 0.15,
        "mean_v": 0.1,
        "n_clusters": 25,
        "field_asymmetry_lr": 0.002,
        "radial_asymmetry": 0.001,
    }
    s2 = summarize_pattern_metrics(m2, "test")
    assert "pattern" in s2.lower()

check("storytelling summaries", _storytelling)
print()

# ------------------------------------------------------------------
print("[7] Export module")
from chirality.export import ensure_dir, save_particle_state
import tempfile

def _export():
    with tempfile.TemporaryDirectory() as tmpdir:
        p = os.path.join(tmpdir, "test.npz")
        pos = np.zeros((10, 2))
        th = np.zeros(10)
        save_particle_state(pos, th, p)
        assert os.path.exists(p)

check("export save_particle_state", _export)
print()

# ------------------------------------------------------------------
print("=== Results ===")
if failures:
    print(f"FAIL: {len(failures)} test(s) failed:")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("PASS: all checks passed.")
    sys.exit(0)
