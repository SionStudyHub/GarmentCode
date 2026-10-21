"""Build a GarmentCode garment for a measured sion-avatar body and cut it into panel meshes for draping.

    ./.venv/bin/python sion_pipeline/make_pattern.py <name> [--body kit/sion_female_default.yaml]
        [--design assets/design_params/t-shirt.yaml] [--res 1.0] [--arm-angle 40]

Writes sion_pipeline/out/<name>/:
  <name>_specification.json, <name>_pattern.png   the GarmentCode pattern (as GarmentCode saves it)
  <name>_panels.json                              per panel: flat 2D vertices, 3D placement, triangles, and the
                                                  seams as groups of panel vertices that sew into one point
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from assets.bodies.body_params import BodyParameters  # noqa: E402
from assets.garment_programs.meta_garment import MetaGarment  # noqa: E402
from pygarment.meshgen.boxmeshgen import BoxMesh  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('name')
    ap.add_argument('--body', default=str(ROOT / 'sion_pipeline/kit/sion_female_default.yaml'))
    ap.add_argument('--design', default=str(ROOT / 'assets/design_params/t-shirt.yaml'))
    ap.add_argument('--res', type=float, default=1.0, help='mesh edge length in cm')
    ap.add_argument('--arm-angle', type=float, default=None,
                    help='place the sleeves for arms this many degrees below horizontal (match drape --arm-angle)')
    ap.add_argument('--front-extra', type=float, default=0.0,
                    help='cm of extra length in the simple-tee front panels, eased into the side seams (bust room test)')
    a = ap.parse_args()

    if a.front_extra:
        import copy
        from assets.garment_programs import tee
        base = tee.TorsoFrontHalfPanel

        class FrontWithBustRoom(base):
            def __init__(self, name, body, design):
                design = copy.deepcopy(design)
                design['shirt']['length']['v'] += a.front_extra / body['waist_line']
                super().__init__(name, body, design)

        tee.TorsoFrontHalfPanel = FrontWithBustRoom

    body = BodyParameters(a.body)
    if a.arm_angle is not None:
        body.params['arm_pose_angle'] = a.arm_angle
    design = yaml.safe_load(open(a.design))['design']
    pattern = MetaGarment(a.name, body, design).assembly()
    out = ROOT / 'sion_pipeline/out'
    folder = Path(pattern.serialize(str(out), to_subfolder=True, with_3d=False, with_text=False, view_ids=True))
    spec = folder / f'{a.name}_specification.json'

    box = BoxMesh(str(spec), res=a.res)
    box.load()

    panels, owner = [], {}
    for name in box.panelNames:
        p = box.panels[name]
        v2 = np.asarray(p.panel_vertices, float)
        glob = [box.verts_loc_glob[(name, i)] if i < p.n_stitches else -1 for i in range(len(v2))]
        for i, g in enumerate(glob):
            if g >= 0:
                owner.setdefault(g, []).append([len(panels), i])
        panels.append({
            'name': name,
            'v2d': np.round(v2, 4).tolist(),
            'v3d': np.round(p.rot_trans_panel(v2), 4).tolist(),
            'faces': np.asarray(p.panel_faces, int).tolist(),
            'normal': [float(x) for x in p.norm],
        })
    seams = [g for g in owner.values() if len(g) > 1]
    data = {'name': a.name, 'units': 'cm, GarmentCode frame (Y up from floor, front +Z, avatar left +X)',
            'body': str(Path(a.body).resolve().relative_to(ROOT)), 'res': a.res, 'panels': panels, 'seams': seams}
    (folder / f'{a.name}_panels.json').write_text(json.dumps(data))

    nv = sum(len(p['v2d']) for p in panels)
    nf = sum(len(p['faces']) for p in panels)
    print(f'{folder}: {len(panels)} panels, {nv} vertices, {nf} triangles, {len(seams)} seam points')
    for p in panels:
        v = np.asarray(p['v3d'])
        print(f"  {p['name']:18s} {len(p['v2d']):5d} verts  normal {np.round(p['normal'], 2)}  "
              f"x {v[:, 0].min():6.1f}..{v[:, 0].max():6.1f}  y {v[:, 1].min():6.1f}..{v[:, 1].max():6.1f}  "
              f"z {v[:, 2].min():6.1f}..{v[:, 2].max():6.1f}")


if __name__ == '__main__':
    main()
