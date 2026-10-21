"""Drape a GarmentCode compiled garment on the Sion female avatar using Marvelous Designer headless,
and render studio previews in Blender.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
MD_BIN = "/Applications/MarvelousDesigner.app/Contents/MacOS/MarvelousDesigner_PER"
BLENDER_BIN = "/Users/vaz/.local/bin/blender"
AVATAR_OBJ = str(ROOT / "sion_avatars/sion-female-apose.obj")
AVATAR_GLB = str(ROOT / "sion_avatars/sion-female-apose.glb")

from pygarment.meshgen.boxmeshgen import Edge

def transform_panel_2d_for_md(p_name, vx, vy):
    """Transforms GarmentCode local 2D panel coordinates (vx, vy) in cm into
    Marvelous Designer 2D pattern coordinates (mx, my) in cm so that:
      - Back torso/collar panels are horizontally reflected (-vx, vy) for back arrangement points.
      - Sleeve panels are rotated 90 degrees so the sleeve length runs vertically (+Y -> shoulder)
        along MD's Arm_* arrangement cylinders, and back sleeves are horizontally reflected.
    """
    if p_name == 'left_sleeve_f':
        return (vy, -vx)
    elif p_name == 'left_sleeve_b':
        return (-vy, -vx)
    elif p_name == 'right_sleeve_f':
        return (-vy, vx)
    elif p_name == 'right_sleeve_b':
        return (vy, vx)
    elif any(k in p_name for k in ['btorso', 'back']):
        return (-vx, vy)
    else:
        return (vx, vy)


def panel_edge_curve(panel, edge_index):
    return Edge(panel['edges'][edge_index], np.asarray(panel['vertices'], dtype=float), 1.0).curve


def boundary_segment_counts(panels, stitches):
    """Pair curved sewing edges with equal counts at equal arc-length fractions."""
    counts = {}
    for name, panel in panels.items():
        for i, edge in enumerate(panel['edges']):
            counts[name, i] = max(1, int(np.ceil(panel_edge_curve(panel, i).length() / 0.8))) if 'curvature' in edge else 1
    for stitch in stitches:
        a, b = [(side['panel'], side['edge']) for side in stitch[:2]]
        counts[a] = counts[b] = max(counts[a], counts[b])
    return counts


def sample_panel_md_points(p_name, p_data, cx_mm, base_y_mm, segment_counts):
    """Emit explicit straight segments and retain each original edge's MD indices.

    MD ignores type-1 points in CreatePatternWithPoints on the installed build.
    All sampled corners are type 0, with paired subsegments sewn individually.
    """
    points, edge_map = [], {}
    for i, edge in enumerate(p_data['edges']):
        curve = panel_edge_curve(p_data, i)
        length = curve.length()
        count = segment_counts[p_name, i]
        edge_map[i] = list(range(len(points), len(points) + count))
        for k in range(count):
            t = curve.ilength(length * k / count) if k else 0.0
            point = curve.point(t)
            mx, my = transform_panel_2d_for_md(p_name, point.real, point.imag)
            points.append((round(cx_mm + mx * 10, 4), round(base_y_mm + my * 10, 4), 0))
    return points, edge_map


def generate_md_script(spec_paths, md_script_path, out_obj_path, out_zprj_path, sim_steps=140):
    """Generates a standalone Marvelous Designer headless Python script that loads the avatar,
    builds pattern panels for 1 or more layers, stitches them, arranges them in 3D,
    simulates drape, and exports the final 3D OBJ and ZPRJ.
    """
    layers_data = []
    for layer_idx, sp in enumerate(spec_paths):
        with open(sp) as f:
            spec = json.load(f)
        layers_data.append({
            'layer_idx': layer_idx,
            'name': Path(sp).stem.replace('_specification', ''),
            'panels': spec['pattern']['panels'],
            'stitches': spec['pattern']['stitches']
        })

    lines = [
        'import sys',
        'import traceback',
        'import json',
        'import pattern_api',
        'import utility_api',
        'import export_api',
        'import import_api',
        'import fabric_api',
        'import ApiTypes',
        '',
        'def run():',
        '    print("=== 1. Loading Sion Female Avatar ===")',
        f'    avatar_path = {repr(AVATAR_OBJ)}',
        '    ok = import_api.ImportFile(avatar_path)',
        '    print(f"Loaded avatar: {ok}")',
        '    arr_list = pattern_api.GetArrangementList()',
        '    print(f"Available arrangement points: {len(arr_list) if arr_list else 0}")',
        '',
        '    panel_ids = {}',
        '    panel_arr_targets = {}',
        '    panel_arr_y = {}',
        ''
    ]

    # Panel placement and creation
    ordered_panel_keys = []
    lines.append('    # === 2. Create Pattern Pieces ===')
    for l_data in layers_data:
        l_idx = l_data['layer_idx']
        prefix = f"l{l_idx}_" if len(layers_data) > 1 else ""
        panels = l_data['panels']
        segment_counts = boundary_segment_counts(panels, l_data['stitches'])
        l_data['edge_maps'] = {}

        # 2D window spacing offsets per layer (well separated in 2D window)
        layout_offsets = {
            'left_ftorso': 0.0,
            'right_ftorso': 0.0,
            'left_btorso': 600.0,
            'right_btorso': 600.0,
            'left_sleeve_f': 1150.0,
            'left_sleeve_b': 1400.0,
            'right_sleeve_f': -550.0,
            'right_sleeve_b': -800.0,
            'left_collar_front': 150.0,
            'right_collar_front': -150.0,
            'left_collar_back': 750.0,
            'right_collar_back': 450.0,
        }

        layer_y_offset = l_idx * 1500.0  # Stack layers vertically in 2D window if multiple

        for p_name, p_data in panels.items():
            key = f"{prefix}{p_name}"
            ordered_panel_keys.append(key)
            verts = p_data['vertices']
            trans = p_data.get('translation', [0, 0, 0])

            cx_mm = layout_offsets.get(p_name, (trans[0] * 10.0))
            base_y_mm = (trans[1] * 10.0) + layer_y_offset

            md_pts, edge_map = sample_panel_md_points(p_name, p_data, cx_mm, base_y_mm, segment_counts)
            l_data['edge_maps'][p_name] = edge_map

            # Determine 3D arrangement point target
            xs_raw = [abs(v[0]) for v in verts]
            sleeve_span_cm = max(xs_raw) - min(xs_raw) if xs_raw else 0.0
            arm_zone = "2" if sleeve_span_cm > 28.0 else "1"
            if "ftorso" in p_name:
                target_name = "Body_Front_Center_1"
            elif "btorso" in p_name:
                target_name = "Body_Back_Center_1"
            elif "sleeve_f" in p_name:
                target_name = f"Arm_Front_{arm_zone}_L" if "left" in p_name else f"Arm_Front_{arm_zone}_R"
            elif "sleeve_b" in p_name:
                target_name = f"Arm_Back_{arm_zone}_L" if "left" in p_name else f"Arm_Back_{arm_zone}_R"
            elif "collar_front" in p_name:
                target_name = "Neck_Front"
            elif "collar_back" in p_name:
                target_name = "Neck_Back"
            else:
                target_name = "Body_Front_Center_1"

            lines.append(f'    # Panel: {key} -> {target_name}')
            lines.append(f'    {key}_pts = [')
            for pt_x, pt_y, pt_t in md_pts:
                lines.append(f'        ({pt_x}, {pt_y}, {pt_t}),')
            lines.append('    ]')
            lines.append(f'    pid = pattern_api.CreatePatternWithPoints({key}_pts)')
            lines.append(f'    if pid is not None:')
            lines.append(f'        panel_ids[{repr(key)}] = pid')
            lines.append(f'        panel_arr_targets[{repr(key)}] = {repr(target_name)}')
            if 'torso' in p_name:
                # Sion's native body cylinder spans Y=803.3..1219.9 mm.
                desired_y = trans[1] * 10 + (min(v[1] for v in verts) + max(v[1] for v in verts)) * 5
                lines.append(f'        panel_arr_y[{key!r}] = {round((desired_y - 803.3) / 4.166)}')
            lines.append(f'        try:')
            lines.append(f'            if hasattr(pattern_api, "SetPatternPieceName"):')
            lines.append(f'                pattern_api.SetPatternPieceName(pid, {repr(key)})')
            lines.append(f'        except Exception:')
            lines.append(f'            pass')
            if len(layers_data) > 1:
                lines.append(f'        pattern_api.SetPatternLayer(pid, {l_idx})')
            lines.append('        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)')
            lines.append(f'        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == {len(md_pts)}, "MD boundary segment mismatch: {key}"')
            lines.append(f'        print(f"Created pattern {key} -> ID {{pid}} (target={target_name})")')
            lines.append('')

    # Sewing Stitches
    lines.append('    # === 3. Apply Sewing Stitches ===')
    lines.append('    print("\\n--- Sewing Seams ---")')
    for l_data in layers_data:
        l_idx = l_data['layer_idx']
        prefix = f"l{l_idx}_" if len(layers_data) > 1 else ""
        stitches = l_data['stitches']

        for s_idx, s in enumerate(stitches):
            p1_raw, e1 = s[0]['panel'], s[0]['edge']
            p2_raw, e2 = s[1]['panel'], s[1]['edge']
            p1 = f"{prefix}{p1_raw}"
            p2 = f"{prefix}{p2_raw}"
            segments1 = l_data['edge_maps'][p1_raw][e1]
            segments2 = l_data['edge_maps'][p2_raw][e2]
            assert len(segments1) == len(segments2)
            # GarmentCode boundaries are oppositely oriented at a standard seam.
            for md1, md2 in zip(segments1, reversed(segments2)):
                lines.append(f'    assert pattern_api.AddSeamlinePairGroup(int(panel_ids[{p1!r}]), {md1}, int(panel_ids[{p2!r}]), {md2}, True, False), "Sewing failed: {p1}/{e1} to {p2}/{e2}"')

    # Native 3D Arrangement
    lines.append('')
    lines.append('    # === 4. Native 3D Arrangement ===')
    lines.append('    print("\\n--- Arranging 3D Panels Around Avatar ---")')
    lines.append('    for key, pid in panel_ids.items():')
    lines.append('        target_name = panel_arr_targets.get(key)')
    lines.append('        if target_name and arr_list:')
    lines.append('            matched_id = None')
    lines.append('            for item in arr_list:')
    lines.append('                if item.get("ArrangementName", "").strip().lower() == target_name.lower():')
    lines.append('                    matched_id = int(item["ArrangementIndex"])')
    lines.append('                    break')
    lines.append('            if matched_id is not None:')
    lines.append('                pattern_api.SetArrangement(pid, matched_id)')
    lines.append('                radial = 52 if key.startswith("l1_") else 50')
    lines.append('                # Native points center each pattern independently; place halves on their own side.')
    lines.append('                if "ftorso" in key:')
    lines.append('                    pattern_api.SetArrangementPosition(pid, 35 if "left" in key else 65, panel_arr_y[key], radial)')
    lines.append('                elif "btorso" in key:')
    lines.append('                    pattern_api.SetArrangementPosition(pid, 15 if "left" in key else 85, panel_arr_y[key], radial)')
    lines.append('                elif "sleeve" in key:')
    lines.append('                    ap = pattern_api.GetArrangementOfPattern(pid)')
    lines.append('                    arm_y = 95 if "_1_" in target_name else 50')
    lines.append('                    pattern_api.SetArrangementPosition(pid, int(ap["ArrangementOffsetX"]), arm_y, radial)')
    lines.append('                elif "collar_front" in key:')
    lines.append('                    pattern_api.SetArrangementPosition(pid, 87 if "left" in key else 13, 50, radial)')
    lines.append('                elif "collar_back" in key:')
    lines.append('                    pattern_api.SetArrangementPosition(pid, 62 if "left" in key else 38, 50, radial)')

    lines.append('                print(f"Arranged {key} -> {target_name} (idx {matched_id})")')
    lines.append('')
    lines.append('    print("\\nResetting cloth arrangement in 3D...")')
    lines.append('    utility_api.ResetClothArrangement()')
    lines.append('')

    lines.append('    opt_initial = ApiTypes.ImportExportOption()')
    lines.append('    opt_initial.bExportGarment = True')
    lines.append('    opt_initial.bExportAvatar = False')
    lines.append(f'    export_api.ExportOBJ({str(Path(out_obj_path).with_name(Path(out_obj_path).stem + "_arranged.obj"))!r}, opt_initial)')

    # Simulation
    lines.append(f'    # === 5. Simulate Cloth Drape ({sim_steps} steps) ===')
    lines.append(f'    print("\\n--- Simulating Physical Drape ({sim_steps} steps) ---")')
    if len(layers_data) > 1:
        untangle_steps = max(100, int(sim_steps * 0.7))
        settle_steps = max(60, sim_steps - untangle_steps)
        lines.append('    utility_api.SetSimulationLayerBasedCollisionDetection(True)')
        lines.append(f'    utility_api.Simulate({untangle_steps})')
        lines.append('    # Reset all patterns to Layer 0 for natural contact settling')
        lines.append('    for pid in panel_ids.values():')
        lines.append('        pattern_api.SetPatternLayer(pid, 0)')
        lines.append(f'    utility_api.Simulate({settle_steps})')
    else:
        lines.append(f'    utility_api.Simulate({sim_steps})')
    lines.append('    print("Simulation completed!")')
    lines.append('')

    # Export
    lines.append('    # === 6. Export Garment Mesh (Non-Interactive) ===')
    lines.append('    print("\\n--- Exporting OBJ & ZPRJ ---")')
    lines.append('    opt = ApiTypes.ImportExportOption()')
    lines.append('    opt.bExportGarment = True')
    lines.append('    opt.bExportAvatar = False')
    lines.append(f'    export_api.ExportOBJ({repr(str(out_obj_path))}, opt)')
    lines.append(f'    export_api.ExportZPrj({repr(str(out_zprj_path))}, False)')
    lines.append('    print("Finished headless drape export!")')
    lines.append('')
    lines.append('if __name__ == "__main__":')
    lines.append('    try:')
    lines.append('        run()')
    except_block = [
        '    except Exception as e:',
        '        traceback.print_exc()',
        '        sys.exit(1)'
    ]
    lines.extend(except_block)

    Path(md_script_path).parent.mkdir(parents=True, exist_ok=True)
    with open(md_script_path, 'w') as f:
        f.write('\n'.join(lines))
    print(f"Wrote Marvelous Designer script to: {md_script_path}")
    return md_script_path, ordered_panel_keys

def generate_blender_render_script(blender_script_path, avatar_glb_path, garment_obj_path, out_render_dir, garment_color=(0.2, 0.2, 0.22, 1.0), panel_keys=None):
    """Generates a Blender Python script to render turntable views of the avatar wearing the garment.
    Parses the OBJ directly by `g <group_name>` in pattern creation order so multi-layer garments
    (`l0_*` vs `l1_*`) receive distinct colors (light-blue inner turtleneck vs charcoal-gray outer tee).
    """
    av_path = repr(str(avatar_glb_path))
    g_path = repr(str(garment_obj_path))
    out_dir_path = repr(str(out_render_dir))
    p_keys_repr = repr(list(panel_keys) if panel_keys else [])
    lines = [
        'import bpy',
        'import math',
        'from mathutils import Vector, Euler',
        'from pathlib import Path',
        '',
        'def load_garment_obj_with_layer_materials(obj_path, default_color, panel_keys):',
        '    verts = []',
        '    faces = []',
        '    face_groups = []',
        '    seen_groups = []',
        '    cur_group = "default"',
        '    with open(obj_path, "r") as f:',
        '        for line in f:',
        '            if line.startswith("v "):',
        '                parts = line.split()',
        '                # Scale mm -> m and convert MD (X, Y_up, Z_front) to Blender (X, -Z_front, Y_up)',
        '                vx, vy, vz = float(parts[1]) * 0.001, float(parts[2]) * 0.001, float(parts[3]) * 0.001',
        '                verts.append((vx, -vz, vy))',
        '            elif line.startswith("g ") or line.startswith("o "):',
        '                cur_group = line.split(None, 1)[1].strip() if len(line.split()) > 1 else "default"',
        '                if cur_group not in seen_groups:',
        '                    seen_groups.append(cur_group)',
        '            elif line.startswith("f "):',
        '                parts = line.split()[1:]',
        '                f_idxs = [int(p.split("/")[0]) - 1 for p in parts]',
        '                faces.append(f_idxs)',
        '                face_groups.append(cur_group)',
        '',
        '    group_to_key = {}',
        '    for idx, g_name in enumerate(seen_groups):',
        '        if idx < len(panel_keys):',
        '            group_to_key[g_name] = panel_keys[idx]',
        '        else:',
        '            group_to_key[g_name] = g_name',
        '',
        '    mesh = bpy.data.meshes.new("GarmentMesh")',
        '    mesh.from_pydata(verts, [], faces)',
        '    mesh.update()',
        '    g_obj = bpy.data.objects.new("Garment", mesh)',
        '    bpy.context.scene.collection.objects.link(g_obj)',
        '    for poly in mesh.polygons:',
        '        poly.use_smooth = True',
        '',
        '    def make_mat(name, color):',
        '        mat = bpy.data.materials.new(name=name)',
        '        mat.use_nodes = True',
        '        bsdf = mat.node_tree.nodes.get("Principled BSDF")',
        '        if bsdf:',
        '            bsdf.inputs["Base Color"].default_value = color',
        '            bsdf.inputs["Roughness"].default_value = 0.78',
        '            if "Sheen Weight" in bsdf.inputs:',
        '                bsdf.inputs["Sheen Weight"].default_value = 0.45',
        '        return mat',
        '',
        '    mat_l0 = make_mat("Layer1_Inner_LightBlue", (0.55, 0.72, 0.88, 1.0))',
        '    mat_l1 = make_mat("Layer2_Outer_Charcoal", (0.045, 0.045, 0.055, 1.0))',
        '    mat_def = make_mat("GarmentDefault", default_color)',
        '    mesh.materials.append(mat_def)',
        '    mesh.materials.append(mat_l0)',
        '    mesh.materials.append(mat_l1)',
        '',
        '    for poly, grp in zip(mesh.polygons, face_groups):',
        '        mapped = group_to_key.get(grp, grp)',
        '        if mapped.startswith("l0_"):',
        '            poly.material_index = 1',
        '        elif mapped.startswith("l1_"):',
        '            poly.material_index = 2',
        '        else:',
        '            poly.material_index = 0',
        '    return g_obj',
        '',
        'def main():',
        '    # 1. Clear default scene',
        '    bpy.ops.wm.read_factory_settings(use_empty=True)',
        '',
        '    # 2. Import Sion Avatar GLB',
        f'    avatar_path = {av_path}',
        '    print(f"Importing avatar: {avatar_path}")',
        '    bpy.ops.import_scene.gltf(filepath=avatar_path)',
        '',
        '    # Delete unrigged helper meshes (Icosphere)',
        '    for obj in list(bpy.context.scene.objects):',
        '        if "icosphere" in obj.name.lower():',
        '            bpy.data.objects.remove(obj, do_unlink=True)',
        '',
        '    # 3. Load Garment OBJ with per-layer materials',
        f'    garment_path = {g_path}',
        '    print(f"Loading garment: {garment_path}")',
        f'    load_garment_obj_with_layer_materials(garment_path, {garment_color}, {p_keys_repr})',

        '',
        '    # 4. Setup Lighting',
        '    world = bpy.context.scene.world',
        '    if not world:',
        '        world = bpy.data.worlds.new("World")',
        '        bpy.context.scene.world = world',
        '    world.use_nodes = True',
        '    bg = world.node_tree.nodes.get("Background")',
        '    if bg:',
        '        bg.inputs["Color"].default_value = (0.92, 0.92, 0.93, 1.0)',
        '        bg.inputs["Strength"].default_value = 0.5',
        '',
        '    # Key Light',
        '    key_data = bpy.data.lights.new(name="KeyLight", type="SUN")',
        '    key_data.energy = 2.0',
        '    key_data.color = (1.0, 0.98, 0.95)',
        '    key_obj = bpy.data.objects.new(name="KeyLight", object_data=key_data)',
        '    bpy.context.scene.collection.objects.link(key_obj)',
        '    key_obj.rotation_euler = Euler((math.radians(50), math.radians(15), math.radians(35)), "XYZ")',
        '',
        '    # Fill Light',
        '    fill_data = bpy.data.lights.new(name="FillLight", type="SUN")',
        '    fill_data.energy = 0.8',
        '    fill_data.color = (0.95, 0.97, 1.0)',
        '    fill_obj = bpy.data.objects.new(name="FillLight", object_data=fill_data)',
        '    bpy.context.scene.collection.objects.link(fill_obj)',
        '    fill_obj.rotation_euler = Euler((math.radians(45), math.radians(-25), math.radians(-60)), "XYZ")',
        '',
        '    # Rim / Back Light',
        '    rim_data = bpy.data.lights.new(name="RimLight", type="SUN")',
        '    rim_data.energy = 1.2',
        '    rim_obj = bpy.data.objects.new(name="RimLight", object_data=rim_data)',
        '    bpy.context.scene.collection.objects.link(rim_obj)',
        '    rim_obj.rotation_euler = Euler((math.radians(-40), 0, math.radians(160)), "XYZ")',
        '',
        '    # 5. Setup Camera',
        '    cam_data = bpy.data.cameras.new(name="StudioCam")',
        '    cam_data.lens = 75.0  # Portrait lens to avoid perspective distortion',
        '    cam_obj = bpy.data.objects.new(name="StudioCam", object_data=cam_data)',
        '    bpy.context.scene.collection.objects.link(cam_obj)',
        '    bpy.context.scene.camera = cam_obj',
        '',
        '    # Render Settings',
        '    bpy.context.scene.render.engine = "BLENDER_EEVEE"',
        '    bpy.context.scene.render.resolution_x = 1024',
        '    bpy.context.scene.render.resolution_y = 1280',
        '    bpy.context.scene.render.image_settings.file_format = "PNG"',
        '',
        f'    out_dir = Path({out_dir_path})',
        '    out_dir.mkdir(parents=True, exist_ok=True)',
        '',
        '    # Camera targets (torso focus: Z ~ 1.05m)',
        '    views = [',
        '        ("front", (0.0, -2.4, 1.08), (math.radians(88), 0, 0)),',
        '        ("persp", (1.7, -1.9, 1.15), (math.radians(86), 0, math.radians(42))),',
        '        ("side", (2.4, 0.0, 1.08), (math.radians(90), 0, math.radians(90))),',
        '        ("back", (0.0, 2.4, 1.08), (math.radians(92), 0, math.radians(180))),',
        '        ("detail", (0.0, -1.2, 1.15), (math.radians(88), 0, 0)),',
        '    ]',
        '',
        '    for v_name, pos, rot in views:',
        '        cam_obj.location = Vector(pos)',
        '        cam_obj.rotation_euler = Euler(rot, "XYZ")',
        '        out_img = str(out_dir / f"avatar_shirt_{v_name}.png")',
        '        bpy.context.scene.render.filepath = out_img',
        '        print(f"Rendering {v_name} -> {out_img}...")',
        '        bpy.ops.render.render(write_still=True)',
        '        print(f"Saved {out_img}")',
        '',
        '    print("All renders completed successfully!")',
        '',
        'if __name__ == "__main__":',
        '    main()',
    ]

    with open(blender_script_path, 'w') as f:
        f.write('\n'.join(lines))
    print(f"Wrote Blender render script to: {blender_script_path}")
    return blender_script_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--layer', default='2', choices=['1', '2', 'both'], help='Layer to drape: 1 (turtleneck), 2 (outer tee), or both')
    parser.add_argument('--sim-steps', type=int, default=360, help='Simulation frame count')
    args = parser.parse_args()

    out_base = ROOT / 'sion_pipeline/out/layered_tops_test'
    out_base.mkdir(parents=True, exist_ok=True)

    if args.layer == '2':
        specs = [out_base / 'layer_2_outer_oversized_tee/layer_2_outer_oversized_tee_specification.json']
        name = "layer_2_outer_tee"
        color = (0.045, 0.045, 0.055, 1.0)  # Charcoal-gray
    elif args.layer == '1':
        specs = [out_base / 'layer_1_inner_turtleneck/layer_1_inner_turtleneck_specification.json']
        name = "layer_1_inner_turtleneck"
        color = (0.60, 0.75, 0.88, 1.0)  # Light-blue
    else:
        specs = [
            out_base / 'layer_1_inner_turtleneck/layer_1_inner_turtleneck_specification.json',
            out_base / 'layer_2_outer_oversized_tee/layer_2_outer_oversized_tee_specification.json'
        ]
        name = "layered_tops_both"
        color = (0.25, 0.25, 0.27, 1.0)

    md_script = out_base / f"{name}_drape_md.py"
    garment_obj = out_base / f"{name}_draped.obj"
    garment_zprj = out_base / f"{name}_draped.zprj"
    blender_script = out_base / f"{name}_render_blender.py"
    render_dir = out_base / f"{name}_renders"

    print(f"=== 1. Generating Marvelous Designer Script for {name} ===")
    _, ordered_panel_keys = generate_md_script(specs, md_script, garment_obj, garment_zprj, sim_steps=args.sim_steps)

    print(f"\n=== 2. Running Marvelous Designer Headless Simulation ===")
    cmd_md = [MD_BIN, "-headless", str(md_script), "-headlesslog"]
    print("$", " ".join(cmd_md))
    started = time.time()
    md_log = md_script.with_suffix('.log')
    with md_log.open('w') as log:
        r_md = subprocess.run(cmd_md, stdout=log, stderr=subprocess.STDOUT, text=True)
    md_output = md_log.read_text()
    if 'Traceback (most recent call last)' in md_output or 'Finished headless drape export!' not in md_output:
        raise RuntimeError(f'MD script failed; see {md_log}')
    r_md.stdout = md_output
    r_md.stderr = ''
    print(r_md.stdout[-500:] if len(r_md.stdout) > 500 else r_md.stdout)
    if r_md.returncode != 0:
        print(f"MD Error:\n{r_md.stderr}")
        sys.exit(r_md.returncode)

    if not garment_obj.exists() or garment_obj.stat().st_mtime < started:
        print(f"Error: Garment OBJ was not created at {garment_obj}")
        sys.exit(1)
    print(f"Successfully generated draped OBJ: {garment_obj} ({garment_obj.stat().st_size} bytes)")

    print(f"\n=== 3. Rendering in Blender ===")
    generate_blender_render_script(blender_script, AVATAR_GLB, garment_obj, render_dir, garment_color=color, panel_keys=ordered_panel_keys)
    cmd_bl = [BLENDER_BIN, "-b", "--factory-startup", "-P", str(blender_script)]
    print("$", " ".join(cmd_bl))
    r_bl = subprocess.run(cmd_bl, capture_output=True, text=True)
    print(r_bl.stdout[-500:] if len(r_bl.stdout) > 500 else r_bl.stdout)
    if r_bl.returncode != 0:
        print(f"Blender Error:\n{r_bl.stderr}")
        sys.exit(r_bl.returncode)

    print(f"\n[DONE] Renders saved to: {render_dir}")
    for p in sorted(render_dir.glob("*.png")):
        print(f"  - {p.name} ({p.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
