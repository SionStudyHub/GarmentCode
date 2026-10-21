# Digital Tailoring & Avatar Fitting Guide
*A comprehensive engineering manual for AI agents and digital tailors generating fitted garments in Marvelous Designer / CLO3D.*

---

## 1. Executive Summary & Core Ground Truth

The anthropometric measurements stored in [`new_base_female/`](new_base_female/) (`new_base_female_digital_tailor_spec.json` and `new_base_female_body_cross_sections.json`) are **mathematically and geometrically ground-truth accurate** down to sub-millimeter precision against the 3D avatar skin mesh ([`new_base_female.vrm`](new_base_female/new_base_female.vrm), model: `new_base_female`, total height: 173.22 cm).

However, translating raw 3D anthropometric data into 2D sewing patterns that fit correctly in a 3D cloth simulation engine requires understanding three digital tailoring fundamentals:
1. **The Landmark Selection Traps** (avoiding oversized anatomical transition slices).
2. **The 3D Simulation Physics of "Ease"** (why zero ease is NOT skin-tight in cloth simulation).
3. **Anatomical Front-to-Back Asymmetry** (why splitting circumferences 50/50 creates distorted seams).

---

## 2. The Four Landmark Selection Traps

When drafting garments from `new_base_female_digital_tailor_spec.json`, agents frequently fall into four landmark traps by querying the wrong JSON fields:

### Trap 1: The Neck Trap (`neck_narrow` vs `neck_base_reference`)
- **`neck_narrow` (Anatomical Neck):**
  - Circumference: **$21.97\text{ cm}$** | Width: **$6.66\text{ cm}$** (Half-width: **$3.33\text{ cm}$**) | Height: $Y = 147.17\text{ cm}$
  - **Usage:** Snug collars, crewneck t-shirts, turtlenecks, chokers, activewear collars.
- **`neck_base_reference` (Clavicle/Trapezius Junction):**
  - Circumference: **$31.82\text{ cm}$** | Width: **$13.08\text{ cm}$** (Half-width: **$6.54\text{ cm}$**) | Height: $Y = 144.02\text{ cm}$
  - **Usage:** Wide scoop necks, boat necks, off-shoulder collars, jacket lapel bases.
- **The Pitfall:** If you use `neck_base_reference` for a standard t-shirt collar, the collar will be **+45% oversized ($31.8\text{ cm}$ vs $22\text{ cm}$)**, gaping open and hanging down the chest.

---

### Trap 2: The Shoulder Joint Trap (Joint Span vs Arm-Inclusive Span)
- **`shoulder_joint_to_joint_width_cm` (Anatomical Acromion Width):**
  - Total Span: **$18.98\text{ cm}$** | Half-width from center spine: **$9.49\text{ cm}$** (neck center to joint: **$10.28\text{ cm}$**) | Height: $Y = 140.16\text{ cm}$
  - **Usage:** All fitted tops, sleeveless shirts, set-in sleeve armhole corners.
- **Arm-Inclusive Shoulder Span (Deltoid to Deltoid):**
  - Total Span: $\approx 28.50\text{ cm}$ (Half-width: $14.25\text{ cm}$)
  - **Usage:** Drop-shoulder streetwear, oversized hoodies, loose kimono cuts.
- **The Pitfall:** Using $14.25\text{ cm}$ for a fitted shirt causes the shoulder seams to drop $4.76\text{ cm}$ down each arm, collapsing the upper chest, sagging the armhole, and distorting sleeve attachment.

---

### Trap 3: The Arm Taper Trap (Deltoid Root vs Bicep vs Cuff)
The human upper arm tapers steeply from shoulder joint to elbow:
- **Armpit / Deltoid Root ($X \approx 11.7\text{ cm}$ from spine):** Circumference $\approx \mathbf{23.10\text{ cm}}$
- **Mid-Bicep ($X \approx 15-20\text{ cm}$ from spine):** Circumference $\approx \mathbf{20.87\text{ cm}}$
- **Short Sleeve Cuff / Low Bicep:** Circumference $\approx \mathbf{18.0 - 19.0\text{ cm}}$
- **Elbow ($X \approx 25-28\text{ cm}$ from spine):** Circumference $\approx \mathbf{17.62\text{ cm}}$
- **The Pitfall:** Drafting a short sleeve with a uniform $23-24\text{ cm}$ cuff leaves **$+4\text{ to }+5\text{ cm}$ (20% to 25%) of loose flapping fabric** around the arm. A fitted short sleeve cuff must narrow to **$17.5 - 18.5\text{ cm}$**.

---

### Trap 4: The Abdomen / Belly Trap (Waist to High-Hip Interpolation)
- **Natural Waist ($Y = 116.41\text{ cm}$):** Circumference = **$45.40\text{ cm}$** | Lateral Half-Width = **$8.08\text{ cm}$**
- **High Hip / Upper Hem ($Y = 107.78\text{ cm}$):** Circumference = **$61.28\text{ cm}$** | Lateral Half-Width = **$10.93\text{ cm}$**
- **Full Hip / Seat ($Y = 95.21\text{ cm}$):** Circumference = **$83.48\text{ cm}$** | Lateral Half-Width = **$15.58\text{ cm}$**
- **The Pitfall:** If a 2D pattern connects Waist ($116.41\text{ cm}$) to Full Hip ($95.21\text{ cm}$) with a straight linear trapezoid, the pattern width at $Y = 107.8\text{ cm}$ (high hip) becomes $64.4\text{ cm}$—leaving sagging abdominal slack. For a fitted torso, the hem or waist contour must keep the lower abdomen narrow ($56 - 58\text{ cm}$).

---

## 3. The 3D Simulation Physics of "Ease"

In traditional tailoring, "ease" is the difference between body measurement and garment measurement:
$$\text{Pattern Measurement} = \text{Body Measurement} \times (1 + \text{Ease Ratio})$$

### The 3D Simulation Physics of "Ease" & Mesh Penetration
In cloth simulation (Marvelous Designer, Blender, Qualoth), flat 2D cloth mesh panels draping over 3D avatars require balanced ease:

> [!CAUTION]
> **Avoid Negative Ease in Marvelous Designer ($\le -2\%$ to $-8\%$):**
> Drafting patterns with negative ease ($-2\%$ to $-8\%$) creates excessive tension in Marvelous Designer that causes garments to fit uncomfortably tight like a tourniquet or pull the cloth mesh directly into and through the avatar body.
> - **$0\%$ Ease (Exact Body Measurements):** Use strictly for sleek athletic compression tops or swimsuits.
> - **$+3\%$ to $+5\%$ Ease (GarmentCode Default `width: 1.05`):** The golden standard for everyday fitted t-shirts and tops, producing natural drape and zero uncomfortable tightness.

### The Ease Classification Table for Digital Agents:

| Garment Style | Target Ease Ratio | Fabric Real-World Equivalent | 3D Visual Result |
| :--- | :---: | :--- | :--- |
| **Athletic Compression / Swim** | **$0\%$** (Exact Body) | High-spandex compression knit | Form-fitting contour without digging into the mesh. |
| **Fitted Everyday Top / Tee** | **$+3\%$ to $+5\%$** | Cotton jersey, rib knit | Smooth natural drape over torso curves with zero tightness. |
| **Relaxed T-Shirt / Blouse** | **$+6\%$ to $+10\%$** | Linen, woven silk | Relaxed drape, gentle natural folds at waist and hem. |
| **Oversized / Streetwear** | **$+12\%$ to $+25\%$** | Heavy French terry, fleece, denim | Boxy silhouette, dropped shoulders, deep folds. |

---

## 4. Anatomical Front-to-Back Arc Asymmetry

A common beginner mistake is dividing body circumference symmetrically ($50\%$ Front, $50\%$ Back). In real human anatomy:
- **Bust Prominence:** Full bust tape circumference is $75.69\text{ cm}$, but:
  - **Middepth Front Arc:** **$39.60\text{ cm}$** ($52.3\%$ of total)
  - **Middepth Back Arc:** **$36.08\text{ cm}$** ($47.7\%$ of total)
- **Natural Waist:** Waist tape circumference is $45.40\text{ cm}$:
  - **Front Arc:** **$23.63\text{ cm}$** ($52.0\%$ of total)
  - **Back Arc:** **$21.77\text{ cm}$** ($48.0\%$ of total)

### Why Asymmetric Drafting is Mandatory:
1. **Mid-Axillary Line Alignment:** Drafting the front wider and back narrower keeps the side seams vertically aligned directly under the armpit.
2. **Preventing Side-Seam Pulling:** Symmetrical drafting forces the bust to pull the side seams forward towards the chest, causing diagonal tension wrinkles across the ribs and armpits.

---

## 5. Master Specification Table (new_base_female)

Use this table as direct code parameters when generating garments for `new_base_female`:

| Anatomical Landmark | Elevation $Y$ (mm) | Avatar Body Tape (cm) | Fitted Pattern (-2% Ease) (cm) | Standard Fit Pattern (cm) | 2D Half-Width Front / Back (mm) |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Narrow Neck** | $1471.7$ | $21.97$ | **$21.53$** | $24.00$ | $X = \pm 33.3\text{ mm}$ |
| **Neck Base** | $1440.2$ | $31.82$ | — | $31.00$ | $X = \pm 65.4\text{ mm}$ |
| **Shoulder Joint (Acromion)**| $1401.6$ | Joint Span: $18.98$ | **$18.98$** | $22.00$ | $X = \pm 94.9\text{ mm}$ |
| **Underarm / Chest** | $1318.7$ | $61.67$ (underbust) | **$60.50$** | $66.00$ | Front: $160.0$ / Back: $142.5$ |
| **Full Bust Apex** | $1273.1 - 1304.8$ | $75.69$ | **$74.20$** | $80.00$ | Front: $194.0$ / Back: $177.0$ |
| **Natural Waist** | $1164.1$ | $45.40$ | **$44.50$** | $49.00$ | Front: $116.0$ / Back: $107.0$ |
| **High Hip / Hem** | $1077.8$ | $61.28$ | **$60.00$** | $64.00$ | Front: $151.0$ / Back: $149.0$ |
| **Bicep (Upper Arm Root)** | $1389.9$ | $23.10$ | **$22.60$** | $24.50$ | Half-width: $113.0\text{ mm}$ |
| **Sleeve Cuff (Mid-Arm)** | $1392.9$ | $20.87$ | **$20.40$** | $22.00$ | Half-width: $102.0\text{ mm}$ |

---

## 6. Stitching & Edge Reversal Quick-Reference

When calling `pattern_api.AddSeamlinePairGroup(p1, seg1, p2, seg2, reverse, is_fold)`:

### The Mathematical Vector Rule:
$$\text{Use } \mathbf{reverse=True} \text{ whenever two perimeter vectors travel in opposing 3D directions.}$$

1. **Back Bodice 2D Horizontal Reflection Rule:**
   - In 2D, draft the Back Bodice with the identical segment order as Front Bodice, then horizontally reflect it across its center axis ($X' = 2 \cdot cx - X$):
     ```python
     back_pts = [
         (round(2 * cx_b * scale - x, 3), y, z) for (x, y, z) in raw_back_pts
     ]
```
   - This inverts the 2D winding order from Clockwise to Counter-Clockwise and mirrors $X$, ensuring its 3D normal faces outward when placed on the avatar's back (`Body_Back_Center_1`).

2. **Torso & Armhole Seams (`reverse=False`):**
   - Connect all Front-to-Back torso seams and sleeve-to-armhole seams with **`reverse=False`** so bottom connects to bottom and top connects to top without diagonal criss-crossing:
     - Right Shoulder: `front[4] <-> back[4]` (`reverse=False`)
     - Left Shoulder: `front[7] <-> back[7]` (`reverse=False`)
     - Lower Right Side: `front[1] <-> back[1]` (`reverse=False`)
     - Upper Right Side: `front[2] <-> back[2]` (`reverse=False`)
     - Upper Left Side: `front[9] <-> back[9]` (`reverse=False`)
     - Lower Left Side: `front[10] <-> back[10]` (`reverse=False`)
     - Left Armhole Front: `left_sleeve[3] <-> front[8]` (`reverse=False`)
     - Left Armhole Back: `left_sleeve[2] <-> back[8]` (`reverse=False`)
     - Right Armhole Front: `right_sleeve[2] <-> front[3]` (`reverse=False`)
     - Right Armhole Back: `right_sleeve[3] <-> back[3]` (`reverse=False`)

3. **Self-Closing Cylinders (`reverse=True`):**
   - When sewing opposite edges of the SAME 2D piece together into a cylinder:
     - Left Sleeve Tube: `left_sleeve[1] <--> left_sleeve[4]` $\implies$ **`reverse=True`**
     - Right Sleeve Tube: `right_sleeve[1] <--> right_sleeve[4]` $\implies$ **`reverse=True`**
     - Collar Ring: `collar[1] <--> collar[3]` $\implies$ **`reverse=True`**
   - *Reason:* Opposite edges run in opposing directions along the continuous perimeter loop. `reverse=True` untwists the seam and produces a clean cylinder.

---

## 7. Canonical Reference Scripts in Repository

- **[`create_marvelous_skintight_shirt.py`](create_marvelous_skintight_shirt.py):** Production compression skin-tight shirt implementing all negative-ease, narrow-neck, and anatomical shoulder principles.
- **[`create_marvelous_shirt_stitched.py`](create_marvelous_shirt_stitched.py):** Standard fitted daily-wear shirt with 13 automatic stitches and native 3D arrangement.
- **[`MARVELOUS_DESIGNER_PYTHON_API_GUIDE.md`](MARVELOUS_DESIGNER_PYTHON_API_GUIDE.md):** Complete low-level API specification for Marvelous Designer / CLO automation.

---

## 8. Lower-Body (Shorts & Pants) Tailoring & Stitching Invariants

### 8.1 4-Panel Layout & Orientation Invariant
To prevent diagonal cross-overs in both 2D and 3D:
1. **Center Front Meeting ($X = 0$):** `Front Left` and `Front Right` are centered around $X = 0$ and meet along their inner fly/crotch edges.
2. **Outseam Pairing:** Place `Back Left` directly adjacent to `Front Left` with their outseams facing each other. Place `Back Right` directly adjacent to `Front Right` with their outseams facing each other.
3. **3D Native Arrangement:**
   - Left Leg Front $\longrightarrow$ `Leg_Front_L`
   - Left Leg Back $\longrightarrow$ `Leg_Back_L`
   - Right Leg Front $\longrightarrow$ `Leg_Front_R`
   - Right Leg Back $\longrightarrow$ `Leg_Back_R`

### 8.2 The Lower-Body Seam Reversal Rules (`reverse`):
When sewing pants and shorts perimeters:
- **Center Front Fly & Crotch (`rev=True`):** The left and right front panels trace the center seam in opposite vertical perimeter directions $\implies$ **ALWAYS `reverse=True`** to connect Top-to-Top and Fork-to-Fork.
- **Center Back Rise & Crotch (`rev=True`):** The left and right back panels trace the center rise in opposite vertical perimeter directions $\implies$ **ALWAYS `reverse=True`** to connect Top-to-Top and Fork-to-Fork.
- **Outseams (Hip Side Seams) (`rev=False`):** When Front and Back are laid out facing each other, their outseams run in the same vertical direction $\implies$ **ALWAYS `reverse=False`**.
- **Inseams (Inside Thigh) (`rev=False`):** Both Front and Back inseams run Fork $\to$ Hem $\implies$ **ALWAYS `reverse=False`**.
- **Back Darts (`rev=False`):** Closing the adjacent perimeter legs of a dart requires **`reverse=False`**.

---

## 9. GarmentCode Procedural Pipeline & Marvelous Bridge Workflow

The primary method for generating clothing in this repository is **GarmentCode (`pygarment`)**.

### 9.1 The Python Generation Pipeline
To generate a pattern from GarmentCode for any avatar:
1. **Load Avatar Parameters:**
   ```python
   from assets.bodies.body_params import BodyParameters

   body = BodyParameters('assets/bodies/new_base_female.yaml')
```
2. **Load Design Configuration:**
   ```python
   import yaml

   with open('assets/design_params/t-shirt.yaml') as f:
     design = yaml.safe_load(f)['design']
```
3. **Assemble Pattern:**
   ```python
   from assets.garment_programs.meta_garment import MetaGarment

   garment = MetaGarment('NewFemaleTee', body, design)
   pattern = garment.assembly()
```
4. **Translate to Marvelous Designer with Horizontal Reflection:**
   ```python
   from garmentcode_to_marvelous import generate_marvelous_script

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
   generate_marvelous_script(
       pattern,
       'create_marvelous_garmentcode_tee.py',
       arrangement_mapping=arrangement_map,
   )
```

### 9.2 The Horizontal Mirror Rule for Multi-Panel Backs
In Marvelous Designer, arrangement points on the avatar's back (`Body_Back_Center_1`, `Arm_Back_1_L/R`) rotate patterns $180^\circ$ around the vertical axis.
- Any Back panel (`left_btorso`, `right_btorso`, `left_sleeve_b`, `right_sleeve_b`) generated by GarmentCode MUST have its $X$ coordinate horizontally reflected across its center line in 2D space ($X' = cx - X$).
- Without this reflection, the left and right back panels swap places in 3D, creating diagonal cross-body "X" stitches.
- [`garmentcode_to_marvelous.py`](garmentcode_to_marvelous.py) automatically applies this reflection to all panels containing `btorso`, `sleeve_b`, or `back`.

---

## 10. The EveryWear Auto-Rigging & Blender Retarget Pipeline

When transferring simulated clothing from Marvelous Designer into an animated character in Blender, **do NOT use Blender's manual weight transfer scripts** (`DATA_TRANSFER` with `POLYINTERP_NEAREST` or spatial coordinate filters).

### 10.1 Why Manual Blender Weight Transfers Fail
- **Armpit Tearing:** In A-pose, the chest wall and inner arm are closely adjacent ($< 1.5\text{ cm}$). Nearest-surface projection causes armpit cloth vertices to sample the upper arm bone (`J_Bip_L_UpperArm`), creating catastrophic mesh tearing during arm movement.
- **Breast Creasing / Spikes:** The outer bust curve is situated directly in front of the upper arm in A-pose. Distance-based sampling bleeds arm weights into the breast, pulling sharp spikes outward whenever the avatar lowers or rotates her arms.
- **Unweighted Vertices:** Attempting to prune bleeding weights via spatial bounding boxes (e.g. `abs(x) < 0.12`) strips weights from legitimate shoulder/chest transitions, leaving floating vertices with 0 weights that stretch to the scene origin.

### 10.2 The Solution: Marvelous Designer EveryWear Auto-Rigging
Marvelous Designer's built-in **EveryWear** toolkit performs volumetric, cloth-aware skinning directly inside MD:
1. **Drape & Settle Garment:** Drape the GarmentCode patterns on the avatar in A-pose until cloth physics settle.
2. **Auto-Rig in EveryWear:**
   - In MD, access the EveryWear auto-rigging panel.
   - Select the avatar's skeleton (`J_Bip_*` bone hierarchy).
   - Click Auto-Rig / Skin. EveryWear computes volumetric influences that respect the 3D drape topology—breasts deform with the chest, sleeves deform with the arms, and armpits maintain smooth falloff without tears or spikes.
3. **Export Rigged Asset:**
   - Export as **glTF / GLB** (or FBX) with skinning/joints enabled.

### 10.3 The Blender Retarget Step (`setup_everywear_clothes.py`)
When Blender imports an EveryWear GLB:
- The GLB creates its own duplicate armature (`A_pose_new_base_female` or `Armature.001`) and parent empty nodes.
- Character animations (`Model Pose`, `Spin`, `idle`, etc.) live on the scene's primary `Armature`.
- If you simply re-parent by hand, Blender's transform hierarchy will scale the garment 100x or flip it $-90^\circ$.

**The Golden Rule:** Always run [`setup_everywear_clothes.py`](setup_everywear_clothes.py) (or paste its snippet into the Python Console):
```python
import bpy

target_arm = bpy.data.objects['Armature']

# 1. Grab clothing meshes
clothes = [
    o
    for o in bpy.context.selected_objects
    if o.type == 'MESH' and o.name not in ['Body', 'Face']
]
if not clothes:
  clothes = [
      o
      for o in bpy.data.objects
      if o.type == 'MESH'
      and o.name not in ['Body', 'Face']
      and any(
          m.type == 'ARMATURE' and m.object != target_arm for m in o.modifiers
      )
  ]

# 2. Re-point modifier and parent preserving exact world transform
for cloth in clothes:
  for m in cloth.modifiers:
    if m.type == 'ARMATURE':
      m.object = target_arm

  mat = cloth.matrix_world.copy()
  cloth.parent = target_arm
  cloth.matrix_parent_inverse = target_arm.matrix_world.inverted()
  cloth.matrix_world = mat

# 3. Clean up duplicate imported armature
for o in list(bpy.data.objects):
  if o.type == 'ARMATURE' and o != target_arm:
    bpy.data.objects.remove(o, do_unlink=True)
```
- **Preserves 100% of EveryWear weights:** No re-weighting, smoothing, or coordinate stripping.
- **Zero modifiers added:** No Solidify, no scaling offsets—pure raw cloth simulation mesh.
- **Immediately ready for animation:** Garments smoothly follow all animations without tearing or spikes.

