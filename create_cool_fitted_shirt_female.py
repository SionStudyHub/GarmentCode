"""
COOL FITTED BABY-TEE for SionFemaleBodyV1 (female, 152.1cm)
Paste this ENTIRE script into Marvelous Designer: Script > Run Script (or Python tab)

Fit philosophy (from DIGITAL_TAILORING_AND_FITTING_GUIDE.md):
- Slim / form-fitting ease +4% at bust & waist (outlines curves, no sag, no compression squeeze)
- Front/back ASYMMETRIC arcs (bust 58.4% front / 41.6% back, waist 52.5% / 47.5%)
  -> keeps side seams under the armpit, no diagonal pulling
- Narrow neck (19.27cm, NOT neck-base 28.78cm) -> no gaping collar
- Anatomical shoulders (joint span 20.91cm) -> no dropped-shoulder sag
- Tapered cap sleeves (bicep ~21.1cm, cuff ~17.3cm) -> no flapping fabric
- Cropped hem at Y=97cm (just below waist, above navel) -> avoids belly-trap slack,
  shows midriff, cool modern baby-tee silhouette
- Cool details: deep 6.5cm front scoop, shallow back scoop, thick 2.2cm rib neckband,
  9cm cap sleeves, slight A-line flare to cropped hem

Topology: 5 pieces, 11-pt bodice / 5-pt sleeve / 4-pt neckband, 13 seams, all reverse=True
Heights are real avatar Y (cm x10 = mm), so garment spawns ON torso, not at feet.
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

scale = 10.0  # cm -> mm
def pt(x, y):
    return (round(x * scale, 3), round(y * scale, 3), 0)

# ---------- Heights (cm, avatar ground truth) ----------
neck_y  = 127.95   # narrow neck line
sh_y    = 121.29   # shoulder joint
arm_y   = 109.66   # underarm
waist_y = 100.25   # natural waist
hem_y   = 97.00    # CROPPED hem (3.25cm below waist, grazes navel = cool baby-tee)
front_scoop_y = neck_y - 6.5   # 121.45 deep cool scoop (collarbones)
back_scoop_y  = neck_y - 1.8   # 126.15 shallow back

# ---------- Widths (cm, half-widths from center) ----------
# Body arcs: bust F 40.406 / B 28.834, waist F 25.424 / B 22.995
# Ease: +4% bust & waist (slim perfect fit), hem = waist + flare (~+8%)
w_bust_front = 40.406 * 1.04 / 2.0   # = 21.01
w_bust_back  = 28.834 * 1.04 / 2.0   # = 14.99
w_waist_front = 25.424 * 1.04 / 2.0  # = 13.22
w_waist_back  = 22.995 * 1.04 / 2.0  # = 11.96
w_hem_front = 14.10   # total hem circ ~52.6cm, slight A-line flare (cool)
w_hem_back  = 12.20

neck_w = 2.785    # 5.57 / 2 (narrow neck, no gaping)
sh_w   = 10.454   # 20.908 / 2 (anatomical acromion, no drop)
collar_circ = 20.0  # neckband length (19.27 body + ease to slide + rib look)
collar_h = 2.2      # thick cool rib

# Sleeves: tapered cap (bicep 21.1, cuff 17.3), 9cm long, 9cm cap
bicep_w = 10.57
cuff_w  = 8.66
sleeve_len = 9.0
cap_h = 9.0
s_base_y = 103.00

print("=== COOL FITTED BABY-TEE ===")
print(f"Bust pattern : {(w_bust_front+w_bust_back)*2:.2f}cm (body 69.24)")
print(f"Waist pattern: {(w_waist_front+w_waist_back)*2:.2f}cm (body 48.42)")
print(f"Hem pattern  : {(w_hem_front+w_hem_back)*2:.2f}cm cropped@97cm")
print(f"Collar: {collar_circ}cm x {collar_h}cm rib")

# ---------- PIECE 1: FRONT BODICE (X=0, on torso) ----------
cx_front = 0.0
front_pts = [
    pt(cx_front - w_hem_front, hem_y),
    pt(cx_front + w_hem_front, hem_y),
    pt(cx_front + w_waist_front, waist_y),
    pt(cx_front + w_bust_front, arm_y),
    pt(cx_front + sh_w, sh_y),
    pt(cx_front + neck_w, neck_y),
    pt(cx_front, front_scoop_y),
    pt(cx_front - neck_w, neck_y),
    pt(cx_front - sh_w, sh_y),
    pt(cx_front - w_bust_front, arm_y),
    pt(cx_front - w_waist_front, waist_y),
]
front_id = pattern_api.CreatePatternWithPoints(front_pts)
if front_id is None: front_id = 0

# ---------- PIECE 2: BACK BODICE (X=+50cm, beside torso) ----------
cx_back = 50.0
back_pts = [
    pt(cx_back - w_hem_back, hem_y),
    pt(cx_back + w_hem_back, hem_y),
    pt(cx_back + w_waist_back, waist_y),
    pt(cx_back + w_bust_back, arm_y),
    pt(cx_back + sh_w, sh_y),
    pt(cx_back + neck_w, neck_y),
    pt(cx_back, back_scoop_y),
    pt(cx_back - neck_w, neck_y),
    pt(cx_back - sh_w, sh_y),
    pt(cx_back - w_bust_back, arm_y),
    pt(cx_back - w_waist_back, waist_y),
]
back_id = pattern_api.CreatePatternWithPoints(back_pts)
if back_id is None: back_id = 1

# ---------- PIECE 3: LEFT SLEEVE (+X side) ----------
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

# ---------- PIECE 4: RIGHT SLEEVE (-X side) ----------
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

# ---------- PIECE 5: RIB NECKBAND ----------
collar_y = 135.0
neckband_pts = [
    pt(-collar_circ / 2.0, collar_y),
    pt(collar_circ / 2.0, collar_y),
    pt(collar_circ / 2.0, collar_y + collar_h),
    pt(-collar_circ / 2.0, collar_y + collar_h),
]
neckband_id = pattern_api.CreatePatternWithPoints(neckband_pts)
if neckband_id is None: neckband_id = 4

# ---------- 13 SEAMS (all reverse=True per vector law) ----------
print("\n--- Stitching 13 seams ---")
def sew(p1, s1, p2, s2, rev=True, label=""):
    try:
        ok = pattern_api.AddSeamlinePairGroup(int(p1), int(s1), int(p2), int(s2), bool(rev), False)
        print(f"[{'OK' if ok else 'FAIL'}] {label}: P{p1}[{s1}] <-> P{p2}[{s2}] rev={rev}")
        return ok
    except Exception as e:
        print(f"[ERROR] {label}: {e}")
        return False

sew(front_id, 4, back_id, 7, True, "Left Shoulder")
sew(front_id, 7, back_id, 4, True, "Right Shoulder")
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
sew(neckband_id, 1, neckband_id, 3, True, "Neckband Ring")

# ---------- 3D ARRANGEMENT ----------
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
    print("[3D SUCCESS] Wrapped around avatar. Press Spacebar to simulate!")
except Exception as err:
    print(f"[3D WARN] {err}")

print("\nDone! Cool fitted baby-tee ready for simulation.")
