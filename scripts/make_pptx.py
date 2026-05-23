"""
Generate the final hackathon slide deck as PPTX.

Usage: python scripts/make_pptx.py

Output: outputs/slides/Chirality_Atlas_Star_Ascidian_Edition.pptx
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Cm

import shutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "outputs", "slides")
os.makedirs(OUT_DIR, exist_ok=True)

PPTX_PATH = os.path.join(OUT_DIR, "Chirality_Atlas_Star_Ascidian_Edition.pptx")

PANELS = os.path.join(REPO, "outputs", "panels")
MOVIES = os.path.join(REPO, "outputs", "movies")
REF = os.path.join(REPO, "assets", "reference", "star_ascidian_reference.jpg")

INK = RGBColor(0x1F, 0x24, 0x21)
ACCENT = RGBColor(0xC1, 0x5A, 0x3A)
GREEN = RGBColor(0x31, 0x5C, 0x4C)
LIGHT = RGBColor(0xF7, 0xF3, 0xEA)
BORDER = RGBColor(0xDD, 0xD5, 0xC8)
DARK = RGBColor(0x0D, 0x11, 0x17)
BLUE = RGBColor(0x4A, 0x7B, 0xA8)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)


def _add_background(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def _txbox(slide, text, left, top, width, height,
           font_size=18, bold=False, color=None, align=PP_ALIGN.LEFT,
           italic=False):
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf = txb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color if color else INK
    return txb


def _label_box(slide, text, left, top, width, height, bg_color, text_color=None,
               font_size=9, bold=False):
    from pptx.util import Pt
    from pptx.enum.text import PP_ALIGN
    shape = slide.shapes.add_shape(
        1, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = BORDER
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = text_color if text_color else INK
    return shape


def _add_image_safe(slide, path, left, top, width, height=None):
    if os.path.exists(path):
        if height:
            slide.shapes.add_picture(path, left, top, width, height)
        else:
            slide.shapes.add_picture(path, left, top, width)
        return True
    return False


def _slide_number(prs, n, total=5):
    slide = prs.slides[-1]
    _txbox(slide, f"{n} / {total}",
           Inches(12.6), Inches(7.1), Inches(0.7), Inches(0.3),
           font_size=9, color=BORDER, align=PP_ALIGN.RIGHT)


def make_slide1(prs):
    """Slide 1: Can local rules generate a living star pattern?"""
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)
    _add_background(slide, LIGHT)

    _txbox(slide, "Can local rules generate a living star pattern?",
           Inches(0.4), Inches(0.18), Inches(12.5), Inches(0.9),
           font_size=32, bold=True, color=INK, align=PP_ALIGN.CENTER)

    _txbox(slide, "Chirality Atlas: Star Ascidian Edition",
           Inches(0.4), Inches(1.0), Inches(12.5), Inches(0.4),
           font_size=14, color=ACCENT, align=PP_ALIGN.CENTER, italic=True)

    # Reference image left
    ref_placed = False
    if os.path.exists(REF):
        slide.shapes.add_picture(REF, Inches(0.4), Inches(1.5), Inches(4.2), Inches(4.6))
        ref_placed = True

    # Panel right
    panel = os.path.join(PANELS, "slide1_target_and_simulation.png")
    if os.path.exists(panel):
        if ref_placed:
            slide.shapes.add_picture(panel, Inches(4.9), Inches(1.5), Inches(8.0), Inches(4.6))
        else:
            slide.shapes.add_picture(panel, Inches(0.4), Inches(1.5), Inches(12.5), Inches(5.2))

    # Caption row
    if ref_placed:
        _txbox(slide, "Botryllus schlosseri colony",
               Inches(0.4), Inches(6.2), Inches(4.2), Inches(0.4),
               font_size=10, color=ACCENT, align=PP_ALIGN.CENTER, italic=True)
        _txbox(slide, "Left: real colony. Center: GM field. Right: agent simulation.",
               Inches(4.9), Inches(6.2), Inches(8.0), Inches(0.4),
               font_size=10, color=BORDER, align=PP_ALIGN.LEFT, italic=True)
    else:
        _txbox(slide, "Left: target morphology. Center: GM activator field. Right: zooid agents.",
               Inches(0.4), Inches(6.2), Inches(12.5), Inches(0.4),
               font_size=10, color=BORDER, align=PP_ALIGN.CENTER, italic=True)

    _slide_number(prs, 1)


def make_slide2(prs):
    """Slide 2: Model -- centers first, stars second."""
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)
    _add_background(slide, LIGHT)

    _txbox(slide, "Model: centers first, stars second",
           Inches(0.4), Inches(0.18), Inches(12.5), Inches(0.7),
           font_size=30, bold=True, color=INK, align=PP_ALIGN.CENTER)

    panel = os.path.join(PANELS, "slide2_model_schematic.png")
    _add_image_safe(slide, panel, Inches(0.4), Inches(1.0), Inches(12.5))

    _txbox(slide,
           "Layer 1: Gierer-Meinhardt field places star centers via Turing instability (Dh >> Da). "
           "Layer 2: Active zooid agents form arms via radial spring + angular repulsion. "
           "Omega > 0 adds chirality.",
           Inches(0.6), Inches(6.7), Inches(12.1), Inches(0.6),
           font_size=11, color=INK, align=PP_ALIGN.CENTER)

    _slide_number(prs, 2)


def make_slide3(prs):
    """Slide 3: Simulation -- from noise to star systems."""
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)
    _add_background(slide, LIGHT)

    _txbox(slide, "Simulation: from noise to star systems",
           Inches(0.4), Inches(0.18), Inches(12.5), Inches(0.7),
           font_size=30, bold=True, color=INK, align=PP_ALIGN.CENTER)

    panel = os.path.join(PANELS, "slide3_simulation_sequence.png")
    _add_image_safe(slide, panel, Inches(0.4), Inches(1.0), Inches(12.5))

    _txbox(slide,
           "Arms self-organize from noise in ~400 steps. "
           "With omega=0: radial. With omega=2.5: arms rotate. "
           "Swirl score rises from 0.01 to 0.3. Radial order >= 0.8 at clean preset. "
           "Live animations: outputs/movies/star_formation_clean.gif and chiral_twist_emergence.gif",
           Inches(0.6), Inches(6.7), Inches(12.1), Inches(0.6),
           font_size=11, color=INK, align=PP_ALIGN.CENTER)

    _slide_number(prs, 3)


def make_slide4(prs):
    """Slide 4: Phase diagram -- creative exploration."""
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)
    _add_background(slide, LIGHT)

    _txbox(slide, "Creative exploration: phases of living geometry",
           Inches(0.4), Inches(0.18), Inches(12.5), Inches(0.7),
           font_size=30, bold=True, color=INK, align=PP_ALIGN.CENTER)

    panel = os.path.join(PANELS, "slide4_phase_diagram.png")
    _add_image_safe(slide, panel, Inches(0.4), Inches(1.0), Inches(12.5))

    regimes = [
        ("Low k_radial, any omega:", "uniform mat -- no arm structure"),
        ("High k_radial, low omega:", "clean stars -- best morphology"),
        ("High k_radial, high omega:", "twisted stars -- arms rotate"),
        ("Very high omega:", "merged/fragmented -- arm structure lost"),
    ]
    for i, (label, desc) in enumerate(regimes):
        _txbox(slide, f"{label} {desc}",
               Inches(0.6 + i * 3.2), Inches(6.7), Inches(3.1), Inches(0.6),
               font_size=9, color=INK, align=PP_ALIGN.CENTER)

    _slide_number(prs, 4)


def make_slide5(prs):
    """Slide 5: Insight, limits, and LLM use."""
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)
    _add_background(slide, LIGHT)

    _txbox(slide, "Insight, limits, and LLM use",
           Inches(0.4), Inches(0.18), Inches(12.5), Inches(0.7),
           font_size=30, bold=True, color=INK, align=PP_ALIGN.CENTER)

    panel = os.path.join(PANELS, "slide5_insight_and_limits.png")
    _add_image_safe(slide, panel, Inches(0.4), Inches(1.0), Inches(6.8))

    # LLM contribution box
    llm_text = (
        "LLM contributions:\n"
        "1. Proposed two-layer architecture (field + agents). Correct on first try.\n"
        "2. Wrote IMEX Gierer-Meinhardt solver. Unconditionally stable for diffusion.\n"
        "3. Vectorized angular repulsion with sign(dphi)=0 to zero same-arm force.\n"
        "4. Diagnosed broadcast error in swirl metric during smoke test.\n\n"
        "Human judgment:\n"
        "All equation choices, parameter values, and biological scope statements."
    )
    _txbox(slide, llm_text,
           Inches(7.4), Inches(1.0), Inches(5.5), Inches(4.0),
           font_size=11, color=INK, align=PP_ALIGN.LEFT)

    _txbox(slide,
           "Core result: A Turing field plus angular repulsion is sufficient to generate "
           "star-shaped colonial geometry from local rules. Chirality is measurable (swirl_score). "
           "Model does not reproduce Botryllus biochemistry, developmental biology, or 3D mechanics.",
           Inches(0.6), Inches(6.7), Inches(12.1), Inches(0.6),
           font_size=11, color=INK, align=PP_ALIGN.CENTER)

    _slide_number(prs, 5)


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
    print(f"\nSaved: {PPTX_PATH}")
    print(f"Size: {os.path.getsize(PPTX_PATH) // 1024} KB")


if __name__ == "__main__":
    main()
