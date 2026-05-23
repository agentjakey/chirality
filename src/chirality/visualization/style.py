"""
Design constants for Chirality Atlas visualizations.

Palette: scientific field notebook aesthetic.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap

BG = "#F7F3EA"
INK = "#1F2421"
ACCENT = "#C15A3A"
GREEN = "#315C4C"
NEUTRAL = "#666666"
PANEL_BG = "#FFFFFF"
BORDER = "#DDD5C8"

FIELD_CMAP = "YlOrBr"
PHASE_CMAP = "viridis"

# Biological colors for zooid agents (blue-gray, matching reference image)
ZOOID_BLUE = "#4A7BA8"
ZOOID_BLUE_DARK = "#2E5F8A"
ZOOID_BLUE_LIGHT = "#7AA8C8"
ZOOID_TEAL = "#3D7A82"
ZOOID_SLATE = "#5A7A9A"
ZOOID_PERIWINKLE = "#6B7FB8"
ZOOID_INDIGO = "#4A5E9A"

# Biological agent palette (blue-gray tones for zooid bodies)
ZOOID_PALETTE = [
    ZOOID_BLUE,
    ZOOID_TEAL,
    ZOOID_BLUE_DARK,
    ZOOID_PERIWINKLE,
    ZOOID_SLATE,
    ZOOID_INDIGO,
    ZOOID_BLUE_LIGHT,
]

CHIRALITY_CMAP = LinearSegmentedColormap.from_list(
    "chirality",
    [ACCENT, NEUTRAL, GREEN],
)

TITLE_FS = 13
LABEL_FS = 11
TICK_FS = 9


def apply_notebook_style():
    """Apply the project-wide matplotlib rcParams for consistent figures."""
    mpl.rcParams.update({
        "figure.facecolor": BG,
        "axes.facecolor": PANEL_BG,
        "axes.edgecolor": BORDER,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "text.color": INK,
        "font.family": "serif",
        "font.serif": ["Georgia", "DejaVu Serif", "Times New Roman"],
        "axes.titlesize": TITLE_FS,
        "axes.labelsize": LABEL_FS,
        "xtick.labelsize": TICK_FS,
        "ytick.labelsize": TICK_FS,
        "figure.dpi": 100,
    })
