# Agent Handoff: Image → 2D Patterns → 3D Rigged Garment Pipeline (2-Layered Shirt)

## 1. Objective
Resume the **Image → Semantic Deconstruction → GarmentCode 2D Patterns → 3D Draped & EveryWear-Rigged Mesh** pipeline, picking right back up on the **2-Layered Shirt** (`layer_1_inner_turtleneck` + `layer_2_outer_oversized_tee`) for the **Sion Female Avatar** (`152.4 cm`, A-pose):
1. Fix the sleeve/shoulder geometry and drape on **Layer 2** (`layer_2_outer_oversized_tee` — charcoal-gray oversized short-sleeve crew-neck tee).
2. Drape **Layer 1** (`layer_1_inner_turtleneck` — light-blue long-sleeve standing-collar tunic) and **Layer 2 over Layer 1** on the Sion female avatar (`sion_avatars/sion-female-apose.obj`).
3. Rig and export the combined 2-layer shirt via the newly hardened **188-bone EveryWear → `sion-avatar` pipeline** and verify it in the live `sion-avatar` fitting viewport (`http://127.0.0.1:8095/fitting/`).


## Progress update — 2026-10-21

**The original two-layer shirt deliverable is complete, and the animation repair
has shipped in `sion-avatar`.** The owner reports that the shirt no longer visibly
clips during movement. The October 18 diagnosis below describes the pre-repair
runtime and is retained as historical evidence, not the current blocker.

Completed: corrected sleeve/neckline patterns; both physical layers draped together;
front/side/back visual review; 188-bone EveryWear rigging and GLB export; import as
`layered-shirt:top`; body-shape and sampled motion validation.

The runtime repair is committed in sibling repository
`/Users/vaz/Desktop/antigravity_apps/sion-avatar`, commit
`b7fdfda8925833c468e20b1e2c3542b209095637` (2026-10-20,
`fix(fitting): bind authored inner cloth to posed outer surfaces`). Its
`fitting/src/core/cloth-binding.mjs` binds authored inner cloth to the actual posed
outer triangles, maintains a 3 mm local gap, and leaves exposed collars, cuffs and
hems free. The viewer and motion checks share `skinDressed`. Physical layer order
also informs the visible coverage checker, including openings.

Recorded validation in `sion-avatar/fitting/README.md`: shirt alone and with
`shibu:bottom`, 25 posed samples plus rest per item set, 16 views, 2 mm pixels,
default/smallest/largest bodies. Blue-through-black pixel totals fell from
2,720 to 340 on default (87.5%), 11,682 to 1,221 on smallest, and 1,940 to 393 on
largest. These are visible coverage measurements, not triangle-intersection
counts, and cannot be directly compared with the October 18 triangle report.
Small edge artifacts and some skin/cross-item pixels remain. The recorded full
fitting suite passed 277 tests; local geometry renders were reviewed. The owner’s
subsequent live observation supplies the current movement confirmation.

**Remaining scope:** this is a completed shirt proof of concept with a runtime
motion repair, not a fully automated image-to-any-garment service. Generalizing
semantic deconstruction/pattern translation, preserving explicit physical-layer
contracts through every export, and a broader motion/body/contact acceptance gate
remain pipeline work. A fresh post-repair triangle audit would be needed to claim
zero physical intersections; the old report has not been rerun against the repair.
The largest-body collar issue and stale-import warnings recorded below should be
rechecked separately before claiming they are resolved.

Sections 3–4 below are the original task list and have been completed; use this
update and the current result section as the current status.

## Motion correction — 2026-10-18

**Historical pre-repair finding (superseded by the October 21 update above).**
The earlier zero-poke Idle result below checked skin and
separate items, not the shirt's two internal physical layers. Direct triangle
checks now reproduce internal crossings in every sampled moving clip while A/T
poses stay clean. Raw eight-influence EveryWear weights already fail; conversion
can aggravate the failure. See [LAYERED_MOTION_ROOT_CAUSE.md](LAYERED_MOTION_ROOT_CAUSE.md)
for stage isolation, measured evidence, validation limits and pipeline requirements.
Do not interpret the static completion below as animation acceptance.

## Current result — 2026-10-18

The combined two-layer shirt is draped, rigged, exported and imported into the
live fitting app as **Layered Shirt** (`layered-shirt:top`, outfit `layered-shirt`).
This section supersedes the old pending-work descriptions below.

- Final native garment: `out/layered_tops_test/layered_tops_both_draped.zprj` and `.obj`.
- Final portable asset: `out/layered_tops_test/layered_tops_both_rigged.glb`.
- Final front/side/back studio previews: `out/layered_tops_test/layered_tops_both_renders/`.
- Live app screenshots: `out/layered_tops_test/fitting_front.png`, `fitting_back.png`,
  `fitting_smallest.png`, `fitting_largest.png`.
- Live preview: http://127.0.0.1:8095/fitting/?gender=female&item=layered-shirt%3Atop&view=textures&cam=front&wear=layered-shirt%3Atop
- 20 panels (12 inner + 8 outer), 40 original GarmentCode sewing rules,
  26,726 vertices; 188 bones, zero unweighted vertices, maximum weight sum error
  5.13e-8. EveryWear preserved the drape within 0.00049 mm.
- Native MD drape: **zero body and zero inter-layer triangle intersections**
  (`layered_tops_collision_check.json`). The full front/side/back images were visually reviewed.
- Earlier runtime check: zero **skin/separate-item** poke-through points at
  default and smallest shapes; zero at rest and three sampled Idle moments.
  This did not check internal cloth layers; the motion result is superseded above.
- **Known minor limit:** the all-sliders-largest shape has three neck points
  penetrating the collar by 2.6–3.1 mm under the enlarged head. No torso, sleeve
  or hem spots were reported. This was also inspected in the live viewport.
- `fitting_check.json` and `fitting_motion_check.json` retain the full reports.
  Their global `ok` also reflects 11 pre-existing stale-import/catalog-edit
  warnings unrelated to this garment; the motion report has zero poke points.

Corrections made:

1. `CreatePatternWithPoints` on the installed MD build **ignores type-1 points**;
   the pasted continuation's claim that they split segments was not reproduced.
   Curves now use explicit type-0 samples at equal arc-length fractions, with an
   original-edge → MD segment map and reversed paired subsegment order.
   MD line counts and every sewing API return are checked.
2. Native arrangement centers each half-panel independently, so matching both
   halves to torso center points caused overlap at face height. Explicit body
   offsets now separate halves and preserve drafted height. MD's body cylinder
   uses front left/right X=35/65, back left/right X=15/85.
3. The neck cylinder has a different origin: front X=0 and back X=50 by default.
   Collar front left/right use X=87/13, back left/right X=62/38. Copying the body
   offsets sent the collar through the neck. The corrected collar is clean.
4. Sewing uses `reverse=True` for these GarmentCode boundaries. A comparison run
   with False collapsed the garment; it was rejected by visual inspection.
5. Inner length is 1.62, width 1.05, flare 1.15; neckline width -0.20,
   front depth -0.22, back depth -0.16, standing collar depth 3 cm.
   The resulting collar circumference is 24.19 cm on a 22.4 cm neck.
   These negative *normalized neckline controls* offset Shirt's shoulder-depth
   compensation; garment ease stays positive. Outer width is 1.12, length 1.38,
   flare 1.06, neckline width 0.28, front/back depths -0.10/-0.05 (~36 cm opening).
6. `SetPatternPieceName` preserves exact panel identities in OBJ groups. Layer
   colors survive into the GLB. MD logs and export freshness are checked.

Reproduction from the GarmentCode root:

```sh
.venv/bin/python sion_pipeline/test_compile_shirt_layers.py
.venv/bin/python -m unittest sion_pipeline.test_md_boundary_mapping
.venv/bin/python sion_pipeline/drape_marvelous.py --layer both --sim-steps 360
/Applications/MarvelousDesigner.app/Contents/MacOS/MarvelousDesigner_PER -headless "$PWD/sion_pipeline/rig_layered_everywear.py" -headlesslog
/Users/vaz/.local/bin/blender -b --factory-startup -P sion_pipeline/everywear_to_glb.py -- sion_pipeline/out/layered_tops_test/layered_tops_both_everywear.fbx sion_pipeline/out/layered_tops_test/layered_tops_both_everywear.obj sion_pipeline/out/layered_tops_test/layered_tops_both_rigged.glb
/Users/vaz/.local/bin/blender -b --factory-startup -P sion_pipeline/inspect_md_drape.py -- sion_pipeline/out/layered_tops_test/layered_tops_both_draped.obj sion_avatars/sion-female-apose.obj --output sion_pipeline/out/layered_tops_test/layered_tops_collision_check.json
```

Import **all 20 primitives (`prim-0-0` through `prim-0-19`)**, not `Cloth`,
using `import-garment.mjs --as layered-shirt:top --slot top --gender female
--weights source --pose a --name "Layered Shirt" --outfit "Layered Shirt"`.
Then run `prepare-fit.mjs female` and `fit-check.mjs female --outfit layered-shirt`.
The app's global source code and unrelated imports were not changed.


---

## 2. What Was Completed Before This Handoff

### A. Multi-Stage *Modelista* Pipeline Architecture & Stage 0 Prompt
- **Master Architecture Plan:** [`/Users/vaz/Downloads/IMAGE_TO_FANTASY_GOWN_IMPLEMENTATION_PLAN.md`](file:///Users/vaz/Downloads/IMAGE_TO_FANTASY_GOWN_IMPLEMENTATION_PLAN.md)
  - **Call 0 (Stage 0 — Semantic Deconstruction):** Vision model reads the reference garment image and outputs `<name>_deconstruction.md`, decomposing the outfit into $N$ ordered physical 3D layers (`Layer 1` innermost $\rightarrow$ `Layer N` outermost) and detailing silhouette, seams, darts, collars, sleeves, and material behavior without writing code or YAML.
  - **Rule on Materials vs. Layers:** Co-extensive/bonded materials sharing the same 2D pattern outline (e.g., lace bonded to satin lining) are **1 physical layer** (`N = 1`), whereas overlapping pieces with independent movement/drape (e.g., inner long-sleeve turtleneck under an outer short-sleeve tee) are **separate layers** (`Layer 1`, `Layer 2`).
  - **Stages 1–4 (*Modelista* Flat-Pattern Translation):** Map each layer from `<name>_deconstruction.md` into GarmentCode (`pygarment`) `design.yaml` parameters (`MetaGarment`), serialize the 2D pattern (`<name>_pattern.png` + `<name>_specification.json`), visually inspect the 2D pattern, and drape in 3D.
- **Standalone Stage 0 Prompt:** [`sion_pipeline/STAGE_0_DECONSTRUCTION_PROMPT.md`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/STAGE_0_DECONSTRUCTION_PROMPT.md)
  - Tested and validated on both the **2-Layered Shirt** (2 layers) and the **Emerald Couture Gown** (3 layers).

### B. 2-Layered Shirt Compilation (`test_compile_shirt_layers.py`)
- **Script:** [`sion_pipeline/test_compile_shirt_layers.py`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/test_compile_shirt_layers.py)
- **Body Measurements Used:** [`sion_pipeline/kit/sion_female_default.yaml`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/kit/sion_female_default.yaml) (`height: 152.4 cm`, `arm_pose_angle: 46.0°`).
- **Compiled Pattern Outputs:**
  - **Layer 1 (Inner Light-Blue Long-Sleeve Turtleneck Tunic — 12 panels, 28 stitches):**
    - Directory: [`sion_pipeline/out/layered_tops_test/layer_1_inner_turtleneck/`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/out/layered_tops_test/layer_1_inner_turtleneck/)
    - Files: `layer_1_inner_turtleneck_pattern.png`, `layer_1_inner_turtleneck_specification.json`, `layer_1_inner_turtleneck_design.yaml`.
  - **Layer 2 (Outer Charcoal-Gray Oversized Short-Sleeve Tee — 8 panels, 16 stitches):**
    - Directory: [`sion_pipeline/out/layered_tops_test/layer_2_outer_oversized_tee/`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/out/layered_tops_test/layer_2_outer_oversized_tee/)
    - Files: `layer_2_outer_oversized_tee_pattern.png`, `layer_2_outer_oversized_tee_specification.json`, `layer_2_outer_oversized_tee_design.yaml`.
  - **Initial Single-Layer Drape Test of Layer 2:**
    - Directory: [`sion_pipeline/out/layer_2_outer_oversized_tee/`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/out/layer_2_outer_oversized_tee/)
    - Render: [`layer_2_outer_oversized_tee_front.png`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/out/layer_2_outer_oversized_tee/layer_2_outer_oversized_tee_front.png)

### C. End-to-End 188-Bone EveryWear & `sion-avatar` Multi-Layer Fixes (Completed & Verified on Macaw Dress)
All pipeline bugs blocking multi-piece/multi-layer garments in `sion-avatar` have now been solved, tested (31/31 unit tests passing in `dress.test.mjs`), and documented in [`MARVELOUS_DESIGNER_PYTHON_API_GUIDE.md`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/MARVELOUS_DESIGNER_PYTHON_API_GUIDE.md#127-headless-everywear-auto-rigging--skinned-fbxglb-export) and [`AGENTS.md`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/AGENTS.md):
1. **188-Bone VRoid Slider Rig (`export_188_fbx.py`):** Rotates `Sion-Female-Base-PreservedRig.vrm` $180^\circ$ around $Z$ to face $+Z$ and bakes the Pose-Mode A-pose into the rest pose (`DATA == POSE`) so `ew_set_exact_positions` does not unskin A-pose garments by $+37^\circ$.
2. **Per-Pattern Unwelded GLB Builder & Bleed Filter (`fbx_to_glb.py` & `import-vrm.mjs`):** Preserves unwelded pattern groups in `g <pattern>` order, filters cross-pattern welded FBX edges $> 20\text{ mm}$, and strips A-pose `UpperArm`/`Shoulder` and upward `Bust` proximity bleed on torso-dominant panels while preserving full arm weights on sleeve panels (`arm_share >= 0.35`).
3. **Cross-Layer Slider Smoothing (`shape-weights.mjs`):** Couples stacked/parallel garment layers across cloth thickness (`RADIUS = 0.045`, `CROSS_WEIGHT = 4`) with vertical span screening so inner layers never expand through outer layers under `chest-size` / `waist` / `hips` sliders.
4. **Runtime `dresser.dress()` Multi-Piece Invariants (`fitting/src/core/dress.mjs`):** Bypasses `followPiece`, `liftPiece`, and intra-garment `self` `clearLayer` on rig-bound (`vroid`) multi-piece tops/dresses while preserving `ownBody` skin clearance with a pinched-crease normal-inversion guard (`n_shaped · n_rest <= 0` in `slid()`).

---

## 3. Current Issue to Solve First: Why Layer 2's Sleeves Look Wrong

In [`layer_2_outer_oversized_tee_front.png`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/out/layer_2_outer_oversized_tee/layer_2_outer_oversized_tee_front.png), the user noted:
> *"the sleeves dont look correct."*

### Root Causes in [`sion_pipeline/test_compile_shirt_layers.py`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/test_compile_shirt_layers.py#L120-L151):
1. **Excessive `end_width` + `connecting_width` Causing Flared Bell Sleeves & Armpit Pinching:**
   - `layer_2_outer_oversized_tee` currently sets:
     - `sleeve.connecting_width: 0.35` (very deep armscye drop)
     - `sleeve.end_width: 1.10` (wider at the cuff than at the bicep, turning the short sleeve into a flared bell/trumpet sleeve that wings outward instead of hanging as a straight tubular oversized tee sleeve)
     - `collar.width: 0.45` and `collar.fc_depth: 0.45` (over-widened scoop neck that pushes the shoulder seam off the acromion and bunches at the top of the sleeve cap).
   - Compare with the verified reference tee in [`sion_pipeline/FINDINGS.md`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/FINDINGS.md) (`tee_apose_shallow` / `run.py`):
     - A clean crew-neck / relaxed short-sleeve tee on the Sion female avatar uses a moderate armscye (`connecting_width: 0.15–0.22`), straight or slightly tapered cylinder cuff (`end_width: 0.80–0.90`, not `1.10`), shallow sleeve cap (`connect_ruffle: 1.0`), and a balanced crew neck (`collar.width: 0.26–0.32`, `fc_depth: 0.28–0.34`) so the shoulder seam sits cleanly without bunching at the neck-shoulder junction.
2. **Only Layer 2 Was Draped (and without Layer 1 underneath):**
   - `layer_2_outer_oversized_tee_front.png` was rendered as a standalone blue mesh without **Layer 1** (`layer_1_inner_turtleneck`, light-blue long-sleeve high-neck tunic) underneath and without the two-tone materials (light-blue inner tunic + charcoal-gray outer tee).

---

## 4. Concrete Next Steps for the Next Agent

1. **Fix Layer 2 (`layer_2_outer_oversized_tee`) & Layer 1 (`layer_1_inner_turtleneck`) Parameters in [`sion_pipeline/test_compile_shirt_layers.py`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/test_compile_shirt_layers.py):**
   - Check [`sion_pipeline/FINDINGS.md`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/FINDINGS.md) and [`sion_pipeline/designs/`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/designs/) for the verified Sion female sleeve/neckline parameters (`tee_apose_shallow` / `tee_long`).
   - Adjust **Layer 2** (`layer_2_outer_oversized_tee`):
     - Reduce `collar.width` (`0.45` $\rightarrow$ `~0.28–0.32`) and `collar.fc_depth` (`0.45` $\rightarrow$ `~0.30–0.34`) so the shoulder seams sit flat on the shoulders instead of bunching at the neck corners, while still leaving room for Layer 1's turtleneck collar (`collar.width: 0.18–0.20`).
     - Adjust `sleeve.end_width` (`1.10` $\rightarrow$ `~0.85–0.92`) and `sleeve.connecting_width` (`0.35` $\rightarrow$ `~0.20–0.24`) so the short sleeves hang as clean, relaxed boxy cylinders rather than flared bells with underarm creases.
   - Re-compile both 2D patterns (`_pattern.png`) and visually inspect the sleeve caps, armscyes, and collar openings before 3D draping.
2. **Drape Both Layers on the Sion Female Avatar (`sion_avatars/sion-female-apose.obj`):**
   - Drape **Layer 1** (`layer_1_inner_turtleneck`, light-blue jersey) first so it settles cleanly against the Sion female avatar body from turtleneck collar down to the upper-thigh tunic hem and wrists.
   - Drape **Layer 2** (`layer_2_outer_oversized_tee`, charcoal-gray jersey) over Layer 1 (with `2–3 mm` outer layer offset or sequential MD layer arrangement) so the light-blue turtleneck collar, long sleeves, and lower tunic hem emerge cleanly from beneath the charcoal short-sleeve outer tee.
   - Render Front / Side / Back turnaround previews on the Sion female avatar and verify sleeve silhouette and layer separation.
3. **Auto-Rig via 188-Bone EveryWear & Verify in `sion-avatar` Live Viewport (`http://127.0.0.1:8095/fitting/`):**
   - Run headless EveryWear weight transfer against `sion-female-full-188-rigged-fixed.fbx` (`ew_transfer_weights(8)` + `ew_set_exact_positions`), convert to GLB via the `fbx_to_glb.py` pattern (note: because this garment has sleeves, `any(slot_is_sleeve)` will be `True`, so A-pose rest baking is used automatically), import into `sion-avatar` (`import-garment.mjs --weights source` + `prepare-fit.mjs female`), and verify in the live `/fitting/` viewport across body-shape sliders.

---

## 5. Key Files & References
- **Guides (Must-Read):**
  - [`AGENTS.md`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/AGENTS.md)
  - [`MARVELOUS_DESIGNER_PYTHON_API_GUIDE.md`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/MARVELOUS_DESIGNER_PYTHON_API_GUIDE.md) (especially Section 12.7 Step 5 for 188-bone EveryWear + `sion-avatar` multi-layer invariants)
  - [`sion_pipeline/FINDINGS.md`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/FINDINGS.md) (Sion female avatar tee/sleeve parameter findings)
- **Pipeline & Deconstruction Files:**
  - [`/Users/vaz/Downloads/IMAGE_TO_FANTASY_GOWN_IMPLEMENTATION_PLAN.md`](file:///Users/vaz/Downloads/IMAGE_TO_FANTASY_GOWN_IMPLEMENTATION_PLAN.md)
  - [`sion_pipeline/STAGE_0_DECONSTRUCTION_PROMPT.md`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/STAGE_0_DECONSTRUCTION_PROMPT.md)
  - [`sion_pipeline/test_compile_shirt_layers.py`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/test_compile_shirt_layers.py)
  - [`sion_pipeline/drape_blender.py`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/drape_blender.py) & [`sion_pipeline/drape_marvelous.py`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/drape_marvelous.py)
  - [`sion_pipeline/run.py`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/run.py)
- **Live `sion-avatar` Fitting Server:**
  - Running at `http://127.0.0.1:8095/fitting/` (repo: `/Users/vaz/Desktop/antigravity_apps/sion-avatar`).
