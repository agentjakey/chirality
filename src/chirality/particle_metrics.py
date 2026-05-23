"""
Metrics computed on particle simulation histories.

All functions operate on numpy arrays and return scalar floats or arrays.
"""
import numpy as np


def polar_order(thetas):
    """
    Polar (orientational) order parameter.

    phi = |mean(exp(i * theta))|
    phi = 1 means all particles point the same direction.
    phi = 0 means orientations are isotropically distributed.
    """
    return float(np.abs(np.mean(np.exp(1j * thetas))))


def time_averaged_order(thetas_history):
    """
    Average polar order over all snapshots in a history.

    thetas_history: (n_snapshots, N)
    """
    orders = np.array([polar_order(th) for th in thetas_history])
    return float(np.mean(orders))


def polar_order_timeseries(thetas_history):
    """
    Returns polar order at each snapshot.

    thetas_history: (n_snapshots, N)
    Returns: (n_snapshots,) array
    """
    return np.array([polar_order(th) for th in thetas_history])


def mean_squared_displacement(positions_history):
    """
    Compute mean squared displacement relative to first snapshot.

    positions_history: (n_snapshots, N, 2)
    Returns: (n_snapshots,) MSD array
    """
    pos0 = positions_history[0]   # (N, 2)
    diffs = positions_history - pos0[np.newaxis, :, :]  # (n_snapshots, N, 2)
    msd = np.mean(np.sum(diffs ** 2, axis=2), axis=1)
    return msd


def average_neighbor_count(positions, L, R):
    """
    Mean number of neighbors within radius R, using periodic boundary.

    positions: (N, 2)
    Returns: float
    """
    N = len(positions)
    if N < 2:
        return 0.0
    dx = positions[:, 0:1] - positions[:, 0]
    dy = positions[:, 1:2] - positions[:, 1]
    dx = dx - L * np.round(dx / L)
    dy = dy - L * np.round(dy / L)
    dist2 = dx ** 2 + dy ** 2
    # exclude self (diagonal is 0)
    np.fill_diagonal(dist2, np.inf)
    return float(np.mean(np.sum(dist2 < R ** 2, axis=1)))


def swirl_index(positions, thetas, L):
    """
    Angular momentum proxy: measures how much particles circulate around
    the box center.

    For a pure clockwise swirl, this is negative.
    For a pure counter-clockwise swirl, this is positive.
    Returns value in [-1, 1] (normalized).
    """
    center = np.array([L / 2, L / 2])
    r_vec = positions - center     # (N, 2)
    r_mag = np.linalg.norm(r_vec, axis=1)
    r_mag = np.where(r_mag < 1e-9, 1e-9, r_mag)

    v_tangent = np.column_stack([-r_vec[:, 1], r_vec[:, 0]]) / r_mag[:, np.newaxis]
    v_dir = np.column_stack([np.cos(thetas), np.sin(thetas)])

    # dot product of velocity direction with tangent direction
    dots = np.sum(v_dir * v_tangent, axis=1)
    return float(np.mean(dots))


def boundary_accumulation(positions, L, shell_width=0.5):
    """
    Fraction of particles within shell_width of any wall (periodic box).

    Higher values indicate particles are accumulating near boundaries.
    """
    N = len(positions)
    x = positions[:, 0]
    y = positions[:, 1]
    near_wall = (
        (x < shell_width) | (x > L - shell_width) |
        (y < shell_width) | (y > L - shell_width)
    )
    return float(np.sum(near_wall) / N)


def cluster_count(positions, L, R_cluster):
    """
    Count clusters using single-linkage: two particles are in the same
    cluster if within R_cluster (minimum-image).
    Returns number of clusters.
    """
    N = len(positions)
    if N == 0:
        return 0
    dx = positions[:, 0:1] - positions[:, 0]
    dy = positions[:, 1:2] - positions[:, 1]
    dx = dx - L * np.round(dx / L)
    dy = dy - L * np.round(dy / L)
    dist2 = dx ** 2 + dy ** 2
    np.fill_diagonal(dist2, np.inf)
    adj = dist2 < R_cluster ** 2

    # union-find
    parent = list(range(N))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i in range(N):
        for j in range(i + 1, N):
            if adj[i, j]:
                union(i, j)

    return len(set(find(i) for i in range(N)))


def compute_all_particle_metrics(history, R_neighbor=1.0, R_cluster=1.0):
    """
    Compute all particle metrics from a ParticleHistory.

    Returns a dict of scalar metrics (from the final snapshot).
    """
    final_pos = history.positions[-1]
    final_th = history.thetas[-1]
    L = history.L

    phi_final = polar_order(final_th)
    phi_avg = time_averaged_order(history.thetas)
    msd = mean_squared_displacement(history.positions)
    msd_final = float(msd[-1]) if len(msd) > 0 else 0.0
    neighbors = average_neighbor_count(final_pos, L, R_neighbor)
    swirl = swirl_index(final_pos, final_th, L)
    accum = boundary_accumulation(final_pos, L)
    n_clusters = cluster_count(final_pos, L, R_cluster)

    return {
        "polar_order_final": phi_final,
        "polar_order_avg": phi_avg,
        "msd_final": msd_final,
        "avg_neighbor_count": neighbors,
        "swirl_index": swirl,
        "boundary_accumulation": accum,
        "n_clusters": n_clusters,
    }
