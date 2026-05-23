"""
Quantitative metrics for star ascidian-like colony patterns.

All metrics are computed from the final agent positions in a ZooidResult.
Per-center values are averaged across the colony.
"""

import numpy as np
from scipy.signal import find_peaks


def radial_order_score(result, band_fraction=0.3):
    """Fraction of agents within [r_target*(1-band), r_target*(1+band)] from their center.

    Higher = agents well-localized at the target radius (ring-like structure).
    """
    pos = result.positions[-1]
    r_target = result.r_target
    scores = []
    for k, center in enumerate(result.centers):
        mask = result.assignments == k
        if not mask.any():
            continue
        r_vecs = pos[mask] - center
        r = np.linalg.norm(r_vecs, axis=1)
        in_band = (r >= r_target * (1.0 - band_fraction)) & (r <= r_target * (1.0 + band_fraction))
        scores.append(float(in_band.mean()))
    return float(np.mean(scores)) if scores else 0.0


def arm_count_distribution(result, n_bins=36, min_prominence=0.05):
    """Estimate number of radial arms per center using angular histogram peaks.

    Returns dict with per_center (list of int), mean, std.
    """
    pos = result.positions[-1]
    counts = []
    for k, center in enumerate(result.centers):
        mask = result.assignments == k
        if mask.sum() < 3:
            counts.append(0)
            continue
        r_vecs = pos[mask] - center
        angles = np.arctan2(r_vecs[:, 1], r_vecs[:, 0])
        hist, _ = np.histogram(angles, bins=n_bins, range=(-np.pi, np.pi))
        hist = hist.astype(float)
        hist_smooth = np.convolve(hist, np.ones(3) / 3, mode="same")
        max_h = hist_smooth.max()
        if max_h < 1e-9:
            counts.append(0)
            continue
        peaks, _ = find_peaks(
            hist_smooth,
            prominence=min_prominence * max_h,
            distance=max(1, n_bins // (result.n_arms + 2)),
        )
        counts.append(len(peaks))
    return dict(
        per_center=counts,
        mean=float(np.mean(counts)) if counts else 0.0,
        std=float(np.std(counts)) if counts else 0.0,
    )


def angular_uniformity_score(result, n_bins=36, min_prominence=0.05):
    """Measure uniformity of arm angular spacing.

    Returns mean circular variance of inter-arm angles over all centers.
    0 = perfectly uniform, 1 = completely clustered.
    Score returned is (1 - variance), so 1 = perfectly uniform.
    """
    pos = result.positions[-1]
    uniformity_scores = []
    for k, center in enumerate(result.centers):
        mask = result.assignments == k
        if mask.sum() < 3:
            uniformity_scores.append(0.0)
            continue
        r_vecs = pos[mask] - center
        angles = np.arctan2(r_vecs[:, 1], r_vecs[:, 0])
        hist, bin_edges = np.histogram(angles, bins=n_bins, range=(-np.pi, np.pi))
        hist = hist.astype(float)
        hist_smooth = np.convolve(hist, np.ones(3) / 3, mode="same")
        max_h = hist_smooth.max()
        if max_h < 1e-9:
            uniformity_scores.append(0.0)
            continue
        peaks, _ = find_peaks(
            hist_smooth,
            prominence=min_prominence * max_h,
            distance=max(1, n_bins // (result.n_arms + 2)),
        )
        if len(peaks) < 2:
            uniformity_scores.append(0.0)
            continue
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
        peak_angles = bin_centers[peaks]
        diffs = np.diff(np.sort(peak_angles))
        if len(diffs) == 0:
            uniformity_scores.append(0.0)
            continue
        cv = float(diffs.std() / (diffs.mean() + 1e-9))
        uniformity_scores.append(max(0.0, 1.0 - cv))
    return float(np.mean(uniformity_scores)) if uniformity_scores else 0.0


def star_likeness_score(
    result,
    target_arms=7,
    arm_tolerance=2,
    band_fraction=0.3,
):
    """Composite star-likeness score in [0, 1].

    Combines:
      - arm_score: measured arm count close to target
      - radial_score: agents near target radius
      - uniformity_score: arms evenly spaced
    """
    arm_info = arm_count_distribution(result)
    n_arms_measured = arm_info["mean"]
    arm_score = float(
        np.exp(-0.5 * ((n_arms_measured - target_arms) / arm_tolerance) ** 2)
    )
    radial_score = radial_order_score(result, band_fraction=band_fraction)
    uniformity = angular_uniformity_score(result)
    return float((arm_score + radial_score + uniformity) / 3.0)


def swirl_score(result):
    """Net signed angular momentum of agents around their assigned centers.

    Positive = net CCW rotation; negative = CW.
    Normalized by v0 so magnitude is in [~-1, ~1].
    """
    pos = result.positions[-1]
    thetas = result.thetas[-1]
    v0 = result.params.get("v0", 0.05)
    swirls = []
    for k, center in enumerate(result.centers):
        mask = result.assignments == k
        if not mask.any():
            continue
        r_vecs = pos[mask] - center
        r = np.linalg.norm(r_vecs, axis=1, keepdims=True) + 1e-9
        r_hats = r_vecs / r
        t_hats = np.column_stack([-r_hats[:, 1], r_hats[:, 0]])
        vx = v0 * np.cos(thetas[mask])
        vy = v0 * np.sin(thetas[mask])
        v = np.column_stack([vx, vy])
        angular_v = np.sum(v * t_hats, axis=1)
        swirls.append(float(np.mean(angular_v)) / (v0 + 1e-9))
    return float(np.mean(swirls)) if swirls else 0.0


def merge_score(result):
    """Fraction of agent pairs from different centers closer than r_target.

    High value -> stars are merging (overcrowded).
    """
    pos = result.positions[-1]
    r_target = result.r_target
    total_cross = 0
    merged = 0
    N = len(pos)
    for i in range(N):
        for j in range(i + 1, N):
            if result.assignments[i] != result.assignments[j]:
                total_cross += 1
                d = np.linalg.norm(pos[i] - pos[j])
                if d < r_target:
                    merged += 1
    return float(merged / total_cross) if total_cross > 0 else 0.0


def fragmentation_score(result, far_fraction=1.8):
    """Fraction of agents that are farther than far_fraction * r_target from their center.

    High value -> many agents have escaped their star (fragmented/noisy regime).
    """
    pos = result.positions[-1]
    r_target = result.r_target
    far_count = 0
    total = 0
    for k, center in enumerate(result.centers):
        mask = result.assignments == k
        if not mask.any():
            continue
        r_vecs = pos[mask] - center
        r = np.linalg.norm(r_vecs, axis=1)
        far_count += int((r > far_fraction * r_target).sum())
        total += mask.sum()
    return float(far_count / total) if total > 0 else 0.0


def visual_similarity_report(result, target_arms=7):
    """Generate a human-readable summary of simulation vs target.

    Returns a dict with fields: matches, failures, suggested_fix.
    """
    arm_info = arm_count_distribution(result)
    n_arms_measured = arm_info["mean"]
    radial = radial_order_score(result)
    uniformity = angular_uniformity_score(result)
    sl = star_likeness_score(result, target_arms=target_arms)
    swirl = swirl_score(result)
    frag = fragmentation_score(result)
    merge = merge_score(result)

    matches = []
    failures = []
    suggestions = []

    if result.K >= 2:
        matches.append(f"Multiple star centers present (K={result.K})")
    else:
        failures.append("Too few star centers (K < 2); increase Dh/Da ratio")
        suggestions.append("Increase Dh to get more Turing spots")

    if radial > 0.5:
        matches.append(f"Radial ring structure present (radial_order={radial:.2f})")
    else:
        failures.append(f"Agents not localized at r_target (radial_order={radial:.2f})")
        suggestions.append("Increase k_radial or decrease v0")

    if abs(n_arms_measured - target_arms) <= 2:
        matches.append(f"Arm count near target ({n_arms_measured:.1f} vs {target_arms})")
    else:
        failures.append(f"Arm count off target ({n_arms_measured:.1f} vs {target_arms})")
        suggestions.append(
            "Adjust n_per_center or k_angular to control arm count"
        )

    if uniformity > 0.5:
        matches.append(f"Arms approximately evenly spaced (uniformity={uniformity:.2f})")
    else:
        failures.append(f"Irregular arm spacing (uniformity={uniformity:.2f})")
        suggestions.append("Increase k_angular to enforce uniform arm repulsion")

    if frag < 0.2:
        matches.append(f"Agents mostly contained in stars (frag={frag:.2f})")
    else:
        failures.append(f"Many agents scattered outside stars (frag={frag:.2f})")
        suggestions.append("Decrease Dr and v0 to reduce fragmentation")

    if merge < 0.1:
        matches.append(f"Stars not merging (merge={merge:.2f})")
    else:
        failures.append(f"Stars overlapping (merge={merge:.2f})")
        suggestions.append("Decrease n_per_center or increase center spacing (higher Dh/Da)")

    return dict(
        star_likeness_score=sl,
        arm_count_mean=n_arms_measured,
        radial_order=radial,
        angular_uniformity=uniformity,
        swirl_score=swirl,
        fragmentation=frag,
        merge_score=merge,
        matches=matches,
        failures=failures,
        suggested_fix="; ".join(suggestions) if suggestions else "Parameters look good",
    )
