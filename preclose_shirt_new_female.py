"""Geometrically pre-close the GarmentCode shirt (deterministic alternative to
long-range sewing-spring sim, which proved unstable for 10-30cm gaps).

Method: projected gradient descent on mesh verts.
  - Spring step: each stitch-pair endpoint moves 25% toward the pair midpoint.
  - Fairing: light Laplacian (0.05) on non-seam verts keeps fabric smooth.
  - Guard: torso-ellipse projection pushes any vert inside body+3mm back out,
    so fabric slides AROUND the body into closed seams (like real sewing).
Seam verts: any vert snapped by a stitch pair. Panel outlines/stitch pairing
untouched; only positions relax. Sleeves (already 0.0) barely move.

Input:  export_garmentcode/NewFemaleBlenderShirt/{combined_box.obj, stitches.json}
Output: same files overwritten pre-closed (pairs rewritten at new positions).
"""
import json
from pathlib import Path

import numpy as np

OUT = Path(__file__).parent / 'export_garmentcode' / 'NewFemaleBlenderShirt'

# torso ellipse profile (z_m, front, back, halfwidth) measured from Body mesh
_PROFILE = np.array([
    [1.080, 0.094, 0.040, 0.105],
    [1.140, 0.103, 0.023, 0.085],
    [1.164, 0.106, 0.016, 0.081],
    [1.200, 0.106, 0.019, 0.086],
    [1.250, 0.125, 0.045, 0.102],
    [1.290, 0.139, 0.060, 0.118],
    [1.330, 0.120, 0.069, 0.119],
    [1.380, 0.100, 0.060, 0.100],
    [1.460, 0.090, 0.060, 0.090],
])
_PZ, _PF, _PB, _PHW = _PROFILE.T


def guard(verts):
    """Push verts inside torso ellipse + 3mm back outside (radial, per-z)."""
    z = verts[:, 2]
    f = np.interp(z, _PZ, _PF) + 0.003
    b = np.interp(z, _PZ, _PB) + 0.003
    w = np.interp(z, _PZ, _PHW) + 0.003
    yc = (b - f) / 2.0
    c = (f + b) / 2.0
    xn = verts[:, 0] / w
    yn = (verts[:, 1] - yc) / c
    r2 = xn ** 2 + yn ** 2
    inside = r2 < 1.0
    r = np.sqrt(np.maximum(r2, 1e-12))
    s = 1.0 / r
    verts[inside, 0] = xn[inside] * s[inside] * w[inside]
    verts[inside, 1] = yc[inside] + yn[inside] * s[inside] * c[inside]
    return inside.sum()


def load_obj(path):
    verts, faces = [], []
    with open(path) as fh:
        for line in fh:
            if line.startswith('v '):
                verts.append([float(v) for v in line.split()[1:4]])
            elif line.startswith('f '):
                faces.append([int(v.split('/')[0]) - 1 for v in line.split()[1:4]])
    return np.array(verts), np.array(faces)


def main():
    verts, faces = load_obj(OUT / 'combined_box.obj')
    print(f'loaded {len(verts)} verts, {len(faces)} faces')
    stitches = json.loads((OUT / 'stitches.json').read_text())

    # snap pair endpoints to mesh verts (keep zero-distance pairs: coincident
    # center seams would otherwise snap both ends to the SAME vert, get
    # dropped, and retract under fairing -> slit down front/back center)
    springs = []
    for st in stitches:
        for q1, q2 in st['pairs']:
            a = np.array(q1)
            b = np.array(q2)
            d2a = ((verts - a) ** 2).sum(axis=1)
            i = int(np.argmin(d2a))
            d2b = ((verts - b) ** 2).sum(axis=1)
            d2b[i] = np.inf  # never reuse the same vert for both ends
            j = int(np.argmin(d2b))
            springs.append((i, j))
    # unique
    seen = set()
    uniq = []
    for i, j in springs:
        key = (min(i, j), max(i, j))
        if key not in seen:
            seen.add(key)
            uniq.append((i, j))
    springs = np.array(uniq)
    print(f'{len(springs)} unique springs')
    seam = np.zeros(len(verts), dtype=bool)
    seam[springs[:, 0]] = True
    seam[springs[:, 1]] = True
    print(f'{seam.sum()} seam verts')

    # adjacency for fairing
    adj = [set() for _ in range(len(verts))]
    for a, b, c in faces:
        adj[a] |= {b, c}
        adj[b] |= {a, c}
        adj[c] |= {a, b}
    adj = [np.array(sorted(n)) for n in adj]

    for it in range(400):
        # spring step
        vi = verts[springs[:, 0]]
        vj = verts[springs[:, 1]]
        mid = (vi + vj) / 2.0
        verts[springs[:, 0]] += (mid - vi) * 0.25
        verts[springs[:, 1]] += (mid - vj) * 0.25
        # fair non-seam verts
        if it % 2 == 0:
            for v in np.nonzero(~seam)[0]:
                nb = adj[v]
                if len(nb):
                    verts[v] += (verts[nb].mean(axis=0) - verts[v]) * 0.05
        guard(verts)
        if it % 50 == 0:
            d = np.linalg.norm(verts[springs[:, 0]] - verts[springs[:, 1]], axis=1)
            print(f'  iter {it}: max_gap={d.max()*100:.2f}cm mean={d.mean()*100:.2f}cm')

    d = np.linalg.norm(verts[springs[:, 0]] - verts[springs[:, 1]], axis=1)
    print(f'FINAL: max_gap={d.max()*100:.2f}cm mean={d.mean()*100:.3f}cm')

    # write pre-closed OBJ (same groups as before)
    old_lines = (OUT / 'combined_box.obj').read_text().splitlines()
    with open(OUT / 'combined_box.obj', 'w') as fh:
        vi = 0
        for line in old_lines:
            if line.startswith('v '):
                v = verts[vi]
                vi += 1
                fh.write(f'v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n')
            else:
                fh.write(line + '\n')

    # rewrite pairs at relaxed positions (midpoint for both ends)
    for st in stitches:
        new_pairs = []
        for q1, q2 in st['pairs']:
            a = np.array(q1)
            b = np.array(q2)
            i = int(np.argmin(((verts - a) ** 2).sum(axis=1)))
            j = int(np.argmin(((verts - b) ** 2).sum(axis=1)))
            m = ((verts[i] + verts[j]) / 2.0).tolist()
            new_pairs.append([m, m])
        st['pairs'] = new_pairs
    (OUT / 'stitches.json').write_text(json.dumps(stitches, indent=1))
    print('wrote pre-closed combined_box.obj + stitches.json')


if __name__ == '__main__':
    main()
