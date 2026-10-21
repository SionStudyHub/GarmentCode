"""Measure a sion-avatar body (from export_sion_body.mjs) into a GarmentCode body YAML.

    ./.venv/bin/python sion_pipeline/measure_body.py [female]

Reads  sion_pipeline/kit/<gender>_default_body.json
Writes sion_pipeline/kit/sion_<gender>_default.yaml

Measurements follow docs/Body Measurements GarmentCode.pdf. Everything is measured in GarmentCode's frame:
centimetres, Y up from the floor, front +Z, avatar's left +X (a 180 degree turn about Y from the sion-avatar frame).
"""
import json
import sys
from pathlib import Path

import numpy as np
import trimesh
import yaml
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import ConvexHull, cKDTree

HERE = Path(__file__).resolve().parent
STEP = 0.25  # cm between scan slices


def load(gender):
    d = json.loads((HERE / 'kit' / f'{gender}_default_body.json').read_text())
    P = np.asarray(d['positions'], float).reshape(-1, 3)
    P = np.c_[-P[:, 0], P[:, 1] - d['floor'], -P[:, 2]] * 100
    J = {j['name']: np.array([-j['pos'][0], j['pos'][1] - d['floor'], -j['pos'][2]]) * 100 for j in d['joints']}
    mesh = trimesh.Trimesh(P, np.asarray(d['triangles']).reshape(-1, 3), process=False)
    return d, mesh, J


def loops(mesh, origin, normal=(0, 1, 0)):
    """Cross-section of the mesh as a list of connected point clouds (one per closed loop)."""
    seg = trimesh.intersections.mesh_plane(mesh, np.asarray(normal, float), np.asarray(origin, float))
    if len(seg) == 0:
        return []
    pts = seg.reshape(-1, 3)
    n = len(pts)
    pairs = cKDTree(pts).query_pairs(1e-3, output_type='ndarray')
    i = np.r_[np.arange(0, n, 2), pairs[:, 0]]
    j = np.r_[np.arange(1, n, 2), pairs[:, 1]]
    k, lab = connected_components(coo_matrix((np.ones(len(i)), (i, j)), shape=(n, n)))
    return [pts[lab == c] for c in range(k) if (lab == c).sum() >= 6]


def torso(mesh, y):
    """The horizontal loop at height y that spans the centre line (x = 0), as (x, z) points."""
    best = None
    for L in loops(mesh, [0, y, 0]):
        if L[:, 0].min() < 0 < L[:, 0].max() and (best is None or len(L) > len(best)):
            best = L
    return None if best is None else best[:, [0, 2]]


def hull(pts):
    h = ConvexHull(pts)
    return pts[h.vertices], h.area  # 2D: .area is the perimeter


def chain(poly, a, b, back=True):
    """Length along the closed polygon from vertex a to b, taking the back (-Z) or front (+Z) way round."""
    n = len(poly)
    out = []
    for step in (1, -1):
        idx = [a]
        while idx[-1] != b:
            idx.append((idx[-1] + step) % n)
        p = poly[idx]
        out.append((p[:, 1].mean(), np.linalg.norm(np.diff(p, axis=0), axis=1).sum()))
    out.sort()
    return out[0][1] if back else out[1][1]


def back_arc(pts):
    poly, _ = hull(pts)
    return chain(poly, int(poly[:, 0].argmin()), int(poly[:, 0].argmax()))


def profile_len(pts):
    return float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum())


def tape(prof):
    """Length of a tape laid down the front of a (y, z) profile: its convex hull on the +Z side."""
    lo = prof[:, 1].min() - 50
    h = ConvexHull(np.r_[prof, [[prof[-1, 0], lo], [prof[0, 0], lo]]])
    return profile_len(prof[sorted(v for v in h.vertices if v < len(prof))])


def front_profile(mesh, x, y_top, y_bottom):
    """(y, z) profile down the front of the torso on the vertical lines at +-x, from y_top to y_bottom."""
    prof = []
    for y in np.arange(y_top, y_bottom - STEP / 2, -STEP):
        t = torso(mesh, y)
        band = t[np.abs(np.abs(t[:, 0]) - x) < 1.0]
        if len(band):
            prof.append([y, band[:, 1].max()])
    return np.array(prof)


def main(gender='female'):
    d, mesh, J = load(gender)
    V = mesh.vertices
    j = lambda n: J[f'J_Bip_{n}']
    out, note = {}, {}

    height = V[:, 1].max()
    upper_arm = (j('L_UpperArm') + j('R_UpperArm')) / 2
    out['height'] = height

    # Shoulder top line: above the arms, the horizontal slice is only neck + shoulders, so its half-width w(y)
    # traces the shoulder slope from the shoulder ends up to the neck.
    arm_top = V[(np.abs(V[:, 0]) > j('L_UpperArm')[0] + 3) & (np.abs(V[:, 0]) < j('L_LowerArm')[0])][:, 1].max()
    ys = np.arange(arm_top + 0.3, j('C_Head')[1], STEP)
    half_w = np.array([np.abs(t[:, 0]).max() for t in (torso(mesh, y) for y in ys)])
    i_min = int(np.argmin(half_w))  # narrowest part of the neck, under the jaw
    neck_half = half_w[i_min]
    i_neck = int(np.nonzero(half_w[:i_min] > neck_half + 0.75)[0].max())  # neck base: where the shoulders spread
    y_neck = ys[i_neck]
    nape_y = y_neck

    def shoulder_line(x):
        """Height of the shoulder top line at half-width x."""
        return np.interp(x, half_w[::-1], ys[::-1]) if x > neck_half else y_neck

    # Armpit: the lowest point of the arm right next to the torso side.
    side = np.abs(torso(mesh, upper_arm[1] - 12)[:, 0]).max()
    near = V[(np.abs(V[:, 0]) > side + 1) & (np.abs(V[:, 0]) < side + 6) & (V[:, 1] > upper_arm[1] - 20)]
    armpit_y = near[:, 1].min()

    # Collarbone ends: where the shoulder line meets the arm, taken at the torso side just under the armpit.
    shoulder_half = max(side, abs(j('L_UpperArm')[0]))
    y_end = np.interp(shoulder_half, half_w[::-1], ys[::-1]) if shoulder_half < half_w.max() else ys[0]
    out['shoulder_w'] = 2 * shoulder_half
    out['shoulder_incl'] = np.degrees(np.arctan2(y_neck - y_end, shoulder_half - neck_half))
    out['armscye_depth'] = y_end - armpit_y
    out['head_l'] = height - nape_y

    nb = torso(mesh, y_neck + 1.0)
    out['neck_w'] = back_arc(nb)
    note['neck_half_width'] = neck_half

    # Bust: the most forward point of the chest (off the centre line), between armpit and waist. Breasts stand out
    # past the breastbone somewhere in that band; a flat chest never does, so there the bust points are placed by
    # GarmentCode's male average (m_smpl_average_A40: 17 cm apart, 24.4 cm down the front from the shoulder line at
    # 178.1 cm tall), scaled to this height.
    best, breasts = None, False
    for y in np.arange(armpit_y - 2, armpit_y - 30, -STEP):
        t = torso(mesh, y)
        off = t[np.abs(t[:, 0]) > 3]
        breasts |= off[:, 1].max() > t[np.abs(t[:, 0]) < 1.5][:, 1].max() + 0.5
        if best is None or off[:, 1].max() > best[1]:
            best = (y, off[:, 1].max())
    if breasts:
        bust_y = best[0]
        t = torso(mesh, bust_y)
        lp, rp = t[t[:, 0] > 2], t[t[:, 0] < -2]
        lb, rb = lp[lp[:, 1].argmax()], rp[rp[:, 1].argmax()]
        bust_x = (lb[0] - rb[0]) / 2
        out['bust_points'] = np.linalg.norm(lb - rb)
    else:
        s = height / 178.1
        bust_x = 17 / 2 * s
        prof = front_profile(mesh, bust_x, shoulder_line(bust_x), armpit_y - 30)
        run = np.r_[0, np.cumsum(np.linalg.norm(np.diff(prof, axis=0), axis=1))]
        bust_y = np.interp(24.4 * s, run, prof[:, 0])
        t = torso(mesh, bust_y)
        out['bust_points'] = 2 * bust_x
    note['breasts'] = breasts
    out['bust'] = hull(t)[1]
    out['back_width'] = back_arc(t)
    out['vert_bust_line'] = nape_y - bust_y

    # Waist: narrowest torso girth between the hip joint and the bust.
    ys_w = np.arange(j('C_Hips')[1] + 3, bust_y - 5, STEP)
    girth = [hull(torso(mesh, y))[1] for y in ys_w]
    waist_y = ys_w[int(np.argmin(girth))]
    t = torso(mesh, waist_y)
    out['waist'] = hull(t)[1]
    out['waist_back_width'] = back_arc(t)
    waist_half = np.abs(t[:, 0]).max()

    # Underbust: where the front under the breast is deepest (least forward), just under the bust. A flat chest
    # has only the fold under the chest muscle, a few centimetres down; further down it would find the waist.
    ys_u = np.arange(bust_y - 1, bust_y - (15 if breasts else 6), -STEP)
    front = []
    for y in ys_u:
        t = torso(mesh, y)
        band = t[np.abs(np.abs(t[:, 0]) - bust_x) < 1.5]
        front.append(band[:, 1].max())
    front = np.array(front)
    k = int(np.argmin(front))
    under_y = ys_u[k]
    out['underbust'] = hull(torso(mesh, under_y))[1]

    # Crotch: highest level where the legs are two separate loops.
    crotch_y = None
    for y in np.arange(j('C_Hips')[1], j('L_LowerLeg')[1], -STEP):
        if torso(mesh, y) is None:
            crotch_y = y
            break

    # Hips: widest girth between crotch and waist; bum points are the rearmost points of each cheek.
    ys_h = np.arange(crotch_y + 1, waist_y - 3, STEP)
    girth = [hull(torso(mesh, y))[1] for y in ys_h]
    hip_y = ys_h[int(np.argmax(girth))]
    t = torso(mesh, hip_y)
    out['hips'] = hull(t)[1]
    out['hip_back_width'] = back_arc(t)
    lp, rp = t[t[:, 0] > 2], t[t[:, 0] < -2]
    out['bum_points'] = np.linalg.norm(lp[lp[:, 1].argmin()] - rp[rp[:, 1].argmin()])
    out['hips_line'] = waist_y - hip_y
    out['crotch_hip_diff'] = hip_y - crotch_y
    hip_half = np.abs(t[:, 0]).max()
    out['hip_inclination'] = np.degrees(np.arctan2(hip_half - waist_half, waist_y - hip_y))

    # Thigh: thickest single-leg girth just under the crotch (avatar's left leg, +X).
    leg = []
    for y in np.arange(crotch_y - 0.5, crotch_y - 12, -STEP):
        L = [l for l in loops(mesh, [0, y, 0]) if l[:, 0].mean() > 2]
        if L:
            leg.append(hull(max(L, key=len)[:, [0, 2]])[1])
    out['leg_circ'] = max(leg)

    # Back length: nape to waist down the spine, following the surface.
    prof = []
    for y in np.arange(nape_y, waist_y - 0.5, -1.0):
        t = torso(mesh, y)
        c = t[np.abs(t[:, 0]) < 1.5]
        prof.append([y, c[:, 1].min()])
    out['waist_line'] = profile_len(np.array(prof))

    # Front over the bust, on the vertical line through a bust point: from the shoulder line down to the
    # bust point (bust_line) and on to the waist bridging hollows like a tape (waist_over_bust_line).
    prof = front_profile(mesh, bust_x, shoulder_line(bust_x), waist_y)
    out['bust_line'] = tape(prof[prof[:, 0] >= bust_y - STEP])
    out['waist_over_bust_line'] = tape(prof)

    # Arm: collarbone end to wrist; wrist girth across the forearm at the hand joint.
    end = np.array([shoulder_half, y_end, j('L_UpperArm')[2]])
    out['arm_length'] = np.linalg.norm(j('L_Hand') - end)
    axis = j('L_Hand') - j('L_LowerArm')
    axis /= np.linalg.norm(axis)
    origin = j('L_Hand') - 1.0 * axis
    wr = min(loops(mesh, origin, axis), key=lambda l: np.linalg.norm(l.mean(0) - origin))
    e1 = np.cross(axis, [0, 0, 1.0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(axis, e1)
    out['wrist'] = hull(np.c_[(wr - origin) @ e1, (wr - origin) @ e2])[1]
    arm = j('L_Hand') - j('L_UpperArm')
    out['arm_pose_angle'] = np.degrees(np.arctan2(-arm[1], np.hypot(arm[0], arm[2])))

    levels = dict(nape=nape_y, collarbone_end=y_end, armpit=armpit_y, bust=bust_y, underbust=under_y,
                  waist=waist_y, hips=hip_y, crotch=crotch_y)
    body = {k: round(float(v), 2) for k, v in sorted(out.items())}
    path = HERE / 'kit' / f'sion_{gender}_default.yaml'
    with open(path, 'w') as f:
        f.write(f'# Measured from sion-avatar {gender}-catalog.vrm at the default slider shape by measure_body.py.\n')
        f.write('# Levels (cm above floor): ' + ', '.join(f'{k} {v:.1f}' for k, v in levels.items()) + '\n')
        yaml.safe_dump({'body': body}, f, sort_keys=True)

    ref = yaml.safe_load(open(HERE.parent / 'assets/bodies/mean_female.yaml'))['body']
    s = body['height'] / ref['height']
    print(f'{path}\n{"param":22s} {"sion":>8s} {"mean_female x height":>22s}')
    for k, v in body.items():
        r = ref[k] * (s if k not in ('hip_inclination', 'shoulder_incl', 'arm_pose_angle') else 1)
        print(f'{k:22s} {v:8.2f} {r:22.2f}')
    print('levels', {k: round(float(v), 1) for k, v in levels.items()})


if __name__ == '__main__':
    main(*sys.argv[1:])
