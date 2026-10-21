"""Automated Scalp Cap Extraction Script for Blender.

Extracts the canonical rigid scalp cap from `new_base_female.blend` as the
permanent mounting interface for modular hairstyles:
1. Locates the 1296 scalp faces (HairBack material) on the `Body` mesh.
2. Extracts and duplicates them into an independent `ScalpCap` object.
3. Offsets vertices outward by +1.0 mm (+0.001 m) along vertex normals to eliminate z-fighting.
4. Cleans all vertex groups and locks 100% influence (weight 1.0) to `J_Bip_C_Head`.
5. Parents to the scene `Armature` with an `ARMATURE` modifier.
6. Assigns stylized dark `M_ScalpCap` material.
7. Exports canonical assets to `assets/hair/scalp_cap.glb` and `assets/hair/scalp_cap.obj`.

Usage:
  /Applications/Blender.app/Contents/MacOS/Blender --background new_base_female/new_base_female.blend --python scripts/extract_scalp_cap.py
"""

import sys
from pathlib import Path
import bmesh
import bpy


def find_repo_root() -> Path:
    """Locate the root directory of the GarmentCode repository."""
    if "__file__" in globals():
        return Path(__file__).resolve().parent.parent
    if bpy.data.filepath:
        blend_path = Path(bpy.data.filepath).resolve()
        if blend_path.parent.name == "new_base_female":
            return blend_path.parent.parent
        return blend_path.parent
    return Path.cwd().resolve()


def ensure_blend_loaded(repo_root: Path):
    """Ensure new_base_female.blend is loaded if running headless without blend argument."""
    if "Body" not in bpy.data.objects:
        blend_file = repo_root / "new_base_female" / "new_base_female.blend"
        if not blend_file.exists():
            raise FileNotFoundError(f"Blend file not found at: {blend_file}")
        print(f"[ScalpCap] Loading blend file: {blend_file}")
        bpy.ops.wm.open_mainfile(filepath=str(blend_file))


def extract_scalp_cap():
    repo_root = find_repo_root()
    ensure_blend_loaded(repo_root)

    print("[ScalpCap] Starting canonical scalp cap extraction...")

    # 1. Locate Body object
    body = bpy.data.objects.get("Body")
    if not body or body.type != "MESH":
        raise RuntimeError("Target object 'Body' not found in Blender scene!")

    # 2. Locate HairBack material slot(s)
    hair_slots = {
        i
        for i, slot in enumerate(body.material_slots)
        if slot.material and "HairBack" in slot.material.name
    }
    if not hair_slots:
        raise RuntimeError(
            "No material slot matching 'HairBack' found on 'Body'!"
        )

    print(f"[ScalpCap] Identified HairBack material slot indices: {hair_slots}")

    # 3. Extract scalp faces into BMesh
    bm = bmesh.new()
    bm.from_mesh(body.data)

    # Delete all non-hair faces
    faces_to_delete = [
        f for f in bm.faces if f.material_index not in hair_slots
    ]
    bmesh.ops.delete(bm, geom=faces_to_delete, context="FACES")

    # Clean up isolated vertices
    isolated_verts = [v for v in bm.verts if not v.link_faces]
    if isolated_verts:
        bmesh.ops.delete(bm, geom=isolated_verts, context="VERTS")

    # Clear inherited vertex deform layers to avoid invalid group indices
    while bm.verts.layers.deform:
        bm.verts.layers.deform.remove(bm.verts.layers.deform[0])

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    bm.normal_update()

    num_faces = len(bm.faces)
    num_verts = len(bm.verts)
    print(f"[ScalpCap] Extracted {num_faces} faces, {num_verts} vertices.")
    if num_faces != 1296:
        print(
            f"[WARNING] Expected 1296 faces for canonical scalp, but got {num_faces}."
        )

    # 4. Offset vertices +0.001 m (+1.0 mm) along vertex normals
    NORMAL_OFFSET_M = 0.001  # 1.0 mm
    for v in bm.verts:
        v.co += v.normal * NORMAL_OFFSET_M
    print(
        f"[ScalpCap] Applied +{NORMAL_OFFSET_M * 1000.0:.1f} mm outward normal offset to all {num_verts} vertices."
    )

    # 5. Create new independent mesh and object
    cap_mesh_name = "ScalpCap"
    existing_obj = bpy.data.objects.get("ScalpCap")
    if existing_obj:
        print(
            "[ScalpCap] Removing existing 'ScalpCap' object before recreating."
        )
        bpy.data.objects.remove(existing_obj, do_unlink=True)

    cap_mesh = bpy.data.meshes.new(name=cap_mesh_name)
    bm.to_mesh(cap_mesh)
    bm.free()

    # Validate mesh integrity
    is_invalid = cap_mesh.validate(verbose=True)
    if is_invalid:
        print("[WARNING] Mesh validation reported corrections.")
    else:
        print("[ScalpCap] Mesh validated successfully (no geometry errors).")

    scalp_cap_obj = bpy.data.objects.new(name="ScalpCap", object_data=cap_mesh)
    bpy.context.scene.collection.objects.link(scalp_cap_obj)

    # 6. Rigging & Vertex Weights: 100% influence to J_Bip_C_Head
    scalp_cap_obj.vertex_groups.clear()
    head_vg = scalp_cap_obj.vertex_groups.new(name="J_Bip_C_Head")
    all_vert_indices = list(range(len(scalp_cap_obj.data.vertices)))
    head_vg.add(all_vert_indices, 1.0, "REPLACE")
    print(
        f"[ScalpCap] Assigned 100% weight to 'J_Bip_C_Head' for all {len(all_vert_indices)} vertices."
    )

    # 7. Parent to Armature & attach ARMATURE modifier
    armature = bpy.data.objects.get("Armature")
    if armature:
        armature.hide_set(False)
        armature.hide_viewport = False
        armature.hide_render = False

        scalp_cap_obj.parent = armature
        scalp_cap_obj.matrix_world = armature.matrix_world

        arm_mod = scalp_cap_obj.modifiers.new(name="Armature", type="ARMATURE")
        arm_mod.object = armature
        print(
            "[ScalpCap] Parented 'ScalpCap' to 'Armature' with ARMATURE modifier."
        )
    else:
        print(
            "[WARNING] 'Armature' object not found in scene. Skipping armature modifier."
        )

    # 8. Material Setup: M_ScalpCap
    scalp_cap_obj.data.materials.clear()
    mat_name = "M_ScalpCap"
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        mat = bpy.data.materials.new(name=mat_name)

    mat.use_nodes = True
    bsdf = None
    for node in mat.node_tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            bsdf = node
            break
    if bsdf is None:
        bsdf = mat.node_tree.nodes.new(type="ShaderNodeBsdfPrincipled")

    if "Base Color" in bsdf.inputs:
        bsdf.inputs["Base Color"].default_value = (0.08, 0.07, 0.06, 1.0)
    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = 0.4
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = 0.0

    scalp_cap_obj.data.materials.append(mat)
    print(
        f"[ScalpCap] Configured and assigned '{mat_name}' material (Dark brown/black RGB [0.08, 0.07, 0.06], Roughness 0.4, Metallic 0.0)."
    )

    # 9. Exports
    output_dir = repo_root / "assets" / "hair"
    output_dir.mkdir(parents=True, exist_ok=True)

    glb_path = output_dir / "scalp_cap.glb"
    obj_path = output_dir / "scalp_cap.obj"

    # Export GLB (Rigged with Armature)
    bpy.ops.object.select_all(action="DESELECT")
    if armature:
        armature.select_set(True)
    scalp_cap_obj.select_set(True)
    bpy.context.view_layer.objects.active = scalp_cap_obj

    print(f"[ScalpCap] Exporting GLB to: {glb_path}")
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format="GLB",
        use_selection=True,
        export_skins=True,
        export_animations=False,
        export_apply=False,
        export_materials="EXPORT",
        export_yup=True,
    )

    # Export OBJ (Clean single mesh)
    bpy.ops.object.select_all(action="DESELECT")
    scalp_cap_obj.select_set(True)
    bpy.context.view_layer.objects.active = scalp_cap_obj

    print(f"[ScalpCap] Exporting OBJ to: {obj_path}")
    bpy.ops.wm.obj_export(
        filepath=str(obj_path),
        export_selected_objects=True,
        export_materials=True,
        export_normals=True,
        export_uv=True,
    )

    # Verification of exported files
    glb_size = glb_path.stat().st_size if glb_path.exists() else 0
    obj_size = obj_path.stat().st_size if obj_path.exists() else 0

    print(f"[ScalpCap] Verification:")
    print(f"  - GLB file: {glb_path} ({glb_size:,} bytes)")
    print(f"  - OBJ file: {obj_path} ({obj_size:,} bytes)")

    if glb_size == 0 or obj_size == 0:
        raise RuntimeError(
            "Export failed: One or more exported files are empty or missing!"
        )

    print(
        "[ScalpCap] Canonical scalp cap extraction and export completed successfully!"
    )


if __name__ == "__main__":
    try:
        extract_scalp_cap()
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
