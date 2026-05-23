"""
Test that all model_library and visualization modules import without error.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_model_library_init():
    from chirality.model_library import FieldResult, ParticleResult, laplacian_2d_periodic, check_finite, ensure_dir


def test_fisher_kpp_import():
    from chirality.model_library.fisher_kpp import simulate_fisher_kpp, front_radius


def test_fitzhugh_nagumo_import():
    from chirality.model_library.fitzhugh_nagumo import simulate_fitzhugh_nagumo, wave_activity


def test_gierer_meinhardt_import():
    from chirality.model_library.gierer_meinhardt import (
        simulate_gierer_meinhardt, find_activator_centers, pattern_strength, cluster_count
    )


def test_cahn_hilliard_import():
    from chirality.model_library.cahn_hilliard import simulate_cahn_hilliard, domain_size_proxy


def test_gray_scott_import():
    from chirality.model_library.gray_scott import (
        initialize_gray_scott, simulate_gray_scott, pattern_strength, cluster_count
    )


def test_active_particles_import():
    from chirality.model_library.active_particles import (
        simulate_abp, simulate_chiral_abp, simulate_vicsek,
        polar_order, swirl_index, msd, avg_neighbors
    )


def test_visualization_init():
    from chirality.visualization import (
        plot_field, plot_phase_diagram, plot_particle_snapshot,
        plot_trajectories, save_field_gif, save_particle_gif,
        BG, INK, ACCENT, GREEN, NEUTRAL,
    )


def test_visualization_style():
    from chirality.visualization.style import apply_notebook_style, CHIRALITY_CMAP
    assert CHIRALITY_CMAP is not None


def test_visualization_plots():
    from chirality.visualization.plots import (
        plot_field, plot_phase_diagram, plot_particle_snapshot, plot_trajectories
    )


def test_visualization_animations():
    from chirality.visualization.animations import save_field_gif, save_particle_gif
