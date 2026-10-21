"""Retarget animations to A-pose for new_base_female.

Usage:
  /Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup new_base_female/new_base_female.blend -P new_base_female/retarget_animations_to_apose.py
"""

import os
import bpy
import mathutils

DELTA_L = mathutils.Quaternion((0.9238795325, 0.0, 0.0, 0.3826834324))
DELTA_R = mathutils.Quaternion((0.9238795325, 0.0, 0.0, -0.3826834324))

ANIMATION_NAMES = [
    'idle',
    'Attack Command',
    'Model Pose',
    'Peace Sign',
    'Show Full Body',
    'Spin',
]


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

    adjusted_bones = set()

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
                adjusted_bones.add(bone_name)

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
                adjusted_bones.add(bone_name)

    return list(adjusted_bones)


def setup_utility_pose(arm, act_name, is_t_pose=False):
    """Create or reset utility pose action (A-Pose or T-Pose)."""
    act = bpy.data.actions.get(act_name)
    if act:
        bpy.data.actions.remove(act)
    act = bpy.data.actions.new(name=act_name)
    act.use_fake_user = True
    arm.animation_data.action = act
    bpy.context.scene.frame_set(1)

    for pb in arm.pose.bones:
        pb.location = (0.0, 0.0, 0.0)
        if is_t_pose and pb.name == 'J_Bip_L_UpperArm':
            pb.rotation_quaternion = DELTA_L
        elif is_t_pose and pb.name == 'J_Bip_R_UpperArm':
            pb.rotation_quaternion = DELTA_R
        else:
            pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)

        pb.keyframe_insert(data_path='location', frame=1)
        pb.keyframe_insert(data_path='rotation_quaternion', frame=1)

    if hasattr(act, 'slots'):
        for slot in act.slots:
            try:
                slot.identifier = 'OBArmature'
                slot.name_display = 'Armature'
            except Exception:
                pass

    return act


def main():
    print("\n" + "=" * 60)
    print("STARTING PRECISION ANIMATION RETARGETING TO A-POSE")
    print("=" * 60)

    base_dir = os.path.dirname(bpy.data.filepath)
    if not base_dir:
        base_dir = "/Users/vaz/Desktop/antigravity_apps/GarmentCode/new_base_female"
    glb_export_path = os.path.join(base_dir, "A_pose_new_base_female.glb")
    blend_path = bpy.data.filepath

    arm = bpy.data.objects.get("Armature")
    if not arm or arm.type != 'ARMATURE':
        raise RuntimeError("Could not find 'Armature' in scene!")

    # 1. Enable pose evaluation
    arm.data.pose_position = 'POSE'
    print(f"[Armature] pose_position set to: '{arm.data.pose_position}'")

    if not arm.animation_data:
        arm.animation_data_create()

    # 2. Retarget existing clean integer actions
    for act_name in ANIMATION_NAMES:
        act = bpy.data.actions.get(act_name)
        if not act:
            raise RuntimeError(f"Action '{act_name}' not found!")
        adjusted = retarget_action(act)
        print(f"[Retarget] Action '{act.name}' [{int(act.frame_range[0])}-{int(act.frame_range[1])}]: adjusted {adjusted}")

    # 3. Setup clean A-Pose and T-Pose
    print("[Utility] Configuring 'A-Pose'...")
    setup_utility_pose(arm, 'A-Pose', is_t_pose=False)
    print("[Utility] Configuring 'T-Pose'...")
    setup_utility_pose(arm, 'T-Pose', is_t_pose=True)

    # 4. Configure slots and fake users on all actions
    for act_name in ['A-Pose', 'T-Pose'] + ANIMATION_NAMES:
        act = bpy.data.actions.get(act_name)
        if not act:
            continue
        act.use_fake_user = True
        if hasattr(act, 'slots'):
            for slot in act.slots:
                try:
                    slot.identifier = 'OBArmature'
                    slot.name_display = 'Armature'
                except Exception:
                    pass

    # 5. Set default active action to idle
    idle_act = bpy.data.actions.get('idle')
    if idle_act:
        arm.animation_data.action = idle_act
        if hasattr(arm.animation_data, 'action_slot') and len(idle_act.slots) > 0:
            arm.animation_data.action_slot = idle_act.slots[0]
        bpy.context.scene.frame_start = 0
        bpy.context.scene.frame_end = 239
        bpy.context.scene.frame_set(0)
        bpy.context.view_layer.update()
        print("[Active] Active action set to 'idle' [0-239]")

    # 6. Save blend file
    print(f"[Save] Saving blend file to: {blend_path}")
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print(f"[Save] Blend file saved: {os.path.getsize(blend_path)} bytes")

    # 7. Export GLB
    print(f"[Export] Exporting GLB to: {glb_export_path}...")
    bpy.ops.export_scene.gltf(
        filepath=glb_export_path,
        export_format='GLB',
        export_animations=True,
    )
    print(f"[Export] GLB exported: {os.path.getsize(glb_export_path)} bytes")

    print("\n" + "=" * 60)
    print("[SUCCESS] ANIMATION RETARGETING COMPLETED")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
