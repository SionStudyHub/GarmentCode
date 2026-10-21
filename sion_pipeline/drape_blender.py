"""Drape a GarmentCode garment on a sion-avatar body in Blender (no window) and export it as a rigged GLB.

    /Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
        --python sion_pipeline/drape_blender.py -- <name> [--fabric cotton_jersey] [--gender female] [--pose a] [--no-sim]

Reads  sion_pipeline/kit/<gender>_default_body.json      (export_sion_body.mjs; with --pose a, <gender>_apose_body.json)
       sion_pipeline/out/<name>/<name>_panels.json         (make_pattern.py)
       sion_pipeline/fabrics.json                          fabric presets (cloth settings from fabric_tests.py)
Writes sion_pipeline/out/<name>/<name>.glb                 garment skinned to the avatar's J_Bip_* skeleton
       sion_pipeline/out/<name>/<name>_draped.blend        scene for inspection
       sion_pipeline/out/<name>/<name>_{start,front,side,back}.png   previews

How it drapes (like Marvelous Designer's arrangement + sewing):
  1. Each flat panel is wrapped around a cylinder outside the body: torso panels around the torso from their
     centre line, sleeve panels around their arm from their top seam (sleeves start a little down the arm).
  2. Seam points that sew together get a sewing spring (a loose edge) and are pulled shut with gravity off;
     the flat pattern is the cloth's rest shape, so panel sizes come from the pattern, not the wrap.
     (Blender 5.1 ignores the cloth "rest shape key" setting: the cloth would keep whatever stretch the wrap
     gave it. So the cloth uses "dynamic mesh", which re-reads the natural size from the input mesh every
     step, and the input mesh switches from the wrap (frame 1, where the sim starts) to the flat pattern.)
  3. Gravity comes on, the cloth settles on the body (collision), then seam points are welded.
With --pose a the body stands in the fitting app's A-pose (arms about 46 degrees down) and the GLB's skeleton is
that A-pose, so the fitting app's importer (--pose a) rigs it and takes it back to the rest pose itself.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Vector, kdtree
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument('name')
ap.add_argument('--gender', default='female')
ap.add_argument('--frames', type=int, default=60, help='frames to settle under gravity')
ap.add_argument('--sew-frames', type=int, default=150, help='most frames to close the seams (gravity off)')
ap.add_argument('--sewing-force', type=float, default=0.0,
                help='max sewing spring force (0 = unlimited; 10 left a 17 mm gap under the arm in the A-pose)')
ap.add_argument('--fabric', default='cotton_jersey', help='fabric preset from fabrics.json')
ap.add_argument('--bending', type=float, default=None, help="test only: override the fabric's bending stiffness")
ap.add_argument('--mass', type=float, default=None, help="test only: override the fabric's kg per vertex")
ap.add_argument('--friction', type=float, default=None, help="test only: override the fabric's friction on the body")
ap.add_argument('--compression', type=float, default=None, help="test only: override the fabric's compression stiffness")
ap.add_argument('--sew-gravity', type=float, default=0.0, help='gravity while the seams close (1 = full)')
ap.add_argument('--tag', default='', help='suffix for output files, to compare variants')
ap.add_argument('--no-sim', action='store_true', help='only build the start layout and preview it')
ap.add_argument('--clearance', type=float, default=1.5, help='cm between body and start layout')
ap.add_argument('--sleeve-shift', type=float, default=1.0, help='cm the sleeves start down the arm')
ap.add_argument('--pose', choices=['t', 'a'], default='t',
                help="a: drape on the fitting app's A-pose body and export in that pose (import with --pose a); "
                     'make the pattern with --arm-angle 46')
ap.add_argument('--arm-angle', type=float, default=None,
                help='drape with the arms lowered to this many degrees below horizontal (A-pose), then turn the '
                     'garment back to the rest T-pose for export; make the pattern with the same --arm-angle')
ap.add_argument('--wrap-rest', action='store_true',
                help='old behaviour, for comparison: the cloth keeps the wrapped start layout as its natural size')
ap.add_argument('--free-relax', type=int, default=0,
                help='diagnosis only: after settling, run this many frames with no body and no gravity and save the '
                     'result as "free" in the states file (shows the stretch the cut pieces cannot sew out of)')
args = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])

FABRIC = json.loads((HERE / 'fabrics.json').read_text())['presets'][args.fabric]
CLOTH = dict(FABRIC['blender'], **{k: v for k, v in (('bending', args.bending), ('mass', args.mass),
                                                     ('friction', args.friction), ('compression', args.compression))
                                    if v is not None})
print(f"fabric: {args.fabric} ({FABRIC['label']}){'' if FABRIC.get('calibrated') else ', NOT CALIBRATED'}: {CLOTH}")
OUT = HERE / 'out' / args.name
STEM = args.name + (f'_{args.tag}' if args.tag else '')
if args.pose == 'a' and args.arm_angle is not None:
    sys.exit('--pose a already lowers the arms; leave out --arm-angle')
body = json.loads((HERE / 'kit' / f"{args.gender}_{'apose' if args.pose == 'a' else 'default'}_body.json").read_text())
pat = json.loads((OUT / f'{args.name}_panels.json').read_text())
FLOOR = body['floor']

# Frames: sion (metres, Y up, faces -Z, left -X); GarmentCode (cm, Y up from floor, faces +Z, left +X);
# Blender (metres, Z up, faces +Y, left -X). The glTF exporter turns Blender back into the sion frame.
def sion_to_blender(P):
    P = np.asarray(P, float).reshape(-1, 3)
    return np.c_[P[:, 0], -P[:, 2], P[:, 1]]


def gc_to_blender(P):
    P = np.asarray(P, float).reshape(-1, 3) / 100
    return np.c_[-P[:, 0], P[:, 2], P[:, 1] + FLOOR]


def sion_to_gc(P):
    P = np.asarray(P, float).reshape(-1, 3)
    return np.c_[-P[:, 0], P[:, 1] - FLOOR, -P[:, 2]] * 100


def blender_to_sion(P):
    P = np.asarray(P, float).reshape(-1, 3)
    return np.c_[P[:, 0], P[:, 2], -P[:, 1]]


# Arms-down drape: rotate each arm's joints about the shoulder (UpperArm) joint and skin the body to it, the way the
# fitting app poses bodies (linear blend skinning). ARM[side] = (joints that move, rotation, pivot), Blender frame.
REST_JOINT = {j['name']: sion_to_blender(j['pos'])[0] for j in body['joints']}
ARM = {}


def subtree(root):
    out = {root}
    for _ in body['joints']:
        out |= {j['name'] for j in body['joints'] if j['parent'] in out}
    return out


def arm_weights(groups):
    """Share of each point's skin weight on each arm (arrays, by side)."""
    return {L: np.array([sum(x for n, x in g if n in ARM[L][0]) / max(sum(x for _, x in g), 1e-9) for g in groups])
            for L in ARM}


def pose_points(P, w, inverse=False):
    """Skin points (Blender frame) with the arm rotations, or undo it (per point, the inverse of its blended
    transform)."""
    M = np.tile(np.eye(4), (len(P), 1, 1)) * (1 - sum(w.values()))[:, None, None]
    for L, (_, R, c) in ARM.items():
        A = np.eye(4)
        A[:3, :3], A[:3, 3] = R, c - R @ c
        M += w[L][:, None, None] * A
    if inverse:
        M = np.linalg.inv(M)
    return np.einsum('nij,nj->ni', M[:, :3, :3], P) + M[:, :3, 3]


if args.arm_angle is not None:
    th = math.radians(args.arm_angle)
    for L in 'LR':
        ua, hand = REST_JOINT[f'J_Bip_{L}_UpperArm'], REST_JOINT[f'J_Bip_{L}_Hand']
        target = Vector((math.copysign(math.cos(th), hand[0] - ua[0]), 0.0, -math.sin(th)))
        R = np.array(Vector(hand - ua).normalized().rotation_difference(target).to_matrix())
        ARM[L] = (subtree(f'J_Bip_{L}_UpperArm'), R, ua)
    posed = pose_points(sion_to_blender(body['positions']), arm_weights(body['groups']))
    body['positions'] = blender_to_sion(posed).ravel().tolist()
    for j in body['joints']:
        for L, (moving, R, c) in ARM.items():
            if j['name'] in moving:
                j['pos'] = blender_to_sion(R @ (REST_JOINT[j['name']] - c) + c)[0].tolist()
    print(f'posed the arms {args.arm_angle:.0f} degrees below horizontal')

BODY_GC = sion_to_gc(body['positions'])[:body['bodyVertexCount']]
ARM_SHARE = np.zeros(body['bodyVertexCount'])
for i, g in enumerate(body['groups'][:body['bodyVertexCount']]):
    ARM_SHARE[i] = sum(x for n, x in g if 'Arm' in n or 'Hand' in n or any(f in n for f in ('Thumb', 'Index', 'Middle', 'Ring', 'Little')))
JOINT = {j['name']: sion_to_gc(j['pos'])[0] for j in body['joints']}
unit = lambda v: v / np.linalg.norm(v)


# ---------------------------------------------------------------- start layout (GarmentCode frame, cm)
def torso_layout(panels, clr):
    """Wrap torso panels around the torso on elliptic rings that follow the body's width and depth at each height
    (plus clearance): front panels from the front centre line, back panels from the back centre line."""
    V = BODY_GC[ARM_SHARE < 0.5]  # trunk only: whatever the arm pose, the arms are not part of the torso rings
    ua = JOINT['J_Bip_L_UpperArm']
    band = V[np.abs(V[:, 1] - (ua[1] - 12)) < 0.5]
    side = np.abs(band[:, 0]).max()
    A_ = BODY_GC[ARM_SHARE >= 0.5]
    near = A_[(np.abs(A_[:, 0]) > side + 1) & (np.abs(A_[:, 0]) < side + 6) & (A_[:, 1] > ua[1] - 20)]
    armpit = near[:, 1].min()
    ys = np.concatenate([np.asarray(p['v3d'])[:, 1] for p in panels])
    grid = np.arange(ys.min() - 2, ys.max() + 3)
    trunk = V[(V[:, 1] < armpit - 0.5) | (np.abs(V[:, 0]) < abs(ua[0]) + 2)]  # above the armpit, leave out the arms
    A, B, Z = [], [], []
    for y in grid:
        b = trunk[np.abs(trunk[:, 1] - y) < 1.0]
        if not len(b):  # above the body (neck/head): keep the last ring
            A.append(A[-1]), B.append(B[-1]), Z.append(Z[-1])
            continue
        A.append(np.abs(b[:, 0]).max()), B.append((b[:, 2].max() - b[:, 2].min()) / 2), Z.append((b[:, 2].max() + b[:, 2].min()) / 2)
    smooth = lambda x: np.convolve(np.pad(np.asarray(x, float), 3, mode='edge'), np.ones(7) / 7, mode='valid')
    A, B, Z = smooth(A) + clr, smooth(B) + clr, smooth(Z)
    girth = np.zeros(len(grid))
    for p in panels:
        v = np.asarray(p['v3d'])
        for k, y in enumerate(grid):
            row = v[np.abs(v[:, 1] - y) < 0.75]
            if len(row):
                girth[k] += row[:, 0].max() - row[:, 0].min()
    th = np.linspace(-np.pi, np.pi, 721)
    arcs = []
    for k in range(len(grid)):
        pe = 2 * np.pi * np.sqrt((A[k] ** 2 + B[k] ** 2) / 2)
        if girth[k] > pe:  # the garment is bigger than the ring: grow the ring so the panels fit around it
            A[k] *= girth[k] / pe
            B[k] *= girth[k] / pe
        seg = np.hypot(np.diff(A[k] * np.sin(th)), np.diff(B[k] * np.cos(th)))
        arc = np.r_[0, np.cumsum(seg)]
        arcs.append(arc - np.interp(0, th, arc))  # arc length from the front centre, signed toward +X
    out = {}
    for p in panels:
        v = np.asarray(p['v3d'])
        s = np.sign(p['normal'][2])
        res = np.zeros_like(v)
        for i, (x, y, _) in enumerate(v):
            k = int(np.clip(np.searchsorted(grid, y), 1, len(grid) - 1))
            w = (y - grid[k - 1]) / (grid[k] - grid[k - 1])
            t = (1 - w) * np.interp(x, arcs[k - 1], th) + w * np.interp(x, arcs[k], th)
            a_, b_, z_ = [(1 - w) * q[k - 1] + w * q[k] for q in (A, B, Z)]
            res[i] = [a_ * np.sin(t), y, z_ + s * b_ * np.cos(t)]
        out[p['name']] = res
    return out, dict(armpit=armpit, half_width=(A.min(), A.max()), half_depth=(B.min(), B.max()))


def sleeve_layout(panels, side, clr, shift):
    """Wrap one arm's sleeve panels around the arm, from their top seam: front panels over the front, back
    panels over the back, so their bottom (underarm) edges meet under the arm."""
    L = 'L' if side == 'left' else 'R'
    ua, hand = JOINT[f'J_Bip_{L}_UpperArm'], JOINT[f'J_Bip_{L}_Hand']
    a = unit(hand - ua)
    up = unit(np.array([0, 1.0, 0]) - a[1] * a)
    fwd = unit(np.array([0, 0, 1.0]) - a[2] * a - (np.array([0, 0, 1.0]) @ up) * up)
    rel = BODY_GC - ua
    t_b = rel @ a
    d_b = np.linalg.norm(rel - np.outer(t_b, a), axis=1)
    arm = (t_b > 2) & (d_b < 9)
    grid = np.arange(-2, np.linalg.norm(hand - ua) + 1)
    r_body = np.array([d_b[arm & (np.abs(t_b - t) < 1)].max() if (arm & (np.abs(t_b - t) < 1)).any() else 0 for t in grid])
    r_body[grid < 3] = r_body[grid >= 3][0]
    tops, widths = {}, np.zeros_like(grid)
    for p in panels:
        rv = np.asarray(p['v3d']) - ua
        t, v = rv @ a, rv @ up
        top = np.full(len(grid), np.nan)
        for k, g in enumerate(grid):
            m = np.abs(t - g) < 0.75
            if m.any():
                top[k] = v[m].max()
                widths[k] += v[m].max() - v[m].min()
        ok = ~np.isnan(top)
        tops[p['name']] = (t, v, np.interp(grid, grid[ok], top[ok]))
    r_body = np.convolve(np.pad(r_body, 3, mode='edge'), np.ones(7) / 7, mode='valid')
    R = np.maximum(r_body + clr, widths / (2 * np.pi))
    out = {}
    for p in panels:
        t, v, top = tops[p['name']]
        r = np.interp(t + shift, grid, R)
        psi = (np.interp(t, grid, top) - v) / r
        n = fwd if p['normal'][2] > 0 else -fwd
        out[p['name']] = ua + np.outer(t + shift, a) + (r * np.cos(psi))[:, None] * up + (r * np.sin(psi))[:, None] * n
    return out, dict(R=(R[grid > 0].min(), R.max()))


panels = pat['panels']
layout, info = torso_layout([p for p in panels if 'sleeve' not in p['name']], args.clearance)
for side in ('left', 'right'):
    sl = [p for p in panels if 'sleeve' in p['name'] and p['name'].startswith(side)]
    if sl:
        lay, arm = sleeve_layout(sl, side, args.clearance, args.sleeve_shift)
        info[f'{side}_arm_R'] = arm['R']
        layout.update(lay)
BVH = BVHTree.FromPolygons(sion_to_blender(body['positions']).tolist(), np.asarray(body['triangles']).reshape(-1, 3).tolist())


def clear_of_body(P, clr):
    """Move points (Blender frame, metres) that are inside the body or closer than clr to it out along the normal."""
    moved = 0
    for i, co in enumerate(P):
        hit, n, _, d = BVH.find_nearest(Vector(co))
        if hit is None:
            continue
        depth = (Vector(co) - hit).dot(n)
        if depth < clr:
            P[i] = np.asarray(hit + n * clr)
            moved += 1
    return moved


moved = 0
for name in layout:
    P = gc_to_blender(layout[name])
    moved += clear_of_body(P, args.clearance / 100)
    layout[name] = P
info['points_pushed_out'] = moved
print('start layout (cm):', {k: np.round(v, 1).tolist() for k, v in info.items()})

# ---------------------------------------------------------------- Blender scene
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob)
scene = bpy.context.scene


def material(name, rgba):
    m = bpy.data.materials.new(name)
    m.diffuse_color = rgba
    m.use_backface_culling = False
    m.use_nodes = True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = rgba
    return m


# Body (body + face) as the collider, with the J_Bip weights as vertex groups.
bm_mesh = bpy.data.meshes.new('Body')
bm_mesh.from_pydata(sion_to_blender(body['positions']).tolist(), [], np.asarray(body['triangles']).reshape(-1, 3).tolist())
body_ob = bpy.data.objects.new('Body', bm_mesh)
scene.collection.objects.link(body_ob)
body_ob.data.materials.append(material('skin', (0.85, 0.72, 0.65, 1)))
for f in body_ob.data.polygons:
    f.use_smooth = True
coll = body_ob.modifiers.new('Collision', 'COLLISION')
body_ob.collision.thickness_outer = 0.004
body_ob.collision.cloth_friction = CLOTH['friction']

# Armature from the humanoid joints.
arm_data = bpy.data.armatures.new('Armature')
arm_ob = bpy.data.objects.new('Armature', arm_data)
scene.collection.objects.link(arm_ob)
bpy.context.view_layer.objects.active = arm_ob
bpy.ops.object.mode_set(mode='EDIT')
pos = REST_JOINT  # the exported skeleton: the body kit's own pose (T-pose, or the A-pose with --pose a)
kids = {}
for j in body['joints']:
    kids.setdefault(j['parent'], []).append(j['name'])
prefer = {'J_Bip_C_Hips': 'J_Bip_C_Spine', 'J_Bip_C_UpperChest': 'J_Bip_C_Neck',
          'J_Bip_L_Hand': 'J_Bip_L_Middle1', 'J_Bip_R_Hand': 'J_Bip_R_Middle1'}
bones = {}
for j in body['joints']:
    b = arm_data.edit_bones.new(j['name'])
    b.head = pos[j['name']]
    c = prefer.get(j['name']) or (kids.get(j['name']) or [None])[0]
    if c is not None and np.linalg.norm(pos[c] - pos[j['name']]) > 1e-3:
        b.tail = pos[c]
    else:
        d = pos[j['name']] - pos[j['parent']] if j['parent'] else np.array([0, 0, 1.0])
        b.tail = pos[j['name']] + 0.03 * unit(d)
    bones[j['name']] = b
for j in body['joints']:
    if j['parent']:
        bones[j['name']].parent = bones[j['parent']]
bpy.ops.object.mode_set(mode='OBJECT')

# Garment: all panels as one mesh, seams as loose edges (sewing springs), flat pattern as the rest shape.
verts, flat, faces, uvs, start, panel_of = [], [], [], [], [], []
x_off = 0.0
for k, p in enumerate(panels):
    start.append(len(verts))
    v2 = np.asarray(p['v2d'])
    verts += layout[p['name']].tolist()
    flat += np.c_[(v2[:, 0] - v2[:, 0].min()) / 100 + x_off, v2[:, 1] / 100, np.zeros(len(v2))].tolist()
    uvs.append(np.c_[v2[:, 0] - v2[:, 0].min() + x_off * 100, v2[:, 1] - v2[:, 1].min()])
    x_off += (v2[:, 0].max() - v2[:, 0].min()) / 100 + 0.05
    faces += (np.asarray(p['faces']) + start[-1]).tolist()
    panel_of += [k] * len(v2)
groups = [[start[pi] + li for pi, li in g] for g in pat['seams']]
sew = [(g[0], o) for g in groups for o in g[1:]]

g_mesh = bpy.data.meshes.new(args.name)
g_mesh.from_pydata(verts, sew, faces)
g_mesh.validate()
assert len(g_mesh.vertices) == len(verts), 'mesh validation changed the vertex count'
uv_all = np.concatenate(uvs)
uv_all /= uv_all.max()
uvl = g_mesh.uv_layers.new(name='UVMap')
loop_v = np.zeros(len(g_mesh.loops), dtype=np.int32)
g_mesh.loops.foreach_get('vertex_index', loop_v)
uvl.data.foreach_set('uv', uv_all[loop_v].ravel())
for f in g_mesh.polygons:
    f.use_smooth = True
gar = bpy.data.objects.new(args.name, g_mesh)
scene.collection.objects.link(gar)
gar.data.materials.append(material(args.name, (0.25, 0.45, 0.85, 1)))
gar.shape_key_add(name='Basis')
rest = gar.shape_key_add(name='flat', from_mix=False)
rest.data.foreach_set('co', np.asarray(flat).ravel())
rest.value = 0.0


def look(name, eye, target, ortho=1.0):
    cam = bpy.data.objects.get('Cam') or bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam'))
    if cam.name not in scene.collection.objects:
        scene.collection.objects.link(cam)
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = ortho
    cam.location = eye
    d = np.asarray(target) - np.asarray(eye)
    cam.rotation_euler = (math.atan2(math.hypot(d[0], d[1]), -d[2]), 0, math.atan2(d[1], d[0]) - math.pi / 2)
    scene.camera = cam
    scene.render.filepath = str(OUT / f'{STEM}_{name}.png')
    bpy.ops.render.render(write_still=True)


scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
scene.render.resolution_x, scene.render.resolution_y = 700, 900
scene.render.film_transparent = False
mid = np.array([0, 0, 1.18])


def previews(names):
    for n in names:
        eye = {'front': (0, 3, 1.18), 'side': (-3, 0, 1.18), 'back': (0, -3, 1.18), 'start': (-2.1, 2.1, 1.18)}[n]
        look(n, eye, mid, ortho=0.95)


if args.no_sim:
    previews(['start'])
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f'{STEM}_draped.blend'))
    sys.exit(0)

# ---------------------------------------------------------------- cloth simulation
panel_names = [p['name'] for p in panels]
pan = np.asarray(panel_of)
seam_a = np.array([a for a, _ in sew])
seam_b = np.array([b for _, b in sew])
basis = gar.data.shape_keys.key_blocks['Basis']


def positions(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    m = ev.to_mesh()
    co = np.zeros(len(m.vertices) * 3)
    m.vertices.foreach_get('co', co)
    ev.to_mesh_clear()
    return co.reshape(-1, 3)


def simulate(label, frames, gravity, friction, air, sewing_force, stop_gap_mm=None):
    """One cloth run from the current Basis shape; returns the final vertex positions."""
    body_ob.collision.cloth_friction = friction
    cloth = gar.modifiers.new('Cloth', 'CLOTH')
    cs, cc = cloth.settings, cloth.collision_settings
    cs.quality = 10
    cs.mass = CLOTH['mass']
    cs.air_damping = air
    cs.tension_stiffness = CLOTH['tension']
    cs.compression_stiffness = CLOTH['compression']
    cs.shear_stiffness = CLOTH['shear']
    cs.bending_stiffness = CLOTH['bending']
    cs.tension_damping = cs.compression_damping = cs.shear_damping = CLOTH['damping']
    cs.bending_damping = 0.5
    cs.use_sewing_springs = True
    cs.sewing_force_max = sewing_force
    if not args.wrap_rest:
        cs.use_dynamic_mesh = True
        rest.value = 0.0
        rest.keyframe_insert('value', frame=1)
        rest.value = 1.0
        rest.keyframe_insert('value', frame=2)
    cs.effector_weights.gravity = gravity
    cc.use_collision = True
    cc.distance_min = CLOTH['collision_distance']
    cc.collision_quality = 4
    cc.use_self_collision = False
    cloth.point_cache.frame_start = 1
    cloth.point_cache.frame_end = frames
    scene.frame_start, scene.frame_end = 1, frames
    t0 = time.time()
    for f in range(1, frames + 1):
        scene.frame_set(f)
        if f % 5 == 0 or f == frames:
            P = positions(gar)
            gap = np.linalg.norm(P[seam_a] - P[seam_b], axis=1) * 1000
            print(f'{label} frame {f:3d}  seam gap mean {gap.mean():5.1f} mm  max {gap.max():6.1f} mm  '
                  f'{time.time() - t0:5.0f} s', flush=True)
            if stop_gap_mm and gap.max() < stop_gap_mm:
                break
    worst = np.argsort(-gap)[:6]
    print(f'{label} worst seams:', ', '.join(f'{panel_names[pan[seam_a[w]]]}~{panel_names[pan[seam_b[w]]]} '
                                              f'{gap[w]:.0f}mm @z{P[seam_a[w]][2]:.2f}' for w in worst))
    P = positions(gar)
    gar.modifiers.remove(cloth)
    scene.frame_set(1)
    return P


import time
# 1. sew: no gravity, slippery body, calm air, until every seam is shut
P = simulate('sew', args.sew_frames, gravity=args.sew_gravity, friction=0.5, air=10.0, sewing_force=args.sewing_force,
             stop_gap_mm=3.0)
basis.data.foreach_set('co', P.ravel())
P_sewn = P.copy()
# 2. settle: gravity on, seams kept shut
P = simulate('settle', args.frames, gravity=1.0, friction=CLOTH['friction'], air=1.0, sewing_force=args.sewing_force)
extra = {}
if args.free_relax:
    basis.data.foreach_set('co', P.ravel())
    body_ob.collision.use = False
    extra['free'] = simulate('free', args.free_relax, gravity=0.0, friction=0.0, air=10.0, sewing_force=args.sewing_force)
    body_ob.collision.use = True
    basis.data.foreach_set('co', P.ravel())
# every stage, for diagnose.py
np.savez_compressed(OUT / f'{STEM}_states.npz', start=np.asarray(verts), sewn=P_sewn, settled=P, flat=np.asarray(flat),
                    faces=np.asarray(faces), panel=pan, names=np.array(panel_names),
                    pattern=gc_to_blender(np.concatenate([p['v3d'] for p in panels])),
                    seam_v=np.concatenate(groups), seam_n=np.array([len(g) for g in groups]),
                    body=sion_to_blender(body['positions']), **extra)

# ---------------------------------------------------------------- weld seams, clean, stretch report
rest_len = {}
fl = np.asarray(flat)
E = set()
for tri in np.asarray(faces):
    for i in range(3):
        a, b = sorted((tri[i], tri[(i + 1) % 3]))
        E.add((a, b))
E = np.array(sorted(E))
strain = np.linalg.norm(P[E[:, 0]] - P[E[:, 1]], axis=1) / np.linalg.norm(fl[E[:, 0]] - fl[E[:, 1]], axis=1) - 1
print(f'stretch vs pattern: median {np.median(strain) * 100:.1f}%  95th {np.percentile(strain, 95) * 100:.1f}%  '
      f'max {strain.max() * 100:.1f}%')
for k, nm in enumerate(panel_names):
    m = pan[E[:, 0]] == k
    hot = E[m][strain[m] > 0.15]
    where = f'  hot spots around z {np.round(np.percentile(P[hot[:, 0]][:, 2], [10, 50, 90]), 2).tolist()}' if len(hot) else ''
    print(f'  {nm:16s} stretch median {np.median(strain[m]) * 100:5.1f}%  95th {np.percentile(strain[m], 95) * 100:5.1f}%  '
          f'>15%: {len(hot)} edges{where}')
v_strain = np.zeros(len(P))
np.add.at(v_strain, E[:, 0], strain)
np.add.at(v_strain, E[:, 1], strain)
v_strain /= np.maximum(np.bincount(E.ravel(), minlength=len(P)), 1)

rep = np.arange(len(P))
for g in groups:
    P[g] = P[g].mean(0)
    rep[g] = g[0]
keep = np.unique(rep)
new_index = -np.ones(len(P), dtype=int)
new_index[keep] = np.arange(len(keep))
F = new_index[rep[np.asarray(faces)]]
ok = (F[:, 0] != F[:, 1]) & (F[:, 1] != F[:, 2]) & (F[:, 0] != F[:, 2])

gar.shape_key_clear()
final = bpy.data.meshes.new(args.name)
final.from_pydata(P[keep].tolist(), [], F[ok].tolist())
final.validate()
uvf = final.uv_layers.new(name='UVMap')
old_loops = np.asarray(faces)[ok]
uvf.data.foreach_set('uv', uv_all[old_loops.ravel()].ravel())
for f in final.polygons:
    f.use_smooth = True
final.materials.append(gar.data.materials[0])
old = gar.data
gar.data = final
bpy.data.meshes.remove(old)
print(f'welded: {len(final.vertices)} vertices, {len(final.polygons)} triangles')
# stretch map colours: blue = squeezed 20%, white = as cut, red = stretched 20%
c = np.clip(v_strain[keep] / 0.2, -1, 1)[:, None]
rgb = np.where(c > 0, (1 - c) * np.ones(3) + c * np.array([0.85, 0.1, 0.1]), (1 + c) * np.ones(3) - c * np.array([0.15, 0.3, 0.9]))
col = final.color_attributes.new('stretch', 'FLOAT_COLOR', 'POINT')
col.data.foreach_set('color', np.c_[rgb, np.ones(len(rgb))].ravel())
gap = []
for co in P[keep]:
    hit, n, _, d = BVH.find_nearest(Vector(co))
    gap.append((Vector(co) - hit).dot(n) * 100)
gap = np.asarray(gap)
hem_designed = min(np.asarray(p['v3d'])[:, 1].min() for p in panels)
print(f'fit: hem {P[keep][:, 2].min() * 100 - FLOOR * 100:.1f} cm above floor (pattern {hem_designed:.1f}); '
      f'cloth to skin median {np.median(gap):.1f} cm, 90th {np.percentile(gap, 90):.1f} cm; '
      f'{(gap < 0).sum()} points inside the body')

# ---------------------------------------------------------------- skin weights from the nearest body skin
names = sorted({n for g in body['groups'] for n, _ in g})
gar_groups = []
for n in names:
    gar.vertex_groups.new(name=n)
BP = sion_to_blender(body['positions'])
tree = kdtree.KDTree(len(BP))
for i, co in enumerate(BP):
    tree.insert(co, i)
tree.balance()
for vi, co in enumerate(P[keep]):
    acc = {}
    for _, i, d in tree.find_n(co, 6):
        w = 1 / (d + 1e-4)
        for n, x in body['groups'][i]:
            acc[n] = acc.get(n, 0) + w * x
    top = sorted(acc.items(), key=lambda kv: -kv[1])[:4]
    s = sum(x for _, x in top)
    for n, x in top:
        gar.vertex_groups[n].add([vi], x / s, 'REPLACE')
    gar_groups.append([(n, x / s) for n, x in top])

# ---------------------------------------------------------------- outputs
previews(['front', 'side', 'back'])
scene.display.shading.color_type = 'VERTEX'
look('stretch_front', (0, 3, 1.18), mid, ortho=0.95)
look('stretch_back', (0, -3, 1.18), mid, ortho=0.95)
look('stretch_side', (-3, 0, 1.18), mid, ortho=0.95)
scene.display.shading.color_type = 'MATERIAL'
if ARM:
    # back to the rest T-pose: undo the arm rotation on the garment with its own skin weights, and on the body
    rest_P = pose_points(P[keep], arm_weights(gar_groups), inverse=True)
    final.vertices.foreach_set('co', rest_P.ravel())
    final.update()
    body_ob.data.vertices.foreach_set('co', pose_points(sion_to_blender(body['positions']), arm_weights(body['groups']),
                                                        inverse=True).ravel())
    body_ob.data.update()
    RB = BVHTree.FromObject(body_ob, bpy.context.evaluated_depsgraph_get())
    inside = sum((Vector(co) - RB.find_nearest(Vector(co))[0]).dot(RB.find_nearest(Vector(co))[1]) < 0 for co in rest_P)
    print(f'rest pose: {inside} garment points inside the body')
    look('rest_front', (0, 3, 1.18), mid, ortho=0.95)
mod = gar.modifiers.new('Armature', 'ARMATURE')
mod.object = arm_ob
gar.parent = arm_ob
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f'{STEM}_draped.blend'))
bpy.ops.object.select_all(action='DESELECT')
gar.select_set(True)
arm_ob.select_set(True)
bpy.context.view_layer.objects.active = gar
bpy.ops.export_scene.gltf(filepath=str(OUT / f'{STEM}.glb'), export_format='GLB', use_selection=True,
                          export_yup=True, export_skins=True, export_animations=False, export_morph=False)
print('wrote', OUT / f'{STEM}.glb')
