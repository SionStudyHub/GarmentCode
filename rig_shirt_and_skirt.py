"""
Automated Garment Rigging Tool for Blender (Shirt & Skirt) - Natural Drape Edition
Fits and weights GarmentCode clothing to new_base_female avatar.

Key Improvements:
1. Breast / Chest Smooth Drape:
   - Completely strips upper arm bones from torso/breast panels so the arm never pulls on the breasts.
   - Preserves smooth natural cloth curvature without artificial folds or spikes.
2. Subtle Realistic Fabric Thickness:
   - Solidify modifier set to 0.2 mm (0.0002 m) for lightweight clothing.
3. No Shrinkwrap Artifacts:
   - Removed surface-point snapping that was causing lumps around concave breast/armpit areas.
4. Anti-Spike Protection:
   - Automated safety net guarantees 100% of vertices have active bone weights.
5. Preserves Skirt Rigging:
   - Clean pelvic and thigh weighting with no cross-leg dragging.
"""

import bpy
import bmesh
from mathutils import Vector

def ensure_all_vertices_weighted(garment, body_obj):
    """Guarantees that 100% of vertices have at least one valid bone weight."""
    unweighted = [
        v for v in garment.data.vertices 
        if len(v.groups) == 0 or sum(g.weight for g in v.groups) < 0.001
    ]
    if unweighted:
        print(f"[RigTool] Found {len(unweighted)} unassigned vertex/vertices on {garment.name}. Auto-healing from nearest body surface...")
        for v in unweighted:
            world_pt = garment.matrix_world @ v.co
            local_pt = body_obj.matrix_world.inverted() @ world_pt
            found, pt, normal, face_idx = body_obj.closest_point_on_mesh(local_pt)
            if found:
                poly = body_obj.data.polygons[face_idx]
                closest_bv = min(
                    [body_obj.data.vertices[vi] for vi in poly.vertices], 
                    key=lambda bv: (bv.co - pt).length
                )
                for g in closest_bv.groups:
                    vg_name = body_obj.vertex_groups[g.group].name
                    if vg_name not in garment.vertex_groups:
                        garment.vertex_groups.new(name=vg_name)
                    garment.vertex_groups[vg_name].add([v.index], g.weight, 'REPLACE')


def rig_clothing():
    body = bpy.data.objects.get("Body")
    armature = bpy.data.objects.get("Armature")

    if not body or not armature:
        raise RuntimeError("Scene must contain 'Body' mesh and 'Armature'!")

    ignore_names = {"Body", "Face", "Armature"}
    
    # 1. Identify garment candidate meshes
    candidates = []
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.name not in ignore_names and not obj.name.startswith("J_"):
            if obj.dimensions.z > 3.0:  # Filter out unscaled mm-imports
                continue
            candidates.append(obj)

    if not candidates:
        raise RuntimeError("No garment mesh objects found to rig!")

    print(f"[RigTool] Found {len(candidates)} garment candidate(s): {[c.name for c in candidates]}")

    # 2. Put Armature in REST position (matching the A-pose bind state)
    armature.data.pose_position = 'REST'
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.update()

    for garment in candidates:
        name_lower = garment.name.lower()
        z_mid = (garment.matrix_world @ Vector(garment.bound_box[0])).z + (garment.dimensions.z / 2.0)
        
        if any(k in name_lower for k in ["shirt", "tee", "top"]) or z_mid > 1.20:
            garment_type = "shirt"
        else:
            garment_type = "skirt"

        print(f"\n[RigTool] >>> Rigging '{garment.name}' as '{garment_type}' (Z-mid: {z_mid:.2f}m)...")

        bpy.context.view_layer.objects.active = garment
        garment.select_set(True)

        # Clear existing parent (keep visual transform)
        if garment.parent:
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        # Clear existing modifiers
        garment.modifiers.clear()

        # Bake transforms so mesh coordinates match world space
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # Clear vertex groups
        garment.vertex_groups.clear()

        # Surface Weight Transfer from Body
        dt = garment.modifiers.new(name="WeightTransfer", type='DATA_TRANSFER')
        dt.object = body
        dt.use_vert_data = True
        dt.data_types_verts = {'VGROUP_WEIGHTS'}
        dt.vert_mapping = 'POLYINTERP_NEAREST'

        bpy.ops.object.datalayout_transfer(modifier="WeightTransfer")
        bpy.ops.object.modifier_apply(modifier="WeightTransfer")

        vg_map = {vg.name: vg for vg in garment.vertex_groups}

        if garment_type == "shirt":
            # 1. Strip all leg/foot bones from shirt
            leg_bones = {
                'J_Bip_L_UpperLeg', 'J_Bip_R_UpperLeg', 'J_Bip_L_LowerLeg', 
                'J_Bip_R_LowerLeg', 'J_Bip_L_Foot', 'J_Bip_R_Foot', 
                'J_Bip_L_ToeBase', 'J_Bip_R_ToeBase'
            }
            for b_name in leg_bones:
                if b_name in vg_map:
                    garment.vertex_groups.remove(vg_map[b_name])
                    del vg_map[b_name]

            arm_bones = {
                'J_Bip_L_UpperArm', 'J_Bip_L_LowerArm', 'J_Bip_L_Hand', 
                'J_Bip_R_UpperArm', 'J_Bip_R_LowerArm', 'J_Bip_R_Hand'
            }

            # Check if mesh has separate pattern panels/islands
            bm = bmesh.new()
            bm.from_mesh(garment.data)
            visited = set()
            islands = []
            for v in bm.verts:
                if v not in visited:
                    isl = []
                    q = [v]
                    visited.add(v)
                    while q:
                        c = q.pop()
                        isl.append(c)
                        for e in c.link_edges:
                            o = e.other_vert(c)
                            if o not in visited:
                                visited.add(o)
                                q.append(o)
                    islands.append(isl)

            if len(islands) >= 4:
                for isl in islands:
                    xs = [v.co.x for v in isl]
                    cx = (min(xs) + max(xs)) / 2.0
                    v_idxs = [v.index for v in isl]
                    
                    if abs(cx) < 0.12:  # Torso panels (breast, chest, back)
                        # Strictly NO arm bones on breast or torso!
                        for b in arm_bones:
                            if b in vg_map:
                                vg_map[b].remove(v_idxs)
                    elif cx > 0:  # Left sleeve
                        for b in {'J_Bip_R_Shoulder', 'J_Bip_R_UpperArm', 'J_Bip_R_LowerArm', 'J_Bip_R_Hand', 'J_Bip_C_Chest', 'J_Bip_C_Spine', 'J_Bip_C_Hips', 'J_Sec_L_Bust1', 'J_Sec_L_Bust2'}:
                            if b in vg_map:
                                vg_map[b].remove(v_idxs)
                    else:  # Right sleeve
                        for b in {'J_Bip_L_Shoulder', 'J_Bip_L_UpperArm', 'J_Bip_L_LowerArm', 'J_Bip_L_Hand', 'J_Bip_C_Chest', 'J_Bip_C_Spine', 'J_Bip_C_Hips', 'J_Sec_R_Bust1', 'J_Sec_R_Bust2'}:
                            if b in vg_map:
                                vg_map[b].remove(v_idxs)
            else:
                # Geometric fallback for welded mesh
                for v in garment.data.vertices:
                    if abs(v.co.x) < 0.12:
                        for b in arm_bones:
                            if b in vg_map:
                                vg_map[b].remove([v.index])
                    elif v.co.x > 0.15:
                        for b in {'J_Bip_R_Shoulder', 'J_Bip_R_UpperArm', 'J_Bip_R_LowerArm', 'J_Bip_R_Hand'}:
                            if b in vg_map:
                                vg_map[b].remove([v.index])
                    elif v.co.x < -0.15:
                        for b in {'J_Bip_L_Shoulder', 'J_Bip_L_UpperArm', 'J_Bip_L_LowerArm', 'J_Bip_L_Hand'}:
                            if b in vg_map:
                                vg_map[b].remove([v.index])

        elif garment_type == "skirt":
            # Skirt: strictly pelvis, hips, spine, and legs
            allowed_skirt_bones = {
                'Root', 'J_Bip_C_Hips', 'J_Bip_C_Spine', 
                'J_Bip_L_UpperLeg', 'J_Bip_R_UpperLeg', 
                'J_Bip_L_LowerLeg', 'J_Bip_R_LowerLeg'
            }
            for vg_name in list(vg_map.keys()):
                if vg_name not in allowed_skirt_bones:
                    garment.vertex_groups.remove(vg_map[vg_name])
                    del vg_map[vg_name]

            for v in garment.data.vertices:
                if v.co.x < -0.05:  # Right side of skirt: remove left leg influence
                    for b_name in {'J_Bip_L_UpperLeg', 'J_Bip_L_LowerLeg'}:
                        if b_name in vg_map:
                            vg_map[b_name].remove([v.index])
                elif v.co.x > 0.05: # Left side of skirt: remove right leg influence
                    for b_name in {'J_Bip_R_UpperLeg', 'J_Bip_R_LowerLeg'}:
                        if b_name in vg_map:
                            vg_map[b_name].remove([v.index])

        # 3. Clean noise, limit bone influences to 4 (glTF/game standard), normalize
        bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.001)
        bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
        bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)

        # 4. Anti-spike safety net: Ensure NO vertex is left with 0 weights
        ensure_all_vertices_weighted(garment, body)
        bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)

        # 5. Parent to Armature with Armature modifier
        garment.parent = armature
        arm_mod = garment.modifiers.new(name="Armature", type='ARMATURE')
        arm_mod.object = armature

        # 6. Subtle realistic cloth thickness (0.2 mm)
        sol = garment.modifiers.new(name="Solidify", type='SOLIDIFY')
        sol.thickness = 0.0002  # 0.2 mm lightweight fabric
        sol.offset = 1.0        # Outward extrusion

        print(f"[RigTool] Successfully rigged '{garment.name}' with natural drape and 0.2mm thickness!")

    # Restore Pose mode and update view
    armature.data.pose_position = 'POSE'
    bpy.context.view_layer.update()
    print("\n[RigTool] Finished! All garments are rigged. Press Play in the timeline to test!")

if __name__ == "__main__":
    rig_clothing()
