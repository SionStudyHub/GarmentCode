"""Test compiling the 2-layer shirt from the Stage 0 Modelista Deconstruction.
Layer 1: Light-blue turtleneck long-sleeve inner shirt.
Layer 2: Charcoal-gray oversized short-sleeve crew-neck outer tee.
"""
import copy
import json
from pathlib import Path
import yaml
import numpy as np

import sys
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from assets.bodies.body_params import BodyParameters
from assets.garment_programs.meta_garment import MetaGarment

from pygarment.meshgen.boxmeshgen import BoxMesh

def build_layer(name, design_overrides, out_dir, resolution=1.5):
    # Load body parameters for Sion female avatar
    body = BodyParameters(str(ROOT / 'sion_pipeline/kit/sion_female_default.yaml'))
    # Arms in A-pose (46 degrees down)
    body.params['arm_pose_angle'] = 46.0

    # Load baseline default design
    with open(ROOT / 'assets/design_params/default.yaml') as f:
        design = yaml.safe_load(f)['design']

    # Apply overrides
    def recursive_update(base, upd):
        for k, v in upd.items():
            if isinstance(v, dict) and k in base and isinstance(base[k], dict):
                recursive_update(base[k], v)
            else:
                if isinstance(base.get(k), dict) and 'v' in base[k] and not isinstance(v, dict):
                    base[k]['v'] = v
                else:
                    base[k] = v

    recursive_update(design, design_overrides)

    print(f"\n==========================================")
    print(f"Compiling {name} with MetaGarment...")
    print(f"==========================================")
    mg = MetaGarment(name, body, design)
    pattern = mg.assembly()

    out_path = Path(out_dir) / name
    out_path.mkdir(parents=True, exist_ok=True)

    # Save design YAML for record (and to sion_pipeline/designs/)
    for d_path in [out_path / f'{name}_design.yaml', ROOT / 'sion_pipeline/designs' / f'{name}.yaml']:
        d_path.parent.mkdir(parents=True, exist_ok=True)
        with open(d_path, 'w') as f:
            yaml.dump({'design': design}, f, default_flow_style=False)

    # Serialize 2D pattern (generates _specification.json and _pattern.png)
    pattern.serialize(str(out_path), to_subfolder=False, with_3d=False, with_text=True, view_ids=True)

    # Also build BoxMesh 3D panels (_panels.json) for Blender / 3D inspection
    spec_file = out_path / f'{name}_specification.json'
    box = BoxMesh(str(spec_file), res=resolution)
    box.load()
    panels_list, owner = [], {}
    for pname in box.panelNames:
        p = box.panels[pname]
        v2 = np.asarray(p.panel_vertices, float)
        glob = [box.verts_loc_glob[(pname, i)] if i < p.n_stitches else -1 for i in range(len(v2))]
        for i, g in enumerate(glob):
            if g >= 0:
                owner.setdefault(g, []).append([len(panels_list), i])
        panels_list.append({
            'name': pname,
            'v2d': np.round(v2, 4).tolist(),
            'v3d': np.round(p.rot_trans_panel(v2), 4).tolist(),
            'faces': np.asarray(p.panel_faces, int).tolist(),
            'normal': [float(x) for x in p.norm],
        })
    seams = [g for g in owner.values() if len(g) > 1]
    panels_data = {
        'name': name,
        'units': 'cm, GarmentCode frame (Y up from floor, front +Z, avatar left +X)',
        'body': 'sion_pipeline/kit/sion_female_default.yaml',
        'res': resolution,
        'panels': panels_list,
        'seams': seams,
    }
    (out_path / f'{name}_panels.json').write_text(json.dumps(panels_data))

    # Also mirror to sion_pipeline/out/<name> for drape_blender.py compatibility
    std_out = ROOT / 'sion_pipeline/out' / name
    if std_out.resolve() != out_path.resolve():
        std_out.mkdir(parents=True, exist_ok=True)
        pattern.serialize(str(std_out), to_subfolder=False, with_3d=False, with_text=True, view_ids=True)
        (std_out / f'{name}_panels.json').write_text(json.dumps(panels_data))

    print(f"Pattern serialized to: {out_path}")

    # Inspect compiled panels
    with open(spec_file) as f:
        spec = json.load(f)

    panels = spec['pattern']['panels']
    stitches = spec['pattern']['stitches']
    print(f"Total Panels: {len(panels)}")
    for pname, pdata in panels.items():
        n_verts = len(pdata['vertices'])
        trans = pdata.get('translation', [0, 0, 0])
        print(f"  - Panel '{pname}': {n_verts} vertices, 3D translation: [x={trans[0]:.1f}, y={trans[1]:.1f}, z={trans[2]:.1f}] cm")
    print(f"Total Stitches: {len(stitches)}")

    return out_path, spec

def main():
    out_dir = ROOT / 'sion_pipeline/out/layered_tops_test'
    out_dir.mkdir(parents=True, exist_ok=True)

    # ----------------------------------------------------
    # LAYER 1: Light-Blue High-Neck Long-Sleeve Inner Shirt
    # ----------------------------------------------------
    layer1_overrides = {
        'meta': {
            'upper': {'v': 'Shirt'},
            'wb': {'v': None},
            'bottom': {'v': None}
        },
        'shirt': {
            'strapless': {'v': False},
            'length': {'v': 1.62},  # Extended tunic length (~7 cm extra for shoulder wrap so hem clears Layer 2)
            'width': {'v': 1.05},   # Close-fitting comfortable knit
            'flare': {'v': 1.15}    # Hip clearance on 76.2 cm hips so tunic hem drops straight
        },
        'collar': {
            'f_collar': {'v': 'CircleNeckHalf'},
            'b_collar': {'v': 'CircleNeckHalf'},
            'width': {'v': -0.20},   # Normalized neckline control: 7.5 cm width, not negative garment ease
            'fc_depth': {'v': -0.22}, # Offset the plain-Shirt draft's shoulder-slope depth compensation
            'bc_depth': {'v': -0.16}, # Combined collar circumference ~24 cm on a ~22.4 cm neck
            'component': {
                'style': {'v': 'Turtle'},
                'depth': {'v': 3}    # 3 cm standing collar clears the chin without folding outward
            }
        },
        'sleeve': {
            'sleeveless': {'v': False},
            'length': {'v': 0.95},             # Full wrist length
            'connecting_width': {'v': 0.15},   # High, clean armscye
            'end_width': {'v': 0.65},          # Gently tapered wrist
            'sleeve_angle': {'v': 46},         # Match A-pose
            'connect_ruffle': {'v': 1.0},
            'cuff': {'type': {'v': None}}
        }
    }

    l1_path, l1_spec = build_layer('layer_1_inner_turtleneck', layer1_overrides, out_dir)

    # ----------------------------------------------------
    # LAYER 2: Charcoal-Gray Oversized Short-Sleeve Outer Tee
    # ----------------------------------------------------
    layer2_overrides = {
        'meta': {
            'upper': {'v': 'Shirt'},
            'wb': {'v': None},
            'bottom': {'v': None}
        },
        'shirt': {
            'strapless': {'v': False},
            'length': {'v': 1.38},  # High-hip length (shorter than Layer 1's 1.55 tunic hem)
            'width': {'v': 1.12},   # Relaxed boxy ease over Layer 1 without collapsing shoulders
            'flare': {'v': 1.06}
        },
        'collar': {
            'f_collar': {'v': 'CircleNeckHalf'},
            'b_collar': {'v': 'CircleNeckHalf'},
            'width': {'v': 0.28},    # Crew neck wide enough to reveal Layer 1's turtleneck while keeping >4.1 cm shoulder seam
            'fc_depth': {'v': -0.10}, # ~36 cm crew opening after shoulder-slope compensation
            'bc_depth': {'v': -0.05},
            'component': {
                'style': {'v': None} # No collar component
            }
        },
        'sleeve': {
            'sleeveless': {'v': False},
            'length': {'v': 0.32},             # Short sleeves to mid-bicep
            'connecting_width': {'v': 0.18},   # Relaxed armhole without underarm wing flare
            'end_width': {'v': 0.82},          # Cylindrical boxy short-sleeve opening (~20.8 cm circ, tapered from 12.7 cm arm_width)
            'sleeve_angle': {'v': 46},         # Match A-pose
            'connect_ruffle': {'v': 1.0},
            'cuff': {'type': {'v': None}}
        }
    }

    l2_path, l2_spec = build_layer('layer_2_outer_oversized_tee', layer2_overrides, out_dir)

    print("\n[SUCCESS] Both layers compiled successfully!")

if __name__ == '__main__':
    main()
