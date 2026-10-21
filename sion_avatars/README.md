# Sion avatars: the bodies to make clothes on

These are the avatars of the Sion avatar builder
(`/Users/vaz/Desktop/antigravity_apps/sion-avatar`), exported for
clothing tools. **Drape every new garment on one of these**, not on
`new_base_female`. That is an older, taller body,
and clothes made on it come out the wrong size.

| File | What it is |
|---|---|
| `sion-female-apose.obj` | Female body for Marvelous Designer, in millimetres (152 cm tall) |
| `sion-male-apose.obj` | Male body for Marvelous Designer, in millimetres (167 cm tall) |
| `sion-<gender>-apose.glb` | The same body in metres, rigged. Use it to rig the finished garment. |
| `sion-<gender>-apose.json` | Height, width, depth and every joint position, in millimetres |

All files share one setup:

- the default body shape, standing in an A-pose with the arms 45 degrees down;
- Y up, feet on the floor at 0;
- facing +Z, with the avatar's left at +X (Marvelous Designer's and
  GarmentCode's usual frame).

## Making a garment

1. Load the avatar in Marvelous Designer, for example
   `import_api.ImportFile("/Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_avatars/sion-female-apose.obj")`.
2. Take measurements, arrangement heights and hem heights from this body
   (`sion-<gender>-apose.json`, or measure the `.obj`). Don't reuse the
   numbers in older scripts: the `create_marvelous_*.py` scripts, the
   `new_base_female` tables and "1738 mm" are all for the old 173 cm body.
3. Drape the garment. Keep it in this pose and position, and don't move or
   scale it.
4. Export only the garment as `.obj`, in millimetres
   (`opt.bExportGarment = True`).

## GarmentCode patterns for these bodies

GarmentCode needs the body as measurements. `sion_pipeline/kit/` holds them
for the same avatars:

- `sion_female_default.yaml` is the female body, made by
  `node sion_pipeline/export_sion_body.mjs female` and then
  `./.venv/bin/python sion_pipeline/measure_body.py female`.
- Use it with `make_pattern.py --body sion_pipeline/kit/sion_female_default.yaml`,
  or `BodyParameters(...)`, instead of `assets/bodies/new_base_female.yaml`.
- `sion_male_default.yaml` is the male body, made the same way with `male`.

`sion_pipeline/drape_blender.py --gender <g> --pose a` drapes in Blender on
the same bodies. That route is described in `sion_pipeline/FINDINGS.md`.

## Bringing it into the avatar builder

Run these in `/Users/vaz/Desktop/antigravity_apps/sion-avatar`. Use the
same gender's files throughout.

```sh
# 1. Rig the garment to the avatar it was draped on (Blender 4.2+).
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P fitting/tools/rig-obj.py -- \
  <this folder>/sion-female-apose.glb <garment.obj> /tmp/my-shirt.glb --scale 0.001 --name Shirt

# 2. See its parts, then import the garment part.
npm run fitting:import -- /tmp/my-shirt.glb --list
npm run fitting:import -- /tmp/my-shirt.glb --part prim-2-0 --as myset:shirt --slot top --gender female --pose a

# 3. Rebuild and check.
npm run fitting:prepare -- female
npm run fitting:check -- female
```

`--list` shows the part names, so pick the garment's part from it, not the
body's. Then open the fitting app (`npm run fitting`) to look at it.

## Rigging headlessly with Marvelous Designer EveryWear

Instead of Blender weight transfer, you can transfer volumetric skin weights natively inside headless Marvelous Designer using `everywear_bridge.dylib` (`Marvelous::GarmentRiggingManager::Rigging` and `Marvelous::MetaverseConverter::Export`):

1. **Prepare a single-mesh rigged avatar FBX in Blender:**
   - **54-joint animation rig (`sion-<gender>-apose.glb`):** Delete unrigged helper meshes (e.g. `Icosphere` on `sion-female-apose.glb`), join all body meshes deformed by the armature into one `Body` mesh (`bpy.ops.object.join()`), and export FBX (`add_leaf_bones=False`, `use_armature_deform_only=True`, `apply_scale_options='FBX_SCALE_NONE'`).
   - **188-joint VRoid slider rig (`Sion-Female-Base-PreservedRig.vrm` via `export_188_fbx.py`):** Required when importing into `sion-avatar` with `--weights source` so the garment receives weights on VRoid adjustment bones (`J_Adj_*`, `J_Sec_L/R_Bust1/2`, `J_Sec_L/R_Skirt*`). Rotate the armature $180^\circ$ around $Z$ in Blender so it faces $+Z$, and **bake the Pose-Mode A-pose into the rest pose** (`DATA == POSE` via `modifier_apply` + `pose.armature_apply`) before exporting FBX so `ew_set_exact_positions` (`upd_init`) does not unskin the A-pose garment by $+37^\circ$ into a T-pose rest frame.
2. **Run headless MD with `everywear_bridge.dylib`:** Load the draped `.zprj` (`bLoadAvatar=False`, `bLoadGarment=True`), import the rigged avatar FBX with `ImportObjectType = 0` and `scale = 10.0`, unfreeze all patterns, step `Simulate(1)` at zero gravity if needed to populate `SimInterface`, call `ew_transfer_weights(max_influences)` (`1` for hats/rigid items, `4`–`8` for clothing), restore exact draped coordinates via `ew_set_exact_positions` if needed, and export both the native skinned FBX via `ew_export_fbx(out_fbx)` and the unwelded per-pattern OBJ/MTL via `export_api.ExportOBJ(out_obj, opt)`.
3. **Assemble the `sion-avatar` GLB (`fbx_to_glb.py`) and import with `--weights source`:**
   - Run `fbx_to_glb.py` in headless Blender to build the mesh directly from `ExportOBJ` in `g <pattern>` order (`0..N-1` material slots without cross-pattern seam welding or `usemtl` re-sorting), transfer weights per pattern slot from the evaluated FBX mesh (excluding welded seam edges $> 20\text{ mm}$), strip stray A-pose arm/shoulder and upward `Bust` proximity bleed on torso-dominant panels, and patch `baseColorFactor` into the GLB JSON.
   - Import into `sion-avatar`:
     ```sh
     npm run fitting:import -- /path/to/garment-everywear-188.glb --part Cloth --as myset:dress --slot one-piece --gender female --weights source
     npm run fitting:prepare -- female
     node fitting/tools/fit-check.mjs female --outfit myset
     ```

See [Section 12.7 of `MARVELOUS_DESIGNER_PYTHON_API_GUIDE.md`](../MARVELOUS_DESIGNER_PYTHON_API_GUIDE.md#127-headless-everywear-auto-rigging--skinned-fbxglb-export) for the complete C++ bridge source, Python scripts, and `sion-avatar` fitting invariants.

## Remaking these files

The avatars change when the builder's avatars change. Remake them from
sion-avatar with:

```sh
node fitting/tools/export-avatar.mjs --out ../REA-MARVELOUS/sion-avatars --out ../GarmentCode/sion_avatars
```

