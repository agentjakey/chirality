"""
Chirality Atlas: Star Ascidian Edition
Interactive demo app.

Run from repo root:
    streamlit run app.py
"""
import sys
import os
import io
import warnings

warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Chirality Atlas: Star Ascidian",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ── CSS + assets ───────────────────────────────────────────────────────────────

def _load_css():
    p = os.path.join("assets", "style.css")
    if os.path.exists(p):
        with open(p) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def _load_svg(path):
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return ""


_load_css()
_LOGO_SVG = _load_svg(os.path.join("assets", "logo.svg"))


# ── Helpers ────────────────────────────────────────────────────────────────────

def _fig_bytes(fig, dpi=120):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    return buf.getvalue()


def _show_image_safe(path, caption=None, width=None):
    """Show a pregenerated image or a placeholder if missing."""
    if os.path.exists(path):
        kwargs = {"use_container_width": width is None}
        if width:
            kwargs = {"width": width}
        st.image(path, caption=caption, **kwargs)
        return True
    st.markdown(
        f"<div class='limit-box'>Image not found: <code>{path}</code><br>"
        "Run <code>python scripts/05_make_all_assets.py</code> to generate it.</div>",
        unsafe_allow_html=True,
    )
    return False


def _show_gif_safe(path, caption=None):
    """Show a GIF or placeholder."""
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
        st.image(data, caption=caption, use_container_width=True)
        return True
    st.markdown(
        f"<div class='limit-box'>GIF not found: <code>{path}</code><br>"
        "Run <code>python scripts/04_make_movies.py</code></div>",
        unsafe_allow_html=True,
    )
    return False


def _notice(text):
    st.markdown(
        f"<div class='notice-box'><strong>What to notice:</strong> {text}</div>",
        unsafe_allow_html=True,
    )


def _limit(text):
    st.markdown(
        f"<div class='limit-box'><strong>Limitation:</strong> {text}</div>",
        unsafe_allow_html=True,
    )


def _metric_row(pairs):
    """pairs: list of (label, value, help) tuples. Renders st.metric in columns."""
    cols = st.columns(len(pairs))
    for col, (label, value, help_text) in zip(cols, pairs):
        col.metric(label, value, help=help_text)


# ── Cached model runs ─────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False, max_entries=6)
def _cached_colony(
    seed, preset,
    n_arms, n_per_arm, omega, Dr, k_radial, k_angular,
    grid_size, Dh, n_field_steps, n_agent_steps, boundary,
):
    from chirality.star_ascidian.hybrid_model import simulate_star_ascidian_colony
    return simulate_star_ascidian_colony(
        preset=preset, seed=seed,
        n_snapshots=10,
        n_arms=n_arms, n_per_arm=n_per_arm, omega=float(omega),
        Dr=float(Dr), k_radial=float(k_radial), k_angular=float(k_angular),
        grid_size=int(grid_size), Dh=float(Dh),
        n_field_steps=int(n_field_steps), n_steps=int(n_agent_steps),
        boundary=boundary,
        mode="chiral_twist" if omega > 0 else "radial_clean",
    )


@st.cache_data(show_spinner=False, max_entries=3)
def _cached_sweep_A(seed=42):
    from chirality.star_ascidian.phase_diagram import sweep_attraction_vs_chirality
    kv = np.array([0.5, 1.0, 2.0, 3.5, 5.0])
    ov = np.array([0.0, 0.5, 1.5, 3.0, 5.0])
    return sweep_attraction_vs_chirality(k_radial_vals=kv, omega_vals=ov, seed=seed)


@st.cache_data(show_spinner=False, max_entries=3)
def _cached_sweep_B(seed=42):
    from chirality.star_ascidian.phase_diagram import sweep_noise_vs_repulsion
    dv = np.array([0.01, 0.1, 0.3, 0.7, 1.5])
    kav = np.array([0.1, 0.3, 0.6, 1.0, 1.5])
    return sweep_noise_vs_repulsion(Dr_vals=dv, k_angular_vals=kav, seed=seed)


@st.cache_data(show_spinner=False, max_entries=3)
def _cached_sweep_C(seed=42):
    from chirality.star_ascidian.phase_diagram import sweep_inhibition_ratio
    dhv = np.array([0.5, 1.0, 2.0, 5.0, 10.0])
    mhv = np.array([0.02, 0.05, 0.10, 0.20, 0.40])
    return sweep_inhibition_ratio(Dh_vals=dhv, mu_h_vals=mhv, seed=seed)


# ── Header ─────────────────────────────────────────────────────────────────────

def _render_header():
    c1, c2 = st.columns([1, 14])
    with c1:
        if _LOGO_SVG:
            st.markdown(_LOGO_SVG, unsafe_allow_html=True)
    with c2:
        st.markdown(
            "<p class='app-title'>Chirality Atlas: Star Ascidian Edition</p>"
            "<p class='app-subtitle'>Can local rules generate a living star pattern?</p>",
            unsafe_allow_html=True,
        )
    st.markdown("<hr style='margin:0.4rem 0 0.8rem 0;border-color:#DDD5C8'/>",
                unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — TARGET PATTERN
# ─────────────────────────────────────────────────────────────────────────────

def _tab_target():
    st.markdown("## Biological Target: *Botryllus schlosseri*")
    st.markdown(
        "*Botryllus schlosseri* is a colonial tunicate (sea squirt) that tiles "
        "hard substrates as a mat of star-shaped systems. Each star consists of "
        "5–10 zooids (individual filter-feeding animals) arranged radially around "
        "a shared central atrium. Neighboring stars maintain characteristic spacing "
        "and do not merge under normal conditions. Some genetic variants exhibit "
        "consistent rotational handedness — a biological chirality signature."
    )

    col_img, col_info = st.columns([1, 1], gap="large")

    with col_img:
        ref_path = os.path.join("assets", "reference", "star_ascidian_reference.jpg")
        if os.path.exists(ref_path):
            st.image(ref_path, caption="Botryllus schlosseri colony (reference)",
                     use_container_width=True)
        else:
            _show_image_safe(
                os.path.join("outputs", "star_ascidian", "simulation_vs_target_features.png"),
                caption="Simulation vs target features (pregenerated). "
                        "Add assets/reference/star_ascidian_reference.jpg for the real organism.",
            )

    with col_info:
        st.markdown("### Target Features")

        features = [
            ("Multiple star centers", "Repeated tiling of the substrate",
             "n_centers from GM field", True),
            ("Radial zooid arrangement", "Zooids at target radius from center",
             "radial_order_score > 0.7", True),
            ("Discrete arm lobes", "5-10 angular peaks per star",
             "arm_count from angular histogram", True),
            ("Even arm spacing", "Arms equally distributed in angle",
             "angular_uniformity_score > 0.8", True),
            ("Star non-merging", "Neighboring stars stay separate",
             "merge_score < 0.1", True),
            ("Chirality sensitivity", "Omega > 0 produces measurable swirl",
             "swirl_score != 0", True),
            ("Colony-level tiling", "Stars tile the surface without gaps",
             "center_spacing_cv < 0.3", False),
        ]

        for name, desc, metric, implemented in features:
            icon = "+" if implemented else "-"
            color = "#315C4C" if implemented else "#888"
            st.markdown(
                f"<div style='margin:0.35rem 0; padding:0.4rem 0.7rem; "
                f"border-left:3px solid {color}; background:#FAFAF7; font-size:0.88rem'>"
                f"<span style='color:{color};font-weight:700'>{icon}</span> "
                f"<strong>{name}</strong>: {desc} "
                f"<span style='color:#888;font-size:0.82rem'>({metric})</span></div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown("### Model Hypothesis")
    st.info(
        "A two-layer generative model — an activator-inhibitor (Gierer-Meinhardt) "
        "field for center placement, and active zooid-like particles for arm formation "
        "— can reproduce the spatial geometry of Botryllus star colonies using only "
        "local interaction rules, without reference to organism-specific biochemistry."
    )

    _notice(
        "The radial arm structure and colony-level spacing are captured well. "
        "Arm count detection (via angular histogram peaks) is sensitive to agent "
        "density and can undercount at low agents-per-arm. The model does not "
        "reproduce blastogenic cycling, colonial immune recognition, or 3D substrate "
        "mechanics."
    )

    with st.expander("Limitations (expand)"):
        st.markdown("""
- **Not organism-specific.** No Botryllus signaling molecules, no developmental staging.
- **Arm count metric** uses `find_peaks` on angular histograms; underestimates at
  low agent density (< 5 per arm).
- **2D only.** No substrate curvature, no hydrodynamic coupling between zooids.
- **Parameter values** are not derived from organism measurements; they produce
  visually plausible patterns but cannot be compared to biological rates.
- **Colonial immune recognition** (self/non-self fusions) is not modeled.
        """)

    st.markdown("---")
    st.markdown("### What the Simulation Produces")
    _show_image_safe(
        os.path.join("outputs", "panels", "slide1_target_and_simulation.png"),
        caption="Left: target morphology schematic. Center: GM activator field. "
                "Right: zooid agent final state.",
    )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — MODEL BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def _tab_model_builder():
    st.markdown("## Model Builder")
    st.markdown(
        "Configure both layers and run a full colony simulation. "
        "Computationally expensive settings are capped for app safety."
    )

    st.markdown("### Layer 1 — Activator-Inhibitor Field (Gierer-Meinhardt)")
    c1, c2, c3 = st.columns(3)
    with c1:
        grid_size = st.select_slider(
            "Grid size (N x N)", options=[16, 32, 64],
            value=32, help="Larger = more centers possible, slower",
        )
        n_field_steps = st.slider(
            "Field simulation steps", 500, 2000, 1200, step=250,
            help="More steps = better-equilibrated spots",
        )
    with c2:
        Dh = st.slider(
            "Dh (inhibitor diffusion)", 0.5, 15.0, 5.0, step=0.5,
            help="Higher Dh/Da = more Turing spots = more star centers",
        )
        mu_h = st.slider(
            "mu_h (inhibitor decay)", 0.01, 0.40, 0.05, step=0.01,
            help="Higher mu_h = inhibitor decays faster = fewer, denser spots",
        )
    with c3:
        min_distance = st.slider(
            "Min center separation", 1.0, 4.0, 2.0, step=0.25,
            help="Minimum physical distance between star centers",
        )

    st.markdown("### Layer 2 — Zooid Agents")
    c4, c5, c6 = st.columns(3)
    with c4:
        n_arms = st.slider("Target arms per star", 3, 10, 7,
                           help="Sets arm initialization and angular repulsion spacing")
        n_per_arm = st.slider("Agents per arm", 1, 6, 3,
                              help="Total agents per center = n_arms x n_per_arm")
        omega = st.slider(
            "omega (chirality rate)", 0.0, 5.0, 0.0, step=0.25,
            help="0 = no twist. Positive = CCW arm rotation.",
        )
    with c5:
        Dr = st.slider("Dr (rotational noise)", 0.01, 1.5, 0.04, step=0.01,
                       help="Higher Dr = noisier arm structure")
        k_radial = st.slider("k_radial (arm tightness)", 0.5, 5.0, 2.0, step=0.25,
                             help="Radial spring toward r_target")
        k_angular = st.slider("k_angular (arm separation)", 0.1, 2.0, 0.6, step=0.1,
                              help="Repulsion between adjacent arms")
    with c6:
        n_agent_steps = st.slider(
            "Agent simulation steps", 100, 600, 300, step=50,
            help="More steps = better-formed arms, slower",
        )
        boundary = st.selectbox("Boundary condition", ["periodic", "box"],
                                help="Periodic = torus. Box = hard walls.")
        seed = st.number_input("Random seed", min_value=0, max_value=9999,
                               value=42, step=1)

    # Safety cap warning
    if grid_size == 64 and n_field_steps > 1500:
        st.warning(
            "N=64 with >1500 field steps can take 30-60 seconds. "
            "Consider N=32 for quick exploration."
        )

    run_col, _ = st.columns([2, 8])
    with run_col:
        run_clicked = st.button("Run Simulation", type="primary", key="run_model_builder")

    if run_clicked or ("mb_result" in st.session_state):
        if run_clicked:
            with st.spinner("Running simulation..."):
                try:
                    result = _cached_colony(
                        seed=int(seed), preset="clean_star_systems",
                        n_arms=int(n_arms), n_per_arm=int(n_per_arm),
                        omega=float(omega), Dr=float(Dr),
                        k_radial=float(k_radial), k_angular=float(k_angular),
                        grid_size=int(grid_size), Dh=float(Dh),
                        n_field_steps=int(n_field_steps),
                        n_agent_steps=int(n_agent_steps),
                        boundary=boundary,
                    )
                    st.session_state["mb_result"] = result
                except Exception as e:
                    st.error(f"Simulation failed: {e}")
                    return

        result = st.session_state.get("mb_result")
        if result is None:
            return

        st.markdown("---")
        st.markdown("### Simulation Result")

        m = result.metrics
        _metric_row([
            ("Star-likeness", f"{m['star_likeness_score']:.3f}",
             "Composite score in [0,1]. >0.6 = good stars."),
            ("Radial order", f"{m['radial_order']:.3f}",
             "Fraction of agents near r_target. 1.0 = perfect ring."),
            ("Arm count (mean)", f"{m['arm_count_mean']:.1f}",
             f"Detected angular peaks vs target {n_arms}"),
            ("Swirl score", f"{m['swirl_score']:.3f}",
             "Net tangential velocity. 0 = radial, nonzero = chiral."),
            ("Fragmentation", f"{m['fragmentation']:.3f}",
             "Fraction of escaped agents. <0.1 = well-contained."),
        ])

        ic1, ic2 = st.columns(2, gap="medium")
        with ic1:
            fig, ax = plt.subplots(figsize=(5, 5), facecolor="#F7F3EA")
            ax.set_facecolor("#FFFFFF")
            ax.imshow(result.field, origin="lower",
                      extent=[0, result.params["L"], 0, result.params["L"]],
                      cmap="YlOrBr", interpolation="nearest")
            ax.scatter(result.centers[:, 0], result.centers[:, 1],
                       s=40, color="#1F2421", marker="+", linewidths=1.5, zorder=4)
            ax.set_title(
                f"GM activator field  (K={result.zooid.K} centers)",
                fontsize=11, color="#1F2421",
            )
            ax.set_xlabel("x", fontsize=9, color="#1F2421")
            ax.set_ylabel("y", fontsize=9, color="#1F2421")
            ax.tick_params(colors="#1F2421", labelsize=8)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        with ic2:
            palette = ["#C15A3A", "#315C4C", "#7B6B8B", "#8B7355",
                       "#4A7B8B", "#8B4A6B", "#6B8B4A"]
            fig, ax = plt.subplots(figsize=(5, 5), facecolor="#F7F3EA")
            ax.set_facecolor("#F7F3EA")
            pos = result.zooid.positions[-1]
            K = result.zooid.K
            L = result.params["L"]
            for k in range(K):
                mask = result.zooid.assignments == k
                ax.scatter(pos[mask, 0], pos[mask, 1], s=10,
                           color=palette[k % len(palette)], alpha=0.80,
                           linewidths=0, zorder=2)
            ax.scatter(result.centers[:, 0], result.centers[:, 1],
                       s=45, color="#1F2421", marker="+", linewidths=1.5, zorder=4)
            ax.set_xlim(0, L)
            ax.set_ylim(0, L)
            ax.set_title(
                f"Zooid agents  (N={result.zooid.N}, omega={omega:.1f})",
                fontsize=11, color="#1F2421",
            )
            ax.set_xlabel("x", fontsize=9, color="#1F2421")
            ax.set_ylabel("y", fontsize=9, color="#1F2421")
            ax.tick_params(colors="#1F2421", labelsize=8)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        with st.expander("Detailed diagnostic report"):
            matches = m.get("matches", [])
            failures = m.get("failures", [])
            suggestion = m.get("suggested_fix", "")
            if matches:
                st.markdown("**Matches target:**")
                for t in matches:
                    st.markdown(f"  + {t}")
            if failures:
                st.markdown("**Does not match:**")
                for t in failures:
                    st.markdown(f"  - {t}")
            if suggestion and suggestion != "Parameters look good":
                st.info(f"Suggestion: {suggestion}")

        _notice(
            "Radial order near 1.0 means agents are well-confined at r_target. "
            "Arm count below target usually means angular repulsion needs to be "
            "stronger (increase k_angular) or noise lower (decrease Dr). "
            "Nonzero swirl_score confirms chirality is active."
        )

    else:
        st.markdown("---")
        st.markdown("### Default output (clean_star_systems preset)")
        _show_image_safe(
            os.path.join("outputs", "star_ascidian", "clean_star_systems.png"),
            caption="Pregenerated: clean_star_systems. Adjust parameters above and run.",
        )
        _show_image_safe(
            os.path.join("outputs", "panels", "slide2_model_schematic.png"),
            caption="Two-layer model architecture.",
        )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — LIVE PHASE EXPLORER
# ─────────────────────────────────────────────────────────────────────────────

def _tab_phase_explorer():
    st.markdown("## Live Phase Explorer")
    st.markdown(
        "Explore how parameters control colony morphology. "
        "Load pregenerated heatmaps instantly, or run a live sweep on a 5x5 grid."
    )

    sweep_name = st.selectbox(
        "Choose sweep",
        options=[
            "A — Radial attraction vs chirality (star-likeness)",
            "B — Noise vs angular repulsion (fragmentation)",
            "C — Inhibition ratio vs center spacing quality",
        ],
        key="phase_sweep_select",
    )

    run_mode = st.radio(
        "Mode", ["Load pregenerated (fast)", "Run live 5x5 sweep (~30 sec)"],
        horizontal=True, key="phase_run_mode",
    )

    pregenerated_paths = {
        "A — Radial attraction vs chirality (star-likeness)":
            os.path.join("outputs", "phase_diagrams",
                         "star_likeness_attraction_vs_chirality.png"),
        "B — Noise vs angular repulsion (fragmentation)":
            os.path.join("outputs", "phase_diagrams",
                         "fragmentation_noise_vs_repulsion.png"),
        "C — Inhibition ratio vs center spacing quality":
            os.path.join("outputs", "phase_diagrams",
                         "center_spacing_inhibition_ratio.png"),
    }

    interpretations = {
        "A — Radial attraction vs chirality (star-likeness)": (
            "**Reading this plot:** horizontal axis = radial spring strength (k_radial); "
            "vertical = chirality rate (omega). Bright = high star-likeness score. "
            "The hotspot at moderate k_radial, low omega is the 'clean star' regime. "
            "At high omega, the angular momentum overcomes the radial spring and arms blur."
        ),
        "B — Noise vs angular repulsion (fragmentation)": (
            "**Reading this plot:** horizontal = noise (Dr); vertical = angular repulsion "
            "strength (k_angular). Green = low fragmentation (agents stay in stars); "
            "Red = high fragmentation (agents escape). Higher k_angular shifts the "
            "fragmentation boundary toward higher noise — angular repulsion stabilizes arms."
        ),
        "C — Inhibition ratio vs center spacing quality": (
            "**Reading this plot:** horizontal = Dh/Da ratio; vertical = inhibitor decay "
            "mu_h. Bright = regular, well-spaced centers. High Dh/Da gives the "
            "short-range activation / long-range inhibition condition needed for "
            "Turing spots. High mu_h collapses or eliminates spots."
        ),
    }

    if run_mode == "Load pregenerated (fast)":
        _show_image_safe(
            pregenerated_paths[sweep_name],
            caption=f"Pregenerated: {sweep_name.split(' — ')[1]}",
        )
        _show_image_safe(
            os.path.join("outputs", "panels", "slide4_phase_diagram.png"),
            caption="Side-by-side star-likeness and swirl for sweep A.",
        )

    else:
        live_clicked = st.button("Run live sweep", key="phase_live_run")

        if live_clicked or f"phase_result_{sweep_name[0]}" in st.session_state:
            if live_clicked:
                with st.spinner("Running 5x5 sweep (25 simulations)..."):
                    try:
                        if sweep_name.startswith("A"):
                            result = _cached_sweep_A(seed=42)
                            st.session_state["phase_result_A"] = result
                        elif sweep_name.startswith("B"):
                            result = _cached_sweep_B(seed=42)
                            st.session_state["phase_result_B"] = result
                        else:
                            result = _cached_sweep_C(seed=42)
                            st.session_state["phase_result_C"] = result
                    except Exception as e:
                        st.error(f"Sweep failed: {e}")
                        return

            key = f"phase_result_{sweep_name[0]}"
            cached = st.session_state.get(key)
            if cached is not None:
                x_vals, y_vals, grids = cached

                metric_key = list(grids.keys())[0]
                grid = grids[metric_key]

                from chirality.visualization.style import BG, INK, BORDER
                fig, ax = plt.subplots(figsize=(6, 5), facecolor=BG)
                ax.set_facecolor("#FFFFFF")
                im = ax.pcolormesh(x_vals, y_vals, grid, cmap="YlOrBr",
                                   vmin=0, vmax=1, shading="nearest")
                fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04).ax.tick_params(
                    labelsize=8, colors=INK)
                ax.set_title(f"{sweep_name.split(' — ')[1]}  [{metric_key}]",
                             fontsize=11, color=INK)
                ax.set_xlabel(
                    "k_radial" if sweep_name.startswith("A") else
                    "Dr" if sweep_name.startswith("B") else "Dh/Da",
                    fontsize=10, color=INK,
                )
                ax.set_ylabel(
                    "omega" if sweep_name.startswith("A") else
                    "k_angular" if sweep_name.startswith("B") else "mu_h",
                    fontsize=10, color=INK,
                )
                ax.tick_params(colors=INK, labelsize=8)
                for sp in ax.spines.values():
                    sp.set_edgecolor(BORDER)
                fig.tight_layout()
                st.pyplot(fig, use_container_width=False)
                plt.close(fig)

    st.markdown("---")
    st.markdown(interpretations[sweep_name])

    _notice(
        "Each cell in the heatmap is one simulation run at fixed parameters. "
        "The 5x5 grid uses 150 agent steps and 1500 field steps for speed; "
        "production presets use 400+ steps. Phase boundaries shift slightly at "
        "higher resolution."
    )

    _limit(
        "Short sweep runs (n_steps=150) may not reach steady state. "
        "Treat boundary positions as qualitative, not quantitative."
    )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — MOVIE GALLERY
# ─────────────────────────────────────────────────────────────────────────────

def _tab_movie_gallery():
    st.markdown("## Movie Gallery")
    st.markdown(
        "These animations show the system evolving from initialization to steady state. "
        "Each frame is one simulation snapshot."
    )

    movies = [
        (
            os.path.join("outputs", "movies", "star_formation_clean.gif"),
            "Clean star formation (omega = 0)",
            "Watch the arms self-organize. At t=0 agents are in initial arm groups "
            "with small random offsets. By the final frame they have settled into "
            "radial lobes at r_target. Radial spring drives them outward; "
            "angular repulsion pushes arms apart.",
        ),
        (
            os.path.join("outputs", "movies", "chiral_twist_emergence.gif"),
            "Chiral twist emergence (omega = 2.5)",
            "Same initialization, but with a nonzero rotation rate (omega). "
            "The arms slowly rotate CCW over time. Compare the final arm angles "
            "to the clean case — they are rotated by omega * t. "
            "This is the model's analog of biological chirality.",
        ),
        (
            os.path.join("outputs", "movies", "phase_transition_parameter_sweep.gif"),
            "Phase transition: omega 0 to 5",
            "Each frame shows a different omega value. At omega=0 the pattern "
            "is radial and static. As omega increases, arms begin to smear and "
            "eventually lose coherence at omega=5. The transition is gradual — "
            "there is no sharp phase boundary at this agent density.",
        ),
        (
            os.path.join("outputs", "movies", "active_zooid_dynamics.gif"),
            "Single-center zoom: active zooid dynamics",
            "Zoomed into one star center. Individual agents jitter due to "
            "rotational noise (Dr=0.04). The radial spring prevents them from "
            "escaping; angular repulsion maintains arm separation. "
            "Notice that arms are not rigid — they fluctuate around their "
            "equilibrium angles.",
        ),
    ]

    col_a, col_b = st.columns(2, gap="large")
    for i, (path, title, caption) in enumerate(movies):
        col = col_a if i % 2 == 0 else col_b
        with col:
            st.markdown(f"**{title}**")
            _show_gif_safe(path)
            _notice(caption)
            st.markdown("---")

    st.info(
        "GIFs were generated by `scripts/04_make_movies.py` using Pillow. "
        "Each GIF is 16 frames at 6 fps (or 8 frames at 2 fps for the sweep). "
        "If they appear as static images, try opening the GIF file directly."
    )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — MODEL LIBRARY
# ─────────────────────────────────────────────────────────────────────────────

def _tab_model_library():
    st.markdown("## Model Library")
    st.markdown(
        "Six reference models inform the star ascidian simulation. "
        "Each was implemented, tested, and analyzed as part of the project."
    )

    models = [
        {
            "name": "Fisher-KPP",
            "mechanism": (
                "Logistic growth + diffusion. A population front spreads "
                "from an initial seed. The front speed is c = 2 * sqrt(D*r)."
            ),
            "produces": "Invasion fronts; traveling waves; spatial spread.",
            "role": (
                "Establishes the baseline: diffusion alone generates ordered "
                "spatial structure. The front radius metric informed our "
                "r_target design for zooid agent confinement."
            ),
            "image": os.path.join("outputs", "reference", "fisher_kpp_front.png"),
        },
        {
            "name": "Gierer-Meinhardt",
            "mechanism": (
                "Short-range activation, long-range inhibition. "
                "Turing instability when Dh >> Da produces periodic spots. "
                "Spot spacing ~ sqrt(Dh/Da)."
            ),
            "produces": "Quasi-periodic spots; stripes; labyrinths depending on parameters.",
            "role": (
                "Directly used as Layer 1. The activator peaks become star center "
                "positions. The Dh/Da ratio controls how many centers appear, "
                "providing top-down spatial organization without explicit "
                "center-placement rules."
            ),
            "image": os.path.join("outputs", "reference", "gierer_meinhardt_spots.png"),
        },
        {
            "name": "Cahn-Hilliard",
            "mechanism": (
                "Phase separation via spinodal decomposition. "
                "phi_t = M * lap(mu); mu = -A*phi + B*phi^3 - kappa*lap(phi). "
                "Coarsening proceeds as t^{1/3}."
            ),
            "produces": "Phase-separated domains; bicontinuous spinodal patterns; coarsening.",
            "role": (
                "Inspired the spectral semi-implicit numerical scheme used for "
                "GM. The correct IMEX denominator sign (negative A*k2 term) "
                "was derived by analogy with the CH stability analysis."
            ),
            "image": os.path.join("outputs", "reference", "cahn_hilliard_domains.png"),
        },
        {
            "name": "FitzHugh-Nagumo",
            "mechanism": (
                "Excitable activator-inhibitor. Fast u variable, slow v variable. "
                "Spiral waves form in 2D when initialized with spatial gradient "
                "(spiral init)."
            ),
            "produces": "Excitable pulses; spiral waves; target patterns.",
            "role": (
                "Motivated the IMEX approach: FHN also requires implicit diffusion "
                "for stability at N=64. The spiral init design (vs stimulate) "
                "illustrated the importance of initial conditions in periodic domains."
            ),
            "image": os.path.join("outputs", "reference", "fitzhugh_nagumo_spiral.png"),
        },
        {
            "name": "Gray-Scott",
            "mechanism": (
                "Two-component reaction-diffusion. u is substrate, v is product. "
                "u*v^2 autocatalysis with feed F and kill k determines pattern type."
            ),
            "produces": "Spots, labyrinths, traveling waves depending on (F, k) region.",
            "role": (
                "Alternative to GM for center field generation. Used as fallback "
                "when GM fails to produce well-separated spots. Its (F, k) phase "
                "diagram informed the design of the GM parameter sweep structure."
            ),
            "image": os.path.join("outputs", "reference", "gray_scott_pattern.png"),
        },
        {
            "name": "Active Particles",
            "mechanism": (
                "Self-propelled particles (ABP). Orientation diffuses (Dr), "
                "optionally with rotation rate omega (chiral ABP). "
                "Vicsek model adds velocity alignment."
            ),
            "produces": "Polar flocking, chiral vortex clusters, motility-induced phase separation.",
            "role": (
                "Directly used as Layer 2. The omega parameter from chiral ABP "
                "becomes the arm rotation rate. The swirl_score metric is adapted "
                "from the ABP swirl_index. Excluded volume prevents arm collapse."
            ),
            "image": os.path.join("outputs", "reference", "chiral_active_particles.png"),
        },
    ]

    for i in range(0, len(models), 2):
        c1, c2 = st.columns(2, gap="large")
        for col, model in zip([c1, c2], models[i:i + 2]):
            with col:
                with st.expander(f"**{model['name']}**", expanded=(i == 0)):
                    st.markdown(f"**Mechanism:** {model['mechanism']}")
                    st.markdown(f"**Produces:** {model['produces']}")
                    st.markdown(
                        f"<div style='background:#EAF0EC;border-left:3px solid #315C4C;"
                        f"padding:0.4rem 0.7rem;margin:0.4rem 0;font-size:0.87rem'>"
                        f"<strong>Role in project:</strong> {model['role']}</div>",
                        unsafe_allow_html=True,
                    )
                    _show_image_safe(model["image"])

    st.markdown("---")
    _notice(
        "Each model was implemented with a production-quality IMEX numerical scheme "
        "(implicit diffusion in Fourier space). This was the main numerical challenge: "
        "explicit Euler diffusion is unstable when dt > dx^2/(4D). "
        "At N=64 with Dh=5.0 the explicit stability limit is dt < 0.002, "
        "but the IMEX scheme is unconditionally stable for the diffusion term."
    )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 6 — LLM LAB NOTEBOOK
# ─────────────────────────────────────────────────────────────────────────────

def _tab_llm_notebook():
    st.markdown("## LLM Lab Notebook")
    st.markdown(
        "This tab documents how LLM assistance was used in the project — "
        "including the surprising contributions, the human judgment calls, "
        "and the cases where it went wrong."
    )

    st.markdown("### Workflow Overview")
    st.markdown(
        """
The project followed an iterative loop:

1. **Ideation** — human described biological target; LLM proposed candidate model classes
2. **Code generation** — LLM wrote initial implementations of 6 reference models
3. **Debugging** — numerical instability caught by smoke test; LLM diagnosed root cause
4. **Metric design** — LLM proposed anti-cheat metrics when visual inspection was unreliable
5. **Documentation** — LLM wrote docstrings, technical notes, and this app

At every step, the human ran the code, inspected outputs, and made the scientific judgments.
        """
    )

    st.markdown("---")
    st.markdown("### Two Surprising LLM Contributions")

    with st.expander("A: Two-layer architecture (proposed by LLM)", expanded=True):
        st.markdown(
            """
**The problem:** Initial concept was a single-layer model — active particles around
randomly placed centers, with no field-based center placement.

**What LLM proposed:** Separate the model into two layers with different timescales:
a slow reaction-diffusion field to set positional information (colony-level organization),
and a fast local agent dynamics to form arm morphology (zooid-level organization).
The LLM cited the biological analogy: Botryllus development has both a blastogenic
cycle (slow, colony-level) and individual zooid growth (fast, local).

**Why it worked:** The separation of scales is physically principled and matches the
biological reality. The GM field provides quasi-regular center spacing without
requiring explicit distance rules between agents. The agent layer can be fully
local while still producing globally regular patterns.

**Human verification:** Ran both versions. Single-layer version produced irregular
center spacing unless we added an explicit center-repulsion rule (which is ad hoc).
Two-layer version produced regular spacing automatically from the Turing mechanism.
        """
        )

    with st.expander("B: Anti-cheat metrics (designed with LLM)", expanded=True):
        st.markdown(
            """
**The problem:** Early simulations looked like stars in a screenshot but metrics
gave low scores, or looked wrong but metrics gave high scores. Visual inspection
was not enough.

**What LLM proposed:** A hierarchy of metrics designed to catch specific failure modes:

- `radial_order_score`: catches models that produce agents everywhere but not at r_target
- `arm_count_distribution`: uses `find_peaks` on the angular histogram — catches models
  that produce a ring (high radial order) but not discrete arms
- `angular_uniformity_score`: catches models that produce arms but at uneven angles
- `swirl_score`: specifically detects the chiral signature — can't be faked by
  a radially-symmetric pattern
- `fragmentation_score`: catches cases where the pattern looks OK at the center
  but many agents have escaped (high-noise regime)

**Human verification:** Ran the metric suite on a uniform ring initialization
(all agents at r_target, no angular structure). Radial order = 1.0, arm count = 0.
The radial_order check alone would have given a false positive; arm count catches it.
        """
        )

    st.markdown("---")
    st.markdown("### What the Human Decided")

    st.markdown(
        """
**Equations:** The specific GM and agent force equations were human choices
based on standard active matter and RD literature. LLM provided implementations
of equations the human specified; it did not derive them independently.

**Biological scope:** LLM-generated descriptions were often too specific
("models Botryllus blastogenic cycle"). These were corrected to "reproduces the
spatial geometry" — a weaker, defensible claim.

**Parameter values:** All parameter values (Dh/Da=100, n_arms=7, r_target=1.5, etc.)
were tuned by the human inspecting output images. LLM suggested search ranges
but did not determine the values.

**Sanity checks:** Numerical stability analysis (dt < dx^2/(4D) criterion),
compileall verification, and the 53-check smoke test were written by the human
after LLM code passed visual inspection but had subtle instabilities at N=64.

**Limitations section:** All biological caveats (no blastogenic staging, no
immune recognition, no 3D mechanics) were added by the human. LLM tended to
omit these unless explicitly asked.
        """
    )

    st.markdown("---")
    st.markdown("### Failure Gallery")

    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        st.markdown("**Failure 1: Uniform ring — no arms**")
        st.markdown(
            "Initialization with all agents at r_target uniformly in angle, "
            "no arm grouping. Radial order = 1.0, but arm count = 0-1. "
            "Visually looks like a circle, not a star. "
            "Fix: initialize in discrete arm groups."
        )
        _show_image_safe(
            os.path.join("outputs", "star_ascidian", "noisy_fragmented_systems.png"),
            caption="High-noise regime: agents escape arms (fragmentation_score > 0.4)",
        )

    with col_b:
        st.markdown("**Failure 2: GM without Turing instability**")
        st.markdown(
            "With Dh/Da = 3 (below threshold), the GM field converges to a "
            "uniform activator concentration. No centers form. Agents initialize "
            "around the fallback grid center and produce a single-star pattern. "
            "Star-likeness with K=1 is meaningless for colony modeling."
        )
        _show_image_safe(
            os.path.join("outputs", "star_ascidian", "overcrowded_merged_systems.png"),
            caption="Overcrowded: too many agents per arm; stars merge (merge_score > 0.2)",
        )

    st.markdown("---")
    st.markdown("### The Iteration Loop in Practice")

    with st.expander("Show code-level workflow"):
        st.code(
            """
# Iteration 1: explicit Euler diffusion — blew up at N=64
# Symptom: u_final = nan after ~100 steps
# Diagnosis: dt=0.1 >> dt_max=0.002 for Dh=5, N=64
# Fix: IMEX scheme (implicit diffusion in Fourier space)

# denom_a = 1 + dt*(Da*k2 + mu_a)   <-- implicit D and decay
# u_hat = fft2(u + dt*reaction_u) / denom_a

# Iteration 2: Cahn-Hilliard wrong sign — no phase separation
# Symptom: domain_size_proxy = 0 after 2000 steps
# Diagnosis: denom = 1 + dt*M*A*k2 suppresses A*phi (destabilizing term)
# Fix: denom = 1 - dt*M*A*k2 + dt*M*kappa*k2**2

# Iteration 3: FHN wave_activity = 0 — no excitation
# Symptom: spiral init works but stimulate init fails
# Diagnosis: implicit diffusion spreads corner energy over whole periodic domain
#            before threshold is reached; spatial average stays below u_rest
# Fix: use spiral init by default

# Verification at every step:
#   python scripts/06_final_smoke_test.py  (53 checks, all PASS)
#   python -m compileall src scripts
            """,
            language="python",
        )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 7 — PRESENTATION MODE
# ─────────────────────────────────────────────────────────────────────────────

def _tab_presentation():
    st.markdown("## Presentation Mode")
    st.markdown(
        "Everything needed for the 5-minute judging session. "
        "Files are listed with paths relative to repo root."
    )

    st.markdown("### 5-Slide Outline")

    slides = [
        (
            "Slide 1 — Target and Model",
            "outputs/panels/slide1_target_and_simulation.png",
            "1:00",
            (
                "Open with the biological image or schematic. "
                "Point to the star geometry — shared atrium, radial arms, regular spacing. "
                "Say: 'We asked whether local rules alone can generate this pattern. "
                "The answer is yes, with two coupled layers.' "
                "Show the three-panel figure: schematic | GM field | agents."
            ),
        ),
        (
            "Slide 2 — How the Model Works",
            "outputs/panels/slide2_model_schematic.png",
            "0:50",
            (
                "Walk through the architecture diagram. "
                "Layer 1: GM field places the centers — "
                "'Turing instability, short-range activation, long-range inhibition.' "
                "Layer 2: active particles form the arms — "
                "'radial spring, angular repulsion, chirality.' "
                "Point at the key equations. Keep it to two sentences per layer."
            ),
        ),
        (
            "Slide 3 — Dynamics",
            "outputs/panels/slide3_simulation_sequence.png",
            "1:00",
            (
                "Show the time sequence: arms self-organize from initialization. "
                "If the app is running, switch to Movie Gallery and play "
                "'star_formation_clean.gif' and 'chiral_twist_emergence.gif'. "
                "Key point: 'With omega=0 the pattern is radial; "
                "with omega=2.5 the arms rotate — this is the chirality signature.'"
            ),
        ),
        (
            "Slide 4 — Phase Space",
            "outputs/panels/slide4_phase_diagram.png",
            "1:00",
            (
                "Show both heatmaps side by side. "
                "Left: star-likeness peaks at moderate k_radial, low omega. "
                "Right: swirl is zero at omega=0 and rises with chirality. "
                "Key point: 'The two metrics are not correlated — "
                "you can have good arms without chirality, and chirality "
                "without arm degradation (up to omega ~ 2).' "
                "Point to the phase boundary."
            ),
        ),
        (
            "Slide 5 — Honest Assessment",
            "outputs/panels/slide5_insight_and_limits.png",
            "1:10",
            (
                "Green column: what the model matches. "
                "Orange column: what it does not. "
                "Key points: 'Radial geometry: yes. Arm count: approximately. "
                "Blastogenic biology: no.' "
                "End with: 'The value of this model is not biological accuracy — "
                "it is demonstrating that spatial geometry can emerge from "
                "two coupled local rules without global coordination.'"
            ),
        ),
    ]

    for title, path, duration, script in slides:
        with st.expander(f"{title}  ({duration})", expanded=False):
            icol, scol = st.columns([1, 1], gap="large")
            with icol:
                _show_image_safe(path)
            with scol:
                st.markdown(f"**File:** `{path}`")
                st.markdown(f"**Duration:** {duration}")
                st.markdown("**Speaker notes:**")
                st.markdown(script)

    st.markdown("---")
    st.markdown("### Closing Slide")
    _show_image_safe(
        "outputs/panels/final_summary_panel.png",
        caption="Use as a poster/closing slide. Shows all key outputs in one panel.",
    )

    st.markdown("---")
    st.markdown("### 2-Minute Live Demo Script")
    st.markdown(
        """
1. Switch to **Model Builder** tab.
2. Leave defaults. Click **Run Simulation**. (~20 seconds)
3. Point to metric cards: "Radial order is 1.0 — agents are well-contained.
   Star-likeness shows the composite score."
4. Increase omega to 2.5. Click **Run Simulation** again.
5. Compare the agent snapshot: "Arms have rotated — chirality is visible."
6. Switch to **Live Phase Explorer**. Select Sweep A. Click **Load pregenerated**.
7. Point to the heatmap: "Best star-likeness at moderate radial attraction and
   low chirality — the top-left region. High chirality degrades arm structure."
8. Switch to **Movie Gallery**. Play `star_formation_clean.gif`.
9. Say: "This is the arms forming in real time from a uniform initialization."
        """
    )

    st.markdown("---")
    st.markdown("### Backup Plan")
    st.warning(
        "If the app fails: open `outputs/panels/` in a file browser and present "
        "the six PNG files (slide1 through slide5 + final_summary_panel) directly. "
        "All phase diagrams are in `outputs/phase_diagrams/`. "
        "Movies are in `outputs/movies/` and can be opened in any image viewer."
    )

    with st.expander("All pregenerated output files"):
        for subdir in ["panels", "star_ascidian", "phase_diagrams", "movies", "reference"]:
            d = os.path.join("outputs", subdir)
            if os.path.isdir(d):
                files = sorted(f for f in os.listdir(d)
                               if os.path.isfile(os.path.join(d, f)))
                st.markdown(f"**outputs/{subdir}/**  ({len(files)} files)")
                for fname in files:
                    st.markdown(f"  `{fname}`")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

_render_header()

tabs = st.tabs([
    "Target Pattern",
    "Model Builder",
    "Phase Explorer",
    "Movie Gallery",
    "Model Library",
    "LLM Lab Notebook",
    "Presentation Mode",
])

with tabs[0]:
    _tab_target()

with tabs[1]:
    _tab_model_builder()

with tabs[2]:
    _tab_phase_explorer()

with tabs[3]:
    _tab_movie_gallery()

with tabs[4]:
    _tab_model_library()

with tabs[5]:
    _tab_llm_notebook()

with tabs[6]:
    _tab_presentation()
