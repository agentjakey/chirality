"""
Metrics computed on 2D reaction-diffusion fields.
"""
import numpy as np


def pattern_strength(v):
    """
    Standard deviation of the v field.
    High value means the pattern has large spatial variation (spots/stripes).
    Near zero means the field is uniform (homogeneous state).
    """
    return float(np.std(v))


def pattern_mean(v):
    """Mean concentration of v species."""
    return float(np.mean(v))


def count_clusters(v, threshold=0.1):
    """
    Count connected clusters of v > threshold using scipy label.

    Returns: (n_clusters, labeled_array)
    """
    try:
        from scipy.ndimage import label
    except ImportError:
        raise ImportError("scipy is required for cluster counting")
    binary = (v > threshold).astype(np.int32)
    labeled, n = label(binary)
    return int(n), labeled


def field_asymmetry(v):
    """
    Left-right asymmetry of the v field.

    Compares the mean of the left half vs the right half.
    Returns a signed value: positive means more v on the right.
    Range roughly [-1, 1] for normalized fields.
    """
    nx = v.shape[0]
    left = v[:nx // 2, :]
    right = v[nx // 2:, :]
    return float(np.mean(right) - np.mean(left))


def radial_asymmetry(v):
    """
    Top-bottom vs left-right asymmetry ratio.

    Measures whether the pattern has more structure along one axis.
    """
    nx, ny = v.shape
    left_right = abs(np.mean(v[nx // 2:, :]) - np.mean(v[:nx // 2, :]))
    top_bottom = abs(np.mean(v[:, ny // 2:]) - np.mean(v[:, :ny // 2]))
    return float(left_right - top_bottom)


def obstacle_disruption_score(v, obstacle_cx, obstacle_cy, obstacle_r, nx, ny):
    """
    Compare pattern strength inside vs outside the obstacle neighborhood.

    Returns: (strength_inside, strength_outside)
    """
    xs = np.arange(nx) / nx
    ys = np.arange(ny) / ny
    XX, YY = np.meshgrid(xs, ys, indexing="ij")
    dist = np.sqrt((XX - obstacle_cx) ** 2 + (YY - obstacle_cy) ** 2)

    # neighborhood: 1.5x obstacle radius
    near = dist < obstacle_r * 1.5
    far = ~near

    strength_near = float(np.std(v[near])) if near.any() else 0.0
    strength_far = float(np.std(v[far])) if far.any() else 0.0
    return strength_near, strength_far


def compute_all_pattern_metrics(field_history, threshold=0.1):
    """
    Compute all pattern metrics from a FieldHistory.

    Returns a dict of scalar metrics from the final v field.
    """
    v = field_history.v_final
    strength = pattern_strength(v)
    mean_v = pattern_mean(v)
    n_clusters, _ = count_clusters(v, threshold)
    asym_lr = field_asymmetry(v)
    asym_rad = radial_asymmetry(v)

    return {
        "pattern_strength": strength,
        "mean_v": mean_v,
        "n_clusters": n_clusters,
        "field_asymmetry_lr": asym_lr,
        "radial_asymmetry": asym_rad,
    }
