"""Explain a drape: follow the garment through every stage and compare it with the body.

    ./.venv/bin/python sion_pipeline/diagnose.py <name> [--tag t] [--gender female]

Reads sion_pipeline/out/<name>/<name>[_tag]_states.npz (written by drape_blender.py) and the body kit.
Prints, in cm above the floor:
  1. room   garment girth (from the pattern) against body girth at each height: where the ease is small or
            negative the cloth cannot sit there and gets stretched or pushed up/down
  2. stages where the hem, shoulder seam and neckline are in the pattern, the start layout, after sewing and
            after settling: shows at which step something moves
  3. stretch which way the cloth is stretched (around the body or along its length), by height
"""
import argparse
import json
from pathlib import Path

import numpy as np
from scipy.spatial import ConvexHull, cKDTree

from measure_body import load, loops

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument('name')
ap.add_argument('--tag', default='')
ap.add_argument('--gender', default='female')
a = ap.parse_args()
stem = a.name + (f'_{a.tag}' if a.tag else '')
S = np.load(HERE / 'out' / a.name / f'{stem}_states.npz')
d, mesh, J = load(a.gender)
FLOOR = d['floor']
to_gc = lambda P: np.c_[-P[:, 0], P[:, 2] - FLOOR, P[:, 1]] * 100
names = [str(n) for n in S['names']]
pan = S['panel']
st = {k: to_gc(S[k]) for k in ('pattern', 'start', 'sewn', 'settled')}
flat = S['flat'] * 100
groups = np.split(S['seam_v'], np.cumsum(S['seam_n'])[:-1])
torso = np.array(['torso' in n for n in names])[pan]
front = np.array(['ftorso' in n for n in names])[pan]
arm_x = abs(J['J_Bip_L_UpperArm'][0]) + 2
V = mesh.vertices
skin = cKDTree(to_gc(S['body'])[:d['bodyVertexCount']] if 'body' in S else V)  # the body as draped (posed)


def body_girth(y):
    """Perimeter of the body at height y as a tape would go round it (convex hull, arms left out)."""
    pts = np.concatenate([L for L in loops(mesh, [0, y, 0]) if L[:, 0].min() < arm_x and L[:, 0].max() > -arm_x] or [np.zeros((0, 3))])
    pts = pts[np.abs(pts[:, 0]) < arm_x][:, [0, 2]]
    return ConvexHull(pts).area if len(pts) > 5 else np.nan


# ---- 1. room: garment girth vs body girth
pat = st['pattern']
print('1. ROOM  (garment girth from the pattern vs body girth; ease = how much bigger the garment is)')
y0, y1 = pat[torso, 1].min(), pat[torso, 1].max()
top = min((pat[g[torso[g]], 1].min() for g in groups if torso[g].any() and (~torso[g]).any()), default=y1)
for y in np.arange(np.ceil(y0), top, 2.0):
    g = 0.0
    for k, n in enumerate(names):
        if 'torso' not in n:
            continue
        row = pat[(pan == k) & (np.abs(pat[:, 1] - y) < 0.6)]
        if len(row):
            g += row[:, 0].max() - row[:, 0].min()
    b = body_girth(y)
    bar = '#' * int(max(0, min(40, (g / b - 1) * 100)))
    print(f'  {y:6.1f}  garment {g:5.1f}  body {b:5.1f}  ease {(g / b - 1) * 100:+5.0f}%  {bar}')


# ---- 2. stages
def hem(k):
    m = (pan == k) & (np.abs(pat[:, 1] - pat[pan == k, 1].min()) < 0.3)
    return m


shoulder = [g for g in groups if {names[pan[v]][-6:] for v in g} >= {'ftorso', 'btorso'} and pat[g, 1].mean() > 128]
shoulder = np.unique(np.concatenate(shoulder)) if shoulder else np.array([], int)
seamed = np.zeros(len(pan), bool)
seamed[S['seam_v']] = True
# neckline: the free top edge of the torso panels (not in a seam, near the top)
edges = {}
for f in S['faces']:
    for i in range(3):
        e = tuple(sorted((f[i], f[(i + 1) % 3])))
        edges[e] = edges.get(e, 0) + 1
border = np.zeros(len(pan), bool)
for (u, v), c in edges.items():
    if c == 1:
        border[[u, v]] = True
neck = border & torso & ~seamed & (pat[:, 1] > pat[torso, 1].max() - 20)
neck_f = neck & front
neck_b = neck & ~front
cf = np.flatnonzero(neck_f)[np.argmin(np.abs(pat[neck_f, 0]))]  # front centre of the neckline
cb = np.flatnonzero(neck_b)[np.argmin(np.abs(pat[neck_b, 0]))]


def ring_len(P):
    """Length of the neck opening: walk its points in order of angle round the neck."""
    q = P[neck][:, [0, 2]]
    c = q.mean(0)
    o = np.argsort(np.arctan2(q[:, 1] - c[1], q[:, 0] - c[0]))
    q = q[o]
    return np.linalg.norm(np.diff(np.r_[q, q[:1]], axis=0), axis=1).sum()


ua = J['J_Bip_L_UpperArm']
band = V[np.abs(V[:, 1] - (ua[1] - 12)) < 0.5]
side = np.abs(band[:, 0]).max()
armpit = V[(np.abs(V[:, 0]) > side + 1) & (np.abs(V[:, 0]) < side + 6) & (V[:, 1] > ua[1] - 20), 1].min()
print(f'\n2. STAGES  (heights in cm above the floor; body armpit {armpit:.1f}, shoulder joint {ua[1]:.1f})')
print(f"  {'':28s}{'pattern':>9s}{'start':>9s}{'sewn':>9s}{'settled':>9s}")
rows = []
for k, n in enumerate(names):
    if 'torso' in n:
        rows.append((f'hem {n}', hem(k)))
sleeve = ~torso
arm_groups = [g for g in groups if torso[g].any() and sleeve[g].any()]
if arm_groups:
    low = min(arm_groups, key=lambda g: pat[g[torso[g]], 1].min())  # underarm: lowest point of the armhole seam
    rows += [('armhole bottom, torso side', low[torso[low]]), ('armhole bottom, sleeve side', low[sleeve[low]])]
rows += [('shoulder seam', shoulder), ('neckline front centre', np.array([cf])), ('neckline back centre', np.array([cb])),
         ('neckline (all)', neck)]
for label, m in rows:
    print(f'  {label:28s}' + ''.join(f'{st[s][m, 1].mean():9.1f}' for s in ('pattern', 'start', 'sewn', 'settled')))
hem_all = np.any([hem(k) for k, n in enumerate(names) if 'torso' in n], axis=0)
for s in ('sewn', 'settled'):
    P = st[s]
    print(f'  {s:8s} shoulder seam to skin {np.median(skin.query(P[shoulder])[0]):.1f} cm, hem to skin '
          f'{np.median(skin.query(P[hem_all])[0]):.1f} cm (medians); neck opening {ring_len(P):.1f} cm round, '
          f'body there {body_girth(P[neck, 1].mean()):.1f} cm')
print(f'  neck opening in the pattern: {sum(np.linalg.norm(flat[u] - flat[v]) for (u, v), c in edges.items() if c == 1 and neck[u] and neck[v]):.1f} cm round')

# ---- 3. stretch direction by height
print('\n3. STRETCH  (median change in length vs the cut pattern; "round" = across the panel, "down" = along it)')
E = np.array([e for e in edges])
fl = flat[E[:, 1]] - flat[E[:, 0]]
down = np.abs(fl[:, 1]) > np.abs(fl[:, 0])
for s in ('start', 'sewn', 'settled'):
    P = st[s]
    strain = np.linalg.norm(P[E[:, 1]] - P[E[:, 0]], axis=1) / np.linalg.norm(fl, axis=1) - 1
    print(f'  {s}:')
    y = P[E[:, 0], 1]
    for part, m0 in (('torso', torso[E[:, 0]]), ('sleeves', ~torso[E[:, 0]])):
        for lo in np.arange(np.floor(y[m0].min() / 5) * 5, y[m0].max(), 5):
            m = m0 & (y >= lo) & (y < lo + 5)
            if m.sum() < 20:
                continue
            r, dn = strain[m & ~down], strain[m & down]
            print(f'    {part:8s} {lo:5.0f}-{lo + 5:<5.0f} round {np.median(r) * 100:+5.1f}% (worst {np.percentile(r, 95) * 100:+4.0f}%)   '
                  f'down {np.median(dn) * 100:+5.1f}% (worst {np.percentile(dn, 95) * 100:+4.0f}%)')
