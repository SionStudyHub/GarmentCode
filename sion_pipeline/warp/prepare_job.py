"""Pack a GarmentCode garment + the sion-avatar A-pose body into one small job for the Warp simulator on Colab.

    ./.venv/bin/python sion_pipeline/warp/prepare_job.py <name> --design sion_pipeline/designs/tee_long_f11.yaml
        [--front-extra 2.5] [--body-kit sion_pipeline/kit/female_apose_body.json]

Writes sion_pipeline/warp/jobs/<name>/
  <name>_specification.json       the GarmentCode pattern, sleeves placed for the body's measured arm angle
  job.tar.gz                      spec + body (int16 positions, uint16 triangles, uint8 part labels) + sim props
  colab_cell.txt                  a Colab cell that unpacks job.tar.gz into /content/job (paste and run)

Body frame for GarmentCode/Warp: metres, Y up from the floor, faces +Z, avatar's left at +X
(the sion kit is metres, Y up, faces -Z, left -X, floor at kit['floor']).
"""
import argparse
import base64
import copy
import io
import json
import math
import sys
import tarfile
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from assets.bodies.body_params import BodyParameters  # noqa: E402
from assets.garment_programs.meta_garment import MetaGarment  # noqa: E402

# Warp's body segmentation labels (assets/bodies/ggg_body_segmentation.json uses the same names)
PARTS = ['body', 'left_arm', 'right_arm', 'left_leg', 'right_leg', 'face_internal']


def part_of(bone):
    if bone.startswith('J_Adj_') and 'Eye' in bone:
        return 'face_internal'
    side = 'left' if '_L_' in bone else 'right' if '_R_' in bone else None
    if side and any(k in bone for k in ('UpperArm', 'LowerArm', 'Hand', 'Thumb', 'Index', 'Middle', 'Ring', 'Little')):
        return f'{side}_arm'
    if side and any(k in bone for k in ('UpperLeg', 'LowerLeg', 'Foot', 'Toe')):
        return f'{side}_leg'
    return 'body'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('name')
    ap.add_argument('--design', required=True)
    ap.add_argument('--body', default=str(ROOT / 'sion_pipeline/kit/sion_female_default.yaml'),
                    help='GarmentCode measurements of the sion body')
    ap.add_argument('--body-kit', default=str(ROOT / 'sion_pipeline/kit/female_apose_body.json'))
    ap.add_argument('--front-extra', type=float, default=0.0,
                    help='cm of extra length in the simple-tee front panels (bust room), as in make_pattern.py')
    ap.add_argument('--sim-props', default=str(ROOT / 'assets/Sim_props/default_sim_props.yaml'))
    a = ap.parse_args()

    out = ROOT / 'sion_pipeline/warp/jobs' / a.name
    out.mkdir(parents=True, exist_ok=True)

    # ---- body, in the GarmentCode/Warp frame
    kit = json.loads(Path(a.body_kit).read_text())
    P = np.asarray(kit['positions'], float).reshape(-1, 3)
    P = np.c_[-P[:, 0], P[:, 1] - kit['floor'], -P[:, 2]]
    T = np.asarray(kit['triangles'], np.int64).reshape(-1, 3)
    labels = np.zeros(len(P), np.uint8)
    for i, g in enumerate(kit['groups']):
        acc = {}
        for bone, w in g:
            acc[part_of(bone)] = acc.get(part_of(bone), 0) + w
        labels[i] = PARTS.index(max(acc, key=acc.get))

    # arm angle below horizontal, from the kit's own A-pose joints (left arm: upper arm -> lower arm)
    J = {j['name']: np.asarray(j['pos']) for j in kit['joints']}
    d = J['J_Bip_L_LowerArm'] - J['J_Bip_L_UpperArm']
    arm_angle = math.degrees(math.atan2(-d[1], math.hypot(d[0], d[2])))

    # ---- pattern, sleeves placed for that arm angle
    design = yaml.safe_load(open(a.design))['design']
    if 'knit' in design:  # stretch-knit panels with a body-shaped side seam (sion_pipeline/knit_panels.py)
        sys.path.insert(0, str(ROOT / 'sion_pipeline'))
        import knit_panels
        knit_panels.install(design)
    if a.front_extra:
        from assets.garment_programs import tee
        base = tee.TorsoFrontHalfPanel

        class FrontWithBustRoom(base):
            def __init__(self, name, body, design):
                design = copy.deepcopy(design)
                design['shirt']['length']['v'] += a.front_extra / body['waist_line']
                super().__init__(name, body, design)

        tee.TorsoFrontHalfPanel = FrontWithBustRoom

    body = BodyParameters(a.body)
    body.params['arm_pose_angle'] = arm_angle
    pattern = MetaGarment(a.name, body, design).assembly()
    folder = Path(pattern.serialize(str(out), to_subfolder=False, with_3d=False, with_text=False, view_ids=False))
    spec = folder / f'{a.name}_specification.json'

    meas = {'body': dict(body.params)}
    meas['body'] = {k: (float(v) if isinstance(v, (int, float, np.floating)) else v) for k, v in meas['body'].items()}

    # ---- pack
    pos_i16 = np.round(P * 10000).astype(np.int16)        # 0.1 mm steps
    assert np.abs(P * 10000).max() < 32767
    buf = io.BytesIO()
    np.savez_compressed(buf, pos=pos_i16, tri=T.astype(np.uint16), labels=labels)

    def add(tf, name, data):
        info = tarfile.TarInfo(name)
        info.size = len(data)
        tf.addfile(info, io.BytesIO(data))

    tbuf = io.BytesIO()
    with tarfile.open(fileobj=tbuf, mode='w:gz') as tf:
        add(tf, 'body.npz', buf.getvalue())
        add(tf, f'{a.name}_specification.json', spec.read_bytes())
        add(tf, 'body_measurements.yaml', yaml.safe_dump(meas).encode())
        add(tf, 'sim_props.yaml', Path(a.sim_props).read_bytes())
        add(tf, 'run_job.py', (Path(__file__).parent / 'run_job.py').read_bytes())
        add(tf, 'job.json', json.dumps({'name': a.name, 'parts': PARTS, 'arm_angle': arm_angle}).encode())
    data = tbuf.getvalue()
    (out / 'job.tar.gz').write_bytes(data)

    b64 = base64.b64encode(data).decode()
    lines = [b64[i:i + 4000] for i in range(0, len(b64), 4000)]
    cell = ("import base64, io, tarfile, shutil, os\nB = '''\n" + '\n'.join(lines) + "\n'''\n"
            "shutil.rmtree('/content/job', ignore_errors=True)\n"
            "tarfile.open(fileobj=io.BytesIO(base64.b64decode(B.replace(chr(10), ''))), mode='r:gz').extractall('/content/job')\n"
            "print(sorted(os.listdir('/content/job')))\n")
    (out / 'colab_cell.txt').write_text(cell)

    counts = {p: int((labels == k).sum()) for k, p in enumerate(PARTS)}
    print(f'{out}: arm angle {arm_angle:.1f} deg, body {len(P)} verts {len(T)} tris, parts {counts}')
    print(f'job.tar.gz {len(data) / 1024:.0f} KB, colab cell {len(cell) / 1024:.0f} KB')


if __name__ == '__main__':
    main()
