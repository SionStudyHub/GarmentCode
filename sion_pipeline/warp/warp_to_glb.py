"""Turn a Warp drape (run_job.py's result.npz) into a GLB skinned to the sion-avatar J_Bip skeleton, with previews.

    /Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
        --python sion_pipeline/warp/warp_to_glb.py -- <job dir> [--out-dir <dir>] [--stem <name>]

Reads  <job>/out/result.npz                       garment vertices (cm, GarmentCode frame) and triangles
       sion_pipeline/kit/female_apose_body.json    the body the drape ran on (same A-pose)
Writes <out-dir>/<stem>.glb                        skeleton in the A-pose: import with fitting:import --weights body --pose a
       <out-dir>/<stem>_{front,side,back}.png      same cameras as drape_blender.py, to compare side by side
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector, kdtree
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument('job')
ap.add_argument('--body-kit', default=str(HERE.parent / 'kit/female_apose_body.json'))
ap.add_argument('--out-dir', default=None)
ap.add_argument('--stem', default=None)
args = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])

JOB = Path(args.job).resolve()
OUT = Path(args.out_dir).resolve() if args.out_dir else JOB / 'out'
STEM = args.stem or JOB.name
OUT.mkdir(parents=True, exist_ok=True)
body = json.loads(Path(args.body_kit).read_text())
FLOOR = body['floor']


# Frames (as drape_blender.py): sion (metres, Y up, faces -Z, left -X); GarmentCode (cm, Y up from floor, faces +Z,
# left +X); Blender (metres, Z up, faces +Y, left -X). The glTF exporter turns Blender back into the sion frame.
def sion_to_blender(P):
    P = np.asarray(P, float).reshape(-1, 3)
    return np.c_[P[:, 0], -P[:, 2], P[:, 1]]


def gc_to_blender(P):
    P = np.asarray(P, float).reshape(-1, 3) / 100
    return np.c_[-P[:, 0], P[:, 2], P[:, 1] + FLOOR]


def unit(v):
    return v / (np.linalg.norm(v) + 1e-12)


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


# Body, for previews and the fit numbers
BP = sion_to_blender(body['positions'])
bm = bpy.data.meshes.new('Body')
bm.from_pydata(BP.tolist(), [], np.asarray(body['triangles']).reshape(-1, 3).tolist())
body_ob = bpy.data.objects.new('Body', bm)
scene.collection.objects.link(body_ob)
body_ob.data.materials.append(material('skin', (0.85, 0.72, 0.65, 1)))
for f in body_ob.data.polygons:
    f.use_smooth = True

# Armature from the kit's joints, in the kit's own (A-)pose, exactly as drape_blender.py builds it
arm_data = bpy.data.armatures.new('Armature')
arm_ob = bpy.data.objects.new('Armature', arm_data)
scene.collection.objects.link(arm_ob)
bpy.context.view_layer.objects.active = arm_ob
bpy.ops.object.mode_set(mode='EDIT')
pos = {j['name']: sion_to_blender(j['pos'])[0] for j in body['joints']}
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

# Garment from the Warp result
z = np.load(JOB / 'out' / 'result.npz')
P = gc_to_blender(z['verts'])
gm = bpy.data.meshes.new(STEM)
gm.from_pydata(P.tolist(), [], z['faces'].astype(int).tolist())
gm.validate()
gar = bpy.data.objects.new(STEM, gm)
scene.collection.objects.link(gar)
gar.data.materials.append(material(STEM, (0.25, 0.45, 0.85, 1)))
for f in gar.data.polygons:
    f.use_smooth = True
P = np.array([v.co[:] for v in gm.vertices])
print(f'garment: {len(P)} vertices, {len(gm.polygons)} triangles')

# Fit numbers, same as drape_blender.py prints
BVH = BVHTree.FromObject(body_ob, bpy.context.evaluated_depsgraph_get())
gap = np.array([(Vector(co) - BVH.find_nearest(Vector(co))[0]).dot(BVH.find_nearest(Vector(co))[1]) * 100 for co in P])
print(f'fit: hem {P[:, 2].min() * 100 - FLOOR * 100:.1f} cm above floor; cloth to skin median {np.median(gap):.1f} cm, '
      f'90th {np.percentile(gap, 90):.1f} cm; {(gap < 0).sum()} points inside the body')

# Skin weights from the nearest body skin (6 nearest, top 4 bones), as drape_blender.py
names = sorted({n for g in body['groups'] for n, _ in g})
for n in names:
    gar.vertex_groups.new(name=n)
tree = kdtree.KDTree(len(BP))
for i, co in enumerate(BP):
    tree.insert(co, i)
tree.balance()
for vi, co in enumerate(P):
    acc = {}
    for _, i, d in tree.find_n(co, 6):
        w = 1 / (d + 1e-4)
        for n, x in body['groups'][i]:
            acc[n] = acc.get(n, 0) + w * x
    top = sorted(acc.items(), key=lambda kv: -kv[1])[:4]
    s = sum(x for _, x in top)
    for n, x in top:
        gar.vertex_groups[n].add([vi], x / s, 'REPLACE')

# Previews, same cameras as drape_blender.py
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
scene.render.resolution_x, scene.render.resolution_y = 700, 900
mid = np.array([0, 0, 1.18])
cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam'))
scene.collection.objects.link(cam)
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 0.95
for name, eye in (('front', (0, 3, 1.18)), ('side', (-3, 0, 1.18)), ('back', (0, -3, 1.18))):
    cam.location = eye
    d = mid - np.asarray(eye)
    cam.rotation_euler = (math.atan2(math.hypot(d[0], d[1]), -d[2]), 0, math.atan2(d[1], d[0]) - math.pi / 2)
    scene.camera = cam
    scene.render.filepath = str(OUT / f'{STEM}_{name}.png')
    bpy.ops.render.render(write_still=True)

# Export: garment + skeleton
mod = gar.modifiers.new('Armature', 'ARMATURE')
mod.object = arm_ob
gar.parent = arm_ob
bpy.ops.object.select_all(action='DESELECT')
gar.select_set(True)
arm_ob.select_set(True)
bpy.context.view_layer.objects.active = gar
bpy.ops.export_scene.gltf(filepath=str(OUT / f'{STEM}.glb'), export_format='GLB', use_selection=True,
                          export_yup=True, export_skins=True, export_animations=False, export_morph=False)
print('wrote', OUT / f'{STEM}.glb')
