"""Fabric lab tests in Blender, and calibration of the fabric presets in fabrics.json.

    /Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
        --python sion_pipeline/fabric_tests.py -- [--calibrate] [--fabric cotton_jersey ...]

Like Marvelous Designer's fabric library (and CLO's Fabric Kit, which measures real fabric to make a preset), each
preset in fabrics.json describes a real fabric by what you can measure on it, and the Blender cloth settings that
make the simulated cloth behave the same in the same tests:
  stretch   strip hanging from its top edge, gravity x20: how much it lengthens under its own weight
  drape     30 cm circle on an 18 cm round stand (Cusick drape tester): shadow area -> drape coefficient
  bending   strip on a ledge, overhanging (ASTM D1388 cantilever): how far it droops gives the bending length
--calibrate sets each preset's Blender tension from the stretch test, then its bending from the drape test, and
saves them to fabrics.json. Without it, the tests only measure the saved settings.
The test pieces come from fabric_specimens.py (cut and meshed like garments, 1 cm triangles), so the settings
carry over to garments made with make_pattern.py --res 1.0.
Writes sion_pipeline/out/fabrics/<preset>_{drape,bend}.png and <preset>.npz (final cloth shapes).

What the tests showed about Blender cloth on 1 cm triangles (details in FINDINGS.md):
  - Squashing stiffness (compression) set equal to stretch stiffness locks the triangles: cloth can't curve two
    ways at once, which every fold needs, so everything drapes like card. Blender's shear setting does nothing on
    triangles (it only adds springs across quads), and on triangles a low compression is what lets the cloth shear.
    So compression is a small fixed share of tension (tests: compression_ratio), like real cloth, which buckles
    instead of squashing.
  - Bending is set from the drape and not the cantilever: in Blender the two don't agree (cloth with a real
    fabric's bending length drapes far too stiff), and garments are 3D folds. The cantilever result is kept as a
    record of the gap.
  - Firm fabrics (the wovens) would need a tension so high for their weight that the triangles lock again (light
    wovens can't drape softly: chiffon stayed at 0.37-0.45 instead of 0.28) and, for chiffon, the solver stops
    settling. So the stretch test has a floor (tests: min_hang_stretch_pct, 0.5%, about jersey's): in garments
    that is 0.03% stretch under the cloth's own weight, invisible. The cost: pulled tight on the body, wovens
    stretch about like jersey instead of forming tension wrinkles.
  - The drape test gives a different fold pattern from a slightly different start, and the drape coefficient
    varies by about 0.05 between runs, so it is averaged over tests: drape_runs starts.
"""
import argparse
import json
import math
import sys
import time
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument('--fabric', nargs='*', help='presets to test (default: all)')
ap.add_argument('--calibrate', action='store_true', help='adjust the Blender settings to hit the targets and save')
ap.add_argument('--no-render', action='store_true')
ap.add_argument('--sweep', help="e.g. bending=1,3,10,30: measure the first --fabric with each value (renders "
                                "<preset>_<key><value>_drape.png); nothing is saved")
ap.add_argument('--set', default='', help='with --sweep: other settings to change first, e.g. compression=10')
args = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])

LIB_PATH = HERE / 'fabrics.json'
LIB = json.loads(LIB_PATH.read_text())
SPEC = json.loads((HERE / 'kit' / 'fabric_specimens.json').read_text())
OUT = HERE / 'out' / 'fabrics'
OUT.mkdir(parents=True, exist_ok=True)
G = 9.81
T = LIB['tests']

scene = bpy.context.scene
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob)
scene.render.fps = 24


# ---------------------------------------------------------------- the bent strip, in theory (heavy elastica)
def elastica_table():
    """Chord angle (degrees below horizontal, from the ledge edge to the tip) of a uniform strip overhanging by l,
    for lam = (l / c)^3, c = bending length. Solves theta'' = -lam (1 - s) cos(theta), theta(0) = 0, theta'(1) = 0
    by shooting (all lam at once). Peirce's cantilever rule (41.5 degrees when l = 2c) is a check on it."""
    lam = np.logspace(-1, 5, 400)
    lo, hi = np.zeros_like(lam), lam.copy()
    n = 400
    h = 1.0 / n

    def shoot(p):
        th, om, x, y = np.zeros_like(lam), p.copy(), np.zeros_like(lam), np.zeros_like(lam)
        for i in range(n):
            s = i * h
            f = lambda s_, th_, om_: (om_, -lam * (1 - s_) * np.cos(th_))
            k1 = f(s, th, om)
            k2 = f(s + h / 2, th + h / 2 * k1[0], om + h / 2 * k1[1])
            k3 = f(s + h / 2, th + h / 2 * k2[0], om + h / 2 * k2[1])
            k4 = f(s + h, th + h * k3[0], om + h * k3[1])
            th_new = th + h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
            x += h * np.cos((th + th_new) / 2)
            y += h * np.sin((th + th_new) / 2)
            om = om + h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
            th = th_new
        return om, x, y

    for _ in range(45):
        mid = (lo + hi) / 2
        om, _, _ = shoot(mid)
        lo, hi = np.where(om < 0, mid, lo), np.where(om < 0, hi, mid)
    _, x, y = shoot((lo + hi) / 2)
    return lam, np.degrees(np.arctan2(y, x))


LAM, CHORD = elastica_table()
print(f'elastica check: chord angle at l = 2c is {np.interp(8.0, LAM, CHORD):.1f} degrees (Peirce: 41.5)')


def bending_length(l_cm, chord_deg):
    """Bending length (cm) of a strip overhanging l_cm whose tip hangs chord_deg below the ledge edge."""
    lam = np.exp(np.interp(chord_deg, CHORD, np.log(LAM)))
    return l_cm / lam ** (1 / 3)


# ---------------------------------------------------------------- Blender cloth
def mesh_object(name, co, faces, pin=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(co.tolist(), [], faces.tolist())
    me.validate()
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    if pin is not None:
        g = ob.vertex_groups.new(name='pin')
        g.add([int(i) for i in np.flatnonzero(pin)], 1.0, 'REPLACE')
    return ob


def cloth(ob, b, gravity=1.0, self_collision=False, frames=400):
    """Blender cloth with a preset's settings (b = preset['blender']); same solver settings as drape_blender.py."""
    m = ob.modifiers.new('Cloth', 'CLOTH')
    cs, cc = m.settings, m.collision_settings
    cs.quality = 10
    cs.mass = b['mass']
    cs.air_damping = T['air']
    cs.tension_stiffness = b['tension']
    cs.compression_stiffness = b.get('compression', b['tension'])
    cs.shear_stiffness = b['shear']
    cs.bending_stiffness = b['bending']
    cs.tension_damping = cs.compression_damping = cs.shear_damping = b['damping']
    cs.bending_damping = 0.5
    cs.effector_weights.gravity = gravity
    if 'pin' in ob.vertex_groups:
        cs.vertex_group_mass = 'pin'
    cc.use_collision = True
    cc.distance_min = b['collision_distance']
    cc.collision_quality = 4
    cc.use_self_collision = self_collision
    cc.self_distance_min = b['collision_distance']
    m.point_cache.frame_start, m.point_cache.frame_end = 1, frames
    scene.frame_start, scene.frame_end = 1, frames
    return m


def positions(ob):
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    me = ev.to_mesh()
    co = np.zeros(len(me.vertices) * 3)
    me.vertices.foreach_get('co', co)
    ev.to_mesh_clear()
    return co.reshape(-1, 3)


def run_until_still(ob, frames=400, still_mm=0.05, check=10, min_frames=40):
    """Step the simulation until no point moves more than still_mm per frame (averaged over `check` frames)."""
    P0 = positions(ob)
    for f in range(1, frames + 1):
        scene.frame_set(f)
        if f % check == 0:
            P = positions(ob)
            move = np.abs(P - P0).max() * 1000 / check
            P0 = P
            if f >= min_frames and move < still_mm:
                return P, f
    return P0, frames


def clear_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    for me in list(bpy.data.meshes):
        bpy.data.meshes.remove(me)


def box(name, lo, hi):
    lo, hi = np.asarray(lo), np.asarray(hi)
    c = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    f = np.array([[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]])
    me = bpy.data.meshes.new(name)
    me.from_pydata(c.tolist(), [], f.tolist())
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    return ob


# ---------------------------------------------------------------- the three tests
def strip_mesh():
    v = np.asarray(SPEC['strip']['v2d']) / 100  # metres; x along the strip (0..0.30), y across (0..0.05)
    return v, np.asarray(SPEC['strip']['faces'])


def bend_test(b, overhang_cm):
    """Strip lying on a ledge (top at z = 0, edge at x = 0), sticking out by overhang_cm; the part more than 1 cm
    behind the edge is held down. Returns bending length (cm), chord angle, final points."""
    clear_scene()
    v, f = strip_mesh()
    L = v[:, 0].max()
    x = v[:, 0] - (L - overhang_cm / 100)
    lift = b['collision_distance'] + 0.001
    co = np.c_[x, v[:, 1] - v[:, 1].mean(), np.full(len(v), lift)]
    ob = mesh_object('strip', co, f, pin=x < -0.01)
    ledge = box('ledge', (-0.4, -0.1, -0.05), (0, 0.1, 0))
    ledge.modifiers.new('Collision', 'COLLISION')
    ledge.collision.thickness_outer = 0.001
    ledge.collision.cloth_friction = 5
    cloth(ob, b)
    P, frames = run_until_still(ob)
    tip = P[v[:, 0] > L - 0.004]
    dx, dz = tip[:, 0].mean(), lift - tip[:, 2].mean()
    chord = math.degrees(math.atan2(dz, dx))
    return bending_length(overhang_cm, chord), chord, P, frames


def hang_test(b):
    """Strip hanging from its top edge with gravity times T['hang_g']: the average lengthening of the strip in %.
    Under its own weight the strain grows from 0 at the bottom to most at the top, so the average strain is
    w * g' * L / (2 E): the test measures the fabric's tensile stiffness E against its weight w (the gravity is
    raised so the stretch of stiff fabrics is large enough to measure)."""
    clear_scene()
    v, f = strip_mesh()
    co = np.c_[v[:, 1] - v[:, 1].mean(), np.zeros(len(v)), -v[:, 0]]  # top edge at z = 0, hanging down
    ob = mesh_object('strip', co, f, pin=v[:, 0] < 0.002)
    cloth(ob, b, gravity=T['hang_g'])
    P, frames = run_until_still(ob, still_mm=0.01)
    bottom = v[:, 0] > v[:, 0].max() - 0.002
    stretch = (-P[bottom][:, 2].mean()) / v[:, 0].max() - 1
    return stretch * 100, P, frames


def drape_test(b, seed=0):
    """30 cm circle clamped on an 18 cm stand (Cusick): drape coefficient = (shadow - stand) / (circle - stand),
    1 = stays flat as a disc, 0 = hangs straight down; and the number of folds (nodes)."""
    clear_scene()
    v = np.asarray(SPEC['disc']['v2d']) / 100
    f = np.asarray(SPEC['disc']['faces'])
    r_stand, r_disc = T['drape_stand_cm'] / 200, np.linalg.norm(v, axis=1).max()
    co = np.c_[v, np.zeros(len(v))]
    if seed:  # a different start (0.3 mm bumps) gives a different set of folds: average a few for a steady number
        co[:, 2] = np.random.default_rng(seed).normal(0, 0.0003, len(v))
    ob = mesh_object('disc', co, f, pin=np.linalg.norm(v, axis=1) < r_stand)
    cloth(ob, b, self_collision=True)
    P, frames = run_until_still(ob, frames=480)
    # shadow: the furthest the cloth reaches in each direction, from the outline (boundary edges, finely resampled)
    edges = {}
    for t in f:
        for i in range(3):
            e = tuple(sorted((t[i], t[(i + 1) % 3])))
            edges[e] = edges.get(e, 0) + 1
    bnd = np.array([e for e, n in edges.items() if n == 1])
    s = np.linspace(0, 1, 12)[:, None, None]
    pts = (P[bnd[:, 0], :2][None] * (1 - s) + P[bnd[:, 1], :2][None] * s).reshape(-1, 2)
    pts = np.r_[pts, P[:, :2]]
    ang = np.arctan2(pts[:, 1], pts[:, 0])
    rad = np.linalg.norm(pts, axis=1)
    nb = 720
    k = ((ang + np.pi) / (2 * np.pi) * nb).astype(int) % nb
    rmax = np.full(nb, np.nan)
    np.fmax.at(rmax, k, rad)
    ok = ~np.isnan(rmax)
    th = np.arange(nb)
    rmax = np.interp(th, th[ok], rmax[ok], period=nb)
    shadow = 0.5 * (rmax ** 2).sum() * (2 * np.pi / nb)
    a_stand, a_disc = math.pi * r_stand ** 2, math.pi * r_disc ** 2
    dc = (shadow - a_stand) / (a_disc - a_stand)
    sm = np.convolve(np.r_[rmax[-15:], rmax, rmax[:15]], np.ones(31) / 31, mode='valid')
    peaks = int(((sm > np.roll(sm, 1)) & (sm >= np.roll(sm, -1)) & (sm > np.median(sm))).sum())
    return dc, peaks, P, frames, rmax


# ---------------------------------------------------------------- previews
def render(name, P, faces, eye, target, ortho, extra=()):
    clear_scene()
    ob = mesh_object('cloth', P, faces)
    for poly in ob.data.polygons:
        poly.use_smooth = True
    mat = bpy.data.materials.get('fab') or bpy.data.materials.new('fab')
    mat.diffuse_color = (0.25, 0.45, 0.85, 1)
    ob.data.materials.append(mat)
    for e in extra:
        e()
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'MATERIAL'
    scene.display.shading.show_cavity = True
    scene.render.resolution_x = scene.render.resolution_y = 500
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam'))
    scene.collection.objects.link(cam)
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = ortho
    cam.location = eye
    d = np.asarray(target) - np.asarray(eye)
    cam.rotation_euler = (math.atan2(math.hypot(d[0], d[1]), -d[2]), 0, math.atan2(d[1], d[0]) - math.pi / 2)
    scene.camera = cam
    scene.render.filepath = str(OUT / f'{name}.png')
    bpy.ops.render.render(write_still=True)


def stand():
    me = bpy.data.meshes.new('stand')
    n, r = 48, T['drape_stand_cm'] / 200 - 0.002
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    top = np.c_[r * np.cos(a), r * np.sin(a), np.full(n, -0.004)]
    bot = np.c_[r * np.cos(a), r * np.sin(a), np.full(n, -0.14)]
    me.from_pydata(np.r_[top, bot].tolist(), [], [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)] +
                   [list(range(n))[::-1]])
    ob = bpy.data.objects.new('stand', me)
    scene.collection.objects.link(ob)
    mat = bpy.data.materials.new('grey')
    mat.diffuse_color = (0.6, 0.6, 0.6, 1)
    ob.data.materials.append(mat)


def ledge():
    ob = box('ledge', (-0.4, -0.04, -0.06), (0, 0.04, 0))
    mat = bpy.data.materials.new('grey')
    mat.diffuse_color = (0.6, 0.6, 0.6, 1)
    ob.data.materials.append(mat)


# ---------------------------------------------------------------- run
def drape_avg(b):
    """Drape test from T['drape_runs'] slightly different starts: mean drape coefficient, each run's, and the
    first run's folds, shape and frames."""
    runs = [drape_test(b, seed) for seed in range(T['drape_runs'])]
    return float(np.mean([r[0] for r in runs])), [round(float(r[0]), 3) for r in runs], runs[0][1], runs[0][2], runs[0][3]


def measure(name, b, phys, renders=True):
    t0 = time.time()
    oh = overhang(phys)
    c, chord, Pb, fb = bend_test(b, oh)
    s, Ph, fh = hang_test(b)
    dc, dcs, nodes, Pd, fd = drape_avg(b)
    res = {'stretch_pct': round(s, 3), 'drape_coefficient': round(dc, 3), 'drape_runs': dcs, 'drape_folds': nodes,
           'bending_length_cm': round(c, 2), 'cantilever_overhang_cm': oh, 'cantilever_chord_deg': round(chord, 1)}
    print(f'  {name}: stretch {s:.3f}% (target {target_stretch(phys):.3f}), drape {dc:.2f} {dcs} with {nodes} folds '
          f'(target {phys["drape_coefficient"]}), bending length {c:.2f} cm (real fabric {phys["bending_length_cm"]}); '
          f'{fb}/{fh}/{fd} frames, {time.time() - t0:.0f} s', flush=True)
    np.savez_compressed(OUT / f'{name}.npz', bend=Pb, hang=Ph, drape=Pd)
    if renders and not args.no_render:
        fs, fd_ = np.asarray(SPEC['strip']['faces']), np.asarray(SPEC['disc']['faces'])
        render(f'{name}_drape', Pd, fd_, (0.0, -0.6, 0.45), (0, 0, -0.05), 0.36, [stand])
        render(f'{name}_bend', Pb, fs, (0.03, -1.0, -0.05), (0.03, 0, -0.05), 0.16, [ledge])
    return res


def overhang(phys):
    """Cantilever overhang: twice the target bending length (Peirce's 41.5 degree point), at least 4 cm so the
    strip spans several 1 cm triangles."""
    return float(np.clip(round(2 * phys['bending_length_cm']), 4, 20))


def target_stretch(phys):
    """Average stretch (%) the real fabric would show in the hanging-strip test: its tensile stiffness E (N/m) is
    T['ref_load_n_per_cm'] per cm of width over phys['stretch_pct'] %, its weight w = g/m2 * g. Not below
    T['min_hang_stretch_pct'] (see the top of this file)."""
    E = T['ref_load_n_per_cm'] * 100 / (phys['stretch_pct'] / 100)
    w = phys['weight_gsm'] / 1000 * G
    L = np.asarray(SPEC['strip']['v2d'])[:, 0].max() / 100
    return max(100 * T['hang_g'] * w * L / (2 * E), T['min_hang_stretch_pct'])


def calibrate(name, p):
    b, phys = p['blender'], p['physical']
    b['mass'] = round(phys['weight_gsm'] * LIB['mass_per_gsm'], 5)
    b['collision_distance'] = round(max(T['min_collision_distance'], phys['thickness_mm'] / 1000), 4)
    b['friction'] = phys['friction']
    # 1. tension from the stretch test (compression follows tension, and a softer compression lets the strip
    #    narrow and so lengthen more, hence the loop)
    tgt = target_stretch(phys)
    for it in range(8):
        b['compression'] = b['shear'] = round(b['tension'] * T['compression_ratio'], 4)
        s, _, _ = hang_test(b)
        err = s / tgt - 1
        print(f'  {name} tension {b["tension"]:9.2f}: stretch {s:.3f}% ({err * 100:+.0f}% off {tgt:.3f}%)', flush=True)
        if abs(err) < 0.04:
            break
        b['tension'] = round(float(np.clip(b['tension'] * s / tgt, 1, 50000)), 3)
    # 2. bending from the drape coefficient: double or halve until the target is between two settings, then
    #    halve the gap (in log steps). Drape only depends on bending / weight, so the start is per kg of vertex mass,
    #    scaled from jersey (about 400 per kg for a 1.7 cm bending length).
    tgt = phys['drape_coefficient']
    lo_k, hi_k = 10 * b['mass'], 30000 * b['mass']
    seen = {}

    def dc_at(k):
        k = round(float(k), 4)
        if k not in seen:
            seen[k] = drape_avg(dict(b, bending=k))
            print(f'  {name} bending {k:10.3f} ({k / b["mass"]:6.0f}/kg): drape {seen[k][0]:.3f} {seen[k][1]} '
                  f'(target {tgt})', flush=True)
        return seen[k][0]

    k = b['bending'] if p.get('calibrated') else 400 * b['mass'] * (phys['bending_length_cm'] / 1.7) ** 2.4
    lo = hi = None
    for _ in range(10):
        if dc_at(k) < tgt:
            lo = k
            if hi is None:
                k = k * 2
        else:
            hi = k
            if lo is None:
                k = k / 2
        if (lo is not None and hi is not None) or not lo_k <= k <= hi_k:
            break
    if lo is None or hi is None:
        b['bending'] = round(float(np.clip(k, lo_k, hi_k)), 4)
        p['note'] = f'drape target {tgt} out of reach: drape {dc_at(b["bending"]):.2f} at the bending limit'
        print(f'  {name}: {p["note"]}')
        return
    for _ in range(5):
        if min(abs(dc_at(lo) - tgt), abs(dc_at(hi) - tgt)) < 0.02:
            break
        k = math.sqrt(lo * hi)
        if dc_at(k) < tgt:
            lo = k
        else:
            hi = k
    dl, dh = dc_at(lo), dc_at(hi)
    t = float(np.clip((tgt - dl) / (dh - dl), 0, 1)) if dh > dl else 0.5
    b['bending'] = round(math.exp(math.log(lo) + t * (math.log(hi) - math.log(lo))), 4)
    p.pop('note', None)


if args.sweep:
    key, vals = args.sweep.split('=')
    name = args.fabric[0]
    p = LIB['presets'][name]
    base = dict(p['blender'], **{k: float(v) for k, v in (kv.split('=') for kv in args.set.split(',') if kv)})
    for v in vals.split(','):
        measure(f'{name}_{key}{v}', dict(base, **{key: float(v)}), p['physical'])
    sys.exit(0)

names = args.fabric or list(LIB['presets'])
for name in names:
    p = LIB['presets'][name]
    print(f'== {name}: {p["label"]}', flush=True)
    if args.calibrate:
        calibrate(name, p)
    p['measured'] = measure(name, p['blender'], p['physical'])
    if args.calibrate:
        p['calibrated'] = time.strftime('%Y-%m-%d') + f", Blender {bpy.app.version_string}, res {SPEC['res']} cm"
        LIB_PATH.write_text(json.dumps(LIB, indent=2) + '\n')
print('done')
