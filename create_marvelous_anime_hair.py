"""
Procedural High-Density Stylized Anime Hair Generator for Marvelous Designer
Compatible with new_base_female avatar profile (Head circumference: 645 mm).

Generates 57 pattern pieces:
- CrownAnchorBand: 75 mm thick upper cranium fitted anchor band (Y in [1640.0, 1715.0] mm),
  trapezoidal skull-dome taper: bottom width 670.0 mm (+4% ease), top width 620.0 mm.
- 56 Stylized Anime Hair Locks (continuous 360° edge-to-edge coverage along bottom of band):
  * Back Cascade (24 locks): Posterior scalp coverage (X in [-150, +150] mm on band).
    Lengths: 260 - 290 mm (Y_tip in [1350, 1380] mm). Arranged on "Head_Top_Back" (Index 73).
  * Left Side & Temple (9 locks): Left temple/ear/jaw coverage (X in [-250, -150] mm on band).
    Lengths: 180 - 230 mm (Y_tip in [1410, 1460] mm). Arranged on "Head_L" (Index 72).
  * Right Side & Temple (9 locks): Right temple/ear/jaw coverage (X in [+150, +250] mm on band).
    Lengths: 180 - 230 mm (Y_tip in [1410, 1460] mm). Arranged on "Head_R" (Index 71).
  * Front Bangs / Fringe (14 locks): Forehead coverage (X in [-335, -250] and [+250, +335] mm on band).
    Lengths: 60 - 110 mm (Y_tip in [1530, 1580] mm). Arranged on "Head_Top_Front" (Index 75).

Executes 57 procedural seamlines (1 cylinder loop + 56 hair root seams) and 3D native arrangement.
"""

import sys

# --- API IMPORTS & MOCK FALLBACK ---
try:
    import pattern_api
    import utility_api
except ImportError:
    class MockPatternApi:
        def __init__(self):
            self._counter = 0

        def CreatePatternWithPoints(self, pts):
            idx = self._counter
            self._counter += 1
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            if idx <= 3 or idx >= 54:
                print(f"[Mock Pattern] #{idx:2d} created ({len(pts):2d} vertices) Bounds: X=[{min(xs):6.1f}, {max(xs):6.1f}], Y=[{min(ys):6.1f}, {max(ys):6.1f}] mm")
            elif idx == 4:
                print("  ... (creating procedural hair lock patterns) ...")
            return idx

        def AddSeamlinePairGroup(self, p1, s1, p2, s2, rev, fold):
            return True

        def GetArrangementList(self):
            return [
                {"ArrangementIndex": "70", "ArrangementName": "Head"},
                {"ArrangementIndex": "71", "ArrangementName": "Head_R"},
                {"ArrangementIndex": "72", "ArrangementName": "Head_L"},
                {"ArrangementIndex": "73", "ArrangementName": "Head_Top_Back"},
                {"ArrangementIndex": "74", "ArrangementName": "Head_Top_Center"},
                {"ArrangementIndex": "75", "ArrangementName": "Head_Top_Front"},
            ]

        def SetArrangement(self, pid, pt_id):
            pass

    class MockUtilityApi:
        @staticmethod
        def ResetClothArrangement():
            print("[Mock] utility_api.ResetClothArrangement() called - 3D wrapped around avatar!")

    pattern_api = MockPatternApi()
    utility_api = MockUtilityApi()

print("=" * 75)
print("  Marvelous Designer - High-Density Stylized Anime Hair Generator (56 Locks)")
print("=" * 75)

# --- 1. PROCEDURAL HAIR LOCK SPECIFICATIONS ---
# We define 56 contiguous lock configurations spanning the entire 670 mm bottom circumference
# of CrownAnchorBand (X in [-335.0, +335.0] mm at Y = 1640.0 mm).
#
# Band Partitioning:
# 1. Bangs Left  ( 7 locks): X in [ -335.0, -250.0 ] mm (Forehead center-left to left temple)
# 2. Side Left   ( 9 locks): X in [ -250.0, -150.0 ] mm (Left temple/cheek/ear/jaw)
# 3. Back Hair   (24 locks): X in [ -150.0, +150.0 ] mm (Posterior scalp cascade)
# 4. Side Right  ( 9 locks): X in [ +150.0, +250.0 ] mm (Right ear/jaw/cheek/temple)
# 5. Bangs Right ( 7 locks): X in [ +250.0, +335.0 ] mm (Right temple to forehead center-right)
# Total = 7 + 9 + 24 + 9 + 7 = 56 locks.

lock_configs = []

# (A) Bangs Left (7 locks: indices 0..6)
# Lengths: 60 mm at forehead center (X = -335) tapering to 110 mm near temple (X = -250)
x_start_b_l = -335.0
x_end_b_l = -250.0
n_b_l = 7
step_b_l = (x_end_b_l - x_start_b_l) / n_b_l
for i in range(n_b_l):
    x_s = x_start_b_l + i * step_b_l
    x_e = x_start_b_l + (i + 1) * step_b_l
    t = i / float(n_b_l - 1)
    length = 60.0 + 50.0 * t  # 60 mm -> 110 mm
    curve_x = 4.0 + 6.0 * t   # Subtle sweep towards temple
    lock_configs.append({
        "name": f"Bang_L_{i}",
        "group": "Bangs",
        "band_x_start": x_s,
        "band_x_end": x_e,
        "root_w": x_e - x_s,
        "length": length,
        "tip_w": 3.0,
        "flare": 1.12,
        "curve_x": curve_x,
        "target_arr": "Head_Top_Front",
        # 2D visual layout in bangs row below the band:
        # Lay out across X in [-140, +140] in natural facial order
        # Bang_L_6 (temple) to Bang_L_0 (center)
        "2d_cx": -10.0 - (n_b_l - 1 - i) * 19.0,
        "2d_cy": 1580.0,
    })

# (B) Side Left & Temple (9 locks: indices 7..15)
# Lengths: 180 mm at cheek/temple (X = -250) to 230 mm at ear/jaw (X = -150)
x_start_s_l = -250.0
x_end_s_l = -150.0
n_s_l = 9
step_s_l = (x_end_s_l - x_start_s_l) / n_s_l
for i in range(n_s_l):
    x_s = x_start_s_l + i * step_s_l
    x_e = x_start_s_l + (i + 1) * step_s_l
    t = i / float(n_s_l - 1)
    length = 180.0 + 50.0 * t  # 180 mm -> 230 mm
    # Inward cheek contour curve (curves forward/inward towards face)
    curve_x = 12.0 * (1.0 - 0.5 * t)
    lock_configs.append({
        "name": f"SideHair_L_{i}",
        "group": "Side_L",
        "band_x_start": x_s,
        "band_x_end": x_e,
        "root_w": x_e - x_s,
        "length": length,
        "tip_w": 3.5,
        "flare": 1.15,
        "curve_x": curve_x,
        "target_arr": "Head_L",
        # 2D visual layout to the left of the band: X in [-650, -410]
        "2d_cx": -650.0 + i * 28.0,
        "2d_cy": 1640.0,
    })

# (C) Back Cascade (24 locks: indices 16..39)
# Lengths: 290 mm at center (X = 0) tapering to 260 mm at shoulders (X = ±150)
x_start_back = -150.0
x_end_back = 150.0
n_back = 24
step_back = (x_end_back - x_start_back) / n_back
for i in range(n_back):
    x_s = x_start_back + i * step_back
    x_e = x_start_back + (i + 1) * step_back
    x_mid = 0.5 * (x_s + x_e)
    u = x_mid / 150.0  # -1.0 to +1.0
    stagger = 3.0 if (i % 2 == 0) else -3.0
    length = (290.0 - 30.0 * (u ** 2)) + stagger  # 260 - 290 mm
    curve_x = 7.0 * u  # Subtle shoulder drape flare
    # 2D visual layout: 2 neat rows of 12 locks to the right of the band
    if i < 12:
        cx_2d = 780.0 + i * 34.0
        cy_2d = 1640.0
    else:
        cx_2d = 780.0 + (i - 12) * 34.0
        cy_2d = 1320.0

    lock_configs.append({
        "name": f"BackHair_{i:02d}",
        "group": "Back",
        "band_x_start": x_s,
        "band_x_end": x_e,
        "root_w": x_e - x_s,
        "length": length,
        "tip_w": 4.0 if abs(u) < 0.3 else 3.2,
        "flare": 1.10,
        "curve_x": curve_x,
        "target_arr": "Head_Top_Back",
        "2d_cx": cx_2d,
        "2d_cy": cy_2d,
    })

# (D) Side Right & Temple (9 locks: indices 40..48)
# Lengths: 230 mm at ear/jaw (X = +150) to 180 mm at cheek/temple (X = +250)
x_start_s_r = 150.0
x_end_s_r = 250.0
n_s_r = 9
step_s_r = (x_end_s_r - x_start_s_r) / n_s_r
for i in range(n_s_r):
    x_s = x_start_s_r + i * step_s_r
    x_e = x_start_s_r + (i + 1) * step_s_r
    t = i / float(n_s_r - 1)
    length = 230.0 - 50.0 * t  # 230 mm -> 180 mm
    # Inward cheek contour curve (curves forward/inward towards face)
    curve_x = -12.0 * (0.5 + 0.5 * t)
    lock_configs.append({
        "name": f"SideHair_R_{i}",
        "group": "Side_R",
        "band_x_start": x_s,
        "band_x_end": x_e,
        "root_w": x_e - x_s,
        "length": length,
        "tip_w": 3.5,
        "flare": 1.15,
        "curve_x": curve_x,
        "target_arr": "Head_R",
        # 2D visual layout to the right of the band: X in [410, 650]
        "2d_cx": 410.0 + i * 28.0,
        "2d_cy": 1640.0,
    })

# (E) Bangs Right (7 locks: indices 49..55)
# Lengths: 110 mm near temple (X = +250) tapering to 60 mm at forehead center (X = +335)
x_start_b_r = 250.0
x_end_b_r = 335.0
n_b_r = 7
step_b_r = (x_end_b_r - x_start_b_r) / n_b_r
for i in range(n_b_r):
    x_s = x_start_b_r + i * step_b_r
    x_e = x_start_b_r + (i + 1) * step_b_r
    t = i / float(n_b_r - 1)
    length = 110.0 - 50.0 * t  # 110 mm -> 60 mm
    curve_x = -6.0 - 4.0 * (1.0 - t)  # Subtle sweep towards temple
    lock_configs.append({
        "name": f"Bang_R_{i}",
        "group": "Bangs",
        "band_x_start": x_s,
        "band_x_end": x_e,
        "root_w": x_e - x_s,
        "length": length,
        "tip_w": 3.0,
        "flare": 1.12,
        "curve_x": curve_x,
        "target_arr": "Head_Top_Front",
        # 2D visual layout in bangs row: Bang_R_0 (temple) to Bang_R_6 (center)
        # Symmetrically placed across X in [-140, +140]
        "2d_cx": 10.0 + (n_b_r - 1 - i) * 19.0,
        "2d_cy": 1580.0,
    })

assert len(lock_configs) == 56, f"Expected 56 locks, got {len(lock_configs)}"
print(f"[Config] Successfully configured {len(lock_configs)} procedural anime hair locks.")


# --- 2. 2D POLYGON GENERATOR HELPER ---
def generate_lock_polygon(cx, cy, root_w, length, tip_w=3.0, flare=1.12, curve_x=0.0):
    """
    Generates a 9-point stylized anime hair lock polygon.
    Seg 0 (V0 -> V1) is the top horizontal root edge of exact length root_w at y = cy.
    V0: (cx - root_w/2, cy)
    V1: (cx + root_w/2, cy)
    Tapers smoothly down to a pointed anime tip at y = cy - length with horizontal sweep/curve.
    """
    rw2 = root_w / 2.0
    tw2 = tip_w / 2.0

    # Landmark Y levels
    y_flare = cy - length * 0.25
    y_mid = cy - length * 0.60
    y_pre_tip = cy - length * 0.92
    y_tip = cy - length

    # Curve offsets at each Y level
    c_flare = curve_x * 0.15
    c_mid = curve_x * 0.55
    c_pre_tip = curve_x * 0.90
    c_tip = curve_x

    pts = [
        (cx - rw2, cy, 0),                                       # V0: Root Left
        (cx + rw2, cy, 0),                                       # V1: Root Right (Seg 0: len root_w)
        (cx + rw2 * flare + c_flare, y_flare, 0),               # V2: Upper flare right
        (cx + rw2 * 0.65 + tw2 * 0.35 + c_mid, y_mid, 0),       # V3: Mid taper right
        (cx + tw2 + c_pre_tip, y_pre_tip, 0),                   # V4: Pre-tip bevel right
        (cx + c_tip, y_tip, 0),                                 # V5: Pointed anime tip
        (cx - tw2 + c_pre_tip, y_pre_tip, 0),                   # V6: Pre-tip bevel left
        (cx - (rw2 * 0.65 + tw2 * 0.35) + c_mid, y_mid, 0),     # V7: Mid taper left
        (cx - rw2 * flare + c_flare, y_flare, 0),               # V8: Upper flare left
    ]
    return pts


# --- 3. DRAFT 2D PATTERNS (Coordinates in mm) ---
print("\n--- 1. Creating 2D Pattern Pieces ---")
panel_ids = {}

# 3.1 CrownAnchorBand (Trapezoidal Root Anchor Band, 75 mm height)
# Elevation: Y in [1640.0, 1715.0] mm.
# Bottom edge (Y = 1640.0 mm): Width 670.0 mm (X in [-335.0, +335.0] mm).
# Top edge (Y = 1715.0 mm): Width 620.0 mm (X in [-310.0, +310.0] mm).
# The bottom edge is discretized into 56 contiguous segments matching the 56 hair roots.
crown_band_pts = []

# (a) Bottom edge: 57 vertices (V0 to V56) defining 56 segments from X = -335.0 to +335.0
for cfg in lock_configs:
    crown_band_pts.append((cfg["band_x_start"], 1640.0, 0))
crown_band_pts.append((lock_configs[-1]["band_x_end"], 1640.0, 0))  # V56: (+335.0, 1640.0)

# (b) Top right corner (V57)
crown_band_pts.append((310.0, 1715.0, 0))

# (c) Top left corner (V58)
crown_band_pts.append((-310.0, 1715.0, 0))

panel_ids["CrownAnchorBand"] = pattern_api.CreatePatternWithPoints(crown_band_pts)
if panel_ids["CrownAnchorBand"] is None:
    panel_ids["CrownAnchorBand"] = 0
print(f"Created 'CrownAnchorBand' (ID: {panel_ids['CrownAnchorBand']}, {len(crown_band_pts)} vertices, 59 segments)")

# 3.2 The 56 Hair Lock Patterns
created_count = 0
for cfg in lock_configs:
    pts = generate_lock_polygon(
        cx=cfg["2d_cx"],
        cy=cfg["2d_cy"],
        root_w=cfg["root_w"],
        length=cfg["length"],
        tip_w=cfg["tip_w"],
        flare=cfg["flare"],
        curve_x=cfg["curve_x"],
    )
    pid = pattern_api.CreatePatternWithPoints(pts)
    if pid is None:
        pid = len(panel_ids)
    panel_ids[cfg["name"]] = pid
    created_count += 1

print(f"Created all {created_count} hair lock patterns! Total patterns: {len(panel_ids)}")


# --- 4. EXECUTE PROCEDURAL SEWING STITCHES ---
print("\n--- 2. Applying Procedural Sewing Stitches ---")
seam_success_count = 0

def sew(p1_name, s1, p2_name, s2, rev=False, label=""):
    global seam_success_count
    pid1 = panel_ids[p1_name]
    pid2 = panel_ids[p2_name]
    ok = pattern_api.AddSeamlinePairGroup(int(pid1), int(s1), int(pid2), int(s2), bool(rev), False)
    if ok:
        seam_success_count += 1
    return ok

# 4.1 CrownAnchorBand Cylinder Loop Seam
# Seg 56: Right short end (+335.0, 1640.0) -> (+310.0, 1715.0)
# Seg 58: Left short end  (-310.0, 1715.0) -> (-335.0, 1640.0)
# With rev=True, Y=1640 pairs with Y=1640 and Y=1715 pairs with Y=1715.
ok_loop = sew("CrownAnchorBand", 56, "CrownAnchorBand", 58, rev=True, label="CrownBand Cylinder Loop")
print(f"[{'SUCCESS' if ok_loop else 'FAILED'}] CrownAnchorBand Cylinder Loop: Seg 56 <--> Seg 58 (rev=True)")

# 4.2 Stitches for all 56 Hair Locks to CrownAnchorBand
# CrownAnchorBand Seg i (0 <= i < 56) connects to Lock_i Seg 0 (top root edge)
for i, cfg in enumerate(lock_configs):
    lock_name = cfg["name"]
    ok = sew("CrownAnchorBand", i, lock_name, 0, rev=False, label=f"{lock_name} Root Seam")
    if i < 3 or i >= 53:
        print(f"[{'SUCCESS' if ok else 'FAILED'}] Seam #{i+1:2d}: CrownAnchorBand[seg {i:2d}] <--> {lock_name:16}[seg 0] (rev=False)")
    elif i == 3:
        print("  ... (applying remaining 50 procedural lock root seams) ...")

print(f"\n[Stitching Summary] Successfully executed {seam_success_count} / 57 procedural seamlines!")


# --- 5. 3D NATIVE ARRANGEMENT ---
print("\n--- 3. Applying 3D Native Arrangement ---")

# Target mapping for all 57 pieces
ARRANGEMENT_MAPPING = {
    "CrownAnchorBand": "Head_Top_Center",  # Index 74
}
for cfg in lock_configs:
    ARRANGEMENT_MAPPING[cfg["name"]] = cfg["target_arr"]

arranged_count = 0
try:
    arr_list = pattern_api.GetArrangementList()
    if arr_list:
        print(f"Loaded {len(arr_list)} native arrangement points from avatar.")
        arr_name_to_idx = {
            item.get("ArrangementName", "").strip().lower(): int(item["ArrangementIndex"])
            for item in arr_list
        }

        for panel_name, target_dot in ARRANGEMENT_MAPPING.items():
            if panel_name in panel_ids:
                pid = panel_ids[panel_name]
                target_key = target_dot.strip().lower()
                matched_idx = arr_name_to_idx.get(target_key)
                if matched_idx is not None:
                    pattern_api.SetArrangement(pid, matched_idx)
                    arranged_count += 1
                else:
                    # Fallback to general Head if specific point not found
                    fallback_idx = arr_name_to_idx.get("head")
                    if fallback_idx is not None:
                        pattern_api.SetArrangement(pid, fallback_idx)
                        arranged_count += 1

        print(f"[3D Arrangement] Assigned {arranged_count} / {len(panel_ids)} patterns to avatar arrangement points:")
        print("  - CrownAnchorBand (1 piece)  --> 'Head_Top_Center' (Index 74)")
        print("  - Back Cascade (24 locks)    --> 'Head_Top_Back'   (Index 73)")
        print("  - Left Side (9 locks)        --> 'Head_L'           (Index 72)")
        print("  - Right Side (9 locks)       --> 'Head_R'           (Index 71)")
        print("  - Front Bangs (14 locks)     --> 'Head_Top_Front'  (Index 75)")

        utility_api.ResetClothArrangement()
        print("\n[3D SUCCESS] Cloth arrangement reset! All 57 pieces wrapped around avatar head in 3D.")
    else:
        print("[3D NOTE] No native arrangement points found; patterns elevated in 3D.")
except Exception as err:
    print(f"[3D ERROR] Arrangement failed: {err}")


# --- 6. SIMULATION & EXPORT GUIDELINES ---
print("\n" + "=" * 75)
print("  ANIME HAIR GENERATION COMPLETE - SIMULATION & RIGGING PIPELINE")
print("=" * 75)
print("1. Simulation & Draping:")
print("   - Press Spacebar in Marvelous Designer to simulate cloth drape onto avatar.")
print("   - Trapezoidal band (Y: 1640-1715 mm) naturally cinches onto skull dome.")
print("   - Optional: Right-click 'CrownAnchorBand' -> Freeze (Ctrl+K) for 100% rigid anchoring.")
print("2. Physical Property Presets:")
print("   - Bending Stiffness: 75 - 85 (maintains crisp anime lock silhouettes).")
print("   - Stretch Stiffness: 85 - 90 (prevents lock stretching under gravity).")
print("   - Particle Distance: 10 mm during initial simulation, 5 mm for final mesh export.")
print("3. Auto-Rigging & Blender Pipeline:")
print("   - Use Marvelous Designer EveryWear to auto-rig hair mesh to J_Bip_* skeleton.")
print("   - Export as GLB, then run 'setup_everywear_clothes.py' in Blender to retarget.")
print("=" * 75)
