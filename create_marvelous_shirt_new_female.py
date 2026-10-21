"""
Marvelous Designer Skin-Tight Tailored Compression Garment
Avatar Model: new_base_female (new_base_female.vrm)
Total Height: 173.22 cm
Anthropometric Ground Truth: new_base_female/new_base_female_digital_tailor_spec.json

Verified Production Specifications:
1. Back Bodice: Reflected 2D Horizontal Flip (X' = 2*cx - X)
2. Torso & Armhole Seams: reverse=False (straight, parallel non-crossing)
3. Self-Closing Tubes (Sleeves & Collar): reverse=True (closes cylinders cleanly without Mobius twist)
"""

try:
    import pattern_api
    import utility_api
except ImportError:
    class MockPatternApi:
        def __init__(self): self._counter = 0
        def CreatePatternWithPoints(self, pts):
            idx = self._counter; self._counter += 1
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            print(f"[Mock Pattern] #{idx} created ({len(pts)} vertices) Bounds: X=[{min(xs):.1f}, {max(xs):.1f}], Y=[{min(ys):.1f}, {max(ys):.1f}] mm")
            return idx
        def AddSeamlinePairGroup(self, p1, s1, p2, s2, rev, fold):
            print(f"[Mock Stitch] Pattern {p1}[seg {s1}] <--> Pattern {p2}[seg {s2}] (reverse={rev})")
            return True
        def GetArrangementList(self):
            return [
                {"ArrangementIndex": "18", "ArrangementName": "Arm_Outside_1_L"},
                {"ArrangementIndex": "19", "ArrangementName": "Arm_Outside_1_R"},
                {"ArrangementIndex": "59", "ArrangementName": "Body_Front_Center_1"},
                {"ArrangementIndex": "42", "ArrangementName": "Body_Back_Center_1"},
                {"ArrangementIndex": "78", "ArrangementName": "Neck_Front"},
            ]
        def SetArrangement(self, pid, pt_id):
            print(f"[Mock Arrangement] Pattern {pid} --> Point {pt_id}")
    class MockUtilityApi:
        @staticmethod
        def ResetClothArrangement(): print("[Mock] utility_api.ResetClothArrangement() called - 3D wrapped!")
        @staticmethod
        def Simulate(state): pass
    pattern_api = MockPatternApi()
    utility_api = MockUtilityApi()

scale = 10.0
def pt(x, y): return (round(x * scale, 3), round(y * scale, 3), 0)

# Heights (cm)
neck_y = 144.02
sh_y   = 140.16
arm_y  = 131.87
waist_y = 116.41
hem_y  = 107.78
front_scoop_y = 140.52
back_scoop_y  = 142.82

# Widths (cm) with -2% ease
neck_w = 3.33
sh_w   = 9.49
w_underarm_f = 16.00
w_underarm_b = 14.25
w_waist_f    = 11.60
w_waist_b    = 10.70
w_hem_f      = 15.10
w_hem_b      = 14.90

# Sleeve parameters (cm) with -2% ease
bicep_w    = 11.30   # Half-width (Circumference: 22.6 cm)
cuff_w     = 10.20   # Half-width (Circumference: 20.4 cm)
sleeve_len = 12.00   # Sleeve length
cap_h      = 11.00   # Armscye cap height
s_base_y   = 124.00  # 2D window sleeve elevation

# Collar band (cm)
collar_circ = 21.53  # -2% narrow neck circumference
collar_h    = 2.50   # Stand collar height
c_elev_y    = 150.00 # 2D window collar elevation

# ==============================================================================
# 2. GENERATE 2D PATTERNS
# ==============================================================================
print("=== Generating Skin-Tight Tailored Top for new_base_female ===")

# 1. Front Bodice (Clockwise)
front_pts = [
    pt(0, hem_y),             # 0: Center Hem
    pt(-w_hem_f, hem_y),      # 1: Right Hem Corner       (Seg 0: Lower Right Hem)
    pt(-w_waist_f, waist_y),  # 2: Right Waist            (Seg 1: Lower Right Side)
    pt(-w_underarm_f, arm_y), # 3: Right Underarm         (Seg 2: Upper Right Side)
    pt(-sh_w, sh_y),          # 4: Right Shoulder Tip     (Seg 3: Right Armhole)
    pt(-neck_w, neck_y),      # 5: Right Neck Point       (Seg 4: Right Shoulder)
    pt(0, front_scoop_y),     # 6: Center Front Scoop     (Seg 5: Right Neckline)
    pt(neck_w, neck_y),       # 7: Left Neck Point        (Seg 6: Left Neckline)
    pt(sh_w, sh_y),           # 8: Left Shoulder Tip      (Seg 7: Left Shoulder)
    pt(w_underarm_f, arm_y),  # 9: Left Underarm          (Seg 8: Left Armhole)
    pt(w_waist_f, waist_y),   # 10: Left Waist            (Seg 9: Upper Left Side)
    pt(w_hem_f, hem_y),       # 11: Left Hem Corner       (Seg 10: Lower Left Side)
]
front_id = pattern_api.CreatePatternWithPoints(front_pts)
if front_id is None: front_id = 0

# 2. Back Bodice (Reflected 2D Horizontal Flip: X' = 2*cx_b - X)
cx_b = 55.0
raw_back_pts = [
    pt(cx_b, hem_y),              # 0: Center Hem
    pt(cx_b - w_hem_b, hem_y),    # 1: Right Hem Corner       (Seg 0: Lower Right Hem)
    pt(cx_b - w_waist_b, waist_y), # 2: Right Waist            (Seg 1: Lower Right Side)
    pt(cx_b - w_underarm_b, arm_y),# 3: Right Underarm         (Seg 2: Upper Right Side)
    pt(cx_b - sh_w, sh_y),        # 4: Right Shoulder Tip     (Seg 3: Right Armhole)
    pt(cx_b - neck_w, neck_y),    # 5: Right Neck Point       (Seg 4: Right Shoulder)
    pt(cx_b, back_scoop_y),       # 6: Center Back Scoop      (Seg 5: Right Neckline)
    pt(cx_b + neck_w, neck_y),    # 7: Left Neck Point        (Seg 6: Left Neckline)
    pt(cx_b + sh_w, sh_y),        # 8: Left Shoulder Tip      (Seg 7: Left Shoulder)
    pt(cx_b + w_underarm_b, arm_y),# 9: Left Underarm          (Seg 8: Left Armhole)
    pt(cx_b + w_waist_b, waist_y), # 10: Left Waist           (Seg 9: Upper Left Side)
    pt(cx_b + w_hem_b, hem_y),    # 11: Left Hem Corner       (Seg 10: Lower Left Side)
]
back_pts = [(round(2 * cx_b * scale - x, 3), y, z) for (x, y, z) in raw_back_pts]

back_id = pattern_api.CreatePatternWithPoints(back_pts)
if back_id is None: back_id = 1

# 3. Left Sleeve
cx_sl = -50.0
left_sleeve_pts = [
    pt(cx_sl - cuff_w, s_base_y),               # 0: Cuff Left
    pt(cx_sl + cuff_w, s_base_y),               # 1: Cuff Right      (Seg 0: Cuff Hem)
    pt(cx_sl + bicep_w, s_base_y + sleeve_len), # 2: Underarm Right  (Seg 1: Underarm Right)
    pt(cx_sl, s_base_y + sleeve_len + cap_h),   # 3: Cap Crown Apex  (Seg 2: Cap Right)
    pt(cx_sl - bicep_w, s_base_y + sleeve_len), # 4: Underarm Left   (Seg 3: Cap Left)
]
left_sleeve_id = pattern_api.CreatePatternWithPoints(left_sleeve_pts)
if left_sleeve_id is None: left_sleeve_id = 2

# 4. Right Sleeve
cx_sr = 110.0
right_sleeve_pts = [
    pt(cx_sr - cuff_w, s_base_y),               # 0: Cuff Left
    pt(cx_sr + cuff_w, s_base_y),               # 1: Cuff Right      (Seg 0: Cuff Hem)
    pt(cx_sr + bicep_w, s_base_y + sleeve_len), # 2: Underarm Right  (Seg 1: Underarm Right)
    pt(cx_sr, s_base_y + sleeve_len + cap_h),   # 3: Cap Crown Apex  (Seg 2: Cap Right)
    pt(cx_sr - bicep_w, s_base_y + sleeve_len), # 4: Underarm Left   (Seg 3: Cap Left)
]
right_sleeve_id = pattern_api.CreatePatternWithPoints(right_sleeve_pts)
if right_sleeve_id is None: right_sleeve_id = 3

# 5. Collar Band
hw_c = collar_circ / 2.0
collar_pts = [
    pt(-hw_c, c_elev_y),            # 0: Bottom-Left
    pt(hw_c, c_elev_y),             # 1: Bottom-Right   (Seg 0: Collar Base)
    pt(hw_c, c_elev_y + collar_h),  # 2: Top-Right      (Seg 1: Right Closure Edge)
    pt(-hw_c, c_elev_y + collar_h), # 3: Top-Left       (Seg 2: Top Rim)
]
collar_id = pattern_api.CreatePatternWithPoints(collar_pts)
if collar_id is None: collar_id = 4


# ==============================================================================
# 3. VERIFIED SEWING STITCHES
# ==============================================================================
print("\n--- Applying Stitches ---")
def sew(p1, s1, p2, s2, rev=False, label=""):
    ok = pattern_api.AddSeamlinePairGroup(int(p1), int(s1), int(p2), int(s2), bool(rev), False)
    status = "SUCCESS" if ok else "FAILED"
    print(f"[{status}] {label}: Pattern {p1}[seg {s1}] <--> Pattern {p2}[seg {s2}] (rev={rev})")
    return ok

# Shoulders (rev=False)
sew(front_id, 4, back_id, 4, rev=False, label="Right Shoulder")
sew(front_id, 7, back_id, 7, rev=False, label="Left Shoulder")

# Sides (rev=False)
sew(front_id, 1, back_id, 1, rev=False, label="Lower Right Side")
sew(front_id, 2, back_id, 2, rev=False, label="Upper Right Side")
sew(front_id, 9, back_id, 9, rev=False, label="Upper Left Side")
sew(front_id, 10, back_id, 10, rev=False, label="Lower Left Side")

# Armholes (rev=False)
sew(left_sleeve_id, 3, front_id, 8, rev=False, label="Left Armhole (Front)")
sew(left_sleeve_id, 2, back_id, 8,  rev=False, label="Left Armhole (Back)")
sew(right_sleeve_id, 2, front_id, 3, rev=False, label="Right Armhole (Front)")
sew(right_sleeve_id, 3, back_id, 3,  rev=False, label="Right Armhole (Back)")

# Self-Closing Cylinders (reverse=True closes opposing perimeter edges cleanly)
sew(left_sleeve_id, 1, left_sleeve_id, 4, rev=True, label="Left Sleeve Tube")
sew(right_sleeve_id, 1, right_sleeve_id, 4, rev=True, label="Right Sleeve Tube")
sew(collar_id, 1, collar_id, 3, rev=True, label="Collar Ring Closure")


# ==============================================================================
# 4. 3D ARRANGEMENT
# ==============================================================================
print("\n--- Applying 3D Native Arrangement ---")
ARRANGEMENT_TARGETS = [
    ("Front Bodice",  front_id,        ["Body_Front_Center_1", "Body_Front_Center_2"]),
    ("Back Bodice",   back_id,         ["Body_Back_Center_1", "Body_Back_Center_2"]),
    ("Left Sleeve",   left_sleeve_id,  ["Arm_Outside_1_L", "Arm_Front_1_L"]),
    ("Right Sleeve",  right_sleeve_id, ["Arm_Outside_1_R", "Arm_Front_1_R"]),
    ("Collar Band",   collar_id,       ["Neck_Front", "Neck_Collar"]),
]

try:
    arr_list = pattern_api.GetArrangementList()
    if arr_list:
        arr_dict = {item.get("ArrangementName", "").strip().lower(): int(item["ArrangementIndex"]) for item in arr_list}
        for label, pid, candidates in ARRANGEMENT_TARGETS:
            matched_id = None
            matched_name = None
            for c in candidates:
                if c.lower() in arr_dict:
                    matched_id = arr_dict[c.lower()]
                    matched_name = c
                    break
            if matched_id is not None:
                pattern_api.SetArrangement(pid, matched_id)
                print(f"[3D ARRANGED] {label:16} (ID {pid}) --> '{matched_name}' [ID: {matched_id}]")
        utility_api.ResetClothArrangement()
        print("\n[3D SUCCESS] Cloth arrangement reset!")
except Exception as err:
    print(f"[3D ERROR] Arrangement error: {err}")

print("\nFinished! Ready for test run in Marvelous Designer.")
