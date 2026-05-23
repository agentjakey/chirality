"""
Save simulation results and figures to disk.
"""
import os
import csv
import numpy as np
import matplotlib.pyplot as plt


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def save_figure(fig, path, dpi=150, close=True):
    ensure_dir(os.path.dirname(path) or ".")
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    if close:
        plt.close(fig)


def save_field_npy(field, path):
    ensure_dir(os.path.dirname(path) or ".")
    np.save(path, field)


def save_particle_state(positions, thetas, path):
    ensure_dir(os.path.dirname(path) or ".")
    np.savez(path, positions=positions, thetas=thetas)


def save_phase_diagram_data(results, path):
    ensure_dir(os.path.dirname(path) or ".")
    np.savez(path, **{k: np.asarray(v) for k, v in results.items()})


def load_phase_diagram_data(path):
    data = np.load(path, allow_pickle=True)
    return dict(data)


def save_frames_as_gif(frames, path, fps=15):
    """frames: list of RGB uint8 arrays (H, W, 3)"""
    ensure_dir(os.path.dirname(path) or ".")
    try:
        import imageio
        imageio.mimsave(path, frames, fps=fps, loop=0)
        return True
    except Exception as e:
        print(f"  imageio failed: {e}")
        return False


def save_frame_sequence(frames, directory, prefix="frame"):
    """Fallback: save individual frames as PNG files."""
    ensure_dir(directory)
    from PIL import Image
    for i, frame in enumerate(frames):
        img = Image.fromarray(frame)
        img.save(os.path.join(directory, f"{prefix}_{i:04d}.png"))
    print(f"  Saved {len(frames)} frames to {directory}/")


def save_sweep_csv(results, param_keys, metric_keys, path):
    """Save a 2D parameter sweep to a flat CSV file.

    results:     dict returned by a sweep function
    param_keys:  list of two keys that hold the 1D parameter arrays,
                 e.g. ["noise_values", "chirality_values"]
    metric_keys: list of keys for the 2D metric grids to include
    path:        output .csv path

    The output has one row per grid point.
    """
    ensure_dir(os.path.dirname(path) or ".")
    p1_vals = np.asarray(results[param_keys[0]])
    p2_vals = np.asarray(results[param_keys[1]])

    header = [param_keys[0].rstrip("_values"), param_keys[1].rstrip("_values")]
    header += metric_keys

    rows = []
    for i, v1 in enumerate(p1_vals):
        for j, v2 in enumerate(p2_vals):
            row = [v1, v2]
            for mk in metric_keys:
                row.append(float(results[mk][i, j]))
            rows.append(row)

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    print(f"  CSV: {path}  ({len(rows)} rows)")


def save_sanity_report(results_dict, path):
    """Write a plain-text sanity check: min/max/finite for each metric array.

    results_dict: dict of {label: np.ndarray}
    """
    ensure_dir(os.path.dirname(path) or ".")
    lines = ["Chirality Atlas -- Sanity Check Report", "=" * 45, ""]
    all_ok = True
    for label, arr in results_dict.items():
        arr = np.asarray(arr, dtype=float)
        has_nan = bool(np.any(np.isnan(arr)))
        has_inf = bool(np.any(np.isinf(arr)))
        status = "OK" if not has_nan and not has_inf else "FAIL"
        if status == "FAIL":
            all_ok = False
        lines.append(
            f"{status:4s}  {label:<45s}  "
            f"min={arr.min():.4f}  max={arr.max():.4f}  "
            f"nan={has_nan}  inf={has_inf}"
        )
    lines.append("")
    lines.append("OVERALL: " + ("PASS" if all_ok else "FAIL"))

    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"  Sanity report: {path}  ({'PASS' if all_ok else 'FAIL'})")
    return all_ok
