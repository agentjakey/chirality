"""
Integration tests for the model_library.

Each test runs a minimal simulation and verifies:
- Output types are correct (FieldResult or ParticleResult)
- Arrays have the expected shape
- All values are finite
- Metric functions return scalar floats in valid ranges
"""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from chirality.model_library import FieldResult, ParticleResult


N_SMALL = 16
N_MED = 32


class TestFisherKPP:
    def setup_method(self):
        from chirality.model_library.fisher_kpp import simulate_fisher_kpp
        self.result = simulate_fisher_kpp(N=N_SMALL, n_steps=30, n_snapshots=3, seed=0)

    def test_type(self):
        assert isinstance(self.result, FieldResult)

    def test_shape(self):
        assert self.result.u_final.shape == (N_SMALL, N_SMALL)
        assert self.result.shape == (N_SMALL, N_SMALL)

    def test_finite(self):
        assert np.all(np.isfinite(self.result.u_final))

    def test_bounds(self):
        assert self.result.u_final.min() >= 0.0
        assert self.result.u_final.max() <= 1.0 + 1e-6

    def test_snapshots(self):
        assert self.result.snapshots_u.shape[0] > 0
        assert self.result.v_final is None

    def test_front_radius(self):
        from chirality.model_library.fisher_kpp import front_radius
        r = front_radius(self.result)
        assert isinstance(r, float)
        assert r >= 0.0


class TestFitzHughNagumo:
    def setup_method(self):
        from chirality.model_library.fitzhugh_nagumo import simulate_fitzhugh_nagumo
        self.result = simulate_fitzhugh_nagumo(N=N_SMALL, n_steps=50, n_snapshots=3, seed=0)

    def test_type(self):
        assert isinstance(self.result, FieldResult)

    def test_shape(self):
        assert self.result.u_final.shape == (N_SMALL, N_SMALL)
        assert self.result.v_final.shape == (N_SMALL, N_SMALL)

    def test_finite(self):
        assert np.all(np.isfinite(self.result.u_final))
        assert np.all(np.isfinite(self.result.v_final))

    def test_wave_activity(self):
        from chirality.model_library.fitzhugh_nagumo import wave_activity
        wa = wave_activity(self.result)
        assert 0.0 <= wa <= 1.0


class TestGiererMeinhardt:
    def setup_method(self):
        from chirality.model_library.gierer_meinhardt import simulate_gierer_meinhardt
        self.result = simulate_gierer_meinhardt(N=N_MED, n_steps=300, n_snapshots=3, seed=0)

    def test_type(self):
        assert isinstance(self.result, FieldResult)

    def test_shape(self):
        assert self.result.u_final.shape == (N_MED, N_MED)
        assert self.result.v_final.shape == (N_MED, N_MED)

    def test_finite_positive(self):
        assert np.all(np.isfinite(self.result.u_final))
        assert np.all(np.isfinite(self.result.v_final))
        assert self.result.u_final.min() > 0
        assert self.result.v_final.min() > 0

    def test_pattern_strength(self):
        from chirality.model_library.gierer_meinhardt import pattern_strength
        ps = pattern_strength(self.result)
        assert ps >= 0.0

    def test_cluster_count(self):
        from chirality.model_library.gierer_meinhardt import cluster_count
        cc = cluster_count(self.result)
        assert isinstance(cc, int)
        assert cc >= 0

    def test_find_centers(self):
        from chirality.model_library.gierer_meinhardt import find_activator_centers
        centers = find_activator_centers(self.result)
        assert centers.ndim == 2 or len(centers) == 0
        if len(centers) > 0:
            assert centers.shape[1] == 2


class TestCahnHilliard:
    def setup_method(self):
        from chirality.model_library.cahn_hilliard import simulate_cahn_hilliard
        self.result = simulate_cahn_hilliard(N=N_MED, n_steps=100, n_snapshots=3, seed=0)

    def test_type(self):
        assert isinstance(self.result, FieldResult)

    def test_shape(self):
        assert self.result.u_final.shape == (N_MED, N_MED)

    def test_finite(self):
        assert np.all(np.isfinite(self.result.u_final))

    def test_conservation(self):
        mean0 = self.result.snapshots_u[0].mean()
        meanf = self.result.u_final.mean()
        assert abs(mean0 - meanf) < 0.05

    def test_domain_size_proxy(self):
        from chirality.model_library.cahn_hilliard import domain_size_proxy
        dsp = domain_size_proxy(self.result)
        assert isinstance(dsp, float)
        assert dsp >= 0.0

    def test_spectral_stable_large_dt(self):
        from chirality.model_library.cahn_hilliard import simulate_cahn_hilliard
        # Semi-implicit scheme should tolerate dt=1.0 without blowing up
        result = simulate_cahn_hilliard(N=N_MED, dt=1.0, n_steps=20)
        assert np.all(np.isfinite(result.u_final))


class TestGrayScott:
    def setup_method(self):
        from chirality.model_library.gray_scott import simulate_gray_scott
        self.result = simulate_gray_scott(N=N_MED, n_steps=300, n_snapshots=3, seed=0)

    def test_type(self):
        assert isinstance(self.result, FieldResult)

    def test_shape(self):
        assert self.result.u_final.shape == (N_MED, N_MED)
        assert self.result.v_final.shape == (N_MED, N_MED)

    def test_finite_bounds(self):
        assert np.all(np.isfinite(self.result.u_final))
        assert np.all(np.isfinite(self.result.v_final))
        assert self.result.u_final.min() >= -1e-6
        assert self.result.u_final.max() <= 1.0 + 1e-6

    def test_metrics(self):
        from chirality.model_library.gray_scott import pattern_strength, cluster_count
        ps = pattern_strength(self.result)
        cc = cluster_count(self.result)
        assert ps >= 0.0
        assert cc >= 0

    def test_initialize(self):
        from chirality.model_library.gray_scott import initialize_gray_scott
        u, v = initialize_gray_scott(N=N_MED, seed=1)
        assert u.shape == (N_MED, N_MED)
        assert v.shape == (N_MED, N_MED)
        assert np.all(u >= 0) and np.all(u <= 1)


class TestActiveParticles:
    def test_abp(self):
        from chirality.model_library.active_particles import simulate_abp, polar_order, msd
        r = simulate_abp(N=50, n_steps=50, n_snapshots=5, seed=0)
        assert isinstance(r, ParticleResult)
        assert r.positions.shape == (5, 50, 2)
        assert r.thetas.shape == (5, 50)
        assert np.all(np.isfinite(r.positions))
        phi = polar_order(r)
        assert 0.0 <= phi <= 1.0 + 1e-6
        d = msd(r)
        assert d >= 0.0

    def test_chiral_modes(self):
        from chirality.model_library.active_particles import simulate_chiral_abp, swirl_index
        for mode in ["uniform", "left", "right", "racemic", "random"]:
            r = simulate_chiral_abp(N=30, omega=1.5, mode=mode, n_steps=30, n_snapshots=3, seed=0)
            assert isinstance(r, ParticleResult)
            assert np.all(np.isfinite(r.positions))
            si = swirl_index(r)
            assert np.isfinite(si), f"swirl_index not finite for mode={mode}"

    def test_vicsek_low_noise(self):
        from chirality.model_library.active_particles import simulate_vicsek, polar_order
        r = simulate_vicsek(N=100, eta=0.05, R=1.5, n_steps=200, n_snapshots=5, seed=42)
        phi = polar_order(r)
        assert phi > 0.5, f"Low-noise Vicsek should have phi > 0.5, got {phi:.3f}"

    def test_avg_neighbors(self):
        from chirality.model_library.active_particles import simulate_abp, avg_neighbors
        r = simulate_abp(N=100, n_steps=50, n_snapshots=5, seed=0)
        an = avg_neighbors(r)
        assert np.isfinite(an)
        assert an >= 0.0
