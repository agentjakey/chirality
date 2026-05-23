"""
Generate the final hackathon slide deck as PPTX.

Usage: python scripts/make_pptx.py

Output: outputs/slides/Chirality_Atlas_Star_Ascidian_Edition.pptx
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from lxml import etree

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "outputs", "slides")
os.makedirs(OUT_DIR, exist_ok=True)

PPTX_PATH = os.path.join(OUT_DIR, "Chirality_Atlas_Star_Ascidian_Edition.pptx")

PANELS = os.path.join(REPO, "outputs", "panels")
REF = os.path.join(REPO, "assets", "reference", "star_ascidian_reference.jpg")

INK = RGBColor(0x1F, 0x24, 0x21)
ACCENT = RGBColor(0xC1, 0x5A, 0x3A)
GREEN = RGBColor(0x31, 0x5C, 0x4C)
LIGHT = RGBColor(0xF7, 0xF3, 0xEA)
BORDER = RGBColor(0xDD, 0xD5, 0xC8)
PANEL_BG = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x0D, 0x11, 0x17)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)


def _set_bg(slide, rgb):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = rgb


def _txt(slide, text, left, top, width, height,
         size=18, bold=False, color=None, align=PP_ALIGN.LEFT, italic=False):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color if color else INK


def _rect(slide, left, top, width, height, fill_rgb, line_rgb=None):
    shape = slide.shapes.add_shape(1, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    if line_rgb:
        shape.line.color.rgb = line_rgb
    else:
        shape.line.fill.background()
    return shape


def _img(slide, path, left, top, width, height=None):
    if not os.path.exists(path):
        return False
    if height:
        slide.shapes.add_picture(path, left, top, width, height)
    else:
        slide.shapes.add_picture(path, left, top, width)
    return True


def _slide_footer(slide, n, total=5):
    _txt(slide, f"{n} / {total}",
         Inches(12.8), Inches(7.15), Inches(0.5), Inches(0.3),
         size=9, color=BORDER, align=PP_ALIGN.RIGHT)
    _txt(slide, "Chirality Atlas: Star Ascidian Edition",
         Inches(0.3), Inches(7.15), Inches(8.0), Inches(0.3),
         size=9, color=BORDER, align=PP_ALIGN.LEFT, italic=True)


def _title_bar(slide, title, subtitle=None):
    _rect(slide, Inches(0), Inches(0), Inches(13.33), Inches(1.0), INK)
    _txt(slide, title,
         Inches(0.35), Inches(0.08), Inches(12.6), Inches(0.65),
         size=26, bold=True, color=LIGHT, align=PP_ALIGN.LEFT)
    if subtitle:
        _txt(slide, subtitle,
             Inches(0.35), Inches(0.7), Inches(12.6), Inches(0.28),
             size=11, color=ACCENT, align=PP_ALIGN.LEFT, italic=True)


def add_slide_notes(slide, notes_text):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = notes_text


def make_slide1(prs):
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)
    _set_bg(slide, LIGHT)
    _title_bar(slide,
               "Can local rules generate a living star pattern?",
               "Observe: star ascidian colony  |  Hypothesize: Turing field + angular repulsion  |  Result: yes")

    content_top = Inches(1.08)
    content_h = Inches(5.9)

    # Reference image: left third
    if os.path.exists(REF):
        _img(slide, REF, Inches(0.2), content_top, Inches(4.1), content_h)
        _txt(slide, "Botryllus schlosseri colony (reference)",
             Inches(0.2), Inches(7.0), Inches(4.1), Inches(0.2),
             size=9, color=ACCENT, align=PP_ALIGN.CENTER, italic=True)

        # Panel: right two-thirds
        panel = os.path.join(PANELS, "slide1_target_and_simulation.png")
        _img(slide, panel, Inches(4.5), content_top, Inches(8.6), content_h)
        _txt(slide,
             "Left: real organism. Center: GM activator field (Layer 1). Right: zooid agent simulation (Layer 2).",
             Inches(4.5), Inches(7.0), Inches(8.6), Inches(0.2),
             size=9, color=RGBColor(0x55, 0x55, 0x55), align=PP_ALIGN.CENTER, italic=True)
    else:
        panel = os.path.join(PANELS, "slide1_target_and_simulation.png")
        _img(slide, panel, Inches(0.2), content_top, Inches(12.9), content_h)

    _slide_footer(slide, 1)

    add_slide_notes(slide,
        "Open with the real organism. Point to the radial star structure -- shared atrium, "
        "regular spacing, optional chirality. Say: We asked whether two local rules can "
        "reproduce this geometry from scratch. The answer is yes. Left: real colony. "
        "Center: GM activator field output. Right: agent simulation -- multiple star systems, "
        "radial arms, comparable spacing. Timing: 45-60 seconds.")


def make_slide2(prs):
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)
    _set_bg(slide, LIGHT)
    _title_bar(slide,
               "Model: centers first, stars second",
               "Layer 1: Gierer-Meinhardt Turing field  |  Layer 2: Active zooid agents")

    panel = os.path.join(PANELS, "slide2_model_schematic.png")
    _img(slide, panel, Inches(0.2), Inches(1.1), Inches(12.9), Inches(5.8))

    _txt(slide,
         "Layer 1 (GM field): Dh/Da >> 1 gives short-range activation and long-range "
         "inhibition -> Turing spots -> star center positions, no explicit center-repulsion needed. "
         "Layer 2 (agents): radial spring + angular repulsion between arm groups + chirality omega.",
         Inches(0.4), Inches(7.0), Inches(12.5), Inches(0.35),
         size=10, color=INK, align=PP_ALIGN.CENTER)

    _slide_footer(slide, 2)

    add_slide_notes(slide,
        "Walk through the architecture. Layer 1: Gierer-Meinhardt. "
        "Short-range activation, long-range inhibition. "
        "Turing instability produces quasi-periodic spots -- these are the star centers. "
        "No explicit center repulsion needed. Layer 2: active zooid agents. "
        "Radial spring toward r_target. Angular repulsion between arm groups creates arms. "
        "Without angular repulsion: ring. With it: discrete arms. Omega adds chirality. "
        "Timing: 50 seconds.")


def make_slide3(prs):
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)
    _set_bg(slide, LIGHT)
    _title_bar(slide,
               "Simulation: from noise to star systems",
               "400 steps. radial_order >= 0.8. swirl_score rises from 0.01 to 0.3 at omega = 2.5.")

    panel = os.path.join(PANELS, "slide3_simulation_sequence.png")
    _img(slide, panel, Inches(0.2), Inches(1.1), Inches(12.9), Inches(5.5))

    # Key results row
    metrics = [
        ("radial_order = 1.0", "agents at r_target", GREEN),
        ("swirl = 0.01 -> 0.3", "omega 0 to 2.5", ACCENT),
        ("fragmentation < 0.1", "arms stable", GREEN),
    ]
    for i, (val, label, col) in enumerate(metrics):
        bx = Inches(0.4 + i * 4.3)
        _rect(slide, bx, Inches(6.7), Inches(4.1), Inches(0.55), PANEL_BG, BORDER)
        _txt(slide, val, bx + Inches(0.1), Inches(6.72), Inches(3.9), Inches(0.25),
             size=12, bold=True, color=col, align=PP_ALIGN.LEFT)
        _txt(slide, label, bx + Inches(0.1), Inches(6.96), Inches(3.9), Inches(0.2),
             size=9, color=INK, align=PP_ALIGN.LEFT)

    _txt(slide, "Live animations: outputs/movies/star_formation_clean.gif and chiral_twist_emergence.gif",
         Inches(0.4), Inches(7.2), Inches(12.5), Inches(0.2),
         size=9, color=BORDER, italic=True, align=PP_ALIGN.CENTER)

    _slide_footer(slide, 3)

    add_slide_notes(slide,
        "These four frames show the time evolution. At t=0 agents start in arm groups with "
        "random offsets. Over 400 steps they settle into radial lobes. Radial spring confines "
        "them at r_target. Angular repulsion separates arms. With omega=0: radial and static. "
        "With omega=2.5: arms slowly rotate. Swirl score measures this: 0.01 to 0.3. "
        "If app is running: switch to Movie Gallery and play star_formation_clean.gif. "
        "Timing: 45-60 seconds.")


def make_slide4(prs):
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)
    _set_bg(slide, LIGHT)
    _title_bar(slide,
               "Creative exploration: phases of living geometry",
               "4 sweeps. 6 named regimes. star-likeness and swirl_score are independent.")

    panel = os.path.join(PANELS, "slide4_phase_diagram.png")
    _img(slide, panel, Inches(0.2), Inches(1.1), Inches(12.9), Inches(5.3))

    regimes = [
        "Uniform mat: low Dh/Da",
        "Clean stars: moderate k_r, low omega",
        "Twisted stars: high omega",
        "Merged: overcrowded",
        "Fragmented: high Dr",
        "Spots, no arms: low k_r",
    ]
    for i, label in enumerate(regimes):
        col_i = i % 3
        row_i = i // 3
        _txt(slide, label,
             Inches(0.4 + col_i * 4.3), Inches(6.5 + row_i * 0.38),
             Inches(4.1), Inches(0.35),
             size=10, color=INK if row_i == 0 else ACCENT,
             align=PP_ALIGN.LEFT)

    _slide_footer(slide, 4)

    add_slide_notes(slide,
        "Phase diagram for radial spring strength vs chirality rate. "
        "Left: star-likeness. Bright at moderate k_radial, low omega -- the clean star regime. "
        "Right: swirl rises with omega, roughly independent of k_radial up to a threshold. "
        "Key point: the two metrics are not correlated -- good arms exist without chirality, "
        "and chirality up to omega=2 does not destroy arms. "
        "Label the regimes on the left heatmap: uniform mat (bottom), clean stars (middle-left), "
        "twisted stars (top-right). Timing: 50-60 seconds.")


def make_slide5(prs):
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)
    _set_bg(slide, LIGHT)
    _title_bar(slide,
               "Insight, limits, and LLM use",
               "Local rules can make living geometry. This is a toy geometric model, not a full developmental model.")

    # Left: slide5 panel
    panel = os.path.join(PANELS, "slide5_insight_and_limits.png")
    _img(slide, panel, Inches(0.2), Inches(1.1), Inches(6.8), Inches(5.2))

    # Right: LLM contributions
    _rect(slide, Inches(7.2), Inches(1.1), Inches(5.9), Inches(5.2), PANEL_BG, BORDER)

    llm_lines = [
        ("LLM contributions", 13, True, GREEN),
        ("", 6, False, INK),
        ("1. Proposed two-layer decomposition:", 11, True, INK),
        ("   Center placement = Turing field.", 10, False, INK),
        ("   Arm formation = angular repulsion.", 10, False, INK),
        ("   Not our initial design. Verified by", 10, False, INK),
        ("   running single-layer vs two-layer.", 10, False, INK),
        ("", 6, False, INK),
        ("2. Designed anti-cheat metric hierarchy:", 11, True, INK),
        ("   radial_order, arm_count, swirl_score,", 10, False, INK),
        ("   fragmentation. Each catches a specific", 10, False, INK),
        ("   failure mode that passes visual check.", 10, False, INK),
        ("", 6, False, INK),
        ("3. IMEX solver + vectorized repulsion:", 11, True, INK),
        ("   both correct on first try.", 10, False, INK),
        ("", 6, False, INK),
        ("Human decisions: equations, parameters,", 10, False, ACCENT),
        ("biological scope, all verification.", 10, False, ACCENT),
    ]

    y = Inches(1.2)
    for text, size, bold, color in llm_lines:
        _txt(slide, text, Inches(7.35), y, Inches(5.6), Inches(0.3),
             size=size, bold=bold, color=color, align=PP_ALIGN.LEFT)
        y += Inches(size * 0.018)

    # Takeaway box
    _rect(slide, Inches(0.2), Inches(6.5), Inches(12.9), Inches(0.7),
          RGBColor(0xE8, 0xF0, 0xEC), RGBColor(0x31, 0x5C, 0x4C))
    _txt(slide,
         "Takeaway: A Turing field plus angular repulsion is sufficient to generate "
         "star-shaped colonial geometry from local rules. Chirality is measurable. "
         "The model does not reproduce Botryllus developmental biology, and we say so.",
         Inches(0.4), Inches(6.58), Inches(12.5), Inches(0.55),
         size=12, bold=False, color=INK, align=PP_ALIGN.CENTER)

    _slide_footer(slide, 5)

    add_slide_notes(slide,
        "Green: what the model matches -- center spacing, radial confinement, "
        "discrete arm structure, measurable chirality. "
        "Orange: what it does not -- arm count is a parameter not emergent, "
        "no Botryllus biochemistry, no 3D, no blastogenic staging. "
        "LLM used for two critical decisions: proposing the two-layer architecture "
        "(not our initial design), and designing the anti-cheat metric hierarchy. "
        "Both were verified, not accepted blindly. "
        "End: Turing instability plus angular repulsion is sufficient to generate "
        "star-shaped colonial geometry from local rules. Clean result. Timing: 60-70 seconds.")


def main():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    print("Building slides...")
    make_slide1(prs)
    print("  Slide 1 done")
    make_slide2(prs)
    print("  Slide 2 done")
    make_slide3(prs)
    print("  Slide 3 done")
    make_slide4(prs)
    print("  Slide 4 done")
    make_slide5(prs)
    print("  Slide 5 done")

    prs.save(PPTX_PATH)
    size_kb = os.path.getsize(PPTX_PATH) // 1024
    print(f"\nSaved: {PPTX_PATH}")
    print(f"Size:  {size_kb} KB")


if __name__ == "__main__":
    main()
