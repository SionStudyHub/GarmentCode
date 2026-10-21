"""Blender 3.x/4.x setup for NewFemaleBlenderShirt (run INSIDE Blender Text Editor).
1. Place combined_box.obj, stitches.json next to this script (or edit IMPORT_DIR).
2. Have your new_base_female avatar in the scene with the body mesh named "Body".
3. Run this script, then press Spacebar from frame 1.

What it does: imports panels, snaps sewing springs between stitch pairs,
adds Collision to Body, Cloth (with sewing springs) + Weld to garment.
"""
import bpy, json, os
from mathutils import Vector

IMPORT_DIR = None
for _cand in [os.path.dirname(bpy.data.filepath), r"/Users/vaz/Desktop/antigravity_apps/GarmentCode/export_garmentcode/NewFemaleBlenderShirt"]:
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
