"""
Biological target specification for the star ascidian model.

Target organism: Botryllus schlosseri (star ascidian).

This module defines the visual and quantitative features we are trying to
reproduce. It does NOT contain organism-specific developmental biology.
All descriptions are observational, not mechanistic.
"""


TARGET_NAME = "Star ascidian / Botryllus schlosseri"

TARGET_VISUAL_FEATURES = {
    "repeated_star_systems": "Multiple star-shaped colony units tile the substrate surface",
    "radial_zooid_arrangement": "Zooids arranged radially around a shared central opening",
    "shared_central_opening": "Each star system shares a common atrium at the center",
    "colony_level_spacing": "Stars maintain characteristic spacing; neighboring stars do not merge",
    "arm_count_range": "Approximately 5-10 zooid-containing arms per star system",
    "arm_regularity": "Arms are roughly equally spaced angularly around each center",
    "radial_extent": "Each arm extends a characteristic distance from the center",
}

TARGET_QUANTITATIVE = {
    "n_arms_target": 7,
    "n_arms_range": (4, 10),
    "radial_order_target": 0.7,
    "angular_uniformity_target": 0.8,
    "star_likeness_target": 0.65,
}

MODEL_CAVEAT = (
    "This is a toy generative model, not an organism-specific developmental model. "
    "It reproduces the spatial geometry of star ascidian colonies using simple local rules "
    "(activator-inhibitor field + active agent dynamics) without reference to Botryllus "
    "biochemistry, blastogenic cycles, or colonial immune recognition."
)

LIMITATIONS = [
    "No actual Botryllus signaling molecules or developmental stages",
    "No hydrodynamic interactions between zooids",
    "No 3D substrate mechanics or tissue stiffness",
    "No colonial immune recognition (self/non-self discrimination)",
    "Quantitative parameter values are not derived from organism-specific measurements",
    "Arm count target (7) is approximate and varies in real colonies",
    "The model cannot distinguish genetically identical from non-identical colonies",
]


def get_target_feature_checklist():
    """Return a list of (feature_name, description, measurable_metric) tuples.

    Used in compare.py to compare simulation output to target features.
    """
    return [
        ("Repeated star centers",
         "Multiple colony centers spread across domain",
         "n_centers (from GM field)"),
        ("Correct center spacing",
         "Centers do not merge; spacing > 2 * r_target",
         "center_spacing_mean"),
        ("Radial arm structure",
         "Agents cluster at target radius from each center",
         "radial_order_score"),
        ("Discrete arms",
         "Angular histogram shows distinct peaks",
         "arm_count (per center)"),
        ("Arm regularity",
         "Arms approximately equally spaced in angle",
         "angular_uniformity_score"),
        ("Star-like overall shape",
         "Composite score capturing all star geometry requirements",
         "star_likeness_score"),
        ("Chirality sensitivity",
         "Nonzero omega produces measurable swirl vs. omega=0 baseline",
         "swirl_score"),
    ]
