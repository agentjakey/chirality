"""
Layer 1: Activator-inhibitor field for generating star center positions.

Uses Gierer-Meinhardt by default. Falls back to Gray-Scott or Poisson-disk
random placement if GM fails to produce well-separated centers.

All center coordinates are returned in physical units (not grid indices).
"""

import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import maximum_filter

from chirality.model_library.gierer_meinhardt import simulate_gierer_meinhardt
from chirality.model_library.gray_scott import simulate_gray_scott
from chirality.model_library import ensure_dir


def generate_star_centers(
    grid_size=64,
    L=10.0,
    Da=0.05,
    Dh=5.0,
    mu_a=0.05,
    mu_h=0.05,
    rho=0.1,
    rho_0=0.001,
    kappa=0.1,
    dt=0.5,
    n_steps=3000,
    n_snapshots=6,
    min_distance=1.5,
    threshold_fraction=0.55,
    min_separation_pixels=5,
    seed=42,
    method="gm",
):
    """Run the activator-inhibitor field and extract star center positions.

    Returns a dict with:
      field:    (N, N) final activator array
      inhibitor: (N, N) final inhibitor array
      centers:  (K, 2) center positions in physical coordinates [x, y]
      snapshots_u: (n_snapshots, N, N) field time series
      field_params: dict of field parameters
      quality:  dict of center quality metrics
      method:   which method was used
    """
    N = grid_size
    dx = L / N

    if method == "gm" or method == "auto":
        field_result = simulate_gierer_meinhardt(
            N=N, L=L, Da=Da, Dh=Dh, mu_a=mu_a, mu_h=mu_h,
            rho=rho, rho_0=rho_0, kappa=kappa, dt=dt,
            n_steps=n_steps, n_snapshots=n_snapshots, seed=seed,
        )
        activator = field_result.u_final
        inhibitor = field_result.v_final
        snapshots = field_result.snapshots_u
        centers_px = _find_centers_from_field(
            activator, threshold_fraction, min_separation_pixels
        )
        used_method = "gm"

    elif method == "gray_scott":
        gs_result = simulate_gray_scott(
            N=N, L=L, Du=0.16, Dv=0.08, F=0.035, k=0.065,
            dt=1.0, n_steps=n_steps, n_snapshots=n_snapshots, seed=seed
        )
        activator = gs_result.v_final
        inhibitor = gs_result.u_final
        snapshots = gs_result.snapshots_v
        centers_px = _find_centers_from_field(
            activator, threshold_fraction, min_separation_pixels
        )
        used_method = "gray_scott"

    elif method == "poisson_disk":
        activator = np.zeros((N, N))
        inhibitor = np.zeros((N, N))
        snapshots = np.zeros((1, N, N))
        centers_px = _poisson_disk_centers(N, L, min_distance, seed)
        used_method = "poisson_disk"

    else:
        raise ValueError(f"Unknown method: {method}. Use 'gm', 'gray_scott', or 'poisson_disk'.")

    if len(centers_px) == 0 and method == "auto":
        centers_px = _poisson_disk_centers(N, L, min_distance, seed)
        used_method = "poisson_disk"

    centers_phys = _pixel_to_physical(centers_px, dx)
    centers_phys = _filter_by_min_distance(centers_phys, min_distance)

    quality = compute_center_quality(centers_phys, L)

    return dict(
        field=activator,
        inhibitor=inhibitor,
        snapshots_u=snapshots,
        centers=centers_phys,
        field_params=dict(
            N=N, L=L, Da=Da, Dh=Dh, mu_a=mu_a, mu_h=mu_h,
            rho=rho, rho_0=rho_0, kappa=kappa, dt=dt, n_steps=n_steps,
        ),
        quality=quality,
        method=used_method,
    )


def _find_centers_from_field(field, threshold_fraction, min_sep_px):
    """Find local maxima in a 2D field above a threshold."""
    threshold = threshold_fraction * field.max()
    local_max = (field == maximum_filter(field, size=min_sep_px)) & (field > threshold)
    indices = np.argwhere(local_max)
    return indices


def _pixel_to_physical(centers_px, dx):
    """Convert (row, col) pixel indices to physical (x, y) coordinates."""
    if len(centers_px) == 0:
        return np.empty((0, 2))
    rows = centers_px[:, 0].astype(float)
    cols = centers_px[:, 1].astype(float)
    x = cols * dx
    y = rows * dx
    return np.column_stack([x, y])


def _filter_by_min_distance(centers, min_distance):
    """Remove centers that are closer than min_distance to another center."""
    if len(centers) <= 1:
        return centers
    keep = []
    used = np.zeros(len(centers), dtype=bool)
    for i in range(len(centers)):
        if used[i]:
            continue
        keep.append(i)
        for j in range(i + 1, len(centers)):
            if not used[j]:
                d = np.linalg.norm(centers[i] - centers[j])
                if d < min_distance:
                    used[j] = True
    return centers[keep]


def _poisson_disk_centers(N, L, min_distance, seed, n_attempts=100):
    """Generate centers using Poisson disk sampling as fallback."""
    rng = np.random.default_rng(seed)
    centers = []
    for _ in range(n_attempts):
        candidate = rng.uniform(0.5, L - 0.5, 2)
        if all(np.linalg.norm(candidate - c) >= min_distance for c in centers):
            centers.append(candidate)
    return np.array(centers) if centers else np.array([[L / 2, L / 2]])


def compute_center_quality(centers, L):
    """Compute quality metrics for a set of centers.

    Returns dict with n_centers, spacing_mean, spacing_cv, boundary_fraction.
    """
    K = len(centers)
    if K == 0:
        return dict(n_centers=0, spacing_mean=0.0, spacing_cv=0.0, boundary_fraction=0.0)

    if K == 1:
        return dict(n_centers=1, spacing_mean=L, spacing_cv=0.0, boundary_fraction=0.0)

    tree = cKDTree(centers)
    dists, _ = tree.query(centers, k=2)
    nn_dists = dists[:, 1]

    spacing_mean = float(nn_dists.mean())
    spacing_cv = float(nn_dists.std() / (spacing_mean + 1e-9))

    margin = spacing_mean * 0.5
    near_boundary = np.any(
        (centers < margin) | (centers > L - margin), axis=1
    )
    boundary_fraction = float(near_boundary.mean())

    return dict(
        n_centers=K,
        spacing_mean=spacing_mean,
        spacing_cv=spacing_cv,
        boundary_fraction=boundary_fraction,
    )
