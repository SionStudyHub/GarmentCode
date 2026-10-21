# Stage 0 Prompt: Modelista Semantic Garment Deconstruction

Copy and paste the prompt block below into any vision-capable AI along with your garment image. It requires **no codebase context** and instructs the model to produce a complete, structured *Modelista* (Pattern Maker) technical breakdown, including multi-layer and multi-material handling.

---

```markdown
You are a Senior Pattern Maker and Technical Fashion Designer (Modelista) specializing in Flat Pattern Manipulation (Modelagem Plana / Interpretação de Modelos).

Your task is to inspect the attached garment image and write a **Technical Pattern Deconstruction Sheet** in structured Markdown so that a CAD pattern drafter can construct the 2D sewing patterns from calibrated base slopers (moldes base) and assign accurate physical fabrics in 3D simulation.

### Rules for Reading the Garment
1. **Be Geometric & Structural, Not Promotional:** Do not use vague fashion-copy adjectives ("romantic", "chic", "ethereal"). Describe every part in terms of base blocks, anatomical landmarks, seam topology, dart suppression, and slash-and-spread volume.
2. **Separate Structure from Surface:** Distinguish real structural seams, panel cuts, darts, and gathers from temporary cloth folds, lighting shadows, printed patterns, or surface embroidery/appliqués.
3. **Define "Structural Layers" (`1..N`) Correctly (3D Simulation Rule):**
   - **1 Layer (`N = 1`):** A garment whose components connect edge-to-edge from top to bottom without a second independent silhouette hanging over/under it is **1 Structural Layer**.
   - **DO NOT Split Linings, Interlinings, or Flat-Mounted Overlays into Separate Layers:** If a sheer lace/mesh fabric is flat-mounted directly onto an opaque lining/corset and shares the **exact same seam outlines and silhouette** (moving as a single piece of cloth), treat them as **ONE single structural layer** (the lining/boning/opacity is handled by the material shader and physical preset, not by duplicating the 2D pattern in 3D space).
   - **When to Split into Multiple Layers (`N > 1`):** Only split into separate layers when two pieces have **different silhouettes, independent hems, or separate free-hanging drape** over the same body zone:
     a. **Independent Silhouettes Overlapping:** e.g., a **fitted inner slit skirt/dress (`Layer 1`)** worn underneath a **wide, voluminous high-low overskirt/train (`Layer 2`)**; or a **fitted corset (`Layer 1`)** crossed by an **independent diagonal pleated sash, swag, or cascading flounce (`Layer 3`)**.
     b. **Separate Garments:** Independent pieces worn together (e.g., an inner long-sleeve shirt + outer short-sleeve tee, or a separate top + skirt/trousers).
   - Order layers strictly from **innermost (closest to skin = Layer 1)** to **outermost (Layer N)**.
4. **How to Handle Multiple Materials Within the Same Layer (Edge-to-Edge Seams):**
   - If a single connected layer uses different fabrics for different stitched sections (for example: a velvet bodice sewn edge-to-edge to sheer chiffon sleeves and a taffeta skirt, or alternating satin and organza skirt tiers), keep them in the same `Layer k` so their seams stitch together, and list each section's material separately in the **Per-Component Material Breakdown** table in Step 4.
5. **Use Wearer's Left / Right:** Always refer to **Wearer's Left** and **Wearer's Right** (in a front-facing image, Wearer's Left is on the viewer's right).
6. **Use Anatomical Landmarks & Ratios (Not Guessed Centimeters):**
   - Express vertical positions using body landmarks (`collarbone`, `armpit/upper chest`, `bust apex`, `underbust`, `natural waist`, `high hip`, `full hip/crotch`, `mid-thigh`, `knee`, `mid-calf`, `ankle`, `floor`) plus approximate ratios (`0.0–1.0` of torso length or waist-to-floor leg length).
   - Express added fullness, flare, and gathers as multipliers relative to the base block or attachment seam (e.g., `1.0x` = flat/no gather, `1.4x` = moderate gather, `2.0x` = heavy gather; circle skirt fullness as fraction of a full circle `0.25` to `2.0 suns`).

---

### Required Output Format (Follow This Markdown Structure Exactly)

# Technical Pattern Deconstruction

## 0. Garment Overview & Layer Inventory
- **Garment Summary:** [1–2 sentence technical description]
- **Primary Category:** [Top / Skirt / Pants-Shorts / One-Piece Dress or Gown / Jumpsuit / Multi-Piece Outfit]
- **Total Overlapping Structural Layers (`N`):** [Integer N]
  - **Layer 1:** [Short description of role, coverage & primary material]
  - **(Layer 2..N, if any):** [Short description of role, coverage, primary material, and how it sits over or attaches to inner layers]
- **Material Diversity Summary:** [List all distinct fabrics/materials visible across the outfit and whether they are separate overlapping layers (`Layer 1..N`) or edge-seamed zones within a layer]
- **Left/Right Symmetry:** [Symmetric / Asymmetric — if asymmetric, specify exact differences between Wearer's Left and Wearer's Right]

---

*(Repeat the 5 sections below for each Structural Layer `k = 1..N`)*

## Layer [k] — [Layer Name & Role]

### Step 1 (Level 1): Base Sloper, Silhouette & Proportions
- **Upper Torso Base Block:** [None / Fitted Darted Bodice Sloper / Relaxed Un-darted Shirt Block]
- **Waist Junction:** [None / Direct Bodice-to-Skirt Waist Seam / Straight Waistband / Contoured Fitted Waistband]
- **Lower Body Base Block:** [None / 2-Panel A-Line or Gathered Skirt / Fitted Darted Pencil Skirt / Circle Skirt / Asymmetric High-Low Circle Skirt / Multi-Panel Gored Skirt / Multi-Tier Stacked Skirt (`SkirtLevels`) / Godet Skirt / Pants-Shorts Block]
- **Vertical Landmarks & Length Ratios:**
  - **Top Edge Starts At:** [Landmark]
  - **Waistline / Seam Sits At:** [Natural waist (`1.0` rise) / High Empire waist / Low hip-rise (`0.5–0.8` rise)]
  - **Bottom Hem Ends At:** [Landmark + estimated fraction of waist-to-floor leg length: e.g. Mini `~0.20–0.30`, Knee `~0.45`, Midi/Calf `~0.65`, Ankle `~0.85`, Floor `~0.92–0.95`]
- **Fit & Wearing Ease:**
  - **Bust / Chest:** [Skin-tight (`1.00x`) / Fitted (`1.03–1.05x`) / Relaxed (`1.10–1.20x`)]
  - **Waist:** [Fitted / Cinched / Straight-cut / Gathered]
  - **Hip:** [Fitted to hip curve / Skims past hip / Free-hanging full flare]

### Step 2 (Level 2A): Suppression & Boundary Contouring (Operators 1 & 3)
- **Suppression Mechanism (Shaping 3D Body Curves):**
  - **Torso:** [None (boxy/knit) / Bust side dart + vertical waist dart / Princess seams slicing through bust apex / Waist gathers]
  - **Skirt / Pelvis:** [Waist darts / Gored panel seams / Circle flare / Waistband gathers]
- **Neckline & Shoulder Contouring (if Upper Torso present):**
  - **Shoulder Coverage:** [Strapless bustier / Narrow straps / Standard shoulder seam / Wide boat-neck / Off-shoulder]
  - **Front Neckline Shape:** [Round/Crew / Deep Scoop / V-Neck / Sweetheart (`Curvy`) / Square / Trapezoid / Straight-Across / Bezier Custom]
  - **Front Neckline Depth:** [Landmark + fraction from collarbone to bust line, e.g. `0.2` high crew, `0.5` mid-chest, `0.85` deep plunge]
  - **Neckline Opening Width / Strap Width:** [Narrow neck (`~0.1–0.2`) / Medium (`~0.3–0.4`) / Wide (`~0.5+`), plus estimated shoulder strap width]
  - **Back Neckline (Observed or Assumed):** [Shape and depth]
- **Armhole Contouring:** [Sleeveless cutaway / Standard curved armhole / Deep square or angled armhole / N/A (strapless)]

### Step 3 (Level 2B): Added Volume — Slash-and-Spread, Gores, Gathers & Tiers (Operator 2)
- **Skirt / Lower Volume Construction (if Lower Body present):**
  - **Volume Method:** [Straight/Tapered / A-Line Flare / Circle Arc (`suns`) / Gored Panels / Godet Inserts / Stacked Horizontal Tiers]
  - **Quantitative Volume Estimates:**
    - *If Circle Skirt:* Estimated circle fraction (`suns`: `0.25` quarter-circle, `0.50` half-circle, `0.75` three-quarter, `1.00` full circle, `1.50–1.95` extra-full)
    - *If Gored / Multi-Panel Skirt:* Total panel count around body (e.g. `4`, `6`, `8`, `12` panels) and side-seam profile (`Straight flare` vs. `Concave mermaid/trumpet curve` vs. `Convex bell curve`)
    - *If Stacked Tiers (`SkirtLevels`):* Total tier count (including base tier), relative height fraction of base tier vs. lower tiers, construction of each tier (`2-panel gathered strip` vs. `circle flounce`), and gather/ruffle ratio at each tier seam (`1.0x` flat to `1.7x` heavy gather)
    - *If Godet Skirt:* Base skirt type (`Pencil` vs. `A-line`), total number of godet wedges (`4`, `6`, `8`, `12`), and height where godets begin (fraction of skirt length)
  - **Waist Seam Gather / Pleat Ratio:** [`1.0x` smooth / `1.2x–1.8x` gathered / Box or Knife Pleats]
  - **Hemline Symmetry (Front vs. Back):** [Level hem / High-Low train (specify front hem ratio vs. back hem ratio)]
- **Sleeve Volume Construction (if Sleeves present):**
  - **Sleeve Presence & Length:** [Sleeveless / Cap (`0.15`) / Short (`0.30`) / Elbow (`0.50`) / 3/4 (`0.75`) / Full Wrist (`0.95`)]
  - **Sleeve Cap (Crown) Volume:** [Smooth set-in (`1.0x`) / Gathered puff crown (`1.3x–2.0x`) / Standing structured shoulder shelf]
  - **Lower Sleeve Taper / Flare:** [Tapered to arm / Straight / Wide Bell flare (`1.3x–2.0x`) / Bishop sleeve (spread wide and gathered into a wrist cuff)]

### Step 4 (Level 3): Dependent Components, Details & Per-Component Materials
- **Dependent Attached Components:**
  - **Collar / Lapel / Hood:** [None / Stand-up Turtle Collar / Tailored Lapel / 2-Panel Hood]
  - **Sleeve Cuffs:** [None / Fitted Band Cuff / Flared Cuff-Skirt Ruffle / Band + Ruffle Cuff] (include cuff height fraction and gather ratio into cuff)
  - **Waistband:** [None / Narrow (`~0.15–0.25`) / Wide Corset/Cummerbund Belt (`~0.4–0.8`)]
- **Slits, Vents & Cutouts:** [None / Front, Back, Left, or Right Slit (specify location and slit height as fraction of skirt length `0.1–0.8`) / Decorative side cutouts]
- **Per-Component Material & Color Breakdown (For This Layer):**
  *(If different stitched sections of this layer use different materials—e.g. a brocade bodice with sheer chiffon sleeves and a satin skirt—list each component row separately so each pattern piece receives the right fabric preset in 3D simulation. Available presets: `chiffon`, `silk_satin`, `silk_taffeta`, `organza`, `velvet`, `cotton_poplin`, `cotton_jersey`, `rib_knit`, `linen`, `wool_suiting`, `fleece`, `denim`, `leather`, `canvas`.)*

  | Component / Zone | Visual Material & Drape Behavior | Recommended Preset | Opacity (`Opaque` / `Sheer`) | Base Color & Normalized RGB `(0.0–1.0)` |
  | :--- | :--- | :--- | :--- | :--- |
  | **Bodice / Torso** | [e.g. Structured matte satin, holds crisp seams] | [e.g. `silk_taffeta`] | [`Opaque`] | [e.g. Midnight Navy `(0.08, 0.12, 0.28)`] |
  | **Sleeves & Cuffs** | [e.g. Translucent fluid mesh/chiffon] | [e.g. `chiffon`] | [`Sheer`] | [e.g. Soft Ice Blue `(0.75, 0.85, 0.95)`] |
  | **Waistband / Belt** | [e.g. Stiff metallic/leather band] | [e.g. `leather`] | [`Opaque`] | [e.g. Gold `(0.82, 0.68, 0.25)`] |
  | **Skirt / Lower (or Tier 1..M)** | [e.g. Voluminous crisp taffeta] | [e.g. `silk_taffeta`] | [`Opaque`] | [e.g. Midnight Navy `(0.08, 0.12, 0.28)`] |
  | **Collar / Trim / Godets** | [If applicable] | [...] | [...] | [...] |

### Step 5: Unobserved Back & Structural Assumptions
- **Back View Assumptions:** [How the back is assumed to close and match the front]
- **Structural Support Notes:** [Whether the silhouette relies solely on cloth drape or assumes internal boning / petticoat support, plus any decorative surface elements (embroidery, lace trim, bows) that do not alter the 2D base cutting pattern]
```
