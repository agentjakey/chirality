"""
Generate human-readable summaries of simulation results.
Used in the final presentation and README.
"""
import numpy as np


def summarize_particle_metrics(metrics: dict, preset_name: str = "") -> str:
    phi = metrics.get("polar_order_final", float("nan"))
    phi_avg = metrics.get("polar_order_avg", float("nan"))
    swirl = metrics.get("swirl_index", float("nan"))
    accum = metrics.get("boundary_accumulation", float("nan"))
    clusters = metrics.get("n_clusters", "?")

    lines = []
    if preset_name:
        lines.append(f"Preset: {preset_name}")

    if phi > 0.7:
        order_desc = "highly ordered (flocking)"
    elif phi > 0.3:
        order_desc = "partially ordered"
    else:
        order_desc = "disordered (gas-like)"

    lines.append(f"Polar order (final): {phi:.3f} -- {order_desc}")
    lines.append(f"Polar order (time-averaged): {phi_avg:.3f}")

    if abs(swirl) > 0.3:
        swirl_dir = "counter-clockwise" if swirl > 0 else "clockwise"
        lines.append(f"Swirl index: {swirl:.3f} -- significant {swirl_dir} circulation")
    else:
        lines.append(f"Swirl index: {swirl:.3f} -- weak net circulation")

    if accum > 0.4:
        lines.append(f"Boundary accumulation: {accum:.3f} -- strong edge current")
    elif accum > 0.2:
        lines.append(f"Boundary accumulation: {accum:.3f} -- moderate boundary preference")
    else:
        lines.append(f"Boundary accumulation: {accum:.3f} -- bulk distribution")

    lines.append(f"Clusters detected: {clusters}")

    return "\n".join(lines)


def summarize_pattern_metrics(metrics: dict, preset_name: str = "") -> str:
    strength = metrics.get("pattern_strength", float("nan"))
    mean_v = metrics.get("mean_v", float("nan"))
    n_clusters = metrics.get("n_clusters", "?")
    asym = metrics.get("field_asymmetry_lr", float("nan"))

    lines = []
    if preset_name:
        lines.append(f"Preset: {preset_name}")

    if strength > 0.15:
        pat_desc = "strong patterning (spots or stripes)"
    elif strength > 0.05:
        pat_desc = "weak patterning"
    else:
        pat_desc = "near-homogeneous state"

    lines.append(f"Pattern strength (std of v): {strength:.4f} -- {pat_desc}")
    lines.append(f"Mean v concentration: {mean_v:.4f}")
    lines.append(f"Discrete clusters: {n_clusters}")

    if abs(asym) > 0.005:
        side = "right" if asym > 0 else "left"
        lines.append(f"Left-right asymmetry: {asym:.5f} -- pattern biased toward {side}")
    else:
        lines.append(f"Left-right asymmetry: {asym:.5f} -- symmetric pattern")

    return "\n".join(lines)


def summarize_phase_sweep(results: dict, param1: str, param2: str, metric: str) -> str:
    vals = np.asarray(results[metric])
    p1 = np.asarray(results[param1 + "_values"])
    p2 = np.asarray(results[param2 + "_values"])

    idx = np.unravel_index(np.argmax(vals), vals.shape)
    best_p1 = p1[idx[0]]
    best_p2 = p2[idx[1]]
    max_val = vals[idx]

    lines = [
        f"Phase sweep: {metric} over {param1} vs {param2}",
        f"  Range {param1}: [{p1.min():.3f}, {p1.max():.3f}]",
        f"  Range {param2}: [{p2.min():.3f}, {p2.max():.3f}]",
        f"  Peak {metric}: {max_val:.4f} at {param1}={best_p1:.3f}, {param2}={best_p2:.3f}",
        f"  Mean: {vals.mean():.4f}, Std: {vals.std():.4f}",
    ]
    return "\n".join(lines)


def write_science_summary(particle_results: dict, pattern_results: dict) -> str:
    """Compose a short text summary suitable for a slide or README."""
    lines = [
        "=== Chirality Atlas: Science Summary ===",
        "",
        "Particle simulations:",
    ]
    for name, metrics in particle_results.items():
        lines.append(f"  [{name}]")
        for k, v in metrics.items():
            if isinstance(v, float):
                lines.append(f"    {k}: {v:.4f}")
            else:
                lines.append(f"    {k}: {v}")
    lines.append("")
    lines.append("Pattern simulations:")
    for name, metrics in pattern_results.items():
        lines.append(f"  [{name}]")
        for k, v in metrics.items():
            if isinstance(v, float):
                lines.append(f"    {k}: {v:.4f}")
            else:
                lines.append(f"    {k}: {v}")
    return "\n".join(lines)
