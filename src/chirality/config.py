"""
Default parameter dataclasses for all simulations.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ABPConfig:
    N: int = 200
    L: float = 10.0
    v0: float = 0.5
    Dr: float = 0.5
    dt: float = 0.01
    n_steps: int = 500
    seed: int = 42
    boundary_mode: str = "periodic"
    save_every: int = 10


@dataclass
class ChiralABPConfig:
    N: int = 200
    L: float = 10.0
    v0: float = 0.5
    Dr: float = 0.5
    omega: float = 1.0
    chirality_mode: str = "right"
    dt: float = 0.01
    n_steps: int = 500
    seed: int = 42
    boundary_mode: str = "periodic"
    repulsion: bool = False
    repulsion_strength: float = 2.0
    repulsion_range: float = 0.3
    save_every: int = 10


@dataclass
class VicsekConfig:
    N: int = 200
    L: float = 10.0
    v0: float = 0.5
    R: float = 1.0
    eta: float = 0.2
    omega: float = 0.0
    dt: float = 0.1
    n_steps: int = 500
    seed: int = 42
    boundary_mode: str = "periodic"
    save_every: int = 10


@dataclass
class GrayScottConfig:
    nx: int = 256
    ny: int = 256
    Du: float = 0.16
    Dv: float = 0.08
    F: float = 0.035
    k: float = 0.065
    dt: float = 1.0
    n_steps: int = 5000
    seed: int = 42
    save_every: int = 500


@dataclass
class FeedGradientConfig(GrayScottConfig):
    F_left: float = 0.02
    F_right: float = 0.06


@dataclass
class ObstacleConfig(GrayScottConfig):
    obstacle_cx: float = 0.5
    obstacle_cy: float = 0.5
    obstacle_r: float = 0.15


@dataclass
class ChiralSourceConfig(GrayScottConfig):
    source_strength: float = 0.02
    source_omega: float = 0.05
    source_r_orbit: float = 0.2
    source_sigma: float = 0.05
