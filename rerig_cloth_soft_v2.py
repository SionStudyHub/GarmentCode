"""Soft-cloth re-rig v2 — fixes blocky/faceted + armpit tearing on EveryWear/Marvelous shirts.

YOUR CASE: GarmentCode -> Marvelous sim -> EveryWear rig -> duplicate armature.
Problem with v1: raw POLYINTERP_NEAREST transfer preserves Body's hard
shoulder/chest transitions + EveryWear triangulated mesh shades faceted,
so bends look blocky and armpits tear.

V2 PIPELINE (run in your OPEN .blend, shirt selected):
  1. Mesh cleanup: merge doubles 0.2mm, recalc normals outside, shade smooth
     (fixes "solid/faceted in still" without changing shape).
  2. Weight transfer from Body (REST, frame 0) with gentle clean 0.0001
     (keeps soft falloff tails that v1 cut off at 0.001).
  3. Topological SMOOTH 5x -> limit 4 -> normalize -> SMOOTH 3x -> normalize
     (this is the actual fix for blocky bending + armpit tear).
  4. Armature first with use_deform_preserve_volume=True, optional
     Corrective-Smooth after it to un-pinch armpits during animation.
  5. Drift check + report rigid-vert % (verts stuck to 1 bone >0.99).

USAGE: Text Editor -> Open this file -> Run Script (shirt selected).
FLAGS below control smoothing strength / cleanup / corrective.
"""

import bpy

# ==================== CONFIGURATION ====================
GARMENT_OBJECT_NAME = None   # None = active selection
CORRECT_ARMATURE_NAME = "Armature"
DELETE_DUPLICATE = True
# Mesh cleanup (fixes faceted/solid look):
MERGE_DISTANCE_M = 0.0002    # 0.2mm weld — closes Marvelous micro-cracks, keeps detail
DO_TRIS_TO_QUADS = False     # True = softer shading but slightly alters topology; keep False for sim mesh
SHADE_SMOOTH = True
# Weight softness (fixes blocky bending / armpit tear):
SMOOTH_REPEAT_1 = 5
SMOOTH_REPEAT_2 = 3
SMOOTH_FACTOR = 0.5
CLEAN_LIMIT = 0.0001         # gentler than v1's 0.001 — preserves blend tails
# Deform stack:
PRESERVE_VOLUME = True
ADD_CORRECTIVE_SMOOTH = True # smooths armpit pinch during pose; delete later if unwanted
CORRECTIVE_FACTOR = 0.5
CORRECTIVE_REPEAT = 2
# =======================================================


def log(m):
    print(f"[SoftRig] {m}")


def find_correct():
    arms = [o for o in bpy.data.objects if o.type == 'ARMATURE']
    if not arms:
        raise RuntimeError("No armature in scene!")
    if len(arms) == 1:
        return arms[0]
    for src in (bpy.data.objects.get("Body"), bpy.data.objects.get("Face")):
        if src and src.parent and src.parent.type == 'ARMATURE':
            log(f"Correct = parent of {src.name}: {src.parent.name}")
            return src.parent
    if CORRECT_ARMATURE_NAME in bpy.data.objects:
        return bpy.data.objects[CORRECT_ARMATURE_NAME]
    raise RuntimeError(f"Ambiguous armatures: {[a.name for a in arms]}")


def find_garment():
    ignore = {"Body", "Face"}
    if GARMENT_OBJECT_NAME and GARMENT_OBJECT_NAME in bpy.data.objects:
        return bpy.data.objects[GARMENT_OBJECT_NAME]
    a = bpy.context.active_object
    if a and a.type == 'MESH' and a.name not in ignore and "Collider" not in a.name:
        return a
    for o in bpy.context.selected_objects:
        if o.type == 'MESH' and o.name not in ignore and "Collider" not in o.name:
            return o
    best, bn = None, -1
    for o in bpy.data.objects:
        if o.type == 'MESH' or o.name in ignore or "Collider" in o.name:
            pass
        if o.type == 'MESH' and o.name not in ignore and "Collider" not in o.name:
            n = len(o.data.vertices)
            if n > bn:
                best, bn = o, n
    if best:
        return best
    raise RuntimeError("Select your shirt and re-run.")


def main():
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    correct = find_correct()
    garment = find_garment()
    body = bpy.data.objects.get("Body")
    if not body:
        raise RuntimeError("Missing 'Body'!")
    wrong = None
    if garment.parent and garment.parent.type == 'ARMATURE' and garment.parent != correct:
        wrong = garment.parent
    else:
        for m in garment.modifiers:
            if m.type == 'ARMATURE' and m.object and m.object != correct:
                wrong = m.object
                break
        if not wrong:
            others = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != correct]
            if len(others) == 1:
                wrong = others[0]

    log(f"Garment '{garment.name}' {len(garment.data.vertices)}v {len(garment.vertex_groups)}g -> '{correct.name}'")
    if wrong:
        log(f"Duplicate: '{wrong.name}'")
    correct_bones = set(b.name for b in correct.data.bones)

    bpy.context.view_layer.update()
    pre = [garment.matrix_world @ v.co for v in list(garment.data.vertices)[:8]]

    saved = {}
    for arm in ([correct] + ([wrong] if wrong and wrong != correct else [])):
        saved[arm.name] = arm.data.pose_position
        arm.data.pose_position = 'REST'
    sframe = bpy.context.scene.frame_current
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.update()

    try:
        bpy.ops.object.select_all(action='DESELECT')
        garment.select_set(True)
        bpy.context.view_layer.objects.active = garment
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Mute sim modifiers during transfer
        muted = []
        for m in garment.modifiers:
            if m.type in {'CLOTH', 'COLLISION', 'SURFACE_DEFORM', 'MESH_DEFORM', 'LATTICE', 'CURVE', 'CORRECTIVE_SMOOTH'}:
                try:
                    if m.show_viewport:
                        m.show_viewport = False
                        muted.append(m.name)
                except Exception:
                    pass
        for m in list(garment.modifiers):
            if m.type in {'ARMATURE', 'DATA_TRANSFER'}:
                garment.modifiers.remove(m)
        if garment.parent:
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        if garment.data.shape_keys:
            log("WARNING: shape keys present — skipping transform_apply.")
        else:
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # ---- MESH CLEANUP (faceted/solid fix, shape-preserving) ----
        me = garment.data
        # merge doubles + recalc normals in Edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        before = len(me.vertices)
        bpy.ops.mesh.remove_doubles(threshold=MERGE_DISTANCE_M)
        bpy.ops.mesh.normals_make_consistent(inside=False)
        if DO_TRIS_TO_QUADS:
            try:
                bpy.ops.mesh.tris_convert_to_quads(face_threshold=40, shape_threshold=40)
            except Exception as e:
                log(f"tris_to_quads skipped: {e}")
        bpy.ops.object.mode_set(mode='OBJECT')
        after = len(garment.data.vertices)
        log(f"Mesh cleanup: {before}->{after} verts (merged {before-after}), normals outside.")
        if SHADE_SMOOTH:
            try:
                bpy.ops.object.shade_smooth()
            except Exception:
                pass
            # auto-smooth by angle keeps seams crisp but faces soft (Blender 4/5)
            try:
                bpy.ops.object.shade_auto_smooth()
            except Exception:
                pass

        garment.vertex_groups.clear()

        # ---- TRANSFER ----
        dt = garment.modifiers.new("WeightTransfer", 'DATA_TRANSFER')
        dt.object = body
        dt.use_vert_data = True
        dt.data_types_verts = {'VGROUP_WEIGHTS'}
        dt.vert_mapping = 'POLYINTERP_NEAREST'
        try:
            dt.layers_vgroup_select_src = 'ALL'
            dt.layers_vgroup_select_dst = 'NAME'
        except Exception:
            pass
        bpy.ops.object.datalayout_transfer(modifier="WeightTransfer")
        bpy.ops.object.modifier_apply(modifier="WeightTransfer")
        log(f"Transferred: {len(garment.vertex_groups)} raw groups.")

        # ---- SOFT PIPELINE (the fix) ----
        # Note: vertex_group_smooth.poll() requires WEIGHT_PAINT mode in Blender 5.x
        def smooth_all(factor, repeat):
            bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
            bpy.ops.object.vertex_group_smooth(group_select_mode='ALL', factor=factor, repeat=repeat)
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=CLEAN_LIMIT)
        smooth_all(SMOOTH_FACTOR, SMOOTH_REPEAT_1)
        log(f"Smoothed {SMOOTH_REPEAT_1}x f={SMOOTH_FACTOR} (removes blocky islands).")
        bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
        bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)
        smooth_all(SMOOTH_FACTOR, SMOOTH_REPEAT_2)
        # smooth re-expands beyond 4 bones — clamp again for clean game-ready weights
        bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
        bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)
        log(f"Limit 4 + normalize + smooth {SMOOTH_REPEAT_2}x + limit 4 + normalize.")

        # Prune by NAME (index-shift safe)
        idx2name = {vg.index: vg.name for vg in garment.vertex_groups}
        used_names = set()
        rigid = 0
        for v in garment.data.vertices:
            top = 0.0
            for g in v.groups:
                if g.weight > 0.001 and g.group in idx2name:
                    used_names.add(idx2name[g.group])
                top = max(top, g.weight)
            if top > 0.99:
                rigid += 1
        for vg in list(garment.vertex_groups):
            if vg.name not in used_names or vg.name not in correct_bones:
                garment.vertex_groups.remove(vg)
        log(f"Kept {len(garment.vertex_groups)} bones. Rigid verts (>0.99 one bone): {rigid}/{len(garment.data.vertices)} ({100.0*rigid/max(1,len(garment.data.vertices)):.1f}%). Lower is softer.")

        # ---- PARENT + STACK ----
        garment.parent = correct
        garment.matrix_parent_inverse = correct.matrix_world.inverted()
        arm_mod = garment.modifiers.new("Armature", 'ARMATURE')
        arm_mod.object = correct
        try:
            arm_mod.use_deform_preserve_volume = PRESERVE_VOLUME
        except Exception:
            pass
        while garment.modifiers.find("Armature") > 0:
            try:
                bpy.ops.object.modifier_move_up(modifier="Armature")
            except Exception:
                break
        if ADD_CORRECTIVE_SMOOTH and "CorrectiveSmooth" not in garment.modifiers:
            try:
                cs = garment.modifiers.new("CorrectiveSmooth", 'CORRECTIVE_SMOOTH')
                cs.factor = CORRECTIVE_FACTOR
                cs.iterations = CORRECTIVE_REPEAT
                cs.use_only_smooth = True
                log(f"Added Corrective Smooth f={CORRECTIVE_FACTOR} x{CORRECTIVE_REPEAT} (un-pinches armpits).")
            except Exception as e:
                log(f"Corrective smooth skipped: {e}")

        for mn in muted:
            m = garment.modifiers.get(mn)
            if m:
                try:
                    m.show_viewport = True
                except Exception:
                    pass
    finally:
        for arm in ([correct] + ([wrong] if wrong and wrong != correct else [])):
            try:
                arm.data.pose_position = saved[arm.name]
            except Exception:
                pass
        bpy.context.scene.frame_set(sframe)
        bpy.context.view_layer.update()

    bpy.context.view_layer.update()
    post = [garment.matrix_world @ v.co for v in list(garment.data.vertices)[:8]]
    drift = max((a - b).length for a, b in zip(pre, post))
    log(f"Drift: {drift*1000:.3f}mm. Scrub to Spin/Peace Sign — armpits should bend soft, no tear.")
    if wrong and DELETE_DUPLICATE and wrong != correct:
        used_by = [o.name for o in bpy.data.objects if o.parent == wrong]
        if not used_by:
            wrong_name = wrong.name
            bpy.data.objects.remove(wrong, do_unlink=True)
            log(f"Deleted duplicate '{wrong_name}'.")
    log("SUCCESS — v2 soft rig done.")


if __name__ == "__main__":
    main()
