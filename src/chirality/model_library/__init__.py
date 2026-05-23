"""
Shared data structures and utilities for the model library.
"""

import os
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class FieldResult:
    u_final: np.ndarray
    v_final: Optional[np.ndarray]
    snapshots_u: np.ndarray
    snapshots_v: Optional[np.ndarray]
    times: np.ndarray
    params: Dict[str, Any]
    shape: tuple

    @property
    def n_snapshots(self):
        return len(self.times)


@dataclass
class ParticleResult:
    positions: np.ndarray
    thetas: np.ndarray
    omegas: np.ndarray
    times: np.ndarray
    L: float
    N: int
    params: Dict[str, Any]

    @property
    def n_snapshots(self):
        return len(self.times)


def laplacian_2d_periodic(f, dx):
    return (
        np.roll(f, 1, axis=0) + np.roll(f, -1, axis=0)
        + np.roll(f, 1, axis=1) + np.roll(f, -1, axis=1)
        - 4.0 * f
    ) / (dx * dx)


def check_finite(arr, name="array"):
    if not np.all(np.isfinite(arr)):
        n_bad = np.sum(~np.isfinite(arr))
        raise ValueError(f"{name}: {n_bad} non-finite values found")


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


__all__ = [
    "FieldResult",
    "ParticleResult",
    "laplacian_2d_periodic",
    "check_finite",
    "ensure_dir",
]
