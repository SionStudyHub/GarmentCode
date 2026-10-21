"""
Marvelous Designer Pattern, Auto-Stitching & Explicit 3D Native Arrangement
Tailored for: SionFemaleBodyV1 (Height: 152.1 cm)
Measurements Source: trial-female-measurements.yaml

Features:
1. Anatomical 2D Alignment:
   - Front panel lands directly on avatar torso silhouette (X = 0, Y = 902mm -> 1250mm).
   - Back panel sits beside avatar at matching torso height.
   - Sleeves align with avatar arms (Left at X = -500mm, Right at X = +1050mm).
   - Neckband sits right above neckline.
2. Auto-Stitching:
   - Stitches all 13 seams (shoulders, sides, sleeves, armholes, collar) via pattern_api.AddSeamlinePairGroup.
3. Explicit 3D Native Arrangement:
   - Directly assigns user-selected blue dots by their exact Marvelous Designer names:
       * Front Bodice  --> Body_Front_Center_1 (Upper Chest)
       * Back Bodice   --> Body_Back_Center_1  (Upper Back)
       * Left Sleeve   --> Arm_Outside_1_L     (Left Bicep Outside)
       * Right Sleeve  --> Arm_Outside_1_R     (Right Bicep Outside)
       * Neckband      --> Neck_Front          (Front Collar)
   - Calls utility_api.ResetClothArrangement() so all patterns wrap around the 3D avatar!
"""

import math

try:
    import pattern_api
    import utility_api
except ImportError:
    class MockPatternApi:
        def __init__(self):
            self._counter = 0

        def CreatePatternWithPoints(self, points):
            idx = self._counter
            self._counter += 1
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            print(f"[Mock] Created pattern #{idx} with {len(points)} vertices. Bounds: X=[{min(xs):.1f}, {max(xs):.1f}], Y=[{min(ys):.1f}, {max(ys):.1f}]")
            return idx

        def AddSeamlinePairGroup(self, p1, s1, p2, s2, reverse, is_fold):
            print(f"[Mock] Stitched Pattern {p1}[seg {s1}] <--> Pattern {p2}[seg {s2}] (reverse={reverse})")
            return True

        def GetArrangementList(self):
            return [
                {'ArrangementIndex': '0', 'ArrangementName': 'Arm_Front_1_L', 'ArrangementType': 'Curved'},
                {'ArrangementIndex': '1', 'ArrangementName': 'Arm_Front_1_R', 'ArrangementType': 'Curved'},
                {'ArrangementIndex': '2', 'ArrangementName': 'Arm_Outside_1_L', 'ArrangementType': 'Curved'},
                {'ArrangementIndex': '3', 'ArrangementName': 'Arm_Outside_1_R', 'ArrangementType': 'Curved'},
                {'ArrangementIndex': '4', 'ArrangementName': 'Body_Front_Center_1', 'ArrangementType': 'Curved'},
                {'ArrangementIndex': '5', 'ArrangementName': 'Body_Back_Center_1', 'ArrangementType': 'Curved'},
                {'ArrangementIndex': '6', 'ArrangementName': 'Neck_Front', 'ArrangementType': 'Curved'},
            ]

        def SetArrangement(self, pattern_id, point_id):
            print(f"[Mock] SetArrangement: Pattern {pattern_id} -> Point {point_id}")

    class MockUtilityApi:
        @staticmethod
        def ResetClothArrangement():
            print("[Mock] utility_api.ResetClothArrangement() called - patterns wrapped in 3D!")
        @staticmethod
        def Simulate(state):
            pass

    pattern_api = MockPatternApi()
    utility_api = MockUtilityApi()


# ==============================================================================
# 1. EXPLICIT 3D ARRANGEMENT SELECTION (Exact Marvelous Designer Blue Dots)
# ==============================================================================
# You can choose any exact blue dot name from the avatar's arrangement points.
# Default anatomical targets for a fitted t-shirt:
EXPLICIT_ARRANGEMENT_TARGETS = {
    "front": "Body_Front_Center_1",  # Upper Chest / Sternum
    "back": "Body_Back_Center_1",    # Upper Back / Intersnapular Spine
    "left_sleeve": "Arm_Outside_1_L",# Left Bicep Outside / Shoulder Cap
    "right_sleeve": "Arm_Outside_1_R",# Right Bicep Outside / Shoulder Cap
    "neckband": "Neck_Front",        # Front Collar Ring
}


# ==============================================================================
# 2. SCALE & ANATOMICAL LANDMARK HEIGHTS (cm -> mm)
# ==============================================================================
scale = 10.0

def pt(x, y):
    """Converts (x, y) in cm to scaled (x, y, 0) in MD millimeters."""
    return (round(x * scale, 3), round(y * scale, 3), 0)

# Avatar Anatomical Landmark Y Heights (from SionFemaleBodyV1 3D skeleton in cm):
neck_y = 125.0             # 1250 mm: Nape of neck / shoulder neck point
sh_tip_y = 122.5           # 1225 mm: Acromion / shoulder tip
armscye_y = 109.0          # 1090 mm: Underarm level
waist_y = 100.0            # 1000 mm: Natural waistline
hem_y = 90.2               # 902 mm: Bottom hem level (mid-hip, above inseam 77.7cm)
front_scoop_y = 118.2      # 1182 mm: Front neck scoop apex (6.8 cm drop)
back_scoop_y = 123.2       # 1232 mm: Back neck shallow drop (1.8 cm drop)

# Avatar Widths & Design Ease (in cm):
bust_w = 18.3              # 18.3 cm half-width (73.2 cm total circumference with ease)
waist_w = 13.5             # 13.5 cm half-width (54.0 cm total circumference with ease)
hem_w = 17.0               # 17.0 cm half-width (68.0 cm total circumference)
sh_w = 15.5                # 15.5 cm shoulder tip distance from center
neck_w = 6.0               # 6.0 cm half neck opening width (12.0 cm total)

# Sleeve parameters (in cm):
sleeve_len = 14.0          # 14.0 cm short sleeve length
sleeve_cap_h = 10.5        # 10.5 cm sleeve cap height
bicep_w = 12.5             # 12.5 cm bicep half-width (25.0 cm total)
cuff_w = 11.0              # 11.0 cm cuff half-width (22.0 cm total)
sleeve_base_y = 100.0      # Aligned with waist level, crown reaches shoulder level


# ==============================================================================
# 3. CREATE PATTERNS AT ANATOMICAL POSITIONS
# ==============================================================================

# --- PIECE 1: FRONT BODICE (Directly Centered on Avatar Torso: X = 0) ---
cx_front = 0.0
front_pts = [
    pt(cx_front - hem_w, hem_y),                     # 0: Hem Left
    pt(cx_front + hem_w, hem_y),                     # 1: Hem Right      (Seg 0: Hem)
    pt(cx_front + waist_w, waist_y),                 # 2: Waist Right    (Seg 1: Lower Side R)
    pt(cx_front + bust_w, armscye_y),                # 3: Underarm Right (Seg 2: Upper Side R)
    pt(cx_front + sh_w, sh_tip_y),                   # 4: Sh-Tip Right   (Seg 3: Armhole R)
    pt(cx_front + neck_w, neck_y),                   # 5: Neck Right     (Seg 4: Shoulder R)
    pt(cx_front, front_scoop_y),                     # 6: Center Scoop   (Seg 5: Neck R)
    pt(cx_front - neck_w, neck_y),                   # 7: Neck Left      (Seg 6: Neck L)
    pt(cx_front - sh_w, sh_tip_y),                   # 8: Sh-Tip Left    (Seg 7: Shoulder L)
    pt(cx_front - bust_w, armscye_y),                # 9: Underarm Left  (Seg 8: Armhole L)
    pt(cx_front - waist_w, waist_y),                 # 10: Waist Left    (Seg 9: Upper Side L)
]                                                    #                   (Seg 10: Lower Side L)
front_id = pattern_api.CreatePatternWithPoints(front_pts)
if front_id is None: front_id = 0

# --- PIECE 2: BACK BODICE (Placed Right of Avatar: X = 550mm) ---
cx_back = 55.0
back_pts = [
    pt(cx_back - hem_w, hem_y),                      # 0
    pt(cx_back + hem_w, hem_y),                      # 1
    pt(cx_back + waist_w, waist_y),                  # 2
    pt(cx_back + bust_w, armscye_y),                 # 3
    pt(cx_back + sh_w, sh_tip_y),                    # 4
    pt(cx_back + neck_w, neck_y),                    # 5
    pt(cx_back, back_scoop_y),                       # 6: Shallow back neck
    pt(cx_back - neck_w, neck_y),                    # 7
    pt(cx_back - sh_w, sh_tip_y),                    # 8
    pt(cx_back - bust_w, armscye_y),                 # 9
    pt(cx_back - waist_w, waist_y),                  # 10
]
back_id = pattern_api.CreatePatternWithPoints(back_pts)
if back_id is None: back_id = 1

# --- PIECE 3: LEFT SLEEVE (Placed near Left Arm: X = -500mm) ---
# --- PIECE 3: LEFT SLEEVE (Placed near Left Arm: +X side, X = +1050mm) ---
cx_ls = 105.0
left_sleeve_pts = [
    pt(cx_ls - cuff_w, sleeve_base_y),               # 0: Cuff Left
    pt(cx_ls + cuff_w, sleeve_base_y),               # 1: Cuff Right     (Seg 0: Cuff Hem)
    pt(cx_ls + bicep_w, sleeve_base_y + sleeve_len), # 2: Underarm Right (Seg 1: Underarm Seam R)
    pt(cx_ls, sleeve_base_y + sleeve_len + sleeve_cap_h), # 3: Crown Top  (Seg 2: Cap R)
    pt(cx_ls - bicep_w, sleeve_base_y + sleeve_len), # 4: Underarm Left  (Seg 3: Cap L)
]                                                    #                   (Seg 4: Underarm Seam L)
left_sleeve_id = pattern_api.CreatePatternWithPoints(left_sleeve_pts)
if left_sleeve_id is None: left_sleeve_id = 2

# --- PIECE 4: RIGHT SLEEVE (Placed near Right Arm: -X side, X = -500mm) ---
cx_rs = -50.0
right_sleeve_pts = [
    pt(cx_rs - cuff_w, sleeve_base_y),               # 0: Cuff Left
    pt(cx_rs + cuff_w, sleeve_base_y),               # 1: Cuff Right     (Seg 0: Cuff Hem)
    pt(cx_rs + bicep_w, sleeve_base_y + sleeve_len), # 2: Underarm Right (Seg 1: Underarm Seam R)
    pt(cx_rs, sleeve_base_y + sleeve_len + sleeve_cap_h), # 3: Crown Top  (Seg 2: Cap R)
    pt(cx_rs - bicep_w, sleeve_base_y + sleeve_len), # 4: Underarm Left  (Seg 3: Cap L)
]                                                    #                   (Seg 4: Underarm Seam L)
right_sleeve_id = pattern_api.CreatePatternWithPoints(right_sleeve_pts)
if right_sleeve_id is None: right_sleeve_id = 3

# --- PIECE 5: NECKBAND COLLAR (Above Neck: X = 0, Y = 1330mm) ---
neck_len = 34.0
neck_h = 2.5
collar_y = 133.0
neckband_pts = [
    pt(-neck_len / 2.0, collar_y),                   # 0: Bottom-Left
    pt(neck_len / 2.0, collar_y),                    # 1: Bottom-Right   (Seg 0: Neck Seam Edge)
    pt(neck_len / 2.0, collar_y + neck_h),           # 2: Top-Right      (Seg 1: Short End R)
    pt(-neck_len / 2.0, collar_y + neck_h),          # 3: Top-Left       (Seg 2: Finished Edge)
]                                                    #                   (Seg 3: Short End L)
neckband_id = pattern_api.CreatePatternWithPoints(neckband_pts)
if neckband_id is None: neckband_id = 4


# ==============================================================================
# 4. AUTOMATIC SEWING / STITCHING (pattern_api.AddSeamlinePairGroup)
# ==============================================================================
print("\n--- Applying Sewing Stitches ---")

def stitch(p1, seg1, p2, seg2, reverse=False, label=""):
    """Sews two pattern segments together."""
    try:
        success = pattern_api.AddSeamlinePairGroup(int(p1), int(seg1), int(p2), int(seg2), bool(reverse), False)
        status = "SUCCESS" if success else "FAILED"
        print(f"[{status}] {label}: Pattern {p1}[seg {seg1}] <--> Pattern {p2}[seg {seg2}]")
        return success
    except Exception as err:
        print(f"[WARN] Failed {label}: {err}")
        return False

# 1. Shoulder Seams (Back is horizontally flipped by MD arrangement point)
stitch(front_id, 4, back_id, 7, reverse=True, label="Left Shoulder Seam (Front L <--> Back L)")
stitch(front_id, 7, back_id, 4, reverse=True, label="Right Shoulder Seam (Front R <--> Back R)")

# 2. Side Seams (Back is horizontally flipped by MD arrangement point)
stitch(front_id, 1, back_id, 10, reverse=True, label="Left Lower Side Seam (Hem->Waist)")
stitch(front_id, 2, back_id, 9, reverse=True, label="Left Upper Side Seam (Waist->Arm)")
stitch(front_id, 9, back_id, 2, reverse=True, label="Right Upper Side Seam (Arm->Waist)")
stitch(front_id, 10, back_id, 1, reverse=True, label="Right Lower Side Seam (Waist->Hem)")

# 3. Sleeve Tubes (Self-seaming opposite edges of polygon requires reverse=True to pair Cuff-to-Cuff)
stitch(left_sleeve_id, 1, left_sleeve_id, 4, reverse=True, label="Left Sleeve Tube (Cuff<->Cuff, Underarm<->Underarm)")
stitch(right_sleeve_id, 1, right_sleeve_id, 4, reverse=True, label="Right Sleeve Tube (Cuff<->Cuff, Underarm<->Underarm)")

# 4. Sleeves to Armholes (Correct Front/Back Orientation & reverse=True for opposite loop tracing):
# Left Sleeve (Pattern 2): seg 3 is Front (+Z), seg 2 is Back (-Z)
stitch(left_sleeve_id, 3, front_id, 3, reverse=True, label="Left Sleeve Front to Front Left Armhole")
stitch(left_sleeve_id, 2, back_id, 8, reverse=True, label="Left Sleeve Back to Back Left Armhole")

# Right Sleeve (Pattern 3): seg 2 is Front (+Z), seg 3 is Back (-Z)
stitch(right_sleeve_id, 2, front_id, 8, reverse=True, label="Right Sleeve Front to Front Right Armhole")
stitch(right_sleeve_id, 3, back_id, 3, reverse=True, label="Right Sleeve Back to Back Right Armhole")

# 5. Collar Ring Closure (Self-seaming opposite edges of polygon requires reverse=True to pair Bottom-to-Bottom)
stitch(neckband_id, 1, neckband_id, 3, reverse=True, label="Neckband Ring Closure (Bottom<->Bottom, Top<->Top)")


# ==============================================================================
# 5. EXPLICIT 3D NATIVE ARRANGEMENT BY EXACT BLUE DOT NAME
# ==============================================================================
print("\n--- Applying Explicit 3D Native Arrangement ---")

def resolve_arrangement_point(arr_list, exact_target, fallback_keywords=None, forbidden=None):
    """
    1. Attempts exact name match first (e.g. 'Body_Front_Center_1').
    2. Falls back to keyword matching if the avatar uses an alternate preset.
    """
    # 1. Exact match
    for item in arr_list:
        name = item.get("ArrangementName", "")
        if name.strip().lower() == exact_target.strip().lower():
            return int(item["ArrangementIndex"]), name

    # 2. Fallback keyword match
    if fallback_keywords:
        for kw_group in fallback_keywords:
            for item in arr_list:
                name = item.get("ArrangementName", "").lower()
                if forbidden and any(f.lower() in name for f in forbidden):
                    continue
                if all(k.lower() in name for k in kw_group):
                    return int(item["ArrangementIndex"]), item.get("ArrangementName")

    return None, None

try:
    arr_list = pattern_api.GetArrangementList()
    if arr_list and len(arr_list) > 0:
        print(f"Loaded {len(arr_list)} arrangement points from avatar.")
        
        mappings = [
            ("Front Bodice", front_id, EXPLICIT_ARRANGEMENT_TARGETS["front"], 
             [["body_front"], ["front", "body"], ["chest"]], ["arm", "leg"]),
            ("Back Bodice", back_id, EXPLICIT_ARRANGEMENT_TARGETS["back"], 
             [["body_back"], ["back", "body"], ["back_torso"]], ["arm", "leg"]),
            ("Left Sleeve", left_sleeve_id, EXPLICIT_ARRANGEMENT_TARGETS["left_sleeve"], 
             [["arm", "outside", "l"], ["arm", "front", "l"], ["arm", "_l"]], ["_r", "right", "leg", "body"]),
            ("Right Sleeve", right_sleeve_id, EXPLICIT_ARRANGEMENT_TARGETS["right_sleeve"], 
             [["arm", "outside", "r"], ["arm", "front", "r"], ["arm", "_r"]], ["_l", "left", "leg", "body"]),
            ("Neckband", neckband_id, EXPLICIT_ARRANGEMENT_TARGETS["neckband"], 
             [["neck", "front"], ["neck"], ["collar"]], ["arm", "leg", "body"]),
        ]

        for part_name, pattern_id, exact_target, fallbacks, forbidden in mappings:
            pt_id, pt_name = resolve_arrangement_point(arr_list, exact_target, fallbacks, forbidden)
            if pt_id is not None:
                pattern_api.SetArrangement(pattern_id, pt_id)
                print(f"[3D ASSIGN] {part_name:12} (ID {pattern_id}) --> Point [{pt_id:2}] '{pt_name}' (Target: {exact_target})")
            else:
                print(f"[3D WARN] Could not find arrangement point for {part_name} (Target: {exact_target})")

        # Snap all patterns in 3D to their assigned arrangement cylinders
        utility_api.ResetClothArrangement()
        print("\n[3D SUCCESS] Cloth arrangement reset! Patterns are now wrapped around the avatar in 3D.")
    else:
        print("[3D NOTE] No arrangement points found on avatar.")
except Exception as e:
    print(f"[3D WARN] Error applying 3D arrangement: {e}")

print("\nFinished! Ready for 3D simulation (Spacebar).")
