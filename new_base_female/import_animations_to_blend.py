"""Import, retarget, and configure trial animations into new_base_female.blend.

Run this script either inside Blender (Text Editor -> Run Script)
OR from terminal via:
  /Applications/Blender.app/Contents/MacOS/Blender new_base_female/new_base_female.blend -P new_base_female/import_animations_to_blend.py
"""

import bpy
import mathutils
import os

GLB_PATH = os.path.join(os.path.dirname(__file__), "animations_trial.glb")
if not os.path.isfile(GLB_PATH):
    GLB_PATH = "/Users/vaz/Desktop/antigravity_apps/GarmentCode/new_base_female/animations_trial.glb"

print(f"[ImportAnimations] Importing animations from: {GLB_PATH}")

# Delta transformations for UpperArm bones to map T-pose animations to A-pose mesh
DELTA_L = mathutils.Quaternion((0.9238795325, 0.0, 0.0, 0.3826834324))   # +45 deg around local Z
DELTA_R = mathutils.Quaternion((0.9238795325, 0.0, 0.0, -0.3826834324))  # -45 deg around local Z

ANIMATION_NAMES = [
    'idle',
    'Attack Command',
    'Model Pose',
    'Peace Sign',
    'Show Full Body',
    'Spin',
]

# 1. Target Armature in new_base_female
armature = bpy.data.objects.get("Armature")
if not armature:
    raise RuntimeError("Could not find 'Armature' in the scene!")

# Ensure Armature is in POSE position
armature.data.pose_position = 'POSE'
print(f"[ImportAnimations] Armature pose_position set to: '{armature.data.pose_position}'")

if not armature.animation_data:
    armature.animation_data_create()

# 2. Remove pre-existing animation actions to avoid '.001' duplication on import
for act_name in ANIMATION_NAMES:
    old_act = bpy.data.actions.get(act_name)
    if old_act:
        bpy.data.actions.remove(old_act)

# 3. Track existing objects & import GLB
existing_objs = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=GLB_PATH)

# 4. Remove any newly imported meshes/empties/armature duplicates to keep scene pristine
new_objs = set(bpy.data.objects) - existing_objs
for obj in new_objs:
    data = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    if data and data.users == 0:
        if isinstance(data, bpy.types.Mesh):
            bpy.data.meshes.remove(data)
        elif isinstance(data, bpy.types.Armature):
            bpy.data.armatures.remove(data)


def retarget_action(act):
    """Adjust UpperArm rotation fcurves in act by multiplying with Delta_L / Delta_R on the left."""
    channelbags = []
    if hasattr(act, 'layers'):
        for l in act.layers:
            for s in l.strips:
                if hasattr(s, 'channelbags'):
                    channelbags.extend(s.channelbags)

    targets = [
        ('J_Bip_L_UpperArm', DELTA_L),
        ('J_Bip_R_UpperArm', DELTA_R),
    ]

    adjusted = set()

    for cb in channelbags:
        for bone_name, delta in targets:
            dp = f'pose.bones["{bone_name}"].rotation_quaternion'
            fcs = [cb.fcurves.find(dp, index=i) for i in range(4)]
            if all(fcs):
                num_keys = len(fcs[0].keyframe_points)
                for k in range(num_keys):
                    q_orig = mathutils.Quaternion((
                        fcs[0].keyframe_points[k].co[1],
                        fcs[1].keyframe_points[k].co[1],
                        fcs[2].keyframe_points[k].co[1],
                        fcs[3].keyframe_points[k].co[1],
                    ))
                    q_new = delta @ q_orig
                    fcs[0].keyframe_points[k].co[1] = q_new.w
                    fcs[1].keyframe_points[k].co[1] = q_new.x
                    fcs[2].keyframe_points[k].co[1] = q_new.y
                    fcs[3].keyframe_points[k].co[1] = q_new.z
                for fc in fcs:
                    fc.update()
                adjusted.add(bone_name)

    if hasattr(act, 'fcurves') and len(act.fcurves) > 0:
        for bone_name, delta in targets:
            dp = f'pose.bones["{bone_name}"].rotation_quaternion'
            fcs = [act.fcurves.find(dp, index=i) for i in range(4)]
            if all(fcs):
                num_keys = len(fcs[0].keyframe_points)
                for k in range(num_keys):
                    q_orig = mathutils.Quaternion((
                        fcs[0].keyframe_points[k].co[1],
                        fcs[1].keyframe_points[k].co[1],
                        fcs[2].keyframe_points[k].co[1],
                        fcs[3].keyframe_points[k].co[1],
                    ))
                    q_new = delta @ q_orig
                    fcs[0].keyframe_points[k].co[1] = q_new.w
                    fcs[1].keyframe_points[k].co[1] = q_new.x
                    fcs[2].keyframe_points[k].co[1] = q_new.y
                    fcs[3].keyframe_points[k].co[1] = q_new.z
                for fc in fcs:
                    fc.update()
                adjusted.add(bone_name)

    return list(adjusted)


def setup_utility_pose(arm, act_name, is_t_pose=False):
    """Create or reset utility pose action (A-Pose or T-Pose)."""
    act = bpy.data.actions.get(act_name)
    if act:
        bpy.data.actions.remove(act)
    act = bpy.data.actions.new(name=act_name)
    act.use_fake_user = True
    arm.animation_data.action = act
    bpy.context.scene.frame_set(0)

    for pb in arm.pose.bones:
        pb.location = (0.0, 0.0, 0.0)
        if is_t_pose and pb.name == 'J_Bip_L_UpperArm':
            pb.rotation_quaternion = DELTA_L
        elif is_t_pose and pb.name == 'J_Bip_R_UpperArm':
            pb.rotation_quaternion = DELTA_R
        else:
            pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)

        pb.keyframe_insert(data_path='location', frame=0)
        pb.keyframe_insert(data_path='rotation_quaternion', frame=0)

    if hasattr(act, 'slots'):
        for slot in act.slots:
            slot.identifier = 'OBArmature'
            slot.name_display = 'Armature'

    return act


# 5. Retarget each imported action
imported_count = 0
for act_name in ANIMATION_NAMES:
    act = bpy.data.actions.get(act_name)
    if act:
        retarget_action(act)
        act.use_fake_user = True

        if hasattr(act, 'slots'):
            for slot in act.slots:
                try:
                    slot.identifier = 'OBArmature'
                    slot.name_display = 'Armature'
                except Exception as e:
                    print(f"  Note on slot rename: {e}")

        print(f"[ImportAnimations] Loaded and retargeted: '{act.name}' (Frames {int(act.frame_range[0])} to {int(act.frame_range[1])})")
        imported_count += 1

# 6. Update utility poses
setup_utility_pose(armature, 'A-Pose', is_t_pose=False)
setup_utility_pose(armature, 'T-Pose', is_t_pose=True)

# 7. Set default active animation to 'idle'
idle_act = bpy.data.actions.get('idle')
if idle_act:
    armature.animation_data.action = idle_act
    if hasattr(armature.animation_data, 'action_slot') and len(idle_act.slots) > 0:
        armature.animation_data.action_slot = idle_act.slots[0]
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = 239
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.update()
    print("[ImportAnimations] Default active action set to 'idle' (Frames 0 to 239)")

print(f"[SUCCESS] {imported_count} animations successfully imported, retargeted, and configured!")
