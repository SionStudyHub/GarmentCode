import bpy
import math
from mathutils import Vector, Euler
from pathlib import Path

def load_garment_obj_with_layer_materials(obj_path, default_color, panel_keys):
    verts = []
    faces = []
    face_groups = []
    seen_groups = []
    cur_group = "default"
    with open(obj_path, "r") as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                # Scale mm -> m and convert MD (X, Y_up, Z_front) to Blender (X, -Z_front, Y_up)
                vx, vy, vz = float(parts[1]) * 0.001, float(parts[2]) * 0.001, float(parts[3]) * 0.001
                verts.append((vx, -vz, vy))
            elif line.startswith("g ") or line.startswith("o "):
                cur_group = line.split(None, 1)[1].strip() if len(line.split()) > 1 else "default"
                if cur_group not in seen_groups:
                    seen_groups.append(cur_group)
            elif line.startswith("f "):
                parts = line.split()[1:]
                f_idxs = [int(p.split("/")[0]) - 1 for p in parts]
                faces.append(f_idxs)
                face_groups.append(cur_group)

    group_to_key = {}
    for idx, g_name in enumerate(seen_groups):
        if idx < len(panel_keys):
            group_to_key[g_name] = panel_keys[idx]
        else:
            group_to_key[g_name] = g_name

    mesh = bpy.data.meshes.new("GarmentMesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    g_obj = bpy.data.objects.new("Garment", mesh)
    bpy.context.scene.collection.objects.link(g_obj)
    for poly in mesh.polygons:
        poly.use_smooth = True

    def make_mat(name, color):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = color
            bsdf.inputs["Roughness"].default_value = 0.78
            if "Sheen Weight" in bsdf.inputs:
                bsdf.inputs["Sheen Weight"].default_value = 0.45
        return mat

    mat_l0 = make_mat("Layer1_Inner_LightBlue", (0.55, 0.72, 0.88, 1.0))
    mat_l1 = make_mat("Layer2_Outer_Charcoal", (0.18, 0.18, 0.20, 1.0))
    mat_def = make_mat("GarmentDefault", default_color)
    mesh.materials.append(mat_def)
    mesh.materials.append(mat_l0)
    mesh.materials.append(mat_l1)

    for poly, grp in zip(mesh.polygons, face_groups):
        mapped = group_to_key.get(grp, grp)
        if mapped.startswith("l0_"):
            poly.material_index = 1
        elif mapped.startswith("l1_"):
            poly.material_index = 2
        else:
            poly.material_index = 0
    return g_obj

def main():
    # 1. Clear default scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 2. Import Sion Avatar GLB
    avatar_path = '/Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_avatars/sion-female-apose.glb'
    print(f"Importing avatar: {avatar_path}")
    bpy.ops.import_scene.gltf(filepath=avatar_path)

    # Delete unrigged helper meshes (Icosphere)
    for obj in list(bpy.context.scene.objects):
        if "icosphere" in obj.name.lower():
            bpy.data.objects.remove(obj, do_unlink=True)

    # 3. Load Garment OBJ with per-layer materials
    garment_path = '/Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/out/layered_tops_test/diagnostics/false_seams.obj'
    print(f"Loading garment: {garment_path}")
    load_garment_obj_with_layer_materials(garment_path, (0.2, 0.2, 0.22, 1.0), [])

    # 4. Setup Lighting
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.92, 0.92, 0.93, 1.0)
        bg.inputs["Strength"].default_value = 0.5

    # Key Light
    key_data = bpy.data.lights.new(name="KeyLight", type="SUN")
    key_data.energy = 2.0
    key_data.color = (1.0, 0.98, 0.95)
    key_obj = bpy.data.objects.new(name="KeyLight", object_data=key_data)
    bpy.context.scene.collection.objects.link(key_obj)
    key_obj.rotation_euler = Euler((math.radians(50), math.radians(15), math.radians(35)), "XYZ")

    # Fill Light
    fill_data = bpy.data.lights.new(name="FillLight", type="SUN")
    fill_data.energy = 0.8
    fill_data.color = (0.95, 0.97, 1.0)
    fill_obj = bpy.data.objects.new(name="FillLight", object_data=fill_data)
    bpy.context.scene.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = Euler((math.radians(45), math.radians(-25), math.radians(-60)), "XYZ")

    # Rim / Back Light
    rim_data = bpy.data.lights.new(name="RimLight", type="SUN")
    rim_data.energy = 1.2
    rim_obj = bpy.data.objects.new(name="RimLight", object_data=rim_data)
    bpy.context.scene.collection.objects.link(rim_obj)
    rim_obj.rotation_euler = Euler((math.radians(-40), 0, math.radians(160)), "XYZ")

    # 5. Setup Camera
    cam_data = bpy.data.cameras.new(name="StudioCam")
    cam_data.lens = 75.0  # Portrait lens to avoid perspective distortion
    cam_obj = bpy.data.objects.new(name="StudioCam", object_data=cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Render Settings
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.render.resolution_x = 1024
    bpy.context.scene.render.resolution_y = 1280
    bpy.context.scene.render.image_settings.file_format = "PNG"

    out_dir = Path('/Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/out/layered_tops_test/diagnostics/false_renders')
    out_dir.mkdir(parents=True, exist_ok=True)

    # Camera targets (torso focus: Z ~ 1.05m)
    views = [
        ("front", (0.0, -2.4, 1.08), (math.radians(88), 0, 0)),
        ("persp", (1.7, -1.9, 1.15), (math.radians(86), 0, math.radians(42))),
        ("side", (2.4, 0.0, 1.08), (math.radians(90), 0, math.radians(90))),
        ("back", (0.0, 2.4, 1.08), (math.radians(92), 0, math.radians(180))),
        ("detail", (0.0, -1.2, 1.15), (math.radians(88), 0, 0)),
    ]

    for v_name, pos, rot in views[:1]:
        cam_obj.location = Vector(pos)
        cam_obj.rotation_euler = Euler(rot, "XYZ")
        out_img = str(out_dir / f"avatar_shirt_{v_name}.png")
        bpy.context.scene.render.filepath = out_img
        print(f"Rendering {v_name} -> {out_img}...")
        bpy.ops.render.render(write_still=True)
        print(f"Saved {out_img}")

    print("All renders completed successfully!")

if __name__ == "__main__":
    main()