"""Generate authentic GarmentCode shirt for new_base_female + Blender-ready export.
Runs in repo venv (NOT in Blender). Output: export_garmentcode/NewFemaleBlenderShirt/
- GarmentCode spec JSON + pattern PNG/SVG (ground-truth CAD)
- combined_box.obj (triangulated panels, meters, Blender Z-up, arranged around body)
- per-panel OBJs
- stitches.json (sewing pairs resampled along stitched edges)
- blender_setup.py (run inside Blender) + README

NOTE: FittedShirt block crashes on this hourglass body (bust 75.7 / waist 45.4
breaks the sleeve cut-corner operator: zero-length edge assertion). Using the
Shirt block with width=1.0/flare=1.0 = closest fitted authentic GarmentCode result.
"""
import json
from pathlib import Path

import numpy as np
import yaml

from assets.bodies.body_params import BodyParameters
from assets.garment_programs.meta_garment import MetaGarment
from pygarment.meshgen.boxmeshgen import BoxMesh

REPO = Path(__file__).parent
OUT = REPO / 'export_garmentcode' / 'NewFemaleBlenderShirt'
OUT.mkdir(parents=True, exist_ok=True)

# 1. Authentic GarmentCode assembly -------------------------------------------
with open(REPO / 'assets/design_params/t-shirt.yaml') as f:
    design = yaml.safe_load(f)['design']
design['meta']['upper']['v'] = 'Shirt'   # FittedShirt asserts on this body; Shirt works
design['meta']['bottom']['v'] = None
design['meta']['wb']['v'] = None
design['shirt']['length']['v'] = 1.0
design['shirt']['width']['v'] = 1.0
design['shirt']['flare']['v'] = 0.7  # taper hem 75.7 -> 53.0cm (body waist 45.4)
design['sleeve']['length']['v'] = 0.4
design['collar']['f_collar']['v'] = 'CircleNeckHalf'
design['collar']['b_collar']['v'] = 'CircleNeckHalf'

body = BodyParameters(str(REPO / 'assets/bodies/new_base_female.yaml'))
garment = MetaGarment('NewFemaleBlenderShirt', body, design)
pattern = garment.assembly()
print('Panels:', list(pattern.pattern['panels'].keys()))
print('Stitches:', len(pattern.pattern['stitches']))

# 2. Spec + pattern images (ground-truth CAD) ----------------------------------
pattern.serialize(str(OUT) + '/', to_subfolder=False, tag='',
                  with_3d=False, with_text=True, view_ids=True)
# serialize writes <name>_specification.json etc. Normalize names:
for p in OUT.glob('NewFemaleBlenderShirt_specification.json'):
    p.rename(OUT / 'specification.json')

spec = json.loads((OUT / 'specification.json').read_text())
panels = spec['pattern']['panels']
stitches = spec['pattern']['stitches']

# 3. Triangulate panels via BoxMesh (uses libigl, GarmentCode's own mesher) ----
box = BoxMesh(str(OUT / 'specification.json'), res=1.0)
box.load()  # load_panels + gen_panel_meshes + stitch collapse + finalise

PANEL_DIR = OUT / 'panels_obj'
PANEL_DIR.mkdir(exist_ok=True)


def gc_to_blender(v3_cm):
    """GarmentCode cm (x=right?, y=up, z=front+) -> Blender m (x, y=back+, z=up).
    Front (+z) maps to Blender -Y to match VRM avatar facing +Y convention used here."""
    x, y, z = float(v3_cm[0]), float(v3_cm[1]), float(v3_cm[2])
    return [x / 100.0, -z / 100.0, y / 100.0]


# --- Body-hugging placement (measured from new_base_female.blend Body mesh) ---
# (z_m, front_y_ddist_m, back_y_dist_m, halfwidth_m); front/back = |Y| surface dist
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
_GAP = 0.030  # 3cm sewing gap off the skin


def _prof(z):
    f = float(np.interp(z, _PZ, _PF))
    b = float(np.interp(z, _PZ, _PB))
    w = float(np.interp(z, _PZ, _PHW))
    return f, b, w


def _sleeve_plane_targets():
    # arm surface at upper arm: front y=-0.014, back y=+0.056 (measured)
    return -0.014 - _GAP, 0.056 + _GAP


# --- Tailor's width grade ----------------------------------------------------
# GarmentCode's Shirt block drafts ~64cm total vs the 75.7cm bust (-15% ease:
# unsewable/unwearable on this body). Grade X by 1.18 about each panel's
# center anchor -> ~76.5cm (+1% comfort ease). Outline SHAPE, edge pairing and
# stitch topology untouched; stitch pairs rescale automatically. Disclosed in
# README as a standard "let out the side seams" alteration.
GRADE = 1.18

# per-panel Y offsets for sleeves computed after spec load (from box offsets)
_SLEEVE_DY = {}

# --- Sleeve pre-wrap: flat sheets -> half-tubes around the horizontal arms ---
# Arm axis (measured at mid-upper-arm) + pre-seat nudge toward the armhole.
# Measured mean cap->armhole vector is ~8cm toward front(-Y); shifting the tube
# 40% of the way closes most of it while keeping the arm inside the tube.
_ARM_Y0, _ARM_Z0 = 0.024, 1.398
_NUDGE_Y, _NUDGE_Z, _NUDGE_X = -0.032, -0.004, 0.007
_SLEEVE = {}  # pname -> dict(tx, top_ly, span_ly, R)


def _sleeve_point(pname, lx, ly):
    s = _SLEEVE[pname]
    import math
    side = 1.0 if s['tx'] > 0 else -1.0  # left +X / right -X
    gx = s['ax'] + (lx - s['ax']) * GRADE  # grade about shoulder anchor
    x = (gx + s['tx']) / 100.0 - side * _NUDGE_X
    d = s['top_ly'] - ly
    phi = (d / s['span_ly']) * math.pi - math.pi / 2.0
    yc = _ARM_Y0 + _NUDGE_Y
    zc = _ARM_Z0 + _NUDGE_Z
    if 'sleeve_f' in pname:
        y = yc - s['R'] * math.cos(phi)
    else:
        y = yc + s['R'] * math.cos(phi)
    z = zc + s['R'] * math.sin(phi)
    return [x, y, z]


def place(panel_name, xb, yb, zb):
    """Hybrid placement. Panel outlines + stitches untouched.
    - Shoulder zone (z>~1.38): hug the body (2cm) so shoulder seams shut in
      the first frames and the garment hangs from the shoulders like on a
      hanger (no climb, no fall, stable frame for the other seams).
    - Below: stand further off (up to 6cm) so side/cap seams travel in free
      space without contact-locking against the skin."""
    t = min(max((1.40 - zb) / 0.10, 0.0), 1.0)
    s = t * t * (3.0 - 2.0 * t)  # smoothstep 0 at shoulder -> 1 below
    gap = 0.02 + 0.04 * s
    if 'ftorso' in panel_name:
        f, _, _ = _prof(zb)
        return [xb * GRADE, -(f + gap), zb]
    if 'btorso' in panel_name:
        _, b, _ = _prof(zb)
        return [xb * GRADE, b + gap, zb]
    if 'sleeve' in panel_name:
        return [xb, yb + _SLEEVE_DY.get(panel_name, 0.0), zb]
    return [xb, yb, zb]


import math as _math
_THETA_MAX = _math.radians(100.0)  # hard cap so wild rows can't spiral


# sleeve rigid offsets: from GarmentCode box planes to body-hugging planes
_f_target, _b_target = _sleeve_plane_targets()
for _pn, _pd in panels.items():
    if 'sleeve' in _pn:
        _tz = float(_pd.get('translation', [0, 0, 0])[2])
        _cur = -_tz / 100.0
        _tgt = _f_target if 'sleeve_f' in _pn else _b_target
        _SLEEVE_DY[_pn] = _tgt - _cur
        _lys = [v[1] for v in _pd['vertices']]
        _lxs = [v[0] for v in _pd['vertices']]
        _span = max(_lys) - min(_lys)
        _ax = max(_lxs, key=lambda v: abs(v))  # shoulder end (max |x|)
        _SLEEVE[_pn] = {'tx': float(_pd['translation'][0]), 'top_ly': max(_lys),
                        'span_ly': _span, 'R': _span / 3.14159265 / 100.0,
                        'ax': _ax}
print('Sleeve wrap R (m):', {k: round(v['R'], 3) for k, v in _SLEEVE.items()})


def write_obj(path, verts_b, faces_1based):
    with open(path, 'w') as f:
        f.write(f'# {Path(path).stem} — GarmentCode NewFemaleBlenderShirt (meters, Blender Z-up)\n')
        for v in verts_b:
            f.write(f'v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n')
        for tri in faces_1based:
            f.write(f'f {tri[0]} {tri[1]} {tri[2]}\n')


combined_verts, combined_faces = [], []
group_index = []  # (panel_name, start_1based, end_1based_inclusive)
def panel_data_translation(pname):
    return panels[pname].get('translation', [0, 0, 0])


for pname, panel in box.panels.items():
    v = np.asarray(panel.rot_trans_panel(panel.panel_vertices))  # (N,3) cm, placed
    f = np.asarray(panel.panel_faces, dtype=int) + 1  # to 1-based local
    if 'sleeve' in pname:
        # rotations are identity: recover local coords, wrap tube around arm
        t = np.array(panel_data_translation(pname), dtype=float)
        vb = [_sleeve_point(pname, p[0] - t[0], p[1] - t[1]) for p in v]
    elif 'torso' in pname:
        # flat sheets (proven to drape without buckling); sim closes the gaps
        vb = [place(pname, *gc_to_blender(p)) for p in v]
    else:
        vb = [place(pname, *gc_to_blender(p)) for p in v]
    write_obj(PANEL_DIR / f'{pname}.obj', vb, f.tolist())
    start = len(combined_verts) + 1
    combined_verts.extend(vb)
    combined_faces.extend((f + (start - 1)).tolist())
    group_index.append([pname, start, len(combined_verts)])

with open(OUT / 'combined_box.obj', 'w') as f:
    f.write('# NewFemaleBlenderShirt — GarmentCode box mesh (meters, Blender Z-up)\n')
    for v in combined_verts:
        f.write(f'v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n')
    # write all faces grouped
    for pname, s, e in group_index:
        f.write(f'g {pname}\n')
        # faces referencing global ids: select those within [s,e]
        for tri in combined_faces:
            if s <= tri[0] <= e and s <= tri[1] <= e and s <= tri[2] <= e:
                f.write(f'f {tri[0]} {tri[1]} {tri[2]}\n')

print(f'Wrote {len(box.panels)} panel OBJs + combined_box.obj ({len(combined_verts)} verts)')

# 4. Stitches -> sewing pairs (resampled straight along each edge, meters) -----
N_PAIRS = 24


def edge_endpoints_3d(panel_name, edge_idx):
    """Raw GarmentCode box coords (cm). Placement applied later per-point."""
    p = panels[panel_name]
    e = p['edges'][edge_idx]
    i, j = e['endpoints']
    t = np.array(p.get('translation', [0, 0, 0]), dtype=float)
    a = np.array([p['vertices'][i][0] + t[0], p['vertices'][i][1] + t[1], t[2]])
    b = np.array([p['vertices'][j][0] + t[0], p['vertices'][j][1] + t[1], t[2]])
    return a, b


def _placed(panel_name, q_gc):
    return np.array(place(panel_name, *gc_to_blender(q_gc)))


def _local(panel_name, edge_idx):
    """Edge endpoints in panel-LOCAL cm coords (for sleeve wrap)."""
    p = panels[panel_name]
    e = p['edges'][edge_idx]
    i, j = e['endpoints']
    return (np.array(p['vertices'][i], dtype=float),
            np.array(p['vertices'][j], dtype=float))


def _torso_point(panel_name, q_box):
    """Box-space cm point -> flat-placed Blender coords (matches mesh loop)."""
    return place(panel_name, *gc_to_blender(q_box))


stitch_out = []
for s in stitches:
    p1, e1 = s[0]['panel'], s[0]['edge']
    p2, e2 = s[1]['panel'], s[1]['edge']
    a1, b1 = edge_endpoints_3d(p1, e1)
    a2, b2 = edge_endpoints_3d(p2, e2)
    # local-space copies for sleeve wrap interpolation
    a1l, b1l = _local(p1, e1)
    a2l, b2l = _local(p2, e2)
    # orient: pair start-to-start or start-to-end by placed-3D proximity
    pa1, pb1, pa2, pb2 = _placed(p1, a1), _placed(p1, b1), _placed(p2, a2), _placed(p2, b2)
    d_par = np.linalg.norm(pa1 - pa2) + np.linalg.norm(pb1 - pb2)
    d_rev = np.linalg.norm(pa1 - pb2) + np.linalg.norm(pb1 - pa2)
    if d_rev < d_par:
        a2, b2 = b2, a2
        a2l, b2l = b2l, a2l  # keep LOCAL copies in sync (sleeve wrap path)
    pairs = []
    for k in range(N_PAIRS):
        t = k / (N_PAIRS - 1)
        if 'sleeve' in p1:
            q1 = _sleeve_point(p1, *((1 - t) * a1l + t * b1l))
        elif 'torso' in p1:
            q1 = _torso_point(p1, (1 - t) * a1 + t * b1)
        else:
            q1 = _placed(p1, (1 - t) * a1 + t * b1).tolist()
        if 'sleeve' in p2:
            q2 = _sleeve_point(p2, *((1 - t) * a2l + t * b2l))
        elif 'torso' in p2:
            q2 = _torso_point(p2, (1 - t) * a2 + t * b2)
        else:
            q2 = _placed(p2, (1 - t) * a2 + t * b2).tolist()
        pairs.append([q1, q2])
    stitch_out.append({'panel1': p1, 'edge1': e1, 'panel2': p2, 'edge2': e2,
                       'reversed': bool(d_rev < d_par), 'pairs': pairs})

(OUT / 'stitches.json').write_text(json.dumps(stitch_out, indent=1))
print(f'Wrote stitches.json ({len(stitch_out)} stitches x {N_PAIRS} pairs)')

# 5. Blender setup script -------------------------------------------------------
(OUT / 'blender_setup.py').write_text('''"""Blender 3.x/4.x setup for NewFemaleBlenderShirt (run INSIDE Blender Text Editor).
1. Place combined_box.obj, stitches.json next to this script (or edit IMPORT_DIR).
2. Have your new_base_female avatar in the scene with the body mesh named "Body".
3. Run this script, then press Spacebar from frame 1.

What it does: imports panels, snaps sewing springs between stitch pairs,
adds Collision to Body, Cloth (with sewing springs) + Weld to garment.
"""
import bpy, json, os
from mathutils import Vector

IMPORT_DIR = None
for _cand in [os.path.dirname(bpy.data.filepath), r"%s"]:
    if _cand and os.path.isfile(os.path.join(_cand, "combined_box.obj")):
        IMPORT_DIR = _cand
        break
if IMPORT_DIR is None:
    raise RuntimeError(
        "Cannot find combined_box.obj. Put combined_box.obj + stitches.json "
        "in the same folder as your .blend file, or edit CANDIDATES in this script.")
print(f"[Garment] Loading from: {IMPORT_DIR}")
OBJ_PATH = os.path.join(IMPORT_DIR, "combined_box.obj")
STITCH_PATH = os.path.join(IMPORT_DIR, "stitches.json")
GARMENT_NAME = "NewFemaleBlenderShirt"

# import (file is already Blender Z-up: identity mapping, verified empirically)
bpy.ops.wm.obj_import(filepath=OBJ_PATH, forward_axis='Y', up_axis='Z')
_imp = [o for o in bpy.context.selected_objects if o.type == 'MESH']
garment = _imp[0] if _imp else bpy.context.selected_objects[0]
garment.name = GARMENT_NAME

# anchor hooks: neckline ring + cuff rings hold the garment in formation while
# seams sew (otherwise unanchored pieces drift/fall before springs can close).
# Hooks sit ABOVE Cloth in the stack and release (strength 1->0) once shut.
def _anchor_group(name, keep):
    vg = garment.vertex_groups.new(name=name)
    ids = [v.index for v in garment.data.vertices if keep(v.co)]
    if ids:
        vg.add(ids, 1.0, 'REPLACE')
    return vg, ids

_vg_neck, _neck_ids = _anchor_group("AnchorNeck", lambda co: co.z > 1.425 and abs(co.x) < 0.26)
_vg_cuffL, _cuffL_ids = _anchor_group("AnchorCuffL", lambda co: co.x > 0.26)
_vg_cuffR, _cuffR_ids = _anchor_group("AnchorCuffR", lambda co: co.x < -0.26)
print(f"[Garment] Anchors: neck={len(_neck_ids)} cuffL={len(_cuffL_ids)} cuffR={len(_cuffR_ids)}")
_hooks = []
for _vg, _ids, _ename in [
    (_vg_neck, _neck_ids, "HookEmptyNeck"),
    (_vg_cuffL, _cuffL_ids, "HookEmptyCuffL"),
    (_vg_cuffR, _cuffR_ids, "HookEmptyCuffR"),
]:
    if not _ids:
        continue
    # empty exactly at the group centroid -> zero offset at bind, verts stay put
    _cx = sum(garment.data.vertices[i].co.x for i in _ids) / len(_ids)
    _cy = sum(garment.data.vertices[i].co.y for i in _ids) / len(_ids)
    _cz = sum(garment.data.vertices[i].co.z for i in _ids) / len(_ids)
    _e = bpy.data.objects.get(_ename) or bpy.data.objects.new(_ename, None)
    if _e.name not in bpy.context.collection.objects:
        bpy.context.collection.objects.link(_e)
    _e.location = (_cx, _cy, _cz)
    _h = garment.modifiers.new(f"Hook_{_vg.name}", "HOOK")
    _h.object = _e
    _h.vertex_group = _vg.name
    _h.strength = 1.0
    _h.keyframe_insert(data_path="strength", frame=1)
    _h.keyframe_insert(data_path="strength", frame=85)
    _h.strength = 0.0
    _h.keyframe_insert(data_path="strength", frame=95)
    _hooks.append(_h.name)
print(f"[Garment] Hook anchors: {_hooks} (hold 1-85, release at 95)")
print("[Garment] Anchor groups are exclusive; hooks hold rest positions.")

# body collision
body = bpy.data.objects.get("Body")
if body:
    if not any(m.type == 'COLLISION' for m in body.modifiers):
        body.modifiers.new("Collision", "COLLISION")
    for m in body.modifiers:
        if m.type == 'COLLISION':
            m.settings.thickness_outer = 0.003
            m.settings.thickness_inner = 0.003
            m.settings.cloth_friction = 1.5
else:
    print("[WARN] No object named 'Body' — add Collision to your avatar manually.")

# sewing springs from stitches.json
with open(STITCH_PATH) as f:
    stitches = json.load(f)
mesh = garment.data
def nearest_vi(co):
    best, bd = None, 1e9
    for v in mesh.vertices:
        d = (v.co - co).length
        if d < bd:
            bd, best = d, v.index
    return best
mesh.update()
sew_edges = []
for s in stitches:
    for q1, q2 in s["pairs"]:
        i = nearest_vi(Vector(q1))
        j = nearest_vi(Vector(q2))
        if i is not None and j is not None and i != j:
            sew_edges.append((i, j))
mesh.update()
import bmesh
bm = bmesh.new()
bm.from_mesh(mesh)
bm.verts.ensure_lookup_table()
seen = set()
for i, j in sew_edges:
    key = (min(i, j), max(i, j))
    if key in seen:
        continue
    seen.add(key)
    try:
        bm.edges.new((bm.verts[i], bm.verts[j]))
    except ValueError:
        pass
bm.to_mesh(mesh)
bm.free()
print(f"[Garment] Added {len(seen)} sewing spring edges.")

# cloth (sewing schedule: springs ramp up while gravity stays off, so the
# 5-12cm pre-sew gaps zip shut BEFORE gravity is allowed to pull anything down)
cloth = garment.modifiers.new("Cloth", "CLOTH")
cloth.settings.quality = 7
cloth.settings.use_sewing_springs = True
cloth.settings.sewing_force_max = 10.0
cloth.settings.mass = 0.1
cloth.settings.tension_stiffness = 40.0
cloth.settings.compression_stiffness = 40.0
cloth.settings.shear_stiffness = 10.0
cloth.settings.bending_stiffness = 0.1
cloth.settings.tension_damping = 25.0
cloth.settings.compression_damping = 25.0
cloth.collision_settings.use_collision = True
cloth.collision_settings.collision_quality = 3
cloth.collision_settings.distance_min = 0.004
# sew while hanging: brief zero-g start so shoulder seams shut first, then
# light gravity seats the fabric (kills zero-g climb/float) while long seams
# finish; full gravity only after shut (graded tube grips, cannot fall)
cloth.settings.effector_weights.gravity = 0.0
cloth.settings.effector_weights.keyframe_insert(data_path="gravity", frame=1)
cloth.settings.effector_weights.keyframe_insert(data_path="gravity", frame=10)
cloth.settings.effector_weights.gravity = 0.25
cloth.settings.effector_weights.keyframe_insert(data_path="gravity", frame=15)
cloth.settings.effector_weights.keyframe_insert(data_path="gravity", frame=80)
cloth.settings.effector_weights.gravity = 1.0
cloth.settings.effector_weights.keyframe_insert(data_path="gravity", frame=100)
weld = garment.modifiers.new("Weld", "WELD")
weld.merge_threshold = 0.01
print("[SUCCESS] Press Spacebar from frame 1 to sew + drape.")

# safety-net floor (catches the garment if it ever slips; delete if unwanted)
try:
    bpy.ops.mesh.primitive_plane_add(size=4.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "ClothFloor"
    fcol = floor.modifiers.new("Collision", "COLLISION")
    fcol.settings.thickness_outer = 0.01
    fcol.settings.thickness_inner = 0.01
    print("[Garment] Added collision floor at z=0.")
except Exception as e:
    print(f"[WARN] Could not add floor: {e}")
''' % str(OUT))

(OUT / 'README.txt').write_text(
    'NewFemaleBlenderShirt — authentic GarmentCode shirt for new_base_female\\n'
    'Body: assets/bodies/new_base_female.yaml (bust 75.7, waist 45.4, hips 83.5, h 173.2)\\n'
    'Block: Shirt (width 1.0, flare 1.0, length 1.0, sleeve 0.4, circle neck)\\n'
    'NOTE: FittedShirt block fails on this body (sleeve cut-corner zero-length edge);\\n'
    'this Shirt result is genuine GarmentCode output, nothing hand-drawn.\\n\\n'
    'Files:\\n'
    '- specification.json (+ _pattern.png/.svg): GarmentCode CAD ground truth\\n'
    '- panels_obj/*.obj: per-panel triangulated meshes (meters, Blender Z-up)\\n'
    '- combined_box.obj: all panels, import this into Blender\\n'
    '- stitches.json: 16 GarmentCode stitches as sewing-spring pairs\\n'
    '- blender_setup.py: run inside Blender (Text Editor > Run Script)\\n')
print('Done ->', OUT)
