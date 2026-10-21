"""Export animations from new_base_female.blend as FBX files for Marvelous Designer.

Run via:
  /Applications/Blender.app/Contents/MacOS/Blender new_base_female/new_base_female.blend -P export_animations_for_marvelous.py
"""

import bpy
import os

arm = bpy.data.objects.get("Armature")
body = bpy.data.objects.get("Body")
face = bpy.data.objects.get("Face")

if not arm or not body:
    raise RuntimeError("Missing Armature or Body in scene!")

arm.data.pose_position = 'POSE'

out_dir = os.path.join(os.path.dirname(__file__), "new_base_female", "animations_fbx")
os.makedirs(out_dir, exist_ok=True)

# Unhide Armature and meshes so select_set works
arm.hide_set(False)
body.hide_set(False)
if face:
    face.hide_set(False)

# Select Armature, Body, Face
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
body.select_set(True)
if face:
    face.select_set(True)
bpy.context.view_layer.objects.active = arm

ANIMATIONS = [
    'idle',
    'Model Pose',
    'Peace Sign',
    'Show Full Body',
    'Spin',
    'Attack Command',
]

for act_name in ANIMATIONS:
    act = bpy.data.actions.get(act_name)
    if not act:
        print(f"Skipping {act_name}, not found.")
        continue
        
    arm.animation_data.action = act
    if hasattr(arm.animation_data, 'action_slot') and len(act.slots) > 0:
        arm.animation_data.action_slot = act.slots[0]
        
    start_frame = int(act.frame_range[0])
    end_frame = int(act.frame_range[1])
    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame
    
    clean_name = act_name.lower().replace(" ", "_")
    out_file = os.path.join(out_dir, f"new_base_female_{clean_name}.fbx")
    
    print(f"Exporting '{act_name}' (frames {start_frame}-{end_frame}) -> {out_file}...")
    
    bpy.ops.export_scene.fbx(
        filepath=out_file,
        use_selection=True,
        object_types={'ARMATURE', 'MESH'},
        global_scale=1000.0,
        apply_scale_options='FBX_SCALE_ALL',
        armature_nodetype='ROOT',
        bake_anim=True,
        bake_anim_use_all_bones=True,
        bake_anim_use_all_actions=False,
        bake_anim_use_nla_strips=False,
        bake_space_transform=False,
        axis_forward='-Z',
        axis_up='Y'
    )
    print(f"  Exported: {os.path.getsize(out_file)} bytes (Pre-scaled to mm with Armature & Animation)")

print("\n[SUCCESS] All FBX animations for Marvelous Designer exported to:", out_dir)
