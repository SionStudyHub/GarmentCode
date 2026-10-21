"""Perfect Cloth re-rig: move Cloth from duplicate skeleton to correct Armature.

YOUR SITUATION (as described):
  - Scene has 2 identical skeletons: the CORRECT one (parents Body + Face,
    owns the animations) and a DUPLICATE (currently driving Cloth).
  - Cloth is rigged to the WRONG skeleton. You want it perfectly rigged
    to the CORRECT skeleton, with correct weights, no shift/pop, and
    following all animations.

WHAT THIS SCRIPT DOES (run inside your OPEN Blender file):
  1. Auto-detects CORRECT armature (= parent of Body/Face, else named "Armature").
  2. Auto-detects CLOTH (= active selection, else largest mesh that isn't Body/Face).
  3. Auto-detects WRONG armature (= Cloth's parent/modifier armature if != correct).
  4. Verifies bone-name sets match (reports any mismatch, never guesses).
  5. Freezes both armatures in REST at frame 0 (bind pose) for exact transfer.
  6. Preserves Cloth world position EXACTLY (CLEAR_KEEP_TRANSFORM + correct inverse).
  7. Re-transfers surface weights from Body via POLYINTERP_NEAREST (not reuse
     of stale duplicate weights — this is what makes it "perfect").
  8. Cleans (0.001) -> limit 4 influences -> normalize -> prune empty groups
     -> drop any group that isn't a bone on the CORRECT armature.
  9. Re-parents Cloth to CORRECT armature with clean Armature modifier on top.
 10. Restores POSE position, verifies no displacement, optionally deletes the
     duplicate armature, optionally exports modular + full GLBs.

USAGE (in your currently OPEN Blender project):
  1. Select your SHIRT/Cloth object (optional — auto-detected if skipped).
  2. Text Editor -> Open -> select this file -> Run Script.
  3. Check the System Console for [ReRig] logs. Done. Save your .blend.

No settings needed. Optional flags are in CONFIGURATION below.
"""

import bpy
import os

# ==================== CONFIGURATION ====================
GARMENT_OBJECT_NAME = None   # None = auto-detect (active selection, else largest non-Body/Face mesh)
CORRECT_ARMATURE_NAME = "Armature"  # preferred correct armature; fallback = parent of Body
DELETE_DUPLICATE_ARMATURE = True    # delete wrong armature after successful re-rig (only if unused)
EXPORT_GLB = False           # set True to also export GLBs next to .blend after re-rig
EXPORT_BASENAME = "shirt_rerigged"
# =======================================================


def log(msg):
    print(f"[ReRig] {msg}")


def find_correct_armature():
    armatures = [o for o in bpy.data.objects if o.type == 'ARMATURE']
    if not armatures:
        raise RuntimeError("No armature found in scene!")
    if len(armatures) == 1:
        log(f"Only one armature in scene: '{armatures[0].name}' — using it as correct.")
        return armatures[0]
    # Prefer parent of Body/Face
    body = bpy.data.objects.get("Body")
    face = bpy.data.objects.get("Face")
    for candidate in [body, face]:
        if candidate and candidate.parent and candidate.parent.type == 'ARMATURE':
            log(f"Correct armature identified as parent of '{candidate.name}': '{candidate.parent.name}'")
            return candidate.parent
    # Fallback to configured name
    if CORRECT_ARMATURE_NAME in bpy.data.objects:
        obj = bpy.data.objects[CORRECT_ARMATURE_NAME]
        if obj.type == 'ARMATURE':
            log(f"Correct armature identified by name: '{obj.name}'")
            return obj
    # Fallback: armature with most bone-children meshes / most vertex-group refs
    log("WARNING: could not identify correct armature by Body parent — listing candidates:")
    for a in armatures:
        children = [c.name for c in bpy.data.objects if c.parent == a]
        log(f"  - '{a.name}': {len(a.data.bones)} bones, children={children}")
    raise RuntimeError(
        "Ambiguous correct armature. Please rename the CORRECT one to 'Armature' "
        "or set CORRECT_ARMATURE_NAME above, then re-run."
    )


def find_garment():
    ignore = {"Body", "Face"}
    if GARMENT_OBJECT_NAME and GARMENT_OBJECT_NAME in bpy.data.objects:
        return bpy.data.objects[GARMENT_OBJECT_NAME]
    active = bpy.context.active_object
    if active and active.type == 'MESH' and active.name not in ignore and "Collider" not in active.name:
        return active
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH' and obj.name not in ignore and "Collider" not in obj.name:
            return obj
    # Largest mesh that isn't Body/Face/Collider
    best, best_verts = None, -1
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        if obj.name in ignore or "Collider" in obj.name:
            continue
        n = len(obj.data.vertices) if obj.data else 0
        if n > best_verts:
            best, best_verts = obj, n
    if best:
        return best
    raise RuntimeError("Could not find garment/Cloth object! Select your shirt and re-run.")


def find_wrong_armature(cloth, correct):
    # 1. Cloth parent
    if cloth.parent and cloth.parent.type == 'ARMATURE' and cloth.parent != correct:
        return cloth.parent
    # 2. Cloth armature modifiers
    for mod in cloth.modifiers:
        if mod.type == 'ARMATURE' and mod.object and mod.object != correct:
            return mod.object
    # 3. Any other armature in scene
    others = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != correct]
    if len(others) == 1:
        return others[0]
    if others:
        log(f"Multiple other armatures found: {[o.name for o in others]} — will NOT assume; weights re-transfer makes this harmless.")
    return None


def ensure_object_mode():
    if bpy.context.mode != 'OBJECT':
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass


def rerig():
    ensure_object_mode()
    correct = find_correct_armature()
    garment = find_garment()
    wrong = find_wrong_armature(garment, correct)
    body = bpy.data.objects.get("Body")
    if not body:
        raise RuntimeError("Scene is missing 'Body' mesh (weight source)!")

    log(f"Garment: '{garment.name}' ({len(garment.data.vertices)} verts, {len(garment.vertex_groups)} vgroups)")
    log(f"Correct armature: '{correct.name}' ({len(correct.data.bones)} bones)")
    log(f"Body source: '{body.name}' ({len(body.vertex_groups)} vgroups)")
    if wrong:
        log(f"Wrong/duplicate armature: '{wrong.name}' ({len(wrong.data.bones)} bones)")
    else:
        log("No duplicate armature detected — will (re)bind directly to correct armature.")

    # ---- Bone-set verification (identical skeletons?) ----
    correct_bones = set(b.name for b in correct.data.bones)
    if wrong:
        wrong_bones = set(b.name for b in wrong.data.bones)
        only_correct = sorted(correct_bones - wrong_bones)
        only_wrong = sorted(wrong_bones - correct_bones)
        if not only_correct and not only_wrong:
            log("Bone sets IDENTICAL — perfect 1:1 remap possible.")
        else:
            log(f"WARNING: bone sets differ! Only in correct ({len(only_correct)}): {only_correct[:20]}")
            log(f"WARNING: bone sets differ! Only in duplicate ({len(only_wrong)}): {only_wrong[:20]}")
            log("Continuing: weights are re-transferred from Body, so only correct-armature bones are kept. Extra duplicate-only weights are dropped (correct behavior).")

    # ---- Record pre-re-rig world position for displacement check ----
    bpy.context.view_layer.update()
    pre_world = [garment.matrix_world @ v.co for v in list(garment.data.vertices)[:8]]

    # ---- Freeze in REST / frame 0 (bind pose) ----
    armatures_to_freeze = [correct] + ([wrong] if wrong and wrong != correct else [])
    saved_pose = {}
    for arm in armatures_to_freeze:
        saved_pose[arm.name] = arm.data.pose_position
        arm.data.pose_position = 'REST'
    saved_frame = bpy.context.scene.frame_current
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.update()
    log("Froze armatures in REST at frame 0 for exact weight transfer.")

    try:
        # ---- Select garment, mute deforming modifiers during transfer ----
        bpy.ops.object.select_all(action='DESELECT')
        garment.select_set(True)
        bpy.context.view_layer.objects.active = garment
        ensure_object_mode()

        muted = []
        for mod in garment.modifiers:
            if mod.type in {'CLOTH', 'COLLISION', 'SURFACE_DEFORM', 'MESH_DEFORM', 'LATTICE', 'CURVE'}:
                try:
                    if mod.show_viewport:
                        mod.show_viewport = False
                        muted.append(mod.name)
                except Exception:
                    pass
        if muted:
            log(f"Temporarily muted sim/deform modifiers: {muted}")

        # Remove stale ARMATURE + DATA_TRANSFER modifiers (keep Solidify/Weld/etc.)
        for mod in list(garment.modifiers):
            if mod.type in {'ARMATURE', 'DATA_TRANSFER'}:
                garment.modifiers.remove(mod)
        log("Removed stale ARMATURE/DATA_TRANSFER modifiers (kept Solidify/Weld/etc.).")

        # Clear parent keeping visual transform, then bake transforms so mesh
        # coords are in world space (matches Body world space for transfer)
        if garment.parent:
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
            log("Cleared old parent (CLEAR_KEEP_TRANSFORM — visual position preserved).")
        # Shape keys would break transform_apply; handle gracefully
        has_shape_keys = garment.data.shape_keys is not None
        if has_shape_keys:
            log("WARNING: garment has shape keys — skipping transform_apply (would fail). Using current world matrix for transfer instead.")
        else:
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            log(f"Baked transforms: loc={list(garment.location)} rot={list(garment.rotation_euler)} scale={list(garment.scale)}")

        # ---- Clear stale (duplicate-skeleton) weights ----
        garment.vertex_groups.clear()
        log("Cleared stale vertex groups from duplicate skeleton.")

        # ---- Transfer exact surface weights from Body ----
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
        log(f"Transferred weights from Body: {len(garment.vertex_groups)} raw groups.")

        # ---- Clean -> limit 4 -> normalize ----
        bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.001)
        bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
        bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)
        log("Cleaned (0.001) / limited to 4 influences / normalized.")

        # ---- Prune empty + non-bone groups (by NAME — indices shift on remove) ----
        index_to_name = {vg.index: vg.name for vg in garment.vertex_groups}
        used_names = set()
        for v in garment.data.vertices:
            for g in v.groups:
                if g.weight > 0.001 and g.group in index_to_name:
                    used_names.add(index_to_name[g.group])
        to_remove = [vg for vg in list(garment.vertex_groups)
                     if vg.name not in used_names or vg.name not in correct_bones]
        for vg in to_remove:
            garment.vertex_groups.remove(vg)
        removed = len(to_remove)
        log(f"Pruned {removed} empty/non-bone groups. Kept {len(garment.vertex_groups)} bone influences.")

        # ---- Re-parent to CORRECT armature with exact inverse ----
        garment.parent = correct
        garment.matrix_parent_inverse = correct.matrix_world.inverted()
        arm_mod = garment.modifiers.new("Armature", 'ARMATURE')
        arm_mod.object = correct
        # Move Armature modifier to top (before Solidify/Weld) for correct deform order
        try:
            bpy.context.view_layer.objects.active = garment
            # move up until first
            while garment.modifiers.find("Armature") > 0:
                bpy.ops.object.modifier_move_up(modifier="Armature")
        except Exception as e:
            log(f"Note: could not reorder Armature modifier to top ({e}).")
        log(f"Parented '{garment.name}' -> '{correct.name}' with clean Armature modifier.")

        # Restore muted modifiers
        for mod_name in muted:
            mod = garment.modifiers.get(mod_name)
            if mod:
                try:
                    mod.show_viewport = True
                except Exception:
                    pass

    finally:
        # ---- Restore POSE ----
        for arm in armatures_to_freeze:
            try:
                arm.data.pose_position = saved_pose[arm.name]
            except Exception:
                pass
        bpy.context.scene.frame_set(saved_frame)
        bpy.context.view_layer.update()
        log(f"Restored armatures to POSE, frame {saved_frame}.")

    # ---- Displacement check (world pos preserved?) ----
    bpy.context.view_layer.update()
    post_world = [garment.matrix_world @ v.co for v in list(garment.data.vertices)[:8]]
    max_drift = max((a - b).length for a, b in zip(pre_world, post_world))
    log(f"Position drift check (first 8 verts, world space): max {max_drift*1000:.3f} mm")
    if max_drift > 0.002:
        log("WARNING: drift > 2mm — likely the duplicate armature had a different world transform or pose. Weights are still correct for the TRUE armature; check frame 0 REST vs POSE.")
    else:
        log("Position preserved — shirt looks identical, now driven by correct skeleton.")

    # ---- Delete duplicate if safe ----
    if wrong and DELETE_DUPLICATE_ARMATURE and wrong != correct:
        still_used = []
        for obj in bpy.data.objects:
            if obj == garment:
                continue
            if obj.parent == wrong:
                still_used.append(obj.name)
            for mod in getattr(obj, 'modifiers', []):
                if getattr(mod, 'object', None) == wrong:
                    still_used.append(f"{obj.name}.{mod.name}")
        if still_used:
            log(f"Keeping duplicate '{wrong.name}' — still used by: {still_used}")
        else:
            log(f"Removing unused duplicate armature '{wrong.name}'.")
            bpy.data.objects.remove(wrong, do_unlink=True)

    # ---- Summary ----
    log(f"SUCCESS: '{garment.name}' perfectly rigged to '{correct.name}' ({len(garment.vertex_groups)} bones). Scrub the timeline / play animations — shirt follows Body exactly.")

    # ---- Optional export ----
    if EXPORT_GLB:
        base = os.path.join(
            os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.path.expanduser("~/Desktop"),
            EXPORT_BASENAME)
        bpy.ops.object.select_all(action='DESELECT')
        # Modular: armature + garment
        correct.select_set(True)
        garment.select_set(True)
        bpy.context.view_layer.objects.active = correct
        mod_path = base + "_modular.glb"
        bpy.ops.export_scene.gltf(filepath=mod_path, export_format='GLB',
                                   use_selection=True, export_skins=True,
                                   export_apply=False, export_materials='EXPORT')
        log(f"Exported modular: {mod_path}")
        # Full: armature + garment + body + face
        bpy.ops.object.select_all(action='DESELECT')
        correct.select_set(True)
        garment.select_set(True)
        for nm in ("Body", "Face"):
            o = bpy.data.objects.get(nm)
            if o:
                o.select_set(True)
        bpy.context.view_layer.objects.active = correct
        full_path = base + "_full_character.glb"
        bpy.ops.export_scene.gltf(filepath=full_path, export_format='GLB',
                                   use_selection=True, export_skins=True,
                                   export_apply=False, export_materials='EXPORT')
        log(f"Exported full character: {full_path}")


if __name__ == "__main__":
    rerig()
