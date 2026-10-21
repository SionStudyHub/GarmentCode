# Claude Code Assistant Guide: GarmentCode & Marvelous Designer Automation

Welcome. This document provides quick navigation and operational rules for working in this repository.

---

## 0. Which avatar to make clothes on (read first)

New clothes are for the Sion avatar builder
(`/Users/vaz/Desktop/antigravity_apps/sion-avatar`). **Drape and size them on its avatars, in
[`sion_avatars/`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_avatars/README.md):**
`sion-female-apose.obj` (152 cm) and `sion-male-apose.obj` (167 cm), in millimetres, A-pose, facing +Z.
- `new_base_female` (173 cm) is an older, taller body. Its `.vrm`, `.obj`, `assets/bodies/new_base_female.yaml`
  and every number taken from it (1738 mm, 1078 mm hem, the dimension tables) give the wrong size. They are
  kept as a reference for method only.
- For GarmentCode body measurements, use `sion_pipeline/kit/sion_female_default.yaml` or `sion_male_default.yaml`.
- The steps to bring a finished garment into the avatar builder are in
  [`sion_avatars/README.md`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_avatars/README.md).

---

## 1. Primary Mandate: Use GarmentCode for Clothing Generation

**GarmentCode (`pygarment`) is the primary CAD engine for generating clothing in this repository.**
- **Do NOT hand-code ad-hoc geometric coordinate arrays** for complete garments. Hand-crafted shapes lead to seam alignment failures, poor drape, and anatomical mismatches.
- Always use GarmentCode's parametric classes (`MetaGarment`, `FittedBodice`, `Pants`, `Tee`, etc.) driven by the Sion avatar's measurements (`sion_pipeline/kit/sion_female_default.yaml`; see section 0).
- To bridge GarmentCode designs into Marvelous Designer / CLO, use [`garmentcode_to_marvelous.py`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/garmentcode_to_marvelous.py) or reference [`create_marvelous_garmentcode_tee.py`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/create_marvelous_garmentcode_tee.py).

---

## 2. Key References & Documentation

- **Digital Tailoring & Avatar Fitting Guide:** [DIGITAL_TAILORING_AND_FITTING_GUIDE.md](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/DIGITAL_TAILORING_AND_FITTING_GUIDE.md)
  - *Must-read before designing or fitting garments to avatar measurements.*
  - Covers the 4 landmark selection traps (neck, shoulders, arm taper, belly), 3D cloth simulation ease physics, front-to-back arc asymmetry, and the master dimension table for `new_base_female`.
- **Marvelous Designer Python API Guide:** [MARVELOUS_DESIGNER_PYTHON_API_GUIDE.md](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/MARVELOUS_DESIGNER_PYTHON_API_GUIDE.md)
  - *Read this immediately when working on Marvelous Designer or CLO3D automation.*
  - Explains 2D coordinates, pattern IDs, segment indexing rules, and the sewing API (`AddSeamlinePairGroup`).
- **Working Reference Implementations:**
  - [create_marvelous_garmentcode_tee.py](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/create_marvelous_garmentcode_tee.py): Authentic 8-panel GarmentCode tee with mirrored back panels, +5% ease, and automated 3D arrangement.
  - [create_marvelous_shorts.py](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/create_marvelous_shorts.py): Procedural 4-panel short-shorts with 16 automated stitches (darts, crotch rise, inseams, outseams) generated from GarmentCode.
  - [create_marvelous_shirt_stitched.py](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/create_marvelous_shirt_stitched.py): Standard fitted shirt with 13 automatic stitches and 3D native arrangement.
- **GarmentCode Bridge Engine:** [garmentcode_to_marvelous.py](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/garmentcode_to_marvelous.py)
  - Automates procedural CAD generation from GarmentCode into native Marvelous Designer scripts with auto-stitching, back-panel mirroring, and 3D arrangement.

---

## 3. Avatar Measurements & Anthropometric Data

All 3D avatar measurements, cross-sections, and tailor specs are located in:

- **Primary Directory:** [`new_base_female/`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/new_base_female/)
  - Spec: [`new_base_female/new_base_female_digital_tailor_spec.json`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/new_base_female/new_base_female_digital_tailor_spec.json)
  - Slices: [`new_base_female/new_base_female_body_cross_sections.json`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/new_base_female/new_base_female_body_cross_sections.json)
- **Active Female Benchmark Profile:** [`new_base_female/new_base_female.vrm`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/new_base_female/new_base_female.vrm)
  - Body model: `new_base_female` (Height: 173.2 cm, Bust: 75.7 cm, Waist: 45.4 cm, Hips: 83.5 cm).
- **GarmentCode Body Configurations:** [`assets/bodies/`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/assets/bodies/)
  - [`assets/bodies/new_base_female.yaml`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/assets/bodies/new_base_female.yaml): Verified GarmentCode parametrization file for `new_base_female`.

---

## 4. How to Use GarmentCode (Standard Pipeline)

```python
import yaml
from assets.bodies.body_params import BodyParameters
from assets.garment_programs.meta_garment import MetaGarment
from garmentcode_to_marvelous import generate_marvelous_script

# 1. Load avatar body parameters
body = BodyParameters('sion_pipeline/kit/sion_female_default.yaml')  # the Sion female avatar, see section 0

# 2. Load design parameters
with open('assets/design_params/t-shirt.yaml') as f:
    design = yaml.safe_load(f)['design']

# 3. Instantiate and compile garment
garment = MetaGarment('MyTee', body, design)
pattern = garment.assembly()

# 4. Export to Marvelous Designer script
arrangement_map = {
    'left_ftorso': 'Body_Front_Center_1',
    'right_ftorso': 'Body_Front_Center_1',
    'left_btorso': 'Body_Back_Center_1',
    'right_btorso': 'Body_Back_Center_1',
    'left_sleeve_f': 'Arm_Front_1_L',
    'left_sleeve_b': 'Arm_Back_1_L',
    'right_sleeve_f': 'Arm_Front_1_R',
    'right_sleeve_b': 'Arm_Back_1_R',
}
generate_marvelous_script(pattern, 'create_my_garment.py', arrangement_mapping=arrangement_map)
```

---

## 5. Essential Engineering Invariants

1. **Units:**
   - Raw measurements are in **centimeters (cm)**.
   - Marvelous Designer 2D Pattern Window uses **millimeters (mm)**.
   - Scale factor is always `scale = 10.0` (1 cm = 10 mm).
2. **Sewing / Stitching API:**
   - Use `pattern_api.AddSeamlinePairGroup(pattern1, seg1, pattern2, seg2, reverse, is_fold)`.
   - In MD's internal architecture, stitches are called *Seamline Pairs*.
   - Segments are 0-indexed on the polygon perimeter: segment $k$ connects vertex $k \to k+1$.
3. **2D-to-3D Coordinate Coupling & Elevation:**
   - In Marvelous Designer, $Y = 0$ is the floor (feet), and $X = 0$ is the avatar's center axis.
   - Initial 3D elevation matches 2D $Y$ coordinates. Always offset the garment hem to the avatar's actual hip level ($Y_{hem} \approx 1078\text{ mm}$ for `new_base_female`) so clothes spawn at chest height in 3D rather than at the feet.
4. **Back Bodice & Back Sleeve 2D Horizontal Reflection Invariant:**
   - In Marvelous Designer, back arrangement points (`Body_Back_Center_1`, `Arm_Back_1_L/R`) face backward (rotated $180^\circ$ around the vertical axis).
   - **MANDATORY RULE:** Any Back panel (`left_btorso`, `right_btorso`, `left_sleeve_b`, `right_sleeve_b`) MUST be horizontally mirrored across its center line in 2D space:
     $$X' = cx - X$$
   - **Why this is critical:** Without horizontal reflection, the left and right back panels swap places in 3D space, causing seams to cross diagonally through the avatar's body in a massive "X" ("the horizontal mirror issue").
   - With horizontal reflection, `left_btorso` lands on the avatar's LEFT side, `right_btorso` lands on the avatar's RIGHT side, and stitches connect straight without cross-body twisting.
5. **Ease Ratio Invariants (No Negative Ease in MD):**
   - **Do NOT use negative ease ($\le -2\%$ to $-8\%$)** in Marvelous Designer or 3D CAD simulation. Simulated cloth tension makes negative ease feel uncomfortably tight / tourniquet-like and can pull mesh into the avatar body.
   - **$0\%$ ease (exact body measurements):** Used for sleek compression garments.
   - **$+3\%$ to $+5\%$ ease (`width: 1.05`):** Standard comfortable fit for shirts, t-shirts, and everyday apparel (default in GarmentCode).
6. **Marvelous Designer EveryWear Auto-Rigging & Blender Retarget Pipeline (MANDATORY):**
   - **Why Heuristic Weight Transfers in Blender Fail:**
     - Using Blender `DATA_TRANSFER` (`POLYINTERP_NEAREST`) directly from `Body` causes severe armpit tearing, chest/breast spiking (upper arm bones bleed into breast vertices), and coordinate-based weight stripping (`abs(x) < ...`) creates unweighted vertices.
     - **Do NOT attempt manual weight-stripping scripts.**
   - **The Official 3-Step Pipeline:**
     1. **Generate & Drape Garment in Marvelous Designer:**
        - Generate patterns procedurally via GarmentCode (`create_marvelous_*.py`).
        - Simulate and settle the cloth onto the avatar in A-pose.
     2. **Auto-Rig via EveryWear in Marvelous Designer:**
        - Use Marvelous Designer's built-in **EveryWear** auto-rigging feature to skin the draped clothing to the avatar's skeleton (`J_Bip_*` bone hierarchy).
        - MD EveryWear computes volumetric cloth skin weights natively, perfectly handling breasts, armpits, shoulders, and hips.
        - **Interactive vs. Headless Execution:** Can be executed interactively via the EveryWear Garment Tab, or **completely headlessly** via `everywear_bridge.dylib` (`Marvelous::GarmentRiggingManager::Rigging` and `Marvelous::MetaverseConverter::Export`). See Section 12.7 of [`MARVELOUS_DESIGNER_PYTHON_API_GUIDE.md`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/MARVELOUS_DESIGNER_PYTHON_API_GUIDE.md#127-headless-everywear-auto-rigging--skinned-fbxglb-export).
        - **Critical Headless Rigging Invariants:**
          - *Single-Mesh Avatar FBX Prep (`convert_sion_rig.py`):* The input Sion avatar GLB includes an unrigged helper mesh (`Icosphere`, 42 vertices). In Blender headless, delete unrigged helpers and join all body parts into a single `Body` mesh (`bpy.ops.object.join()`) before FBX export; otherwise MD detects `GetAvatarCount() == 2` with invalid joint hierarchies and aborts rigging.
          - *FBX Import Options:* Import avatar FBX with `op.ImportObjectType = 0` (registers as `AvatarRoot`, not static prop) and `op.scale = 10.0` (cm to mm coordinate space).
          - *Pattern Unfreezing:* Unfreeze all pattern pieces (`pattern_api.SetPatternFreeze(pid, False)`) so every piece participates in weight transfer.
          - *Weight Transfer:* Call `ew_transfer_weights(max_influences)` (`1` for rigid accessories/hats, `4`–`8` for full-body garments).
          - *Native Skinned FBX Export:* Call `ew_export_fbx(out_fbx)` to export skinned FBX with intact weights (mandatory: `export_api.ExportFBX()` drops cloth skin weights).
        - Export the rigged outfit as **glTF / GLB** (e.g. `new_base_female/clothes/my_rigged_cloth.glb`) or native skinned FBX.
     3. **Blender Import & Pure Retarget (Preserving EveryWear Weights):**
        - When Blender imports the EveryWear GLB, it bundles a duplicate armature (`A_pose_new_base_female`) and empty parent nodes, while character animations (`Model Pose`, `Spin`, `idle`) live on the main scene `Armature`.
        - **Run [`setup_everywear_clothes.py`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/setup_everywear_clothes.py)** to retarget the clothing:
          - Preserves 100% of the raw EveryWear skin weights and mesh geometry.
          - Re-points the garment's `Armature` modifier directly to `Armature`.
          - Parents to `Armature` while preserving world matrix (prevents 100x scale explosions or $-90^\circ$ flipping).
          - Cleans up duplicate imported armatures and empties.
          - **No Solidify, no size distortion, no destructive weight modification.**
7. **Headless Marvelous Designer Execution (`-headless`):**
   - Marvelous Designer can be run completely offscreen/headless without GUI interaction:
     ```bash
     /Applications/MarvelousDesigner.app/Contents/MacOS/MarvelousDesigner_PER \
       -headless /path/to/script.py \
       -headlesslog > /path/to/run.log 2>&1 &
     ```
   - **Headless Avatar Loading & Arrangement Points:**
     - Load avatar headlessly: `import_api.ImportFile(avatar_path)` (supports OBJ or `.avt`). Load `sion_avatars/sion-<gender>-apose.obj` (section 0).
     - Loading an avatar automatically populates 109 native arrangement points queried via `pattern_api.GetArrangementList()`.
     - Assign panels to points via `pattern_api.SetArrangement(pid, point_idx)` and wrap them into 3D using `utility_api.ResetClothArrangement()`.
   - **Drape Simulation & Non-Interactive Export Rules:**
     - Step drape simulation synchronously with explicit step count: `utility_api.Simulate(100)` (do not pass booleans in headless batch runs).
     - **Crucial Non-Interactive Export Rule:** Do NOT call `ExportOBJ("out.obj")` or `ExportZPrj("out.zprj")` without export options in headless mode; omitting options triggers a Qt GUI modal dialog that blocks forever in `QEventLoop::exec`.
       - OBJ: Pass `opt = ApiTypes.ImportExportOption(); opt.bExportGarment = True; export_api.ExportOBJ("out.obj", opt)`
       - ZPRJ: Pass `export_api.ExportZPrj("out.zprj", False)`
   - **Blender Integration & Scale Alignment:**
     - Marvelous Designer exports OBJ in millimeters (the Sion avatars are 1524 mm female, 1666 mm male).
     - In Blender (meters), import the OBJ and scale by `0.001` (`obj.scale = (0.001, 0.001, 0.001)` and apply scale) to align millimeter-perfect with the character mesh.
   - **Headless EveryWear Auto-Rigging & Skinned Export (`everywear_bridge.dylib`):**
     - Full-garment skeletal rigging and skinned FBX export can be executed headlessly without GUI interaction using `everywear_bridge.dylib` (C++ adapter hooking `libCloScene.dylib` methods `Marvelous::GarmentRiggingManager::Rigging` and `Marvelous::MetaverseConverter::Export`).
     - **Execution Summary:**
       1. Prepare clean rigged avatar FBX via `convert_sion_rig.py` in Blender (`bpy.ops.object.join()` into a single `Body` mesh deformed by `ARMATURE`, stripping helper meshes like `Icosphere`).
       2. In headless MD (`-headless rig_everywear.py`), load draped garment project (`bLoadAvatar=False`, `bLoadGarment=True`).
       3. Import clean rigged avatar FBX with `ImportObjectType = 0` (registers as `AvatarRoot`) and `scale = 10.0` (cm to mm coordinate scaling).
       4. Unfreeze all pattern pieces (`pattern_api.SetPatternFreeze(pid, False)`).
       5. Load bridge via `ctypes.CDLL('everywear_bridge.dylib')` and call `ew_transfer_weights(max_influences)` (`1` for rigid accessories, `4`–`8` for clothing).
       6. Save rigged `.zprj` via `export_api.ExportZPrj(out_zprj, False)` and export native skinned FBX via `ew_export_fbx(out_fbx)` (mandatory: `export_api.ExportFBX()` strips garment weights).
       7. **188-Bone VRoid Slider Rig & `sion-avatar` GLB Assembly (`export_188_fbx.py` & `fbx_to_glb.py`):**
          - For garments imported into `sion-avatar` with `--weights source`, rig against the 188-bone `Sion-Female-Base-PreservedRig.vrm` (which includes `J_Adj_*` and `J_Sec_L/R_Bust1/2` slider bones) rather than the 54-joint `sion-female-apose.glb`.
          - In `export_188_fbx.py`, rotate the armature $180^\circ$ around vertical ($Z$ in Blender) so it faces $+Z$, and **bake the Pose-Mode A-pose into the rest pose** (`DATA == POSE` via `modifier_apply` + `pose.armature_apply`) before exporting FBX so `ew_set_exact_positions` (`upd_init`) does not unskin the A-pose garment by $+37^\circ$ into a T-pose rest frame.
          - In `fbx_to_glb.py`, parse `export_api.ExportOBJ`'s `.obj` directly in `g <pattern>` order (avoiding `MetaverseConverter::Export`'s cross-pattern seam welding and Blender `wm.obj_import`'s `usemtl` face re-sorting), omit `normals_split_custom_set`, transfer weights from the evaluated FBX mesh per pattern slot (`0..N-1`) excluding FBX vertices on welded edges $> 20\text{ mm}$, and strip stray A-pose arm/shoulder and upward `Bust` proximity bleed on torso-dominant panels.
     - Full technical reference, bridge source, and Blender validation scripts are documented in Section 12.7 of [`MARVELOUS_DESIGNER_PYTHON_API_GUIDE.md`](file:///Users/vaz/Desktop/antigravity_apps/GarmentCode/MARVELOUS_DESIGNER_PYTHON_API_GUIDE.md#127-headless-everywear-auto-rigging--skinned-fbxglb-export).
8. **Python Environment:**
   - Run local GarmentCode Python commands with `./.venv/bin/python`.
   - Marvelous Designer scripting modules (`pattern_api`, `utility_api`, `export_api`, `ApiTypes`) are internal C++ pybind11 modules and can only be executed inside MD via `-headless`.

