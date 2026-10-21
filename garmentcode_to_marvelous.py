"""
GarmentCode to Marvelous Designer Bridge Engine
Converts procedural GarmentCode patterns (MetaGarment, Pants, Bodice, Skirt, etc.)
into fully standalone, executable Marvelous Designer Python scripts.

Features:
1. Translates GarmentCode 2D panels and discrete vertices to MD millimeter coordinates.
2. Automatically elevates patterns to avatar anatomical height based on 3D translation.
3. Maps GarmentCode procedural stitches directly to MD AddSeamlinePairGroup seamline pairs.
4. Auto-detects reverse flags (darts, loop inversion) using edge 3D vectors.
5. Emits explicit 3D native arrangement point assignments (Leg_Front_L, Leg_Back_L, Body_Front_Waist, etc.).
"""

import os
import json
import yaml
import numpy as np

from assets.garment_programs.meta_garment import MetaGarment
from assets.bodies.body_params import BodyParameters

def generate_marvelous_script(
    pattern,
    script_output_path,
    title="Marvelous Designer Procedural Garment",
    arrangement_mapping=None,
    scale=10.0,
    y_elevation_offset=0.0
):
    """
    Translates a GarmentCode Pattern object into a standalone Marvelous Designer script.
    """
    panels = pattern.pattern['panels']
    stitches = pattern.pattern['stitches']

    if arrangement_mapping is None:
        arrangement_mapping = {}

    script_lines = [
        f'"""\n{title}\nAuto-generated from GarmentCode procedural CAD engine.\n"""',
        'import math',
        'try:',
        '    import pattern_api',
        '    import utility_api',
        'except ImportError:',
        '    class MockPatternApi:',
        '        def __init__(self): self._counter = 0',
        '        def CreatePatternWithPoints(self, pts):',
        '            idx = self._counter; self._counter += 1',
        '            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]',
        '            print(f"[Mock Pattern] #{idx} created ({len(pts)} vertices) Bounds: X=[{min(xs):.1f}, {max(xs):.1f}], Y=[{min(ys):.1f}, {max(ys):.1f}] mm")',
        '            return idx',
        '        def AddSeamlinePairGroup(self, p1, s1, p2, s2, rev, fold):',
        '            print(f"[Mock Stitch] Pattern {p1}[seg {s1}] <--> Pattern {p2}[seg {s2}] (reverse={rev})")',
        '            return True',
        '        def GetArrangementList(self):',
        '            return [',
        '                {"ArrangementIndex": "18", "ArrangementName": "Arm_Outside_1_L"},',
        '                {"ArrangementIndex": "19", "ArrangementName": "Arm_Outside_1_R"},',
        '                {"ArrangementIndex": "20", "ArrangementName": "Arm_Front_1_L"},',
        '                {"ArrangementIndex": "21", "ArrangementName": "Arm_Front_1_R"},',
        '                {"ArrangementIndex": "22", "ArrangementName": "Arm_Back_1_L"},',
        '                {"ArrangementIndex": "23", "ArrangementName": "Arm_Back_1_R"},',
        '                {"ArrangementIndex": "59", "ArrangementName": "Body_Front_Center_1"},',
        '                {"ArrangementIndex": "42", "ArrangementName": "Body_Back_Center_1"},',
        '                {"ArrangementIndex": "78", "ArrangementName": "Neck_Front"},',
        '                {"ArrangementIndex": "0", "ArrangementName": "Leg_Front_L"},',
        '                {"ArrangementIndex": "1", "ArrangementName": "Leg_Front_R"},',
        '                {"ArrangementIndex": "2", "ArrangementName": "Leg_Back_L"},',
        '                {"ArrangementIndex": "3", "ArrangementName": "Leg_Back_R"},',
        '            ]',
        '        def SetArrangement(self, pid, pt_id):',
        '            print(f"[Mock Arrangement] Pattern {pid} --> Point {pt_id}")',
        '    class MockUtilityApi:',
        '        @staticmethod',
        '        def ResetClothArrangement(): print("[Mock] utility_api.ResetClothArrangement() called - 3D wrapped!")',
        '    pattern_api = MockPatternApi()',
        '    utility_api = MockUtilityApi()',
        '',
        'print("=== Creating Procedural Garment in Marvelous Designer ===")',
        'scale = 10.0',
        'panel_ids = {}',
        ''
    ]

    # 1. Panels Generation
    script_lines.append("# --- 1. CREATE 2D PATTERNS ---")
    
    # 2D window spacing offsets to prevent overlapping in MD 2D view
    layout_2d_offsets = {
        'left_ftorso': 0.0,
        'right_ftorso': 0.0,
        'left_btorso': 600.0,
        'right_btorso': 600.0,
        'left_sleeve_f': 1100.0,
        'left_sleeve_b': 1100.0,
        'right_sleeve_f': -600.0,
        'right_sleeve_b': -600.0,
        'pant_f_l': 0.0,
        'pant_f_r': 0.0,
        'pant_b_l': 300.0,
        'pant_b_r': -300.0,
    }

    panel_names = list(panels.keys())
    for p_idx, (name, panel_data) in enumerate(panels.items()):
        verts = panel_data['vertices']
        trans = panel_data.get('translation', [0, 0, 0])
        
        # In Marvelous Designer, back arrangement points (Body_Back_Center_1, Arm_Back_1_L/R)
        # rotate patterns by 180 degrees. To prevent left/right swapping in 3D, all Back panels
        # MUST be horizontally mirrored in 2D space (X' = -X):
        is_back_panel = any(k in name for k in ['btorso', 'sleeve_b', 'back'])
        
        cx_offset_mm = layout_2d_offsets.get(name, (trans[0] * scale))
        base_y_mm = (trans[1] + y_elevation_offset) * scale
        
        script_lines.append(f"# Panel: {name} (translation: {trans}, mirrored={is_back_panel})")
        pts_var = f"{name}_pts"
        script_lines.append(f"{pts_var} = [")
        for v_idx, v in enumerate(verts):
            vx = -v[0] if is_back_panel else v[0]
            x_mm = round(cx_offset_mm + (vx * scale), 3)
            y_mm = round(base_y_mm + (v[1] * scale), 3)
            script_lines.append(f"    ({x_mm}, {y_mm}, 0),  # v[{v_idx}]")
        script_lines.append("]")
        script_lines.append(f"panel_ids['{name}'] = pattern_api.CreatePatternWithPoints({pts_var})")
        script_lines.append(f"if panel_ids['{name}'] is None: panel_ids['{name}'] = {p_idx}")
        script_lines.append("")

    # 2. Sewing Stitches Generation
    script_lines.append("# --- 2. EXECUTE SEWING STITCHES ---")
    script_lines.append("print('\\n--- Applying Procedural Sewing Stitches ---')")
    script_lines.append("def sew(p1_name, e1, p2_name, e2, rev=True, label=''):")
    script_lines.append("    pid1 = panel_ids[p1_name]")
    script_lines.append("    pid2 = panel_ids[p2_name]")
    script_lines.append("    ok = pattern_api.AddSeamlinePairGroup(int(pid1), int(e1), int(pid2), int(e2), bool(rev), False)")
    script_lines.append("    status = 'SUCCESS' if ok else 'FAILED'")
    script_lines.append("    print(f'[{status}] {label}: {p1_name}[seg {e1}] <--> {p2_name}[seg {e2}] (rev={rev})')")
    script_lines.append("    return ok")
    script_lines.append("")

    # Process all stitches
    for s_idx, s in enumerate(stitches):
        p1, e1 = s[0]['panel'], s[0]['edge']
        p2, e2 = s[1]['panel'], s[1]['edge']
        
        # Determine whether reverse=True is needed:
        # Check 3D distance of start-to-start vs start-to-end:
        pan1 = panels[p1]
        pan2 = panels[p2]
        t1 = np.array(pan1.get('translation', [0, 0, 0]))
        t2 = np.array(pan2.get('translation', [0, 0, 0]))
        
        v1_s_idx, v1_e_idx = pan1['edges'][e1]['endpoints']
        v2_s_idx, v2_e_idx = pan2['edges'][e2]['endpoints']
        
        v1_s_3d = np.array([pan1['vertices'][v1_s_idx][0], pan1['vertices'][v1_s_idx][1], 0.0]) + t1
        v1_e_3d = np.array([pan1['vertices'][v1_e_idx][0], pan1['vertices'][v1_e_idx][1], 0.0]) + t1
        v2_s_3d = np.array([pan2['vertices'][v2_s_idx][0], pan2['vertices'][v2_s_idx][1], 0.0]) + t2
        v2_e_3d = np.array([pan2['vertices'][v2_e_idx][0], pan2['vertices'][v2_e_idx][1], 0.0]) + t2
        
        d_par = np.linalg.norm(v1_s_3d - v2_s_3d) + np.linalg.norm(v1_e_3d - v2_e_3d)
        d_rev = np.linalg.norm(v1_s_3d - v2_e_3d) + np.linalg.norm(v1_e_3d - v2_s_3d)
        
        is_rev = (d_rev <= d_par)
        
        # Label seam
        label = "Dart Closure" if p1 == p2 else "Seamline"
        script_lines.append(f"sew('{p1}', {e1}, '{p2}', {e2}, rev={is_rev}, label='Stitch #{s_idx} ({label})')")

    # 3. Native 3D Arrangement
    script_lines.append("")
    script_lines.append("# --- 3. 3D NATIVE ARRANGEMENT ---")
    script_lines.append("print('\\n--- Applying 3D Native Arrangement ---')")
    script_lines.append(f"ARRANGEMENT_TARGETS = {json.dumps(arrangement_mapping, indent=4)}")
    script_lines.append("""
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
        print("\\n[3D SUCCESS] Cloth arrangement reset! Patterns are wrapped in 3D around avatar.")
    else:
        print("[3D NOTE] No native arrangement points found; patterns elevated in 3D.")
except Exception as err:
    print(f"[3D ERROR] Arrangement failed: {err}")

print("\\nFinished! Ready for 3D simulation (Spacebar).")
""")

    code_content = "\n".join(script_lines)
    with open(script_output_path, "w") as f:
        f.write(code_content)
    print(f"[Bridge] Successfully generated Marvelous script: {script_output_path}")
    return script_output_path


if __name__ == '__main__':
    # Test generation of short-shorts using GarmentCode + Bridge
    body = BodyParameters('assets/bodies/plain_model_female.yaml')
    with open('assets/design_params/default.yaml') as f:
        design = yaml.safe_load(f)['design']

    design['meta']['upper']['v'] = None
    design['meta']['bottom']['v'] = 'Pants'
    design['meta']['wb']['v'] = None
    design['pants']['length']['v'] = 0.15  # Mini short-shorts
    design['pants']['width']['v'] = 1.0   # Snug fit
    design['pants']['flare']['v'] = 1.0

    mg = MetaGarment('short_shorts', body, design)
    pattern = mg.assembly()

    arrangement_map = {
        'pant_f_l': 'Leg_Front_L',
        'pant_f_r': 'Leg_Front_R',
        'pant_b_l': 'Leg_Back_R',  # In MD, Leg_Back_R is behind Left Leg (+X)
        'pant_b_r': 'Leg_Back_L'   # In MD, Leg_Back_L is behind Right Leg (-X)
    }

    generate_marvelous_script(
        pattern,
        'create_marvelous_shorts.py',
        title="Marvelous Designer Procedural Short-Shorts (From GarmentCode)",
        arrangement_mapping=arrangement_map
    )
