import json
import os
import yaml
import numpy as np

from assets.bodies.body_params import BodyParameters
from assets.garment_programs.meta_garment import MetaGarment
from pygarment.meshgen.boxmeshgen import BoxMesh

print("=== 1. Compiling GarmentCode Engine for new_base_female ===")
with open('assets/design_params/t-shirt.yaml') as f:
    design = yaml.safe_load(f)['design']

body = BodyParameters('assets/bodies/new_base_female.yaml')
garment = MetaGarment('NewFemaleTee', body, design)
pattern = garment.assembly()

out_dir = 'export_garmentcode'
os.makedirs(out_dir, exist_ok=True)
spec_dir = pattern.serialize(out_dir, with_3d=False)
spec_file = os.path.join(spec_dir, f'{garment.name}_specification.json')

print(f"Loading GarmentCode BoxMesh at res=1.2cm from: {spec_file}")
bm_gc = BoxMesh(spec_file, res=1.2)
bm_gc.load_panels()
bm_gc.gen_panel_meshes()

data = {
    "garment_name": garment.name,
    "panels": {},
    "sewing_springs": []
}

# Avatar Anatomical Coordinates (in meters) from new_base_female_digital_tailor_spec.json
# Chest apex: X=0, Y=-0.140, Z in [1.07, 1.44]
# Back apex:  X=0, Y=+0.080, Z in [1.07, 1.44]
# Side seams: X=pm 0.14 to 0.16, Y=-0.015

for p_name, panel in bm_gc.panels.items():
    p_verts = panel.panel_vertices
    is_front = 'ftorso' in p_name
    is_back  = 'btorso' in p_name
    is_sleeve = 'sleeve' in p_name
    is_left  = 'left' in p_name
    
    base_elev_m = panel.translation[1] / 100.0
    
    blender_verts = []
    for v in p_verts:
        vx = v[0] / 100.0
        vy = v[1] / 100.0
        bz = base_elev_m + vy
        
        if is_front:
            # Front panel curves smoothly from center to avatar side seam (Y=-0.018)
            w_max = 0.2079
            frac = abs(vx) / w_max
            bx = vx
            by = -0.142 + (-0.018 - (-0.142)) * (frac**1.5)
        elif is_back:
            # Back panel curves smoothly from center to avatar side seam (Y=-0.012)
            w_max = 0.1895
            frac = abs(vx) / w_max
            bx = vx
            by = 0.080 + (-0.012 - 0.080) * (frac**1.5)
        elif is_sleeve:
            # Sleeve wraps around upper arm profile
            arm_center_x = 0.235 if is_left else -0.235
            arm_center_y = -0.020
            sleeve_w = 0.1935
            theta = (vx / sleeve_w) * np.pi
            if 'sleeve_f' in p_name:
                bx = arm_center_x + (0.045 if is_left else -0.045) * np.cos(theta)
                by = arm_center_y - 0.045 * np.sin(abs(theta)) - 0.015
            else:
                bx = arm_center_x + (0.045 if is_left else -0.045) * np.cos(theta)
                by = arm_center_y + 0.045 * np.sin(abs(theta)) + 0.015
        else:
            bx = vx
            by = 0.0
            
        blender_verts.append([round(bx, 5), round(by, 5), round(bz, 5)])
        
    data["panels"][p_name] = {
        "vertices": blender_verts,
        "faces": [list(int(idx) for idx in f) for f in panel.panel_faces]
    }

for stitch in bm_gc.stitches:
    r1, r2 = bm_gc._swap_stitch_ranges(stitch)
    for idx1, idx2 in zip(r1, r2):
        data["sewing_springs"].append({
            "panel_1": stitch.panel_1,
            "vert_1": int(idx1),
            "panel_2": stitch.panel_2,
            "vert_2": int(idx2)
        })

output_json = "garmentcode_blender_data.json"
with open(output_json, 'w') as f:
    json.dump(data, f, indent=2)

print(f"SUCCESS! Exported {len(data['panels'])} pre-curved GarmentCode panels and {len(data['sewing_springs'])} sewing springs to '{output_json}'.")
