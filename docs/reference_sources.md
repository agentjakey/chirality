# Reference Sources: Star Ascidian Biological Reference

## Primary Reference Image

File: `assets/reference/star_ascidian_reference.jpg`

Used in:
- Streamlit app Tab 1 (Target Pattern) — displayed as the biological reference
- `outputs/panels/slide1_target_and_simulation.png` (left panel)
- `outputs/slides/` PPTX deck (Slide 1)

Source note: see `assets/reference/source_note.txt`

## Reference Video

URL: https://www.youtube.com/watch?v=FIQ6pxzuw2s

Do NOT embed, download, or display this video in the app or any output.
This URL is for citation and documentation purposes only.
The still image `star_ascidian_reference.jpg` was extracted from this source for reference purposes.

## Organism

Common name: Star ascidian
Scientific name: Botryllus schlosseri
Phylum: Chordata, Subphylum: Tunicata (Urochordata)
Class: Ascidiacea

Key features visible in reference image:
- Star-shaped colonial systems (5-10 zooids per star)
- Radial arms arranged around a shared central atrium
- Blue-gray translucent zooid bodies on a dark substrate
- Regular spacing between neighboring star systems
- Some stars show rotational orientation (potential chirality)

## Citation

If presenting this work, acknowledge the reference image source as a biological reference image
for Botryllus schlosseri morphology. The model does not claim to reproduce organism-specific
biochemistry, developmental staging, or immune recognition.

## What the model reproduces from the reference

- Colony-level tiling: multiple star systems with regular spacing (from GM Turing field)
- Radial zooid arrangement: agents at characteristic radius from center (radial_order metric)
- Discrete arm structure: angular repulsion between arm groups creates discrete lobes
- Optional chirality: omega parameter introduces measurable rotational bias (swirl_score)

## What the model does NOT reproduce from the reference

- Blue-gray translucent zooid bodies (color is representation only)
- 3D substrate attachment and curvature
- Blastogenic developmental cycle
- Colonial immune recognition (self/non-self fusion)
- Specific arm count (n_arms=7 is a parameter, not emergent)
- Hydrodynamic coupling between zooids
