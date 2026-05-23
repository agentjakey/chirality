# Demo Script: Chirality Atlas -- 2-Minute Live Walk-through

---

## Before you start

Have ready:
- Terminal with `streamlit run app.py` already running at http://localhost:8501
- Browser tab open on Tab 1 (Target Pattern)
- File explorer open at `outputs/panels/` as backup
- Notebook open at `notebooks/Star_Ascidian_Chirality_Atlas.ipynb` as backup

---

## Step 1 (15 sec): Open Target Pattern tab

Click Tab 1 -- "Target Pattern."

Say: "Here is the biological target. The left panel shows a schematic of Botryllus
schlosseri -- seven radial arms, one central atrium. The right panel shows our model
output at the same scale. We want to close that gap quantitatively."

[pause, let the image register]

---

## Step 2 (20 sec): Switch to Model Builder tab

Click Tab 2 -- "Model Builder."

Say: "This is the live model. You can see the parameters here: radial spring,
chirality, noise, number of arms. Everything is adjustable. By default we are
at omega equals zero -- no chirality."

[do not touch sliders yet]

---

## Step 3 (20 sec): Run clean stars

Click the "Run Simulation" button with default parameters.

Say: "The GM field runs first -- that produces the star centers you see in the
top panel. Then the zooid agents settle into arms around those centers. This takes
about 30 seconds."

Wait for the output to appear. When it does:

Say: "Radial order is above 0.8. The arms are there. You can see the agents
organized into lobes around each center."

---

## Step 4 (20 sec): Switch chirality slider

Move the omega slider to approximately 2.5. Click "Run Simulation" again.

Say: "Now we add chirality. Omega equals 2.5. Same forces, but every agent
rotates at that rate."

When the result appears:

Say: "The swirl score went from near zero to about 0.3. The arms are still there
but they are twisted. The model is doing what biology actually does."

---

## Step 5 (15 sec): Phase Explorer

Click Tab 3 -- "Phase Explorer."

Say: "This is the phase diagram. Green means good stars. The model works best at
high radial spring and low chirality. As omega increases, the color shifts -- swirl
increases but star quality stays reasonable until chirality is very high."

[point to the heatmap; do not run a live sweep in the demo]

---

## Step 6 (10 sec): LLM Lab Notebook

Click Tab 6 -- "LLM Notebook."

Say: "This tab documents the prompt-run-test-modify-critique workflow.
Two best prompts, one failure case, what the LLM got wrong and what human judgment
corrected. The full log is in docs/llm_proficiency.md."

---

## Total time: ~100 seconds. Leave 20 seconds for questions.

---

## Backup Plan

**App crashes:**
1. Open `outputs/panels/slide1_target_and_simulation.png` in file explorer (Slide 1).
2. Open `outputs/panels/slide4_phase_diagram.png` (Slide 4).
3. Run notebook sections 6 and 8 live. They regenerate the key figures in under 2 minutes.

**GIFs do not load:**
- `outputs/panels/slide3_simulation_sequence.png` is a static 4-panel sequence.
  Open it and walk through frames manually.

**Port 8501 blocked:**
- Run `streamlit run app.py --server.port=8502` to try a different port.
- Or open the notebook and run cells top to bottom.

**Slow machine:**
- Tab 1 is static and always loads immediately.
- Tab 4 (Movie Gallery) shows pre-generated GIFs with no computation.
- Skip the live Run in Tab 2 and use pregenerated assets only.
