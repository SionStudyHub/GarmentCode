"""
SUPER SEXY MICRO PLUNGE CROP for SionFemaleBodyV1 (female, 152.1cm)
Paste ENTIRE script into Marvelous Designer: Script > Run Script, then Spacebar.

Design: second-skin micro-crop, deep plunge cleavage, wide off-shoulder,
sexy open back, belly + navel fully exposed, ultra-short cap sleeves.
Fit: compression negative ease (-5% bust, -8% mid) so it clings vacuum-tight,
front/back asymmetric arcs keep side seams under armpit (no pull wrinkles).

Body ground truth: bust F40.406/B28.834 (69.24), waist F25.424/B22.995 (48.42),
underbust 58.67, neck narrow 19.27, shoulders 20.91.
Topology: 5 pieces, 11-pt bodice / 5-pt sleeve / 4-pt choker, 13 seams reverse=True.
"""

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
            print(f"[Mock] Pattern #{idx} ({len(points)} pts) X=[{min(xs):.1f},{max(xs):.1f}] Y=[{min(ys):.1f},{max(ys):.1f}] mm")
            return idx
        def AddSeamlinePairGroup(self, p1, s1, p2, s2, reverse, is_fold):
            print(f"[Mock Stitch] P{p1}[{s1}] <-> P{p2}[{s2}] rev={reverse}")
            return True
        def GetArrangementList(self):
            return [
                {'ArrangementIndex': '0', 'ArrangementName': 'Arm_Front_1_L'},
                {'ArrangementIndex': '1', 'ArrangementName': 'Arm_Front_1_R'},
                {'ArrangementIndex': '2', 'ArrangementName': 'Arm_Outside_1_L'},
                {'ArrangementIndex': '3', 'ArrangementName': 'Arm_Outside_1_R'},
                {'ArrangementIndex': '4', 'ArrangementName': 'Body_Front_Center_1'},
                {'ArrangementIndex': '5', 'ArrangementName': 'Body_Back_Center_1'},
                {'ArrangementIndex': '6', 'ArrangementName': 'Neck_Front'},
            ]
        def SetArrangement(self, pid, ptid):
            print(f"[Mock Arrange] Pattern {pid} -> Point {ptid}")
    class MockUtilityApi:
        @staticmethod
        def ResetClothArrangement():
            print("[Mock] ResetClothArrangement -> wrapped in 3D")
        @staticmethod
        def Simulate(s):
            pass
    pattern_api = MockPatternApi()
    utility_api = MockUtilityApi()

scale = 10.0
def pt(x, y):
    return (round(x * scale, 3), round(y * scale, 3), 0)

# ---------- Heights (cm) ----------
neck_y  = 127.95
sh_y    = 121.29
arm_y   = 109.66
mid_y   = 106.80   # sexy mid-torso shaping (above natural waist, below underbust)
hem_y   = 103.50   # MICRO hem (belly + navel fully out, 3.25 above waist)
front_scoop_y = 113.50  # DEEP PLUNGE (14.45 drop, cleavage to bust apex 111.04)
back_scoop_y  = 116.00  # SEXY OPEN BACK (11.95 drop, upper-back bare)

# ---------- Widths (cm half-widths, compression cling) ----------
# Bust -5%: F 40.406*0.95/2, B 28.834*0.95/2 = 65.78 total (vacuum-tight)
w_bust_front = 40.406 * 0.95 / 2.0  # 19.19
w_bust_back  = 28.834 * 0.95 / 2.0  # 13.70
# Mid -8%: tight underbust cinch = 49.9 total
w_mid_front = 12.90
w_mid_back  = 11.60
# Micro hem: tight band under bust = 49.8 total
w_hem_front = 13.00
w_hem_back  = 11.90

neck_w = 5.50   # WIDE 11cm opening (off-shoulder collarbones, sexy straps)
sh_w   = 10.454 # anatomical shoulder tip (strap = 4.95cm, thin + sexy)
collar_circ = 24.0  # loose sexy drape / choker ring
collar_h = 1.5      # delicate thin band

# Ultra-short cap sleeves: tight + bare arms
bicep_w = 9.00   # 18.0 tight
cuff_w  = 7.25   # 14.5 tight
sleeve_len = 6.0
cap_h = 8.5
s_base_y = 105.00  # crown tops at 119.5, meets shoulder 121.29

print("=== SUPER SEXY MICRO PLUNGE ===")
print(f"Bust : {(w_bust_front+w_bust_back)*2:.2f}cm (body 69.24, -5% cling)")
print(f"Mid  : {(w_mid_front+w_mid_back)*2:.2f}cm | Hem: {(w_hem_front+w_hem_back)*2:.2f}cm micro@103.5")
print(f"Plunge: {neck_y-front_scoop_y:.1f}cm deep V | Neck: {neck_w*2:.1f}cm wide | Back: {neck_y-back_scoop_y:.1f}cm open")

cx_front = 0.0
front_pts = [
    pt(cx_front - w_hem_front, hem_y),
    pt(cx_front + w_hem_front, hem_y),
    pt(cx_front + w_mid_front, mid_y),
    pt(cx_front + w_bust_front, arm_y),
    pt(cx_front + sh_w, sh_y),
    pt(cx_front + neck_w, neck_y),
    pt(cx_front, front_scoop_y),
    pt(cx_front - neck_w, neck_y),
    pt(cx_front - sh_w, sh_y),
    pt(cx_front - w_bust_front, arm_y),
    pt(cx_front - w_mid_front, mid_y),
]
front_id = pattern_api.CreatePatternWithPoints(front_pts)
if front_id is None: front_id = 0

cx_back = 50.0
back_pts = [
    pt(cx_back - w_hem_back, hem_y),
    pt(cx_back + w_hem_back, hem_y),
    pt(cx_back + w_mid_back, mid_y),
    pt(cx_back + w_bust_back, arm_y),
    pt(cx_back + sh_w, sh_y),
    pt(cx_back + neck_w, neck_y),
    pt(cx_back, back_scoop_y),
    pt(cx_back - neck_w, neck_y),
    pt(cx_back - sh_w, sh_y),
    pt(cx_back - w_bust_back, arm_y),
    pt(cx_back - w_mid_back, mid_y),
]
back_id = pattern_api.CreatePatternWithPoints(back_pts)
if back_id is None: back_id = 1

cx_ls = 95.0
left_sleeve_pts = [
    pt(cx_ls - cuff_w, s_base_y),
    pt(cx_ls + cuff_w, s_base_y),
    pt(cx_ls + bicep_w, s_base_y + sleeve_len),
    pt(cx_ls, s_base_y + sleeve_len + cap_h),
    pt(cx_ls - bicep_w, s_base_y + sleeve_len),
]
left_sleeve_id = pattern_api.CreatePatternWithPoints(left_sleeve_pts)
if left_sleeve_id is None: left_sleeve_id = 2

cx_rs = -45.0
right_sleeve_pts = [
    pt(cx_rs - cuff_w, s_base_y),
    pt(cx_rs + cuff_w, s_base_y),
    pt(cx_rs + bicep_w, s_base_y + sleeve_len),
    pt(cx_rs, s_base_y + sleeve_len + cap_h),
    pt(cx_rs - bicep_w, s_base_y + sleeve_len),
]
right_sleeve_id = pattern_api.CreatePatternWithPoints(right_sleeve_pts)
if right_sleeve_id is None: right_sleeve_id = 3

collar_y = 135.0
neckband_pts = [
    pt(-collar_circ / 2.0, collar_y),
    pt(collar_circ / 2.0, collar_y),
    pt(collar_circ / 2.0, collar_y + collar_h),
    pt(-collar_circ / 2.0, collar_y + collar_h),
]
neckband_id = pattern_api.CreatePatternWithPoints(neckband_pts)
if neckband_id is None: neckband_id = 4

print("\n--- Stitching 13 seams ---")
def sew(p1, s1, p2, s2, rev=True, label=""):
    try:
        ok = pattern_api.AddSeamlinePairGroup(int(p1), int(s1), int(p2), int(s2), bool(rev), False)
        print(f"[{'OK' if ok else 'FAIL'}] {label}: P{p1}[{s1}] <-> P{p2}[{s2}] rev={rev}")
        return ok
    except Exception as e:
        print(f"[ERROR] {label}: {e}")
        return False

sew(front_id, 4, back_id, 7, True, "Left Shoulder strap")
sew(front_id, 7, back_id, 4, True, "Right Shoulder strap")
sew(front_id, 1, back_id, 10, True, "Left Lower Side")
sew(front_id, 2, back_id, 9, True, "Left Upper Side")
sew(front_id, 9, back_id, 2, True, "Right Upper Side")
sew(front_id, 10, back_id, 1, True, "Right Lower Side")
sew(left_sleeve_id, 1, left_sleeve_id, 4, True, "Left Sleeve Tube")
sew(right_sleeve_id, 1, right_sleeve_id, 4, True, "Right Sleeve Tube")
sew(left_sleeve_id, 3, front_id, 3, True, "Left Sleeve Front -> Front Armhole")
sew(left_sleeve_id, 2, back_id, 8, True, "Left Sleeve Back -> Back Armhole")
sew(right_sleeve_id, 2, front_id, 8, True, "Right Sleeve Front -> Front Armhole")
sew(right_sleeve_id, 3, back_id, 3, True, "Right Sleeve Back -> Back Armhole")
sew(neckband_id, 1, neckband_id, 3, True, "Choker Ring")

print("\n--- 3D Arrangement ---")
try:
    arr_list = pattern_api.GetArrangementList()
    def find(name):
        for it in arr_list:
            if it.get("ArrangementName","").strip().lower() == name.strip().lower():
                return int(it["ArrangementIndex"]), it.get("ArrangementName")
        return None, None
    jobs = [
        ("Front Bodice", front_id, "Body_Front_Center_1"),
        ("Back Bodice", back_id, "Body_Back_Center_1"),
        ("Left Sleeve", left_sleeve_id, "Arm_Outside_1_L"),
        ("Right Sleeve", right_sleeve_id, "Arm_Outside_1_R"),
        ("Neckband", neckband_id, "Neck_Front"),
    ]
    for part, pid, dot in jobs:
        idx, actual = find(dot)
        if idx is not None:
            pattern_api.SetArrangement(pid, idx)
            print(f"[3D] {part} (ID {pid}) -> '{actual}' [{idx}]")
        else:
            print(f"[3D WARN] dot '{dot}' not found")
    utility_api.ResetClothArrangement()
    print("[3D SUCCESS] Wrapped. Press Spacebar to simulate!")
except Exception as err:
    print(f"[3D WARN] {err}")

print("\nDone! Super-sexy micro plunge ready. TIP: use stretch jersey + Spacebar.")
