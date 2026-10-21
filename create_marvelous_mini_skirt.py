"""
GarmentCode Procedural Mini Skirt
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
                {"ArrangementIndex": "62", "ArrangementName": "Body_Front_Waist"},
                {"ArrangementIndex": "45", "ArrangementName": "Body_Back_Waist"},
                {"ArrangementIndex": "98", "ArrangementName": "Leg_Skirt_Front"},
                {"ArrangementIndex": "95", "ArrangementName": "Leg_Skirt_Back"},
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
# Panel: wb_back (translation: [-11.246318615009866, 120.9, -15.0], mirrored=True)
wb_back_pts = [
    (-110.0, 1209.0, 0),  # v[0]
    (-334.926, 1209.0, 0),  # v[1]
    (-352.59, 1170.454, 0),  # v[2]
    (-92.337, 1170.454, 0),  # v[3]
]
panel_ids['wb_back'] = pattern_api.CreatePatternWithPoints(wb_back_pts)
if panel_ids['wb_back'] is None: panel_ids['wb_back'] = 0

# Panel: wb_front (translation: [-10.69770689984528, 120.9, 20.0], mirrored=False)
wb_front_pts = [
    (-113.954, 1209.0, 0),  # v[0]
    (-133.115, 1171.176, 0),  # v[1]
    (119.16, 1171.176, 0),  # v[2]
    (100.0, 1209.0, 0),  # v[3]
]
panel_ids['wb_front'] = pattern_api.CreatePatternWithPoints(wb_front_pts)
if panel_ids['wb_front'] is None: panel_ids['wb_front'] = 1

# Panel: skirt_back (translation: [-19.08, 74.45630233035433, -20.0], mirrored=True)
skirt_back_pts = [
    (-190.8, 744.563, 0),  # v[0]
    (-230.8, 1106.113, 0),  # v[1]
    (-532.4, 1106.113, 0),  # v[2]
    (-572.4, 744.563, 0),  # v[3]
]
panel_ids['skirt_back'] = pattern_api.CreatePatternWithPoints(skirt_back_pts)
if panel_ids['skirt_back'] is None: panel_ids['skirt_back'] = 2

# Panel: skirt_front (translation: [-18.08, 74.45630233035433, 25.0], mirrored=False)
skirt_front_pts = [
    (-180.8, 744.563, 0),  # v[0]
    (187.8, 744.563, 0),  # v[1]
    (147.8, 1106.113, 0),  # v[2]
    (-140.8, 1106.113, 0),  # v[3]
]
panel_ids['skirt_front'] = pattern_api.CreatePatternWithPoints(skirt_front_pts)
if panel_ids['skirt_front'] is None: panel_ids['skirt_front'] = 3

# --- 2. EXECUTE SEWING STITCHES ---
print('\n--- Applying Procedural Sewing Stitches ---')
def sew(p1_name, e1, p2_name, e2, rev=True, label=''):
    pid1 = panel_ids[p1_name]
    pid2 = panel_ids[p2_name]
    ok = pattern_api.AddSeamlinePairGroup(int(pid1), int(e1), int(pid2), int(e2), bool(rev), False)
    status = 'SUCCESS' if ok else 'FAILED'
    print(f'[{status}] {label}: {p1_name}[seg {e1}] <--> {p2_name}[seg {e2}] (rev={rev})')
    return ok

sew('wb_front', 0, 'wb_back', 3, rev=True, label='Stitch #0 (Seamline)')
sew('wb_front', 2, 'wb_back', 1, rev=True, label='Stitch #1 (Seamline)')
sew('skirt_front', 3, 'skirt_back', 0, rev=True, label='Stitch #2 (Seamline)')
sew('skirt_front', 1, 'skirt_back', 2, rev=True, label='Stitch #3 (Seamline)')
sew('wb_front', 1, 'skirt_front', 2, rev=True, label='Stitch #4 (Seamline)')
sew('wb_back', 2, 'skirt_back', 1, rev=True, label='Stitch #5 (Seamline)')

# --- 3. 3D NATIVE ARRANGEMENT ---
print('\n--- Applying 3D Native Arrangement ---')
ARRANGEMENT_TARGETS = {
    "wb_front": ["Body_Front_Waist", "Body_Front_Center_1"],
    "wb_back": ["Body_Back_Waist", "Body_Back_Center_1"],
    "skirt_front": ["Leg_Skirt_Front", "Body_Front_Waist", "Body_Front_Center_1"],
    "skirt_back": ["Leg_Skirt_Back", "Body_Back_Waist", "Body_Back_Center_1"]
}

try:
    arr_list = pattern_api.GetArrangementList()
    if arr_list:
        print(f"Loaded {len(arr_list)} native arrangement points from avatar.")
        for panel_name, targets in ARRANGEMENT_TARGETS.items():
            if panel_name in panel_ids:
                pid = panel_ids[panel_name]
                matched_id = None
                matched_dot = None
                for target_dot in targets:
                    for item in arr_list:
                        if item.get("ArrangementName", "").strip().lower() == target_dot.strip().lower():
                            matched_id = int(item["ArrangementIndex"])
                            matched_dot = target_dot
                            break
                    if matched_id is not None:
                        break
                if matched_id is not None:
                    pattern_api.SetArrangement(pid, matched_id)
                    print(f"[3D ARRANGED] {panel_name:12} (ID {pid}) --> '{matched_dot}' [ID: {matched_id}]")
                else:
                    print(f"[3D WARN] No arrangement dot found for {panel_name} (tried: {targets}).")
        utility_api.ResetClothArrangement()
        print("\n[3D SUCCESS] Cloth arrangement reset! Patterns are wrapped in 3D around avatar.")
    else:
        print("[3D NOTE] No native arrangement points found; patterns elevated in 3D.")
except Exception as err:
    print(f"[3D ERROR] Arrangement failed: {err}")

print("\nFinished! Ready for 3D simulation (Spacebar).")
