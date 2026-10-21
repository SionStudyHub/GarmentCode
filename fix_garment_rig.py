"""Robust Garment Rigging & Reset Tool for Blender.

Fixes the "shirt became huge, flipped, or displaced" issue caused by:
1. Armature being in animated Pose Position during weight transfer.
2. Unapplied scale/rotation or stale parent transforms from Everywear/GLB.

Usage:
1. In Blender, select your SHIRT object.
2. Run this script (Text Editor -> Run Script, or paste in Python Console).
"""

import bpy

def fix_and_rig():
    # 1. Identify selected garment
    garment = bpy.context.active_object
    ignore_names = {"Body", "Face", "Armature"}
    
    if not garment or garment.name in ignore_names or garment.type != 'MESH':
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH' and obj.name not in ignore_names:
                garment = obj
                break
                
    if not garment or garment.name in ignore_names:
        raise RuntimeError("Please select your shirt / garment object in the 3D Viewport first!")

    body = bpy.data.objects.get("Body")
    armature = bpy.data.objects.get("Armature")
    
    if not body or not armature:
        raise RuntimeError("Scene is missing 'Body' or 'Armature'!")

    print(f"[FixRig] Processing garment: '{garment.name}'...")

    # 2. Put Armature in REST POSITION (freezes avatar in bind T-pose)
    original_pose_pos = armature.data.pose_position
    armature.data.pose_position = 'REST'
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.update()

    # 3. Clear existing parent (keep visual transform) and apply all transforms
    bpy.context.view_layer.objects.active = garment
    garment.select_set(True)
    
    # Remove any old armature modifiers
    for mod in list(garment.modifiers):
        if mod.type == 'ARMATURE':
            garment.modifiers.remove(mod)
            
    # Clear parent safely
    if garment.parent:
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        
    # Apply Location, Rotation, and Scale so mesh coords match world space exactly
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    print(f"[FixRig] Transforms baked: loc={garment.location}, rot={garment.rotation_euler}, scale={garment.scale}")

    # 4. Clear old / wrong vertex groups
    garment.vertex_groups.clear()

    # 5. Transfer exact surface weights from Body
    dt = garment.modifiers.new("WeightTransfer", 'DATA_TRANSFER')
    dt.object = body
    dt.use_vert_data = True
    dt.data_types_verts = {'VGROUP_WEIGHTS'}
    dt.vert_mapping = 'POLYINTERP_NEAREST'

    bpy.ops.object.datalayout_transfer(modifier="WeightTransfer")
    bpy.ops.object.modifier_apply(modifier="WeightTransfer")

    # 5b. Anatomical Bone Isolation (Eliminates armpit webbing & rubbery stretching)
    torso_bones = {'Root', 'J_Bip_C_Hips', 'J_Bip_C_Spine', 'J_Bip_C_Chest', 'J_Bip_C_UpperChest', 'J_Sec_L_Bust1', 'J_Sec_L_Bust2', 'J_Sec_R_Bust1', 'J_Sec_R_Bust2', 'J_Bip_C_Neck', 'J_Bip_C_Head'}
    l_arm_bones = {'J_Bip_L_Shoulder', 'J_Bip_L_UpperArm', 'J_Bip_L_LowerArm', 'J_Bip_L_Hand'}
    r_arm_bones = {'J_Bip_R_Shoulder', 'J_Bip_R_UpperArm', 'J_Bip_R_LowerArm', 'J_Bip_R_Hand'}

    vg_map = {vg.name: vg for vg in garment.vertex_groups}

    for v in garment.data.vertices:
        x = v.co.x
        # Torso center: strictly no arm bones pulling ribs
        if abs(x) < 0.12:
            for b_name in (l_arm_bones | r_arm_bones):
                if b_name in vg_map:
                    vg_map[b_name].remove([v.index])
        # Left sleeve: strictly no torso/hips or right arm bones
        elif x > 0.18:
            for b_name in (torso_bones | r_arm_bones):
                if b_name in vg_map:
                    vg_map[b_name].remove([v.index])
        # Right sleeve: strictly no torso/hips or left arm bones
        elif x < -0.18:
            for b_name in (torso_bones | l_arm_bones):
                if b_name in vg_map:
                    vg_map[b_name].remove([v.index])

    # 6. Clean, clamp bone influences to 4, and normalize
    bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.001)
    bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
    bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)

    # 7. Prune unused bone groups
    used_indices = set()
    for v in garment.data.vertices:
        for g in v.groups:
            if g.weight > 0.001:
                used_indices.add(g.group)

    to_remove = [vg for vg in garment.vertex_groups if vg.index not in used_indices]
    for vg in to_remove:
        garment.vertex_groups.remove(vg)

    # 8. Re-parent to Armature safely with correct matrix parent inverse
    garment.parent = armature
    garment.matrix_parent_inverse = armature.matrix_world.inverted()
    
    arm_mod = garment.modifiers.new("Armature", 'ARMATURE')
    arm_mod.object = armature

    # 9. Restore Armature to POSE POSITION
    armature.data.pose_position = original_pose_pos
    bpy.context.view_layer.update()

    print(f"[SUCCESS] '{garment.name}' successfully rigged to Armature! Active bones: {len(garment.vertex_groups)}")

if __name__ == "__main__":
    fix_and_rig()
