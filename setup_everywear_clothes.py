"""Pure EveryWear Retargeter for Blender.

Connects EveryWear-rigged clothing directly to the avatar's animated skeleton:
- Leaves the raw EveryWear mesh, vertices, and skin weights 100% untouched.
- NO Solidify, NO size scaling, NO mask modifiers, NO weight modifications.
- Re-points the Armature modifier directly to 'Armature'.
- Parents the cloth to 'Armature' while preserving exact world transform.
- Cleans up duplicate imported armatures/empties if present.

Usage:
  In Blender -> Scripting workspace (or Python Console) -> Run this script.
"""

import bpy

TARGET_ARMATURE_NAME = "Armature"


def main():
  target_arm = bpy.data.objects.get(TARGET_ARMATURE_NAME)
  if not target_arm or target_arm.type != 'ARMATURE':
    raise RuntimeError(f"Could not find target armature '{TARGET_ARMATURE_NAME}'!")

  # 1. Clean up any Mask modifier or vertex group on Body if previously added
  body = bpy.data.objects.get("Body")
  if body:
    mask_mod = body.modifiers.get("Clothes_Mask")
    if mask_mod:
      body.modifiers.remove(mask_mod)
      print("[Retarget] Removed Clothes_Mask modifier from Body.")
    mask_vg = body.vertex_groups.get("Hide_Under_Clothes")
    if mask_vg:
      body.vertex_groups.remove(mask_vg)
      print("[Retarget] Removed Hide_Under_Clothes vertex group from Body.")

  # 2. Target selected mesh objects, or auto-detect any mesh pointing to another armature
  selected = [
      o for o in bpy.context.selected_objects
      if o.type == 'MESH' and o.name not in ["Body", "Face"]
  ]
  if not selected:
    selected = [
        o for o in bpy.data.objects
        if o.type == 'MESH'
        and o.name not in ["Body", "Face"]
        and any(m.type == 'ARMATURE' and m.object != target_arm for m in o.modifiers)
    ]

  if not selected:
    print("[Retarget] No clothing meshes found needing retargeting.")
    return

  for cloth in selected:
    # Point Armature modifier to target_arm
    for m in cloth.modifiers:
      if m.type == 'ARMATURE':
        m.object = target_arm

    # Preserve world matrix and parent to target_arm
    mat = cloth.matrix_world.copy()
    cloth.parent = target_arm
    cloth.matrix_parent_inverse = target_arm.matrix_world.inverted()
    cloth.matrix_world = mat

    print(f"[Retarget] Successfully connected '{cloth.name}' to '{target_arm.name}'.")

  # 3. Remove duplicate imported armature from EveryWear if present
  for o in list(bpy.data.objects):
    if o.type == 'ARMATURE' and o != target_arm and ("A_pose" in o.name or "Armature." in o.name):
      arm_name = o.name
      bpy.data.objects.remove(o, do_unlink=True)
      print(f"[Retarget] Removed duplicate imported skeleton '{arm_name}'.")

  print("[Retarget] Done! Raw EveryWear clothing is bound to Armature.")


if __name__ == "__main__":
  main()
