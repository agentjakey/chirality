"""
Chirality Atlas: Particles, Patterns, and Handedness in Active Matter.
Interactive Streamlit application.

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
import matplotlib.colors as mcolors
import numpy as np
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from chirality.particle_sim import simulate_abp, simulate_chiral_abp, simulate_vicsek_chiral
from chirality.particle_metrics import (
    polar_order, swirl_index, boundary_accumulation,
    average_neighbor_count, compute_all_particle_metrics,
    polar_order_timeseries, mean_squared_displacement,
)
from chirality.pattern_sim import (
    simulate_gray_scott, simulate_feed_gradient,
    simulate_obstacle, simulate_chiral_source_gray_scott,
)
from chirality.pattern_metrics import (
    pattern_strength, count_clusters, field_asymmetry,
    compute_all_pattern_metrics,
)
from chirality.plotting import (
    plot_particle_snapshot, plot_gray_scott_final,
    plot_field, plot_phase_diagram, plot_trajectory_trails,
    plot_particle_snapshot_simple,
)
from chirality.export import load_phase_diagram_data
from chirality.storytelling import summarize_particle_metrics, summarize_pattern_metrics
from chirality.presets import (
    BASELINE_ACTIVE_BROWNIAN, VICSEK_FLOCKING, CHIRAL_VORTEX_GAS,
    BOUNDARY_EDGE_CURRENT, RACEMIC_LEFT_RIGHT_COMPETITION,
    GRAY_SCOTT_SPOTS, GRAY_SCOTT_LABYRINTH, FEED_GRADIENT_PATTERN,
    OBSTACLE_DISRUPTED_PATTERN, CHIRAL_SOURCE_PATTERN,
)

# ============================================================
# Page config
# ============================================================

st.set_page_config(
    page_title="Chirality Atlas",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CSS + logo
# ============================================================

def _load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def _load_svg(path):
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return ""


_load_css()


# ============================================================
# Utility helpers
# ============================================================

def _fig_to_bytes(fig, dpi=150):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor())
    buf.seek(0)
    return buf.getvalue()


def _download_btn(fig, filename):
    st.download_button(
        label="Download figure",
        data=_fig_to_bytes(fig),
        file_name=filename,
        mime="image/png",
    )


def _sci_caption(text):
    st.markdown(f"<p class='fig-caption'>{text}</p>", unsafe_allow_html=True)


def _rule():
    st.markdown("<hr/>", unsafe_allow_html=True)


# ============================================================
# Cached quick-preview simulations (run once per session)
# ============================================================

@st.cache_data(show_spinner=False)
def _preview_particle():
    hist = simulate_chiral_abp(
        N=100, L=8.0, v0=0.5, Dr=0.2, omega=2.0, chirality_mode="right",
        dt=0.01, n_steps=400, seed=42, boundary_mode="periodic", save_every=20,
    )
    return hist


@st.cache_data(show_spinner=False)
def _preview_pattern():
    hist = simulate_gray_scott(
        nx=128, ny=128, Du=0.16, Dv=0.08, F=0.04, k=0.06,
        dt=1.0, n_steps=4000, seed=42, save_every=4000, n_seeds=6,
    )
    return hist


@st.cache_data(show_spinner=False)
def _cached_particle_sweep(n_pts, n_particles, n_steps_sweep):
    from chirality.phase_sweeps import sweep_noise_vs_chirality
    return sweep_noise_vs_chirality(
        noise_values=np.linspace(0.1, 3.0, n_pts),
        chirality_values=np.linspace(0.0, 4.0, n_pts),
        N=n_particles, n_steps=n_steps_sweep, verbose=False,
    )


@st.cache_data(show_spinner=False)
def _cached_pattern_sweep(n_pts, nx, n_steps_sweep):
    from chirality.phase_sweeps import sweep_gray_scott_F_k
    return sweep_gray_scott_F_k(
        F_values=np.linspace(0.01, 0.07, n_pts),
        k_values=np.linspace(0.04, 0.07, n_pts),
        nx=nx, ny=nx, n_steps=n_steps_sweep, verbose=False,
    )


# ============================================================
# Shared figure helpers
# ============================================================

def _particle_figure(hist, title="", with_trails=False):
    if with_trails and hist.positions.shape[0] >= 3:
        fig = plot_trajectory_trails(
            hist.positions, hist.thetas, hist.omegas, hist.L,
            n_trail=min(6, hist.positions.shape[0]),
            title=title,
        )
    else:
        fig = plot_particle_snapshot(
            hist.positions[-1], hist.thetas[-1], hist.omegas, hist.L,
            title=title, show_arrows=True,
        )
    return fig


def _pattern_figure(hist, title="", show_both=False):
    if show_both:
        return plot_gray_scott_final(hist.u_final, hist.v_final, title=title)
    return plot_field(hist.v_final, title=f"{title} (v field)", vmin=0, vmax=0.5)


def _show_particle_metrics(metrics):
    cols = st.columns(4)
    cols[0].metric("Polar Order", f"{metrics['polar_order_final']:.3f}")
    cols[1].metric("Swirl Index", f"{metrics['swirl_index']:.3f}")
    cols[2].metric("Clusters", f"{int(metrics['n_clusters'])}")
    cols[3].metric("Boundary Accum.", f"{metrics['boundary_accumulation']:.3f}")


def _show_pattern_metrics(metrics):
    cols = st.columns(4)
    cols[0].metric("Pattern Strength", f"{metrics['pattern_strength']:.4f}")
    cols[1].metric("Cluster Count", f"{int(metrics['n_clusters'])}")
    cols[2].metric("Mean v", f"{metrics['mean_v']:.4f}")
    cols[3].metric("LR Asymmetry", f"{metrics['field_asymmetry_lr']:.5f}")


# ============================================================
# Tab 1: Overview
# ============================================================

def tab_overview():
    svg_logo = _load_svg(os.path.join("assets", "logo.svg"))
    logo_html = (
        f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:6px;">'
        f'<div style="width:44px;height:44px;flex-shrink:0;">{svg_logo}</div>'
        f'<div><h1 style="margin:0;border:none;">Chirality Atlas</h1>'
        f'<p style="margin:0;color:#555;font-size:0.95rem;font-style:italic;">'
        f'Particles, patterns, and handedness in active matter.</p></div>'
        f'</div>'
    )
    st.markdown(logo_html, unsafe_allow_html=True)

    st.markdown(
        "<p style='font-size:1.15rem;color:#315C4C;font-weight:700;margin-top:0.3rem;'>"
        "Local rules plus broken symmetry can create large-scale biological structure."
        "</p>",
        unsafe_allow_html=True,
    )
    _rule()

    # Central question
    st.markdown(
        "<h2 style='color:#C15A3A;border:none;'>Can microscopic handedness reshape living matter?</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "Biological systems are pervaded by chirality. Bacteria swim in helical paths. "
        "Developing embryos break left-right symmetry to place heart and liver correctly. "
        "Snail shells coil in a fixed direction. This project asks a computational version "
        "of that question: if we give simulated particles or chemical fields a sense of "
        "handedness, what changes at large scales?"
    )

    _rule()

    # Preview images
    col_p, col_f = st.columns(2)

    with col_p:
        st.markdown("#### Particle track")
        st.markdown(
            "Active Brownian Particles extended with a rotation rate. "
            "Each particle traces a small circle; together they form edge currents and swirl patterns."
        )
        with st.spinner("Generating particle preview..."):
            hist = _preview_particle()
        fig = _particle_figure(hist, title="Chiral ABP (omega=2.0, right)")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        _sci_caption(
            "N=100 chiral right-handed particles in a periodic box. "
            "Red = right-handed, blue = left-handed (all red here). "
            "Polar order is low because individual circles do not align collectively."
        )

    with col_f:
        st.markdown("#### Pattern track")
        st.markdown(
            "Gray-Scott reaction-diffusion with spatial gradients and a chiral source. "
            "Feed and kill rates determine whether spots, stripes, or uniform states appear."
        )
        with st.spinner("Generating pattern preview..."):
            hist_p = _preview_pattern()
        fig2 = _pattern_figure(hist_p, title="Gray-Scott labyrinth (F=0.04, k=0.06)")
        st.pyplot(fig2, use_container_width=True)
        plt.close(fig2)
        _sci_caption(
            "v-field (activator) in the Gray-Scott model after 4000 steps. "
            "Multiple seeds produce labyrinthine stripes. Pattern strength = std(v) > 0.10."
        )

    _rule()

    # Tutorial connections
    st.markdown("#### Built from the two hackathon tutorials")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown(
            "**Active matter tutorial**\n"
            "- NumPy random walks\n"
            "- Active Brownian particles\n"
            "- Vicsek flocking\n"
            "- Polar order parameter\n"
            "- Mean squared displacement\n"
            "- One and two-parameter phase diagrams\n"
            "- Mini-challenge: chirality extension"
        )
    with col_t2:
        st.markdown(
            "**Pattern formation tutorial**\n"
            "- 2D fields as images\n"
            "- Diffusion and logistic growth\n"
            "- Gray-Scott model\n"
            "- Feed and kill parameters\n"
            "- Pattern strength, cluster count\n"
            "- Feed gradients and circular obstacles\n"
            "- Mini-challenge: modify, measure, interpret"
        )

    _rule()

    # What to notice
    st.info(
        "**What to notice**\n\n"
        "In the Particle Lab: adding chirality (omega) makes particles circle. "
        "At a circular boundary, this creates a persistent edge current. "
        "Racemic mixtures compete and produce no net swirl.\n\n"
        "In the Pattern Lab: the feed rate F controls what pattern forms. "
        "An obstacle disrupts the pattern locally. "
        "A rotating source (toy model) introduces a small but detectable left-right asymmetry.\n\n"
        "In the Bridge Lab: both tracks respond to the same principle -- "
        "local symmetry breaking produces macroscopic spatial structure."
    )


# ============================================================
# Tab 2: Particle Lab
# ============================================================

_PARTICLE_PRESETS = {
    "Chiral Vortex Gas": {
        "desc": "All particles rotate right (omega > 0, no boundary confinement). "
                "Individual circular orbits. Low polar order; non-zero swirl.",
        "N": 200, "v0": 0.5, "Dr": 0.2, "omega": 2.0, "chirality_mode": "right",
        "eta_vicsek": 0.15, "align": False, "repulsion": False, "repulsion_str": 1.0,
        "boundary_mode": "periodic", "n_steps": 500, "model": "chiral_abp",
    },
    "Baseline ABP": {
        "desc": "Standard active Brownian particles with no alignment and no chirality. "
                "Low polar order at high noise; ballistic at low noise.",
        "N": 200, "v0": 0.5, "Dr": 0.5, "omega": 0.0, "chirality_mode": "none",
        "eta_vicsek": 0.15, "align": False, "repulsion": False, "repulsion_str": 1.0,
        "boundary_mode": "periodic", "n_steps": 500, "model": "abp",
    },
    "Vicsek Flocking": {
        "desc": "Vicsek model: local alignment within radius R. "
                "Low noise gives high polar order (flock). High noise destroys the flock.",
        "N": 200, "v0": 0.5, "Dr": 0.15, "omega": 0.0, "chirality_mode": "none",
        "eta_vicsek": 0.15, "align": True, "repulsion": False, "repulsion_str": 1.0,
        "boundary_mode": "periodic", "n_steps": 500, "model": "vicsek",
    },
    "Boundary Edge Current": {
        "desc": "Right-handed particles confined in a circular trap. "
                "They accumulate at the boundary and orbit in a fixed direction.",
        "N": 200, "v0": 0.5, "Dr": 0.3, "omega": 3.0, "chirality_mode": "right",
        "eta_vicsek": 0.15, "align": False, "repulsion": False, "repulsion_str": 1.0,
        "boundary_mode": "circular_trap", "n_steps": 600, "model": "chiral_abp",
    },
    "Racemic Competition": {
        "desc": "Equal numbers of left- and right-handed particles with soft repulsion. "
                "Net swirl is near zero; particles mix but form local clusters.",
        "N": 200, "v0": 0.5, "Dr": 0.3, "omega": 2.0, "chirality_mode": "racemic",
        "eta_vicsek": 0.15, "align": False, "repulsion": True, "repulsion_str": 2.0,
        "boundary_mode": "periodic", "n_steps": 600, "model": "chiral_abp",
    },
}


def tab_particle_lab():
    st.markdown("## Particle Lab")
    st.markdown(
        "Run active particle simulations and measure collective order. "
        "Choose a preset or adjust parameters manually, then click **Run**."
    )

    col_ctrl, col_out = st.columns([1, 2], gap="large")

    with col_ctrl:
        preset_name = st.selectbox(
            "Preset",
            list(_PARTICLE_PRESETS.keys()),
            index=0,
            key="p_preset",
        )
        p = _PARTICLE_PRESETS[preset_name]
        st.markdown(
            f"<p style='font-size:0.83rem;color:#555;font-style:italic;'>{p['desc']}</p>",
            unsafe_allow_html=True,
        )
        _rule()

        N = st.slider("N (particles)", 50, 400, p["N"], step=25, key="p_N")
        v0 = st.slider("Speed v0", 0.1, 2.0, p["v0"], step=0.05, key="p_v0")
        Dr = st.slider("Rotational noise Dr", 0.05, 5.0, p["Dr"], step=0.05, key="p_Dr")
        omega = st.slider(
            "Chirality omega", 0.0, 6.0, p["omega"], step=0.1, key="p_omega",
            help="Rotation rate (rad per time unit). 0 = no chirality."
        )

        model_choice = p["model"]
        if model_choice == "vicsek":
            eta = st.slider("Alignment noise eta", 0.0, 1.0, p["eta_vicsek"], step=0.01, key="p_eta")
        else:
            eta = p["eta_vicsek"]

        boundary_mode = st.selectbox(
            "Boundary mode",
            ["periodic", "reflective", "circular_trap"],
            index=["periodic", "reflective", "circular_trap"].index(p["boundary_mode"]),
            key="p_bmode",
        )

        use_repulsion = st.checkbox("Soft repulsion", value=p["repulsion"], key="p_repul")
        if use_repulsion:
            rep_str = st.slider("Repulsion strength", 0.5, 5.0, p["repulsion_str"], step=0.25, key="p_rep_str")
        else:
            rep_str = 1.0

        n_steps = st.slider("Steps", 100, 1000, p["n_steps"], step=50, key="p_nsteps")
        seed = st.number_input("Random seed", value=42, step=1, key="p_seed")

        show_trails = st.checkbox("Show trajectory trails", value=False, key="p_trails")

        _rule()

        if N > 300 and use_repulsion:
            st.warning("N > 300 with repulsion enabled can be slow (O(N^2) pairs). Consider reducing N.")

        run_btn = st.button("Run Particle Simulation", type="primary", key="p_run")

    with col_out:
        if run_btn:
            params = dict(
                N=N, L=10.0, v0=v0, Dr=Dr, omega=omega, n_steps=n_steps,
                seed=int(seed), boundary_mode=boundary_mode,
                repulsion=use_repulsion, repulsion_strength=rep_str,
                repulsion_range=0.4, save_every=max(1, n_steps // 50),
            )
            with st.spinner("Running simulation..."):
                if model_choice == "abp":
                    hist = simulate_abp(
                        N=N, L=10.0, v0=v0, Dr=Dr, dt=0.01,
                        n_steps=n_steps, seed=int(seed),
                        boundary_mode=boundary_mode,
                        save_every=max(1, n_steps // 50),
                    )
                    hist.omegas = np.zeros(N)
                elif model_choice == "vicsek":
                    hist = simulate_vicsek_chiral(
                        N=N, L=10.0, v0=v0, R=1.0, eta=eta, omega=omega,
                        dt=0.1, n_steps=n_steps, seed=int(seed),
                        boundary_mode=boundary_mode,
                        save_every=max(1, n_steps // 50),
                    )
                else:
                    chirality_mode = "right" if omega > 0 else "none"
                    if preset_name == "Racemic Competition":
                        chirality_mode = "racemic"
                    hist = simulate_chiral_abp(
                        N=N, L=10.0, v0=v0, Dr=Dr, omega=abs(omega),
                        chirality_mode=chirality_mode, dt=0.01, n_steps=n_steps,
                        seed=int(seed), boundary_mode=boundary_mode,
                        repulsion=use_repulsion, repulsion_strength=rep_str,
                        repulsion_range=0.4,
                        save_every=max(1, n_steps // 50),
                    )
                metrics = compute_all_particle_metrics(hist, R_neighbor=1.0)
                st.session_state["p_hist"] = hist
                st.session_state["p_metrics"] = metrics
                st.session_state["p_label"] = preset_name

        if "p_hist" in st.session_state:
            hist = st.session_state["p_hist"]
            metrics = st.session_state["p_metrics"]
            label = st.session_state.get("p_label", "")

            fig = _particle_figure(hist, title=label, with_trails=show_trails)
            st.pyplot(fig, use_container_width=True)
            _download_btn(fig, f"particle_{label.lower().replace(' ','_')}.png")
            plt.close(fig)

            _sci_caption(
                f"Final snapshot after {hist.positions.shape[0]-1} saved frames. "
                f"Colors: red = right-handed (omega > 0), blue = left-handed (omega < 0), "
                f"white = no chirality."
            )
            _rule()

            _show_particle_metrics(metrics)
            _rule()

            # Polar order timeseries
            phi_ts = polar_order_timeseries(hist.thetas)
            fig_ts, ax_ts = plt.subplots(figsize=(7, 2.5), facecolor="#F7F3EA")
            ax_ts.plot(hist.times, phi_ts, color="#315C4C", linewidth=1.5)
            ax_ts.axhline(phi_ts.mean(), color="#C15A3A", linestyle="--",
                          linewidth=1, alpha=0.7, label=f"mean={phi_ts.mean():.3f}")
            ax_ts.set_xlabel("Time")
            ax_ts.set_ylabel("Polar order phi")
            ax_ts.set_ylim(0, 1)
            ax_ts.legend(frameon=False, fontsize=8)
            ax_ts.set_facecolor("#F7F3EA")
            ax_ts.spines[["top", "right"]].set_visible(False)
            fig_ts.tight_layout()
            st.pyplot(fig_ts, use_container_width=True)
            plt.close(fig_ts)
            _sci_caption("Polar order over time. phi=1 means all particles point the same way.")

            _rule()
            with st.expander("Interpretation and sanity checks"):
                st.markdown(summarize_particle_metrics(metrics, label))
                st.markdown(
                    "\n**Sanity checks:**\n"
                    "- High noise Dr >> omega should give phi near 0 (gas-like)\n"
                    "- Low Dr with Vicsek alignment should give phi near 1 (flock)\n"
                    "- Zero omega should give swirl index near 0\n"
                    "- Racemic mixture should give swirl near 0 (left and right cancel)"
                )
        else:
            st.markdown(
                "<div style='text-align:center;color:#999;margin-top:4rem;'>"
                "<p style='font-size:1.1rem;'>Select a preset and click Run.</p>"
                "</div>",
                unsafe_allow_html=True,
            )


# ============================================================
# Tab 3: Pattern Lab
# ============================================================

_PATTERN_PRESETS = {
    "Gray-Scott Labyrinth": {
        "desc": "F=0.04, k=0.06. Forms labyrinthine stripes from multiple seeds. "
                "High pattern strength, few large connected regions.",
        "nx": 128, "F": 0.04, "k": 0.06, "Du": 0.16, "Dv": 0.08,
        "n_steps": 4000, "n_seeds": 6, "model": "gray_scott",
        "F_left": 0.02, "F_right": 0.055, "obs_r": 0.12,
        "src_str": 0.015, "src_omega": 0.1,
    },
    "Gray-Scott Spots": {
        "desc": "F=0.035, k=0.065. Produces self-organized spots (Turing-like). "
                "Many small disconnected clusters.",
        "nx": 128, "F": 0.035, "k": 0.065, "Du": 0.16, "Dv": 0.08,
        "n_steps": 5000, "n_seeds": 10, "model": "gray_scott",
        "F_left": 0.02, "F_right": 0.055, "obs_r": 0.12,
        "src_str": 0.015, "src_omega": 0.1,
    },
    "Feed Gradient": {
        "desc": "Feed rate F varies from F_left (x=0) to F_right (x=L). "
                "Creates a phase boundary: spots on one side, uniform on the other.",
        "nx": 128, "F": 0.035, "k": 0.063, "Du": 0.16, "Dv": 0.08,
        "n_steps": 4000, "n_seeds": 6, "model": "gradient",
        "F_left": 0.02, "F_right": 0.055, "obs_r": 0.12,
        "src_str": 0.015, "src_omega": 0.1,
    },
    "Circular Obstacle": {
        "desc": "A circular region where the reaction is blocked. "
                "Pattern forms around the obstacle; topological defects may appear at the boundary.",
        "nx": 128, "F": 0.035, "k": 0.065, "Du": 0.16, "Dv": 0.08,
        "n_steps": 5000, "n_seeds": 10, "model": "obstacle",
        "F_left": 0.02, "F_right": 0.055, "obs_r": 0.12,
        "src_str": 0.015, "src_omega": 0.1,
    },
    "Chiral Source (toy model)": {
        "desc": "A rotating injection point orbits the center, injecting v-species. "
                "Breaks left-right symmetry in the pattern. NOT a real biological mechanism.",
        "nx": 128, "F": 0.035, "k": 0.065, "Du": 0.16, "Dv": 0.08,
        "n_steps": 5000, "n_seeds": None, "model": "chiral_source",
        "F_left": 0.02, "F_right": 0.055, "obs_r": 0.12,
        "src_str": 0.020, "src_omega": 0.1,
    },
}


def tab_pattern_lab():
    st.markdown("## Pattern Lab")
    st.markdown(
        "Run Gray-Scott reaction-diffusion simulations and measure emergent pattern structure. "
        "Choose a preset or adjust parameters, then click **Run**."
    )

    col_ctrl, col_out = st.columns([1, 2], gap="large")

    with col_ctrl:
        preset_name = st.selectbox(
            "Preset",
            list(_PATTERN_PRESETS.keys()),
            index=0,
            key="pat_preset",
        )
        p = _PATTERN_PRESETS[preset_name]
        st.markdown(
            f"<p style='font-size:0.83rem;color:#555;font-style:italic;'>{p['desc']}</p>",
            unsafe_allow_html=True,
        )
        _rule()

        nx = st.select_slider("Grid size (nx=ny)", [64, 128, 192, 256], value=p["nx"], key="pat_nx")
        F = st.slider("Feed rate F", 0.005, 0.08, float(p["F"]), step=0.002, key="pat_F",
                      help="Controls what pattern type forms. Try 0.01-0.07.")
        k = st.slider("Kill rate k", 0.04, 0.08, float(p["k"]), step=0.001, key="pat_k",
                      help="Combined removal rate of v. With F, determines pattern regime.")
        Du = st.slider("Du (substrate diffusion)", 0.08, 0.25, float(p["Du"]), step=0.01, key="pat_Du")
        Dv = st.slider("Dv (activator diffusion)", 0.02, 0.12, float(p["Dv"]), step=0.005, key="pat_Dv")
        n_steps = st.slider("Steps", 1000, 8000, p["n_steps"], step=500, key="pat_nsteps")
        seed = st.number_input("Random seed", value=42, step=1, key="pat_seed")

        model_choice = p["model"]
        if model_choice == "gradient":
            F_left = st.slider("F (left edge)", 0.005, 0.06, float(p["F_left"]), step=0.002, key="pat_Fl")
            F_right = st.slider("F (right edge)", 0.02, 0.08, float(p["F_right"]), step=0.002, key="pat_Fr")
        if model_choice == "obstacle":
            obs_r = st.slider("Obstacle radius (fraction of L)", 0.05, 0.30, float(p["obs_r"]), step=0.01, key="pat_obs")
        if model_choice == "chiral_source":
            src_str = st.slider("Source strength", 0.005, 0.05, float(p["src_str"]), step=0.005, key="pat_ss")
            src_omega = st.slider("Source rotation speed", 0.0, 0.3, float(p["src_omega"]), step=0.01, key="pat_so")

        show_u = st.checkbox("Show u field (substrate)", value=False, key="pat_showu")
        n_seeds_val = p.get("n_seeds")

        _rule()

        if Du > 0.20:
            st.warning("High Du may cause instability. Keep Du*dt/dx^2 < 0.25.")
        if n_steps > 6000 and nx >= 256:
            st.warning("256x256 with >6000 steps can be slow on a laptop (est. >60s).")

        run_btn = st.button("Run Pattern Simulation", type="primary", key="pat_run")

    with col_out:
        if run_btn:
            with st.spinner("Running Gray-Scott simulation..."):
                if model_choice == "gray_scott":
                    hist = simulate_gray_scott(
                        nx=nx, ny=nx, Du=Du, Dv=Dv, F=F, k=k,
                        dt=1.0, n_steps=n_steps, seed=int(seed),
                        save_every=n_steps, n_seeds=n_seeds_val,
                    )
                elif model_choice == "gradient":
                    hist = simulate_feed_gradient(
                        nx=nx, ny=nx, Du=Du, Dv=Dv, F_left=F_left, F_right=F_right,
                        k=k, dt=1.0, n_steps=n_steps, seed=int(seed),
                        save_every=n_steps, n_seeds=6,
                    )
                elif model_choice == "obstacle":
                    hist = simulate_obstacle(
                        nx=nx, ny=nx, Du=Du, Dv=Dv, F=F, k=k,
                        dt=1.0, n_steps=n_steps, seed=int(seed),
                        obstacle_cx=0.5, obstacle_cy=0.5, obstacle_r=obs_r,
                        save_every=n_steps, n_seeds=10,
                    )
                elif model_choice == "chiral_source":
                    hist = simulate_chiral_source_gray_scott(
                        nx=nx, ny=nx, Du=Du, Dv=Dv, F=F, k=k,
                        dt=1.0, n_steps=n_steps, seed=int(seed),
                        source_strength=src_str, source_omega=src_omega,
                        source_r_orbit=0.20, source_sigma=0.05,
                        save_every=n_steps, n_seeds=None,
                    )
                metrics = compute_all_pattern_metrics(hist)
                st.session_state["pat_hist"] = hist
                st.session_state["pat_metrics"] = metrics
                st.session_state["pat_label"] = preset_name
                st.session_state["pat_showu"] = show_u

        if "pat_hist" in st.session_state:
            hist = st.session_state["pat_hist"]
            metrics = st.session_state["pat_metrics"]
            label = st.session_state.get("pat_label", "")
            _show_u = st.session_state.get("pat_showu", False)

            if _show_u:
                fig = plot_gray_scott_final(hist.u_final, hist.v_final, title=label)
                st.pyplot(fig, use_container_width=True)
                _download_btn(fig, f"pattern_{label.lower().replace(' ','_')}_uv.png")
                plt.close(fig)
            else:
                fig = plot_field(hist.v_final, title=f"{label}: v field", vmin=0, vmax=0.5)
                st.pyplot(fig, use_container_width=True)
                _download_btn(fig, f"pattern_{label.lower().replace(' ','_')}_v.png")
                plt.close(fig)

            _sci_caption(
                "v-field (activator species). High v (bright) = high concentration. "
                "Pattern strength = std(v). Near-zero strength = homogeneous state."
            )
            _rule()
            _show_pattern_metrics(metrics)
            _rule()

            with st.expander("Interpretation and sanity checks"):
                st.markdown(summarize_pattern_metrics(metrics, label))
                st.markdown(
                    "\n**Sanity checks:**\n"
                    "- High kill rate k should suppress v (near-homogeneous state)\n"
                    "- No initial v means no pattern (check n_seeds)\n"
                    "- Diffusion alone smooths gradients (run_diffusion preset in code)\n"
                    "- Results should vary with seed -- run multiple seeds to confirm\n"
                    "- Feed gradient LR asymmetry is physical (F varies left to right)\n"
                    "- Chiral source asymmetry is small (~0.001-0.005) -- toy model only"
                )
        else:
            st.markdown(
                "<div style='text-align:center;color:#999;margin-top:4rem;'>"
                "<p style='font-size:1.1rem;'>Select a preset and click Run.</p>"
                "</div>",
                unsafe_allow_html=True,
            )


# ============================================================
# Tab 4: Bridge Lab
# ============================================================

def tab_bridge_lab():
    st.markdown("## Bridge Lab")
    st.markdown(
        "The two tutorial models are different in mechanism but teach the same lesson. "
        "Run both here to compare them side by side."
    )

    st.info(
        "**The shared principle:**  \n"
        "Local interactions with broken symmetry produce macroscopic spatial structure. "
        "In particles, chirality drives edge currents. "
        "In fields, a symmetry-breaking perturbation drives pattern asymmetry. "
        "The models are not the same, but the logic is."
    )

    _rule()

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("#### Particle model")
        p_model = st.selectbox(
            "Comparison scenario",
            [
                "Chiral ABP vs ABP (no chirality)",
                "Vicsek: ordered flock vs chiral flock",
                "Edge current vs bulk gas",
            ],
            key="bridge_p_scenario",
        )
    with col_r:
        st.markdown("#### Pattern model")
        f_model = st.selectbox(
            "Comparison scenario",
            [
                "Spots vs labyrinth (F/k variation)",
                "Gradient: phase boundary across domain",
                "Obstacle vs open field",
            ],
            key="bridge_f_scenario",
        )

    run_bridge = st.button("Run Bridge Comparison", type="primary", key="bridge_run")

    if run_bridge:
        with st.spinner("Running both simulations..."):
            # Particle side
            if p_model == "Chiral ABP vs ABP (no chirality)":
                hist_A = simulate_chiral_abp(
                    N=100, L=10.0, v0=0.5, Dr=0.2, omega=2.0, chirality_mode="right",
                    dt=0.01, n_steps=400, seed=42, save_every=10,
                )
                hist_B = simulate_chiral_abp(
                    N=100, L=10.0, v0=0.5, Dr=0.2, omega=0.0, chirality_mode="none",
                    dt=0.01, n_steps=400, seed=42, save_every=10,
                )
                p_labels = ("Chiral ABP (omega=2)", "ABP (no chirality)")
            elif p_model == "Vicsek: ordered flock vs chiral flock":
                hist_A = simulate_vicsek_chiral(
                    N=100, L=10.0, v0=0.5, R=1.0, eta=0.15, omega=0.0,
                    dt=0.1, n_steps=300, seed=42, save_every=10,
                )
                hist_B = simulate_vicsek_chiral(
                    N=100, L=10.0, v0=0.5, R=1.0, eta=0.15, omega=1.5,
                    dt=0.1, n_steps=300, seed=42, save_every=10,
                )
                p_labels = ("Vicsek flock (omega=0)", "Chiral Vicsek (omega=1.5)")
            else:
                hist_A = simulate_chiral_abp(
                    N=100, L=10.0, v0=0.5, Dr=0.3, omega=3.0, chirality_mode="right",
                    dt=0.01, n_steps=500, seed=42, boundary_mode="circular_trap", save_every=10,
                )
                hist_B = simulate_chiral_abp(
                    N=100, L=10.0, v0=0.5, Dr=0.3, omega=3.0, chirality_mode="right",
                    dt=0.01, n_steps=500, seed=42, boundary_mode="periodic", save_every=10,
                )
                p_labels = ("Edge current (circular trap)", "Bulk periodic")

            # Pattern side
            if f_model == "Spots vs labyrinth (F/k variation)":
                fhist_A = simulate_gray_scott(
                    nx=64, ny=64, F=0.035, k=0.065, dt=1.0, n_steps=4000, seed=42,
                    save_every=4000, n_seeds=8,
                )
                fhist_B = simulate_gray_scott(
                    nx=64, ny=64, F=0.04, k=0.06, dt=1.0, n_steps=4000, seed=42,
                    save_every=4000, n_seeds=6,
                )
                f_labels = ("Spots (F=0.035, k=0.065)", "Labyrinth (F=0.04, k=0.06)")
            elif f_model == "Gradient: phase boundary across domain":
                fhist_A = simulate_gray_scott(
                    nx=64, ny=64, F=0.04, k=0.063, dt=1.0, n_steps=3000, seed=42,
                    save_every=3000, n_seeds=6,
                )
                fhist_B = simulate_feed_gradient(
                    nx=64, ny=64, F_left=0.015, F_right=0.055, k=0.063, dt=1.0,
                    n_steps=3000, seed=42, save_every=3000, n_seeds=6,
                )
                f_labels = ("Uniform F", "Feed gradient (phase boundary)")
            else:
                fhist_A = simulate_gray_scott(
                    nx=64, ny=64, F=0.035, k=0.065, dt=1.0, n_steps=4000, seed=42,
                    save_every=4000, n_seeds=8,
                )
                fhist_B = simulate_obstacle(
                    nx=64, ny=64, F=0.035, k=0.065, dt=1.0, n_steps=4000, seed=42,
                    obstacle_r=0.15, save_every=4000, n_seeds=8,
                )
                f_labels = ("Open field", "Circular obstacle")

            st.session_state["bridge"] = {
                "hist_A": hist_A, "hist_B": hist_B, "p_labels": p_labels,
                "fhist_A": fhist_A, "fhist_B": fhist_B, "f_labels": f_labels,
            }

    if "bridge" in st.session_state:
        b = st.session_state["bridge"]
        _rule()

        # Particle row
        st.markdown("#### Particle results")
        col1, col2 = st.columns(2)
        for col, hist, lbl in zip([col1, col2], [b["hist_A"], b["hist_B"]], b["p_labels"]):
            with col:
                fig = _particle_figure(hist, title=lbl)
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)
                m = compute_all_particle_metrics(hist)
                st.caption(
                    f"phi={m['polar_order_final']:.3f}  |  "
                    f"swirl={m['swirl_index']:.3f}  |  "
                    f"accum={m['boundary_accumulation']:.3f}"
                )

        _rule()

        # Pattern row
        st.markdown("#### Pattern results")
        col3, col4 = st.columns(2)
        for col, fhist, lbl in zip([col3, col4], [b["fhist_A"], b["fhist_B"]], b["f_labels"]):
            with col:
                fig = _pattern_figure(fhist, title=lbl)
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)
                m = compute_all_pattern_metrics(fhist)
                st.caption(
                    f"strength={m['pattern_strength']:.4f}  |  "
                    f"clusters={m['n_clusters']}  |  "
                    f"LR asym={m['field_asymmetry_lr']:.5f}"
                )

        _rule()

        # Shared principles
        st.markdown("#### What both models show")
        pr1, pr2, pr3, pr4 = st.columns(4)
        with pr1:
            st.markdown(
                "<div style='background:#FFFFFF;border:1px solid #DDD5C8;border-top:3px solid #C15A3A;"
                "border-radius:4px;padding:0.8rem;'>"
                "<strong>Local rules generate global structure</strong><br/>"
                "<small>Each particle / each lattice site follows simple local equations. "
                "Collective behavior emerges from interactions alone.</small>"
                "</div>",
                unsafe_allow_html=True,
            )
        with pr2:
            st.markdown(
                "<div style='background:#FFFFFF;border:1px solid #DDD5C8;border-top:3px solid #315C4C;"
                "border-radius:4px;padding:0.8rem;'>"
                "<strong>Symmetry breaking drives asymmetry</strong><br/>"
                "<small>Chirality (omega) or a rotating source breaks a symmetry. "
                "The system adopts a definite handedness.</small>"
                "</div>",
                unsafe_allow_html=True,
            )
        with pr3:
            st.markdown(
                "<div style='background:#FFFFFF;border:1px solid #DDD5C8;border-top:3px solid #C15A3A;"
                "border-radius:4px;padding:0.8rem;'>"
                "<strong>Noise competes with order</strong><br/>"
                "<small>High rotational noise (Dr) or high angular noise (eta) destroys collective order. "
                "In Gray-Scott, high kill rate (k) suppresses v entirely.</small>"
                "</div>",
                unsafe_allow_html=True,
            )
        with pr4:
            st.markdown(
                "<div style='background:#FFFFFF;border:1px solid #DDD5C8;border-top:3px solid #315C4C;"
                "border-radius:4px;padding:0.8rem;'>"
                "<strong>Obstacles reshape structure</strong><br/>"
                "<small>A physical boundary (circular trap) confines edge currents. "
                "A no-reaction zone disrupts pattern symmetry and creates topological defects.</small>"
                "</div>",
                unsafe_allow_html=True,
            )


# ============================================================
# Tab 5: Phase Atlas
# ============================================================

def tab_phase_atlas():
    st.markdown("## Phase Atlas")
    st.markdown(
        "Systematic parameter sweeps reveal which parts of parameter space produce "
        "each type of collective behavior. These are coarse grids for exploration, "
        "not final publication-quality numerics."
    )

    st.warning(
        "Phase sweeps are computationally expensive. "
        "Pregenerated data is loaded automatically if available in `outputs/phase_sweeps/`. "
        "Use the buttons below to generate fresh sweeps in-browser (small grids for speed)."
    )

    _rule()

    # Try loading pregenerated files first
    pregen_particle = "outputs/phase_sweeps/particle_sweep_data.npz"
    pregen_vicsek = "outputs/phase_sweeps/vicsek_sweep_data.npz"
    pregen_pattern = "outputs/phase_sweeps/gray_scott_sweep_data.npz"
    pregen_chiral = "outputs/phase_sweeps/chiral_source_sweep_data.npz"

    def _try_load(path):
        if os.path.exists(path):
            try:
                return load_phase_diagram_data(path)
            except Exception:
                return None
        return None

    p_data = _try_load(pregen_particle)
    v_data = _try_load(pregen_vicsek)
    gs_data = _try_load(pregen_pattern)
    cs_data = _try_load(pregen_chiral)

    has_pregen = any(x is not None for x in [p_data, v_data, gs_data, cs_data])
    if has_pregen:
        st.success(
            f"Pregenerated sweep data found in `outputs/phase_sweeps/`. "
            f"Loaded: "
            + ", ".join(
                n for n, d in [("particle", p_data), ("vicsek", v_data),
                                ("gray_scott", gs_data), ("chiral_source", cs_data)]
                if d is not None
            )
        )

    # In-browser sweep buttons
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        run_p_sweep = st.button(
            "Run small particle sweep (5x5, ~30s)", key="pa_run_p",
            help="5x5 grid, N=60, 150 steps/point"
        )
    with col_btn2:
        run_gs_sweep = st.button(
            "Run small pattern sweep (5x5, ~1-2 min)", key="pa_run_gs",
            help="5x5 grid, 64x64, 1000 steps/point"
        )

    if run_p_sweep:
        with st.spinner("Running particle sweep (5x5)..."):
            p_data = _cached_particle_sweep(5, 60, 150)
            st.session_state["pa_p_data"] = p_data
            st.success("Particle sweep done.")

    if run_gs_sweep:
        with st.spinner("Running pattern sweep (5x5, ~1-2 min)..."):
            gs_data = _cached_pattern_sweep(5, 64, 1000)
            st.session_state["pa_gs_data"] = gs_data
            st.success("Pattern sweep done.")

    # Use session state as fallback
    if p_data is None:
        p_data = st.session_state.get("pa_p_data")
    if gs_data is None:
        gs_data = st.session_state.get("pa_gs_data")

    _rule()

    # Metric explanations
    with st.expander("Metric definitions"):
        st.markdown(
            "**Polar order** phi = |mean(exp(i*theta))|. "
            "phi=1: all particles point the same way. phi~0: random orientations.\n\n"
            "**Swirl index**: average projection of velocity onto the tangent of a circle "
            "centered in the box. Positive = counter-clockwise net rotation. "
            "Near zero = no net circulation.\n\n"
            "**Boundary accumulation**: fraction of particles within 0.5 length units "
            "of any box wall. High = particles crowd near boundaries.\n\n"
            "**Pattern strength**: std(v). Near zero = homogeneous state. "
            "Typical values for spots: 0.08-0.15.\n\n"
            "**Cluster count**: connected regions where v > 0.1. "
            "Labyrinth: few large clusters. Spots: many small clusters."
        )

    # Display sweep results
    if p_data is not None:
        st.markdown("### Chiral ABP phase diagrams (Dr vs omega)")
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            fig = plot_phase_diagram(
                p_data["noise_values"], p_data["chirality_values"],
                p_data["polar_order"],
                "Rotational noise Dr", "Chirality omega", "Polar order",
                title="Polar Order", vmin=0, vmax=1,
            )
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            _sci_caption("phi near 1 = collective alignment (flock).")

        with col_b:
            fig = plot_phase_diagram(
                p_data["noise_values"], p_data["chirality_values"],
                p_data["swirl_index"],
                "Rotational noise Dr", "Chirality omega", "Swirl index",
                title="Swirl Index", vmin=-1, vmax=1, cmap="RdBu",
            )
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            _sci_caption("Red = net CW rotation. Blue = CCW. White = no net swirl.")

        with col_c:
            fig = plot_phase_diagram(
                p_data["noise_values"], p_data["chirality_values"],
                p_data["boundary_accumulation"],
                "Rotational noise Dr", "Chirality omega", "Boundary accum.",
                title="Boundary Accumulation", vmin=0, vmax=1, cmap="hot",
            )
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            _sci_caption("High = particles crowd near walls.")

        _rule()

    if v_data is not None:
        st.markdown("### Chiral Vicsek phase diagram (eta vs omega)")
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            fig = plot_phase_diagram(
                v_data["eta_values"], v_data["chirality_values"],
                v_data["polar_order"],
                "Alignment noise eta", "Chirality omega", "Polar order",
                title="Vicsek: Polar Order", vmin=0, vmax=1,
            )
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            _sci_caption("Low eta, low omega = high flocking order.")

        with col_v2:
            fig = plot_phase_diagram(
                v_data["eta_values"], v_data["chirality_values"],
                v_data["swirl_index"],
                "Alignment noise eta", "Chirality omega", "Swirl index",
                title="Vicsek: Swirl Index", vmin=-1, vmax=1, cmap="RdBu",
            )
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            _sci_caption("Chirality competes with alignment.")

        _rule()

    if gs_data is not None:
        st.markdown("### Gray-Scott phase diagram (F vs k)")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig = plot_phase_diagram(
                gs_data["F_values"], gs_data["k_values"],
                gs_data["pattern_strength"],
                "Feed rate F", "Kill rate k", "Pattern strength",
                title="Pattern Strength",
            )
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            _sci_caption("Bright = high pattern formation (spots or stripes).")

        with col_g2:
            fig = plot_phase_diagram(
                gs_data["F_values"], gs_data["k_values"],
                gs_data["n_clusters"],
                "Feed rate F", "Kill rate k", "Cluster count",
                title="Cluster Count", cmap="plasma",
            )
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            _sci_caption("Many clusters = spot-like regime.")

        _rule()

    if cs_data is not None:
        st.markdown("### Chiral source phase diagram (rotation speed vs F)")
        st.markdown(
            "*Toy model only. The asymmetry values are small (~0.001-0.005) and "
            "should not be over-interpreted.*"
        )
        fig = plot_phase_diagram(
            cs_data["source_omega_values"], cs_data["F_values"],
            cs_data["field_asymmetry"],
            "Source rotation speed", "Feed rate F", "|LR asymmetry|",
            title="Chiral Source: Pattern Asymmetry", cmap="inferno",
        )
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        _sci_caption(
            "Faster rotation + intermediate F tends to produce larger LR asymmetry in the v field."
        )

    if p_data is None and gs_data is None and v_data is None and cs_data is None:
        st.markdown(
            "<div style='text-align:center;color:#999;margin-top:3rem;'>"
            "<p>No pregenerated data found. Run the sweep buttons above, "
            "or run <code>python scripts/run_phase_sweeps.py</code> first.</p>"
            "</div>",
            unsafe_allow_html=True,
        )


# ============================================================
# Tab 6: Presentation Mode
# ============================================================

def _slide(number, title, body, notes=""):
    border_color = "#C15A3A" if number % 2 == 1 else "#315C4C"
    st.markdown(
        f"<div style='background:#FFFFFF;border:1.5px solid #DDD5C8;"
        f"border-left:5px solid {border_color};border-radius:4px;"
        f"padding:1.5rem 1.8rem;margin-bottom:1.2rem;'>"
        f"<p style='color:#888;font-size:0.75rem;letter-spacing:0.1em;text-transform:uppercase;"
        f"margin:0 0 0.4rem 0;'>Slide {number}</p>"
        f"<h2 style='color:#1F2421;border:none;margin:0 0 0.8rem 0;'>{title}</h2>"
        f"{body}"
        f"</div>",
        unsafe_allow_html=True,
    )
    if notes:
        with st.expander(f"Speaker notes: Slide {number}"):
            st.markdown(notes)


def tab_presentation_mode():
    st.markdown("## Presentation Mode")
    st.markdown(
        "A scrollable 5-slide story. Each slide corresponds to a section of the live demo. "
        "Speaker notes are in the expandable sections below each slide."
    )

    _rule()

    _slide(
        1,
        "Can microscopic handedness reshape living matter?",
        """
        <p>Biological systems are pervaded by chirality. Bacteria swim in helical paths
        from the shape of their flagella. Developing embryos break left-right symmetry
        to place the heart on the correct side. Snail shells coil in a fixed direction.
        Cilia beat in coordinated, chiral waves.</p>
        <p>This project asks a minimal computational version of the question:
        if we give simulated particles or chemical fields a sense of handedness,
        what changes at macroscopic scales?</p>
        <p><strong>Answer preview:</strong>
        In particle models, chirality produces edge currents. In field models,
        a chiral source produces pattern asymmetry. Both effects are measurable.</p>
        """,
        notes=(
            "Opening hook: connect to biological motivation. Show the overview tab. "
            "State clearly that this is computational physics, not a claim about specific organisms. "
            "30-45 seconds."
        ),
    )

    _slide(
        2,
        "Two tutorial models, one scientific question",
        """
        <p><strong>Track 1: Particle active matter</strong><br/>
        Each particle self-propels at speed v0 and diffuses in orientation at rate Dr.
        Standard ABP: no order, no chirality.
        Chiral extension: add omega*dt to the orientation update.
        Vicsek extension: add local alignment plus chirality.</p>
        <p><strong>Track 2: Pattern formation</strong><br/>
        Gray-Scott reaction-diffusion: two chemical species that react and diffuse.
        Feed and kill rates (F, k) determine the pattern regime.
        Extensions: feed gradient, circular obstacle, rotating source.</p>
        <p><strong>Connection:</strong>
        Both models are minimal, parameter-controlled, and produce emergent macroscopic structure
        from local rules. Chirality is the symmetry-breaking knob in both.</p>
        """,
        notes=(
            "Explain the tutorials briefly. Show the two preview images from the Overview tab. "
            "Emphasize that this is a direct response to the mini-challenges in both tutorials. "
            "60-75 seconds."
        ),
    )

    _slide(
        3,
        "Baseline reproduction: tutorials in code",
        """
        <ul>
        <li><strong>ABP baseline:</strong> polar order near 0 at high noise -- gas phase, as expected.</li>
        <li><strong>Vicsek flocking:</strong> polar order near 0.95 at eta=0.15 -- flock, as expected.</li>
        <li><strong>Gray-Scott spots:</strong> F=0.035, k=0.065 produces self-organized spots.</li>
        <li><strong>Gray-Scott labyrinth:</strong> F=0.04, k=0.06 produces labyrinthine stripes.</li>
        <li><strong>Feed gradient:</strong> F varying left-to-right creates a phase boundary visible in the field.</li>
        </ul>
        <p>These match established results from the literature and tutorial.
        The code is a correct implementation of the tutorial models.</p>
        """,
        notes=(
            "Show the Particle Lab and Pattern Lab tabs. "
            "Run ABP baseline: show polar order near 0. "
            "Run Vicsek: show polar order near 0.95. "
            "Show Gray-Scott spots and labyrinth images from outputs/demo/. "
            "Total: 90 seconds."
        ),
    )

    _slide(
        4,
        "Creative extension: chirality, obstacles, sources",
        """
        <p><strong>Chiral ABP (particle track):</strong>
        Adding omega=2.0 to ABP creates circular swimming orbits.
        In a circular trap, particles self-organize into a persistent edge current
        measurable by the swirl index.
        Racemic mixtures (half left, half right) show near-zero swirl --
        the two populations cancel.</p>
        <p><strong>Phase diagram:</strong>
        Sweeping Dr vs omega shows that chirality and noise compete.
        Low noise + high omega = strong swirl. High noise destroys it.</p>
        <p><strong>Chiral source (pattern track, toy model):</strong>
        A rotating injection point orbits the center of the Gray-Scott simulation.
        Left-right asymmetry increases from ~0.0001 (no source) to ~0.002-0.005 (omega=0.1).
        Effect is small but reproducible across seeds at constant parameters.</p>
        """,
        notes=(
            "This is the core of the hackathon contribution. "
            "Show the Phase Atlas swirl index heatmap. "
            "Show the chiral_vortex_gas.gif or boundary_edge_current.gif from outputs/videos/. "
            "Show chiral_source_pattern vs gray_scott_spots side by side. "
            "Be clear that the chiral source is a toy model. "
            "90-120 seconds."
        ),
    )

    _slide(
        5,
        "Biological meaning and limitations",
        """
        <p><strong>What we can claim:</strong></p>
        <ul>
        <li>Chirality acts as a control knob in particle models -- clearly demonstrated.</li>
        <li>A chiral source introduces detectable pattern asymmetry in Gray-Scott -- demonstrated as a toy model.</li>
        <li>Both effects arise from the same principle: broken symmetry propagates to macroscopic structure.</li>
        </ul>
        <p><strong>What we cannot claim:</strong></p>
        <ul>
        <li>The omega parameter maps to any specific microswimmer without calibration.</li>
        <li>The chiral source models any specific signaling pathway in biology.</li>
        <li>The Gray-Scott equations describe any particular biochemical system quantitatively.</li>
        </ul>
        <p><strong>Next steps:</strong>
        Hydrodynamic coupling. Comparison to experimental microswimmer data.
        A biologically motivated chiral source (e.g., Nodal signaling gradient).
        Ensemble averaging for statistical rigor.</p>
        """,
        notes=(
            "End with honest science. Don't oversell. "
            "The hackathon judges are scientists -- they respect careful language. "
            "Briefly mention that all code is reproducible (fixed seeds, smoke test passes). "
            "Offer to demo any tab. "
            "30-45 seconds."
        ),
    )

    _rule()

    # File list
    with st.expander("Exact output files to show during live demo"):
        st.markdown(
            "```\n"
            "outputs/demo/baseline_active_brownian.png\n"
            "outputs/demo/vicsek_flocking.png\n"
            "outputs/demo/chiral_vortex_gas.png\n"
            "outputs/demo/boundary_edge_current.png\n"
            "outputs/demo/racemic_competition.png\n"
            "outputs/demo/gray_scott_spots.png\n"
            "outputs/demo/gray_scott_labyrinth.png\n"
            "outputs/demo/feed_gradient_pattern.png\n"
            "outputs/demo/obstacle_disrupted_pattern.png\n"
            "outputs/demo/chiral_source_pattern.png\n"
            "outputs/phase_sweeps/particle_swirl_index.png\n"
            "outputs/phase_sweeps/pattern_strength_F_k.png\n"
            "outputs/videos/chiral_vortex_gas.gif\n"
            "outputs/videos/boundary_edge_current.gif\n"
            "outputs/videos/gray_scott_growth.gif\n"
            "```\n"
        )

    with st.expander("Backup demo plan (if live simulation fails)"):
        st.markdown(
            "1. Open `outputs/demo/*.png` directly in a file viewer.\n"
            "2. Open `outputs/videos/*.gif` for animations.\n"
            "3. Open `notebooks/Chirality_Atlas_Colab.ipynb` in Colab (pre-run all cells).\n"
            "4. Fall back to the Phase Atlas tab which loads pregenerated .npz files.\n"
            "5. If Streamlit fails entirely: use Jupyter and `%matplotlib inline`.\n"
        )


# ============================================================
# Tab 7: Methods and Limits
# ============================================================

def tab_methods():
    st.markdown("## Methods and Limits")

    st.markdown("### Particle model equations")

    with st.expander("Active Brownian Particle (ABP)", expanded=True):
        st.latex(
            r"\theta_i(t + \Delta t) = \theta_i(t) + \sqrt{2 D_r \Delta t}\, \xi_i(t)"
        )
        st.latex(
            r"\mathbf{r}_i(t + \Delta t) = \mathbf{r}_i(t) + v_0 \begin{pmatrix} \cos\theta_i \\ \sin\theta_i \end{pmatrix} \Delta t"
        )
        st.markdown(
            "**Parameters:** v0 = self-propulsion speed, Dr = rotational diffusivity.  \n"
            "**xi** is a standard normal random variable, independent per particle and time step.  \n"
            "No alignment interaction. Particles are non-interacting except through boundaries."
        )

    with st.expander("Chiral ABP extension"):
        st.latex(
            r"\theta_i(t + \Delta t) = \theta_i(t) + \omega_i \Delta t + \sqrt{2 D_r \Delta t}\, \xi_i(t)"
        )
        st.markdown(
            "**omega_i** is the per-particle rotation rate. omega > 0 = right-handed (clockwise in standard coords).  \n"
            "Chirality modes: *none* (omega=0), *right* (+|omega|), *left* (-|omega|), "
            "*racemic* (half each), *random* (N(0, |omega|)).  \n"
            "The radius of the circular orbit is R_c = v0 / |omega|."
        )

    with st.expander("Vicsek model with chirality"):
        st.latex(
            r"\bar{\theta}_i = \mathrm{atan2}\!\left(\sum_{|r_{ij}|<R}\sin\theta_j,\; \sum_{|r_{ij}|<R}\cos\theta_j\right)"
        )
        st.latex(
            r"\theta_i(t + \Delta t) = \bar{\theta}_i + \omega_i \Delta t + \eta \, U[-\pi, \pi]"
        )
        st.markdown(
            "**R** = alignment radius. **eta** = noise amplitude.  \n"
            "Distances use the minimum-image convention for periodic boundaries.  \n"
            "Chirality competes with alignment: high omega reduces polar order."
        )

    _rule()
    st.markdown("### Pattern formation equations")

    with st.expander("Gray-Scott model", expanded=True):
        st.latex(
            r"\frac{\partial u}{\partial t} = D_u \nabla^2 u - uv^2 + F(1-u)"
        )
        st.latex(
            r"\frac{\partial v}{\partial t} = D_v \nabla^2 v + uv^2 - (F+k)v"
        )
        st.markdown(
            "**u** = substrate species (feed F, consumed by reaction).  \n"
            "**v** = activator species (created by reaction, removed at rate F+k).  \n"
            "**Du > Dv** required for Turing instability.  \n"
            "Discretized with explicit Euler (dt=1, dx=1) and periodic Laplacian via `np.roll`.  \n"
            "Stability requires Du * dt / dx^2 < 0.25 in 2D."
        )

    with st.expander("Feed gradient and obstacle extensions"):
        st.markdown(
            "**Feed gradient:** F(x) = F_left + (F_right - F_left) * x/L.  \n"
            "Different x-regions fall in different Gray-Scott parameter regimes, "
            "creating a macroscopic phase boundary.  \n\n"
            "**Circular obstacle:** inside a circle of radius R_obs, "
            "u=1 and v=0 are enforced after each step. "
            "The reaction cannot occur there."
        )

    with st.expander("Chiral source (toy model)"):
        st.latex(
            r"v \mathrel{+}= S \exp\!\left(-\frac{|\mathbf{r} - \mathbf{r}_s(t)|^2}{2\sigma^2}\right) \Delta t"
        )
        st.latex(
            r"\mathbf{r}_s(t) = \left(0.5L + r_{orbit}\cos(\Omega t),\; 0.5L + r_{orbit}\sin(\Omega t)\right)"
        )
        st.markdown(
            "**S** = source strength. **Omega** = angular speed of the focal point.  \n"
            "This is a phenomenological construction, not derived from biology. "
            "It injects v-species at a rotating location, breaking left-right symmetry.  \n"
            "**Not a model of any specific organism.**"
        )

    _rule()
    st.markdown("### Metrics")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown(
            "**Polar order phi**  \n"
            r"phi = |mean(exp(i*theta))| = sqrt(mean(cos theta)^2 + mean(sin theta)^2)"
            "\n\nRange [0,1]. phi=1 means all particles point the same way (flock).  \n\n"
            "**Swirl index**  \n"
            "Average dot product of particle velocity direction with the tangent to a circle "
            "around the box center. Positive = CCW, negative = CW.  \n\n"
            "**Boundary accumulation**  \n"
            "Fraction of particles within 0.5 units of any wall."
        )
    with col_m2:
        st.markdown(
            "**Pattern strength**  \n"
            "std(v). Near zero = homogeneous state. 0.10-0.15 = well-developed spots or stripes.  \n\n"
            "**Cluster count**  \n"
            "Connected regions where v > 0.1 (scipy.ndimage.label). "
            "Few large = labyrinths. Many small = spots.  \n\n"
            "**LR asymmetry**  \n"
            "mean(v[x > L/2]) - mean(v[x < L/2]). "
            "Near zero for symmetric patterns. "
            "Nonzero if chiral source or feed gradient biases one side."
        )

    _rule()
    st.markdown("### LLM workflow")

    st.markdown(
        "Following the tutorial's prompt-run-test-modify-critique cycle:  \n\n"
        "1. **Prompt** a specific, narrow change ('add omega_i * dt to orientation update').  \n"
        "2. **Run** the modified code and check output.  \n"
        "3. **Test** that outputs are finite and physically sensible.  \n"
        "4. **Modify** if something is wrong or unexpected.  \n"
        "5. **Critique** the result -- does it match known physics? Are the claims supported?  \n\n"
        "See `docs/prompt_log.md` for a full record of the prompts used to build this project."
    )

    _rule()
    st.markdown("### Known limitations")

    lims = [
        ("O(N^2) scaling",
         "Vicsek neighbor search and soft repulsion loop over all pairs. "
         "Practical limit N ~ 400. Real-scale simulations use spatial data structures (cell lists)."),
        ("Explicit Euler instability",
         "Gray-Scott uses explicit Euler with dt=1.0. Stable at default parameters but "
         "will blow up for large Du or large dt. Check Du * dt / dx^2 < 0.25."),
        ("Chiral source is a toy model",
         "The rotating injection source is a phenomenological construction. "
         "It has no established connection to any biological signaling pathway."),
        ("MSD with periodic boundaries",
         "MSD underestimates displacement once particles travel more than L/2. "
         "Unwrapped trajectories would fix this but are not implemented."),
        ("Phase diagrams are coarse",
         "Default sweep grids are 6x6 with short run times. "
         "Fine-grained phase boundaries require denser grids and longer equilibration."),
        ("No hydrodynamics",
         "Particles do not interact through the fluid. Real microswimmers have "
         "long-range hydrodynamic interactions that can qualitatively change collective behavior."),
        ("Finite-size effects",
         "All simulations use finite box sizes. Phase boundaries shift with box size. "
         "Results should not be extrapolated to the thermodynamic limit."),
    ]

    for title, body in lims:
        with st.expander(title):
            st.markdown(body)


# ============================================================
# App header + main layout
# ============================================================

def main():
    # Compact top header (tabs take most space)
    svg_logo = _load_svg(os.path.join("assets", "logo.svg"))
    header_html = (
        f"<div style='display:flex;align-items:center;gap:10px;padding:0.4rem 0 0.6rem 0;'>"
        f"<div style='width:36px;height:36px;flex-shrink:0;'>{svg_logo}</div>"
        f"<div>"
        f"<span style='font-size:1.25rem;font-weight:700;color:#1F2421;font-family:Georgia,serif;'>"
        f"Chirality Atlas</span>"
        f"<span style='font-size:0.85rem;color:#888;font-style:italic;margin-left:10px;'>"
        f"Particles, patterns, and handedness in active matter.</span>"
        f"</div></div>"
    )
    st.markdown(header_html, unsafe_allow_html=True)

    tabs = st.tabs([
        "Overview",
        "Particle Lab",
        "Pattern Lab",
        "Bridge Lab",
        "Phase Atlas",
        "Presentation",
        "Methods & Limits",
    ])

    with tabs[0]:
        tab_overview()
    with tabs[1]:
        tab_particle_lab()
    with tabs[2]:
        tab_pattern_lab()
    with tabs[3]:
        tab_bridge_lab()
    with tabs[4]:
        tab_phase_atlas()
    with tabs[5]:
        tab_presentation_mode()
    with tabs[6]:
        tab_methods()


if __name__ == "__main__":
    main()
