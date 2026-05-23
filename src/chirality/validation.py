"""
Sanity checks: verify simulation outputs are finite and in expected ranges.
"""
import numpy as np


def check_finite(arr, name="array"):
    if not np.all(np.isfinite(arr)):
        n_bad = np.sum(~np.isfinite(arr))
        raise ValueError(f"{name} has {n_bad} non-finite values (NaN or Inf)")


def check_range(arr, lo, hi, name="array"):
    if np.any(arr < lo) or np.any(arr > hi):
        raise ValueError(
            f"{name} out of range [{lo}, {hi}]: "
            f"min={arr.min():.4f}, max={arr.max():.4f}"
        )


def check_positions(positions, L, name="positions"):
    check_finite(positions, name)
    check_range(positions, 0.0, L, name)


def check_thetas(thetas, name="thetas"):
    check_finite(thetas, name)


def check_field(field, name="field", lo=0.0, hi=1.0):
    check_finite(field, name)
    if lo is not None and hi is not None:
        check_range(field, lo, hi, name)


def check_metric(value, name="metric"):
    if not np.isfinite(value):
        raise ValueError(f"Metric {name} is not finite: {value}")
    return float(value)


def assert_shape(arr, expected_shape, name="array"):
    if arr.shape != expected_shape:
        raise ValueError(
            f"{name} has shape {arr.shape}, expected {expected_shape}"
        )


def all_finite_report(arrays_dict):
    """Return (passed, messages) for a dict of named arrays."""
    messages = []
    passed = True
    for name, arr in arrays_dict.items():
        arr = np.asarray(arr)
        if not np.all(np.isfinite(arr)):
            n_bad = np.sum(~np.isfinite(arr))
            messages.append(f"FAIL: {name} has {n_bad} non-finite values")
            passed = False
        else:
            messages.append(f"PASS: {name} all finite ({arr.shape})")
    return passed, messages
