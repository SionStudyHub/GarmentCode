"""Turn Marvelous Designer's EveryWear FBX + OBJ output into a clean rigged GLB for the fitting viewer.

Two sources are combined, because neither is enough on its own:

  * the FBX carries the 188-bone skeleton (in the drape pose in `pose.bones`) and the EveryWear
    skin weights, but `MetaverseConverter::Export` welds seam vertices across pattern sewing lines
    (creating stretched bridge triangles when 2D-sewn edges sit apart in 3D) and writes anonymous
    material slots (`Material803526`) with no texture paths;
  * the OBJ+MTL MD writes alongside it (`ExportOBJ`) preserves the exact unwelded per-pattern
    geometry, UVs, normals, real fabric names, base colours, and texture maps, in exact pattern
    order (`g <pattern>`), without cross-pattern seam welding.

This script:
  1. Parses the OBJ directly in pattern (`g`) order (avoiding Blender's `wm.obj_import`, which
     reorders faces by `usemtl`) to build the unwelded garment mesh with exact UVs and normals.
  2. Evaluates the FBX cloth mesh in its posed state (e.g. A-pose) and matches skin weights per
     pattern slot (`0..N-1`), ignoring any FBX vertices corrupted by cross-pattern seam welding
     (triangle edges > 20 mm).
  3. Cleans A-pose arm/shoulder proximity weight bleed from torso-dominant panels (panels where
     < 35% of vertices are arm-dominant and that are not adjacent to an arm-dominant sleeve panel),
     redirecting bled arm/shoulder weight to the upper chest so unskinning between A-pose and
     T-pose never tears chest or torso panels.
  4. Applies the FBX armature's pose (`pose.armature_apply`) so the exported GLB skeleton stands in
     the exact pose in which the garment was draped (A-pose), and patches `baseColorFactor` into
     the GLB materials.
"""
import bpy
import json
from mathutils import Vector
from mathutils.kdtree import KDTree
from pathlib import Path

# The mesh/weight assembly below follows the validated Macaw EveryWear converter.
# Run with Blender -b -P everywear_to_glb.py -- garment.fbx garment.obj output.glb
import argparse
import sys
cli = argparse.ArgumentParser()
cli.add_argument('fbx', type=Path)
cli.add_argument('obj', type=Path)
cli.add_argument('output', type=Path)
args = cli.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
SRC_FBX, SRC_OBJ, DST = args.fbx, args.obj, args.output
SRC_MTL = SRC_OBJ.with_suffix('.mtl')

# How many slots may disagree on face count with the OBJ before we refuse to guess.
FACE_COUNT_TOLERANCE = 0.02
# Maximum clean triangle edge length (m) in the FBX mesh before an edge is treated as a
# cross-pattern seam-weld artifact and its endpoints excluded from weight transfer.
MAX_CLEAN_EDGE_M = 0.020
# Minimum share of arm-dominant vertices for a pattern slot to be considered a sleeve/arm panel.
SLEEVE_ARM_SHARE = 0.35
# Distance (m) within which a torso panel stitched to an actual sleeve panel keeps armhole weights.
SLEEVE_SEAM_REACH_M = 0.040


def read_mtl(path):
    """Material name -> {color, base_texture, normal_texture}, from a CLO MTL."""
    out, current = {}, None
    for line in path.read_text(errors='ignore').splitlines():
        parts = line.split()
        if not parts:
            continue
        key, args = parts[0], parts[1:]
        if key == 'newmtl':
            current = out.setdefault(args[0], {'color': (1, 1, 1), 'base_texture': None, 'normal_texture': None})
        elif current is None:
            continue
        elif key == 'Kd' and len(args) >= 3:
            current['color'] = tuple(float(v) for v in args[:3])
        elif key == 'map_Kd' and args:
            current['base_texture'] = args[-1]
        elif key == 'map_bump' and args:
            current['normal_texture'] = args[-1]
    return out


def parse_obj_unwelded(path):
    """Parse an MD garment OBJ directly in pattern (`g`) order without `usemtl` face sorting."""
    verts_yup = []
    uvs = []
    norms_yup = []
    order = []
    group_faces = {}
    faces_v = []
    faces_uv = []
    faces_vn = []
    faces_slot = []

    cur_group = None
    cur_slot = -1
    seen_group_mtl = set()

    with path.open(errors='ignore') as fh:
        for line in fh:
            if line.startswith('v '):
                p = line.split()
                x, y, z = float(p[1]), float(p[2]), float(p[3])
                # Blender Z-up world coordinates: (x, -z, y)
                verts_yup.append((x, -z, y))
            elif line.startswith('vt '):
                p = line.split()
                uvs.append((float(p[1]), float(p[2])))
            elif line.startswith('vn '):
                p = line.split()
                nx, ny, nz = float(p[1]), float(p[2]), float(p[3])
                norms_yup.append((nx, -nz, ny))
            elif line.startswith('g '):
                cur_group = line[2:].strip()
                group_faces.setdefault(cur_group, 0)
            elif line.startswith('usemtl ') and cur_group is not None and cur_group not in seen_group_mtl:
                seen_group_mtl.add(cur_group)
                cur_slot = len(order)
                order.append((cur_group, line[7:].strip()))
            elif line.startswith('f ') and cur_slot >= 0:
                parts = line.split()[1:]
                fv, fuv, fvn = [], [], []
                for tok in parts:
                    vals = tok.split('/')
                    fv.append(int(vals[0]) - 1)
                    fuv.append(int(vals[1]) - 1 if len(vals) > 1 and vals[1] else -1)
                    fvn.append(int(vals[2]) - 1 if len(vals) > 2 and vals[2] else -1)
                faces_v.append(fv)
                faces_uv.append(fuv)
                faces_vn.append(fvn)
                faces_slot.append(cur_slot)
                group_faces[cur_group] += 1

    if verts_yup and max(abs(c) for v in verts_yup for c in v) > 10.0:
        verts_yup = [(x * 0.001, y * 0.001, z * 0.001) for x, y, z in verts_yup]

    return {
        'verts': verts_yup,
        'uvs': uvs,
        'norms': norms_yup,
        'order': order,
        'group_faces': group_faces,
        'faces_v': faces_v,
        'faces_uv': faces_uv,
        'faces_vn': faces_vn,
        'faces_slot': faces_slot,
    }


def make_material(name, spec):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = False
    nt = mat.node_tree
    bsdf = nt.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*spec['color'], 1.0)
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = 0.35
    bsdf.inputs['Specular IOR Level'].default_value = 0.6
    for tex_path, is_normal in ((spec['base_texture'], False), (spec['normal_texture'], True)):
        if not tex_path:
            continue
        p = Path(tex_path)
        if not p.exists():
            print('  missing texture', p, flush=True)
            continue
        image = bpy.data.images.load(str(p), check_existing=True)
        sampler = nt.nodes.new('ShaderNodeTexImage')
        sampler.image = image
        sampler.location = (-700, -200 if is_normal else 250)
        if is_normal:
            node = nt.nodes.new('ShaderNodeNormalMap')
            node.location = (-400, -200)
            nt.links.new(sampler.outputs['Color'], node.inputs['Color'])
            nt.links.new(node.outputs['Normal'], bsdf.inputs['Normal'])
        else:
            nt.links.new(sampler.outputs['Color'], bsdf.inputs['Base Color'])
    return mat


def patch_base_color_factors(glb_path, order, mtl):
    """glTF tints a material with baseColorTexture * baseColorFactor.

    Blender's exporter drops baseColorFactor whenever Base Color is linked to an image, so the
    fabric colours MD wrote into the MTL would be lost and every panel would come out the pale
    colour of the raw taffeta texture.  glTF's own rule is texture * factor, so writing the Kd
    back into the factor is the exact inverse of what the exporter left out.
    """
    color_of = {pattern: list(mtl[md_material]['color']) + [1.0] for pattern, md_material in order}
    raw = glb_path.read_bytes()
    if raw[:4] != b'glTF':
        raise SystemExit(f'{glb_path} is not a GLB')
    chunks, offset = [], 12
    while offset < len(raw):
        length = int.from_bytes(raw[offset:offset + 4], 'little')
        kind = raw[offset + 4:offset + 8]
        chunks.append([kind, bytearray(raw[offset + 8:offset + 8 + length])])
        offset += 8 + length + ((4 - (length % 4)) % 4)

    patched = 0
    for chunk in chunks:
        if chunk[0] != b'JSON':
            continue
        doc = json.loads(bytes(chunk[1]).decode('utf-8'))
        for material in doc.get('materials', []):
            factor = color_of.get(material.get('name'))
            if not factor:
                continue
            material.setdefault('pbrMetallicRoughness', {})['baseColorFactor'] = [round(v, 6) for v in factor]
            patched += 1
        chunk[1] = bytearray(json.dumps(doc, separators=(',', ':')).encode('utf-8'))
        # glTF pads the JSON chunk to 4 bytes with spaces; JSON.parse rejects NUL padding.
        chunk[1] += bytearray(b' ' * ((4 - (len(chunk[1]) % 4)) % 4))
        break

    body = bytearray()
    for kind, payload in chunks:
        body += len(payload).to_bytes(4, 'little') + kind + bytes(payload)
    glb_path.write_bytes(b'glTF' + (2).to_bytes(4, 'little') + (12 + len(body)).to_bytes(4, 'little') + bytes(body))
    print('PATCHED baseColorFactor on', patched, 'materials', flush=True)
    return patched


def is_arm_bone(name):
    return any(tok in name for tok in ('Arm', 'Hand', 'Wrist', 'Elbow', 'Thumb', 'Index', 'Middle', 'Ring', 'Little'))


def is_shoulder_bone(name):
    return 'Shoulder' in name


mtl = read_mtl(SRC_MTL)
obj_data = parse_obj_unwelded(SRC_OBJ)
order = obj_data['order']
obj_faces = obj_data['group_faces']
print('MTL materials:', len(mtl), ' OBJ groups:', len(order), ' OBJ verts:', len(obj_data['verts']), ' OBJ faces:', len(obj_data['faces_v']), flush=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(SRC_FBX))
fbx_cloth = next(o for o in bpy.context.scene.objects if o.type == 'MESH' and o.name.startswith('Cloth'))
armature = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')

if len(fbx_cloth.data.materials) != len(order):
    raise SystemExit(f'{len(fbx_cloth.data.materials)} FBX material slots but {len(order)} OBJ groups; cannot map them safely')

# MD orders both by pattern, so slot i is group i. Prove it before relying on it.
slot_faces = [0] * len(fbx_cloth.data.materials)
for poly in fbx_cloth.data.polygons:
    slot_faces[poly.material_index] += 1
mismatch = [i for i, (slot, (_, _)) in enumerate(zip(slot_faces, order))
            if abs(slot - obj_faces[order[i][0]]) > FACE_COUNT_TOLERANCE * max(slot, 1)]
if mismatch:
    for i in mismatch:
        print(f'  slot {i}: FBX {slot_faces[i]} faces vs OBJ {obj_faces[order[i][0]]} for {order[i][0]!r}', flush=True)
    raise SystemExit(f'material slots do not line up with the OBJ groups at {mismatch}; refusing to guess')

# 1. Evaluate the FBX cloth mesh in its posed state (e.g. A-pose) so its positions match the draped OBJ.
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
eval_mesh = fbx_cloth.evaluated_get(dg).to_mesh()
mw = fbx_cloth.matrix_world
fbx_world_co = [mw @ v.co for v in eval_mesh.vertices]

# Identify FBX vertices corrupted by cross-pattern seam welding (incident to any triangle edge > MAX_CLEAN_EDGE_M).
bad_fbx_verts = set()
slot_fbx_verts = [set() for _ in range(len(order))]
for poly in eval_mesh.polygons:
    vs = poly.vertices
    s = poly.material_index
    for v in vs:
        slot_fbx_verts[s].add(v)
    for k in range(len(vs)):
        v0, v1 = vs[k], vs[(k + 1) % len(vs)]
        if (fbx_world_co[v0] - fbx_world_co[v1]).length > MAX_CLEAN_EDGE_M:
            bad_fbx_verts.add(v0)
            bad_fbx_verts.add(v1)
fbx_cloth.evaluated_get(dg).to_mesh_clear()

# Build per-slot KDTrees of clean FBX vertices.
slot_kd = []
for s in range(len(order)):
    clean = sorted(slot_fbx_verts[s] - bad_fbx_verts)
    if not clean:
        clean = sorted(slot_fbx_verts[s])
    kd = KDTree(len(clean))
    for idx, fv in enumerate(clean):
        kd.insert(fbx_world_co[fv], idx)
    kd.balance()
    slot_kd.append((kd, clean))

# Extract raw FBX weights per vertex: list of (group_name, weight).
fbx_group_names = {g.index: g.name for g in fbx_cloth.vertex_groups}
fbx_weights = []
for v in fbx_cloth.data.vertices:
    fbx_weights.append([(fbx_group_names[g.group], g.weight) for g in v.groups if g.weight > 1e-6])

# Determine which pattern slots are actual sleeve/arm panels vs torso/skirt panels.
slot_is_sleeve = [False] * len(order)
sleeve_pts = []
for s in range(len(order)):
    vs = slot_fbx_verts[s]
    arm_dom = 0
    for fv in vs:
        w_arm = sum(w for n, w in fbx_weights[fv] if is_arm_bone(n) or is_shoulder_bone(n))
        w_other = sum(w for n, w in fbx_weights[fv] if not (is_arm_bone(n) or is_shoulder_bone(n)))
        if w_arm > w_other:
            arm_dom += 1
    if vs and (arm_dom / len(vs)) >= SLEEVE_ARM_SHARE:
        slot_is_sleeve[s] = True
        for fv in vs - bad_fbx_verts:
            sleeve_pts.append(fbx_world_co[fv])

sleeve_kd = None
if sleeve_pts:
    sleeve_kd = KDTree(len(sleeve_pts))
    for idx, pt in enumerate(sleeve_pts):
        sleeve_kd.insert(pt, idx)
    sleeve_kd.balance()

# Target upper-chest bone for redirecting stray A-pose arm bleed on torso panels.
bone_names = {b.name for b in armature.data.bones}
upper_chest_bone = 'J_Adj_C_UpperChest' if 'J_Adj_C_UpperChest' in bone_names else (
    'J_Bip_C_UpperChest' if 'J_Bip_C_UpperChest' in bone_names else 'J_Bip_C_Chest'
)

# 2. Build the clean unwelded Blender mesh from SRC_OBJ.
mesh_data = bpy.data.meshes.new('Cloth_Mesh')
mesh_data.from_pydata(obj_data['verts'], [], obj_data['faces_v'])
mesh_data.update()

for slot, (pattern, md_material) in enumerate(order):
    spec = mtl.get(md_material)
    if spec is None:
        raise SystemExit(f'no MTL entry for {md_material!r} (group {pattern!r})')
    mesh_data.materials.append(make_material(pattern, spec))
    print(f'  slot {slot:2d} {pattern[:44]:46} -> {md_material[:44]}', flush=True)

for poly, slot in zip(mesh_data.polygons, obj_data['faces_slot']):
    poly.material_index = slot
    poly.use_smooth = True

if obj_data['uvs']:
    uv_layer = mesh_data.uv_layers.new(name='UVMap')
    loop_idx = 0
    for fuv in obj_data['faces_uv']:
        for uv_i in fuv:
            uv_layer.data[loop_idx].uv = obj_data['uvs'][uv_i] if uv_i >= 0 else (0.0, 0.0)
            loop_idx += 1

# Map each OBJ vertex to its pattern slot(s).
obj_vert_slot = [0] * len(obj_data['verts'])
for fv, slot in zip(obj_data['faces_v'], obj_data['faces_slot']):
    for v_i in fv:
        obj_vert_slot[v_i] = slot

# 3. For sleeved garments (draped on A-pose arms), bake the A-pose into the rest pose.
# For sleeveless/strapless garments (torso/hip/leg bones only, which are identical in T and A pose),
# reset pose bones to T-pose rest so the importer does not push torso panels away from lowered A-pose arms.
bpy.data.objects.remove(fbx_cloth, do_unlink=True)
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')
if any(slot_is_sleeve):
    bpy.ops.pose.armature_apply(selected=False)
else:
    for pb in armature.pose.bones:
        pb.matrix_basis.identity()
bpy.ops.object.mode_set(mode='OBJECT')

# Compute the upper vertical limit of the bust region from the neck bone head height (neck_z - 60 mm).
neck_bone = armature.data.bones.get('J_Adj_C_Neck') or armature.data.bones.get('J_Bip_C_Neck')
max_bust_z = (armature.matrix_world @ neck_bone.head_local).z - 0.060 if neck_bone else None

cloth = bpy.data.objects.new('Cloth', mesh_data)
bpy.context.scene.collection.objects.link(cloth)
cloth.parent = armature
cloth.matrix_parent_inverse = armature.matrix_world.inverted()
arm_mod = cloth.modifiers.new(name='Armature', type='ARMATURE')
arm_mod.object = armature

# Create vertex groups matching the armature's bones and assign per-slot weights.
vgroups = {b.name: cloth.vertex_groups.new(name=b.name) for b in armature.data.bones}
exact_matches = 0
repaired_seams = 0
redirected_bleed = 0

for v_i, co in enumerate(obj_data['verts']):
    s = obj_vert_slot[v_i]
    kd, clean = slot_kd[s]
    pt = Vector(co)
    _, idx, dist = kd.find(pt)
    if dist < 1e-4:
        exact_matches += 1
    else:
        repaired_seams += 1
    raw = fbx_weights[clean[idx]]

    # Strip A-pose arm/shoulder proximity bleed on torso panels (unless near an actual sleeve seam).
    strip_arm = not slot_is_sleeve[s]
    if strip_arm and sleeve_kd is not None:
        _, _, sdist = sleeve_kd.find(pt)
        if sdist <= SLEEVE_SEAM_REACH_M:
            strip_arm = False

    bust_fade = 0.0
    if max_bust_z is not None and pt.z > max_bust_z:
        bust_fade = min(1.0, (pt.z - max_bust_z) / 0.015)

    merged = {}
    had_bleed = False
    for bname, w in raw:
        if strip_arm and (is_arm_bone(bname) or is_shoulder_bone(bname)):
            bname = upper_chest_bone
            had_bleed = True
        elif bust_fade > 0.0 and 'Bust' in bname:
            keep = w * (1.0 - bust_fade)
            redir = w * bust_fade
            if keep > 1e-6 and bname in vgroups:
                merged[bname] = merged.get(bname, 0.0) + keep
            if redir > 1e-6 and upper_chest_bone in vgroups:
                merged[upper_chest_bone] = merged.get(upper_chest_bone, 0.0) + redir
            had_bleed = True
            continue
        if bname in vgroups:
            merged[bname] = merged.get(bname, 0.0) + w
    if had_bleed:
        redirected_bleed += 1

    top = sorted(merged.items(), key=lambda kv: -kv[1])[:4]
    total = sum(w for _, w in top)
    if total > 0:
        for bname, w in top:
            vgroups[bname].add([v_i], w / total, 'REPLACE')

unweighted = sum(not any(g.weight > 1e-7 for g in v.groups) for v in cloth.data.vertices)
max_sum_error = max(abs(sum(g.weight for g in v.groups) - 1) for v in cloth.data.vertices)
assert unweighted == 0, f'{unweighted} unweighted vertices'
assert max_sum_error < 1e-4, f'Weight normalization error {max_sum_error}'
assert len(armature.data.bones) == 188
print('VALIDATED', len(cloth.data.vertices), 'vertices, 188 bones, zero unweighted; max sum error', max_sum_error, flush=True)

print(f'WEIGHTS: {exact_matches} exact, {repaired_seams} seam-repaired, {redirected_bleed} bleed redirected (bad FBX verts excluded: {len(bad_fbx_verts)})', flush=True)

bpy.ops.object.select_all(action='DESELECT')
cloth.select_set(True)
armature.select_set(True)
bpy.context.view_layer.objects.active = armature

bpy.ops.export_scene.gltf(
    filepath=str(DST),
    export_format='GLB',
    use_selection=True,
    export_skins=True,
    export_apply=False,
    export_yup=True,
)

print('EXPORTED', DST, flush=True)
print('SLOTS', len(cloth.data.materials), 'IMAGES', len(bpy.data.images), 'BONES', len(armature.data.bones), flush=True)
patch_base_color_factors(DST, order, mtl)