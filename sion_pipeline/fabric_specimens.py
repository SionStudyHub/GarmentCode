"""Cut the fabric test pieces with GarmentCode and mesh them exactly like garments (same triangles, 1 cm edges).

    ./.venv/bin/python sion_pipeline/fabric_specimens.py [--res 1.0]

Writes sion_pipeline/kit/fabric_specimens.json, read by fabric_tests.py:
  strip  5 x 30 cm strip  (bending: hangs off a ledge; stretch: hangs from its top edge)
  disc   30 cm circle     (drape: rests on an 18 cm round stand, like the Cusick drape tester)

Cloth stiffness in Blender depends on the triangle size and shape, so the tests must use the same mesher and edge
length as the garments (make_pattern.py: BoxMesh at res 1.0), or the calibrated settings won't carry over.
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pygarment as pyg  # noqa: E402
from pygarment.meshgen.boxmeshgen import BoxMesh  # noqa: E402

STRIP = (5.0, 30.0)  # width, length (cm)
DISC_R = 15.0


class Strip(pyg.Panel):
    def __init__(self):
        super().__init__('strip')
        w, l = STRIP
        self.edges = pyg.EdgeSeqFactory.from_verts([0, 0], [l, 0], [l, w], [0, w], loop=True)


class Disc(pyg.Panel):
    def __init__(self):
        super().__init__('disc')
        self.edges = pyg.EdgeSequence(
            pyg.CircleEdgeFactory.from_points_angle([-DISC_R, 0], [DISC_R, 0], np.pi, right=False),
            pyg.CircleEdgeFactory.from_points_angle([DISC_R, 0], [-DISC_R, 0], np.pi, right=False))


class Specimens(pyg.Component):
    def __init__(self):
        super().__init__('fabric_specimens')
        self.strip = Strip()
        self.disc = Disc().translate_by([0, 0, 50])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--res', type=float, default=1.0, help='mesh edge length in cm (must match make_pattern.py)')
    a = ap.parse_args()
    pattern = Specimens().assembly()
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(pattern.serialize(tmp, to_subfolder=True, with_3d=False, with_text=False, view_ids=False))
        box = BoxMesh(str(folder / 'fabric_specimens_specification.json'), res=a.res)
        box.load()
        out = {'res': a.res, 'units': 'cm, flat pattern coordinates'}
        for name in box.panelNames:
            p = box.panels[name]
            v = np.asarray(p.panel_vertices, float)
            f = np.asarray(p.panel_faces, int)
            v -= v.min(0) if name == 'strip' else v.mean(0)  # strip from its corner, disc from its centre
            tri = v[f]
            area = 0.5 * np.abs(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])).sum()
            out[name] = {'v2d': np.round(v, 4).tolist(), 'faces': f.tolist(), 'area_cm2': round(float(area), 2)}
            print(f'{name}: {len(v)} vertices, {len(f)} triangles, {area:.1f} cm2, '
                  f'{area / len(v):.3f} cm2 per vertex, extent {np.round(v.max(0) - v.min(0), 2).tolist()}')
    path = ROOT / 'sion_pipeline/kit/fabric_specimens.json'
    path.write_text(json.dumps(out))
    print('wrote', path)


if __name__ == '__main__':
    main()
