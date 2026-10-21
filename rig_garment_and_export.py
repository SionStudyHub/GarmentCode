"""Automated Garment Rigging & GLB Export for Blender.

Run this script inside Blender's Text Editor (with new_base_female.blend open)
OR execute headless via:
  /Applications/Blender.app/Contents/MacOS/Blender new_base_female/new_base_female.blend -P rig_garment_and_export.py

What it does:
1. Locates the garment object (either currently selected or auto-detected).
2. Uses Data Transfer modifier to interpolate vertex weights from avatar 'Body'.
3. Cleans noise, limits bone influences to 4 per vertex, and normalizes weights.
4. Prunes unused zero-weight vertex groups for a clean, lean hierarchy.
5. Parents garment to 'Armature' with an Armature modifier.
6. Exports the rigged garment (and optionally the avatar) to a skin-weighted .glb file.
"""

import bpy
import os

# ==================== CONFIGURATION ====================
# Set to None to auto-rig the currently selected object,
# OR specify the exact name of the imported garment object:
GARMENT_OBJECT_NAME = None  # e.g. "Cloth", "Tee", "NewFemaleTee"

# If you have an unimported .glb file to import and rig directly:
GLB_IMPORT_PATH = None  # e.g. "/path/to/tailored_shirt.glb"

# Export destination:
OUTPUT_GLB_PATH = os.path.join(
    os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.path.expanduser("~/Desktop"),
    "rigged_garment.glb"
)

# Export scope:
# True:  Exports the Armature + Garment + Avatar Body/Face (complete character)
# False: Exports only the Armature + Garment (modular clothing asset)
EXPORT_FULL_CHARACTER = True

# Add Solidify modifier for cloth thickness (in meters, e.g. 0.0012 = 1.2mm)
ADD_THICKNESS = True
THICKNESS_METERS = 0.0012
# =======================================================


def find_garment_object():
    """Finds the target garment object to rig."""
    if GARMENT_OBJECT_NAME and GARMENT_OBJECT_NAME in bpy.data.objects:
        return bpy.data.objects[GARMENT_OBJECT_NAME]
    
    # If an object is actively selected and is not Body/Face/Armature
    active = bpy.context.active_object
    ignore_names = {"Body", "Face", "Armature"}
    if active and active.type == 'MESH' and active.name not in ignore_names:
        return active
        
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH' and obj.name not in ignore_names:
            return obj
            
    # Find any mesh object that isn't avatar body/face
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.name not in ignore_names and not obj.name.startswith("J_"):
            return obj
            
    return None


def rig_garment():
    # 1. Import GLB if specified
    if GLB_IMPORT_PATH and os.path.isfile(GLB_IMPORT_PATH):
        print(f"[RigGarment] Importing GLB from: {GLB_IMPORT_PATH}")
        bpy.ops.import_scene.gltf(filepath=GLB_IMPORT_PATH)
    
    # 2. Locate Body and Armature
    body = bpy.data.objects.get("Body")
    armature = bpy.data.objects.get("Armature")
    
    if not body or not armature:
        raise RuntimeError("Avatar 'Body' mesh or 'Armature' not found in the Blender scene!")
        
    garment = find_garment_object()
    if not garment:
        raise RuntimeError(
            "Could not find garment object to rig! "
            "Please select your garment object or set GARMENT_OBJECT_NAME in the script."
        )
        
    print(f"[RigGarment] Rigging garment object: '{garment.name}' to Armature: '{armature.name}'")

    # 3. Ensure garment has no stale armature modifiers or vertex groups
    garment.modifiers.clear()
    garment.vertex_groups.clear()

    # 4. Data Transfer Modifier (Surface Weight Transfer)
    dt = garment.modifiers.new(name="WeightTransfer", type='DATA_TRANSFER')
    dt.object = body
    dt.use_vert_data = True
    dt.data_types_verts = {'VGROUP_WEIGHTS'}
    dt.vert_mapping = 'POLYINTERP_NEAREST'  # Best surface interpolation for clothing

    bpy.context.view_layer.objects.active = garment
    bpy.ops.object.datalayout_transfer(modifier="WeightTransfer")
    bpy.ops.object.modifier_apply(modifier="WeightTransfer")
    print(f"[RigGarment] Initial transferred vertex groups: {len(garment.vertex_groups)}")

    # 5. Clean, limit influences, and normalize weights
    bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.001)
    bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
    bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)

    # 6. Prune unused bone vertex groups (groups with 0 total weight on garment)
    used_indices = set()
    for v in garment.data.vertices:
        for g in v.groups:
            if g.weight > 0.001:
                used_indices.add(g.group)

    pruned_count = 0
    to_remove = [vg for vg in garment.vertex_groups if vg.index not in used_indices]
    for vg in to_remove:
        garment.vertex_groups.remove(vg)
        pruned_count += 1
    print(f"[RigGarment] Pruned {pruned_count} empty bone groups. Active bone influences: {len(garment.vertex_groups)}")

    # 7. Parent to Armature & add Armature Modifier
    garment.parent = armature
    arm_mod = garment.modifiers.new(name="Armature", type='ARMATURE')
    arm_mod.object = armature

    # 8. Optional: Add Solidify Modifier for realistic fabric thickness
    if ADD_THICKNESS:
        solid = garment.modifiers.new(name="Solidify", type='SOLIDIFY')
        solid.thickness = THICKNESS_METERS
        solid.offset = 0.0
        solid.use_rim = True
        print(f"[RigGarment] Added Solidify modifier ({THICKNESS_METERS * 1000:.1f} mm)")

    # 9. Export to GLB
    bpy.ops.object.select_all(action='DESELECT')
    if EXPORT_FULL_CHARACTER:
        armature.select_set(True)
        garment.select_set(True)
        body.select_set(True)
        face = bpy.data.objects.get("Face")
        if face:
            face.select_set(True)
        bpy.context.view_layer.objects.active = armature
    else:
        armature.select_set(True)
        garment.select_set(True)
        bpy.context.view_layer.objects.active = armature

    print(f"[RigGarment] Exporting to: {OUTPUT_GLB_PATH}")
    bpy.ops.export_scene.gltf(
        filepath=OUTPUT_GLB_PATH,
        export_format='GLB',
        use_selection=True,
        export_skins=True,
        export_apply=False,  # Keep modifiers dynamic/rig intact
        export_materials='EXPORT',
    )
    print(f"[SUCCESS] Rigged garment exported successfully to: {OUTPUT_GLB_PATH}")


if __name__ == "__main__":
    rig_garment()
