"""
Marvelous Designer Procedural Garment
Auto-generated from GarmentCode procedural CAD engine.
"""
import math
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
                {"ArrangementIndex": "20", "ArrangementName": "Arm_Front_1_L"},
                {"ArrangementIndex": "21", "ArrangementName": "Arm_Front_1_R"},
                {"ArrangementIndex": "22", "ArrangementName": "Arm_Back_1_L"},
                {"ArrangementIndex": "23", "ArrangementName": "Arm_Back_1_R"},
                {"ArrangementIndex": "59", "ArrangementName": "Body_Front_Center_1"},
                {"ArrangementIndex": "42", "ArrangementName": "Body_Back_Center_1"},
                {"ArrangementIndex": "78", "ArrangementName": "Neck_Front"},
                {"ArrangementIndex": "0", "ArrangementName": "Leg_Front_L"},
                {"ArrangementIndex": "1", "ArrangementName": "Leg_Front_R"},
                {"ArrangementIndex": "2", "ArrangementName": "Leg_Back_L"},
                {"ArrangementIndex": "3", "ArrangementName": "Leg_Back_R"},
            ]
        def SetArrangement(self, pid, pt_id):
            print(f"[Mock Arrangement] Pattern {pid} --> Point {pt_id}")
    class MockUtilityApi:
        @staticmethod
        def ResetClothArrangement(): print("[Mock] utility_api.ResetClothArrangement() called - 3D wrapped!")
    pattern_api = MockPatternApi()
    utility_api = MockUtilityApi()

print("=== Creating Procedural Garment in Marvelous Designer ===")
scale = 10.0
panel_ids = {}

# --- 1. CREATE 2D PATTERNS ---
# Panel: right_sleeve_b (translation: [-28.666648211309234, 145.0485081514266, -12.5], mirrored=True)
right_sleeve_b_pts = [
    (-600.0, 1450.485, 0),  # v[0]
    (-793.498, 1450.485, 0),  # v[1]
    (-793.461, 1444.279, 0),  # v[2]
    (-706.93, 1237.228, 0),  # v[3]
    (-600.0, 1237.228, 0),  # v[4]
]
panel_ids['right_sleeve_b'] = pattern_api.CreatePatternWithPoints(right_sleeve_b_pts)
if panel_ids['right_sleeve_b'] is None: panel_ids['right_sleeve_b'] = 0

# Panel: right_sleeve_f (translation: [-28.666648211309234, 145.0485081514266, 17.5], mirrored=False)
right_sleeve_f_pts = [
    (-600.0, 1450.485, 0),  # v[0]
    (-600.0, 1237.228, 0),  # v[1]
    (-493.07, 1237.228, 0),  # v[2]
    (-406.502, 1450.485, 0),  # v[3]
]
panel_ids['right_sleeve_f'] = pattern_api.CreatePatternWithPoints(right_sleeve_f_pts)
if panel_ids['right_sleeve_f'] is None: panel_ids['right_sleeve_f'] = 1

# Panel: right_btorso (translation: [0.0, 107.68418779348531, -25.0], mirrored=True)
right_btorso_pts = [
    (600.0, 1076.842, 0),  # v[0]
    (789.525, 1076.842, 0),  # v[1]
    (789.525, 1275.285, 0),  # v[2]
    (685.0, 1450.485, 0),  # v[3]
    (667.4, 1457.632, 0),  # v[4]
    (600.0, 1408.042, 0),  # v[5]
]
panel_ids['right_btorso'] = pattern_api.CreatePatternWithPoints(right_btorso_pts)
if panel_ids['right_btorso'] is None: panel_ids['right_btorso'] = 2

# Panel: right_ftorso (translation: [0.0, 107.6486577278966, 30.0], mirrored=False)
right_ftorso_pts = [
    (0.0, 1076.487, 0),  # v[0]
    (0.0, 1344.181, 0),  # v[1]
    (-67.4, 1457.632, 0),  # v[2]
    (-85.0, 1450.485, 0),  # v[3]
    (-86.422, 1444.421, 0),  # v[4]
    (-207.9, 1275.285, 0),  # v[5]
    (-207.9, 1076.487, 0),  # v[6]
]
panel_ids['right_ftorso'] = pattern_api.CreatePatternWithPoints(right_ftorso_pts)
if panel_ids['right_ftorso'] is None: panel_ids['right_ftorso'] = 3

# Panel: left_ftorso (translation: [0.0, 107.6486577278966, 30.0], mirrored=False)
left_ftorso_pts = [
    (0.0, 1076.487, 0),  # v[0]
    (207.9, 1076.487, 0),  # v[1]
    (207.9, 1275.285, 0),  # v[2]
    (86.422, 1444.421, 0),  # v[3]
    (85.0, 1450.485, 0),  # v[4]
    (67.4, 1457.632, 0),  # v[5]
    (0.0, 1344.181, 0),  # v[6]
]
panel_ids['left_ftorso'] = pattern_api.CreatePatternWithPoints(left_ftorso_pts)
if panel_ids['left_ftorso'] is None: panel_ids['left_ftorso'] = 4

# Panel: left_sleeve_f (translation: [28.666648211309234, 145.0485081514266, 17.5], mirrored=False)
left_sleeve_f_pts = [
    (1100.0, 1450.485, 0),  # v[0]
    (906.502, 1450.485, 0),  # v[1]
    (993.07, 1237.228, 0),  # v[2]
    (1100.0, 1237.228, 0),  # v[3]
]
panel_ids['left_sleeve_f'] = pattern_api.CreatePatternWithPoints(left_sleeve_f_pts)
if panel_ids['left_sleeve_f'] is None: panel_ids['left_sleeve_f'] = 5

# Panel: left_sleeve_b (translation: [28.666648211309234, 145.0485081514266, -12.5], mirrored=True)
left_sleeve_b_pts = [
    (1100.0, 1450.485, 0),  # v[0]
    (1100.0, 1237.228, 0),  # v[1]
    (1206.93, 1237.228, 0),  # v[2]
    (1293.461, 1444.279, 0),  # v[3]
    (1293.498, 1450.485, 0),  # v[4]
]
panel_ids['left_sleeve_b'] = pattern_api.CreatePatternWithPoints(left_sleeve_b_pts)
if panel_ids['left_sleeve_b'] is None: panel_ids['left_sleeve_b'] = 6

# Panel: left_btorso (translation: [0.0, 107.68418779348531, -25.0], mirrored=True)
left_btorso_pts = [
    (600.0, 1076.842, 0),  # v[0]
    (600.0, 1408.042, 0),  # v[1]
    (532.6, 1457.632, 0),  # v[2]
    (515.0, 1450.485, 0),  # v[3]
    (410.475, 1275.285, 0),  # v[4]
    (410.475, 1076.842, 0),  # v[5]
]
panel_ids['left_btorso'] = pattern_api.CreatePatternWithPoints(left_btorso_pts)
if panel_ids['left_btorso'] is None: panel_ids['left_btorso'] = 7

# --- 2. EXECUTE SEWING STITCHES ---
print('\n--- Applying Procedural Sewing Stitches ---')
def sew(p1_name, e1, p2_name, e2, rev=True, label=''):
    pid1 = panel_ids[p1_name]
    pid2 = panel_ids[p2_name]
    ok = pattern_api.AddSeamlinePairGroup(int(pid1), int(e1), int(pid2), int(e2), bool(rev), False)
    status = 'SUCCESS' if ok else 'FAILED'
    print(f'[{status}] {label}: {p1_name}[seg {e1}] <--> {p2_name}[seg {e2}] (rev={rev})')
    return ok

sew('right_sleeve_f', 3, 'right_sleeve_b', 0, rev=True, label='Stitch #0 (Seamline)')
sew('right_sleeve_f', 1, 'right_sleeve_b', 3, rev=True, label='Stitch #1 (Seamline)')
sew('right_sleeve_f', 2, 'right_ftorso', 4, rev=True, label='Stitch #2 (Seamline)')
sew('right_sleeve_b', 1, 'right_ftorso', 3, rev=False, label='Stitch #3 (Seamline)')
sew('right_sleeve_b', 2, 'right_btorso', 2, rev=True, label='Stitch #4 (Seamline)')
sew('right_ftorso', 2, 'right_btorso', 3, rev=True, label='Stitch #5 (Seamline)')
sew('right_ftorso', 5, 'right_btorso', 1, rev=True, label='Stitch #6 (Seamline)')
sew('left_sleeve_f', 0, 'left_sleeve_b', 4, rev=True, label='Stitch #7 (Seamline)')
sew('left_sleeve_f', 2, 'left_sleeve_b', 1, rev=True, label='Stitch #8 (Seamline)')
sew('left_sleeve_f', 1, 'left_ftorso', 2, rev=True, label='Stitch #9 (Seamline)')
sew('left_sleeve_b', 3, 'left_ftorso', 3, rev=False, label='Stitch #10 (Seamline)')
sew('left_sleeve_b', 2, 'left_btorso', 3, rev=True, label='Stitch #11 (Seamline)')
sew('left_ftorso', 4, 'left_btorso', 2, rev=True, label='Stitch #12 (Seamline)')
sew('left_ftorso', 1, 'left_btorso', 4, rev=True, label='Stitch #13 (Seamline)')
sew('right_ftorso', 0, 'left_ftorso', 6, rev=True, label='Stitch #14 (Seamline)')
sew('right_btorso', 5, 'left_btorso', 0, rev=True, label='Stitch #15 (Seamline)')

# --- 3. 3D NATIVE ARRANGEMENT ---
print('\n--- Applying 3D Native Arrangement ---')
ARRANGEMENT_TARGETS = {
    "left_ftorso": "Body_Front_Center_1",
    "right_ftorso": "Body_Front_Center_1",
    "left_btorso": "Body_Back_Center_1",
    "right_btorso": "Body_Back_Center_1",
    "left_sleeve_f": "Arm_Front_1_L",
    "left_sleeve_b": "Arm_Back_1_L",
    "right_sleeve_f": "Arm_Front_1_R",
    "right_sleeve_b": "Arm_Back_1_R"
}

try:
    arr_list = pattern_api.GetArrangementList()
    if arr_list:
        print(f"Loaded {len(arr_list)} native arrangement points from avatar.")
        for panel_name, target_dot in ARRANGEMENT_TARGETS.items():
            if panel_name in panel_ids:
                pid = panel_ids[panel_name]
                matched_id = None
                for item in arr_list:
                    if item.get("ArrangementName", "").strip().lower() == target_dot.strip().lower():
                        matched_id = int(item["ArrangementIndex"])
                        break
                if matched_id is not None:
                    pattern_api.SetArrangement(pid, matched_id)
                    print(f"[3D ARRANGED] {panel_name:12} (ID {pid}) --> '{target_dot}' [ID: {matched_id}]")
                else:
                    print(f"[3D WARN] Arrangement dot '{target_dot}' not found on avatar.")
        utility_api.ResetClothArrangement()
        print("\n[3D SUCCESS] Cloth arrangement reset! Patterns are wrapped in 3D around avatar.")
    else:
        print("[3D NOTE] No native arrangement points found; patterns elevated in 3D.")
except Exception as err:
    print(f"[3D ERROR] Arrangement failed: {err}")

print("\nFinished! Ready for 3D simulation (Spacebar).")
