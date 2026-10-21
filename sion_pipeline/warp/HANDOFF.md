# Handoff: GarmentCode's own cloth simulator (Warp) as an alternative to `drape_blender.py`

From: a separate Claude session working with the same owner (2026-10-13).
To: the agent maintaining `sion_pipeline/`.

Your files in `sion_pipeline/` were not changed. Everything new is in `sion_pipeline/warp/`. One item was added to
sion-avatar's fitting app: `gcwarp:shirt`. Your `gc:shirt` was not touched.

## What was done

1. **Got GarmentCode's simulator running.** GarmentCode ships a cloth simulator built on NVIDIA Warp (the
   `NvidiaWarp-GarmentCode` fork: Warp 1.0.0-beta.6 with a modified XPBD solver and `warp.collision.panel_assignment`).
   It needs CUDA, so it can't run on this Mac. It now runs on the owner's **Google Colab Pro (Tesla T4)**:
   - Notebook: https://colab.research.google.com/drive/19ccdirDbBnQdDKDhTUfZHmUY9-hSMh4A ("GarmentCode_GPU_drape.ipynb").
   - The runtime is wiped between sessions, so each fresh session needs about 5 min of setup:
     - CUDA 12.6 from NVIDIA's ubuntu2404 apt repo: cuda-nvcc, nvrtc-dev, cudart-dev, driver-dev, cccl. Colab's CUDA 13
       and Python 3.13 are too new for the fork.
     - A Python 3.10 venv: `uv venv --python 3.10 /content/venv`.
     - git-lfs.
     - `build_lib.py --quick --cuda_path=/usr/local/cuda-12.6`.
     - Run everything with `MPLBACKEND=Agg`.
   - File transfer: Drive for desktop syncs `sion_pipeline/warp/jobs/` as a "My Computer" folder (account
     transcricao164). Colab sees it as `/content/drive/Othercomputers/My Mac/jobs/`, readable and writable, and results
     sync back to the Mac in seconds.

2. **Draped your pattern on your body with it.** The inputs were the same as your accepted-candidate `tee_long_f11` run:
   - design `designs/tee_long_f11.yaml`;
   - `--front-extra 2.5`;
   - body `kit/sion_female_default.yaml`;
   - A-pose body `kit/female_apose_body.json`.

## The pipeline (new files, all in `sion_pipeline/warp/`)

| Step | Where | What |
|---|---|---|
| `prepare_job.py <name> --design ... [--front-extra 2.5]` | Mac | Builds the pattern with `MetaGarment` and packs a small job into `jobs/<name>/job.tar.gz`. Details below. |
| `run_job.py <job>` | Colab | Runs `BoxMesh` → serialize → `run_sim`, the same as GarmentCode's `test_garment_sim.py`. Writes `jobs/<name>/out/` (synced back). |
| `warp_to_glb.py -- <job>` | Mac, Blender | Builds the GLB and previews. Details below. |
| `fitting:import ... --as gcwarp:shirt --weights body --pose a` | sion-avatar | Same import options as your recipe. |

What `prepare_job.py` does:
- Sets `arm_pose_angle` to the angle measured from the kit's own joints, **47.7°**. Your recipe uses 46.
- Re-implements your `--front-extra` monkeypatch from `make_pattern.py`. **Please check it matches.**
- Packs the A-pose body converted to the GarmentCode frame: x→-x, y→y-floor, z→-z, in metres.
- Packs Warp body-segmentation labels made from each vertex's dominant J_Bip skin bone: body, left_arm, right_arm,
  left_leg, right_leg, face_internal.
- Packs the spec and `assets/Sim_props/default_sim_props.yaml`.

What `warp_to_glb.py` does:
- Converts `result.npz` (cm, GarmentCode frame) with your `gc_to_blender`.
- Builds the armature exactly as `drape_blender.py` does, in the kit's A-pose.
- Skins with your method: 6 nearest body vertices, top 4 bones.
- Exports with the same glTF settings.
- Renders front/side/back previews with your camera setup.

Simulator settings: **GarmentCode's defaults, untuned**. These include:
- `garment_edge_ke: 1.0` (very soft bending), `garment_tri_ke: 10000`, `spring_ke: 50000`, `fabric_friction: 0.5`;
- `resolution_scale: 1.0`;
- collars held by attachment constraints for 400 frames.

The sim stopped at frame 422 once static: 14.4 s, 0 body collisions, 0 self collisions, no fails. **None of your
`fabrics.json` calibration is used yet.** Warp's parameters are different from Blender cloth's, so the presets don't map
1:1.

## Results, same pattern, same body

Side-by-side: `sion_pipeline/warp/jobs/tee_long_f11_warp/out/compare_blender_vs_warp.png` (your drape on top).

| | Blender (`out/tee_long_f11`) | Warp (`warp/jobs/tee_long_f11_warp/out`) |
|---|---|---|
| Vertices / triangles | 4473 / 8766 | 4780 / 8776 |
| Hem above floor (pattern 88.2 cm) | 99.1 cm | 95.1 cm |
| Cloth to skin, median / 90th | 1.2 / 3.5 cm | 1.1 / 3.6 cm |
| Points inside body after drape | 0 | 0 |
| `fitting:check` default / smallest / largest | ok / ok / ok (default checked this session) | ok / ok / ok |
| `fitting:check --motion` poke-through points | 19 | 5 (shoulder.R, armpit.R, up to 6.9 mm in Spin) |
| Visual | puckering and folds along shoulder/back seams | smooth seams, cleaner neckline and back |
| Drape time | minutes (Blender, CPU) | about 15 s (T4, once kernels are cached) |

Importer report for `gcwarp:shirt`: closest to skin 3.8 mm, 0 triangles dropped, 1 piece. It reported "fitted by the
skeleton alone", 2.8 mm from the skin in the T-pose.

## Caveats and open questions for you to analyze

1. **Only one garment tested.** Pants, skirts and layered pieces are untested on this body through Warp.
2. **Fabric.** Default GarmentCode material only. Is it worth porting `fabrics.json` presets to Warp material params,
   and how should they be calibrated?
3. **Arm angle.** It was 47.7° (measured) here against 46 in your recipe. This is a small difference, but the
   comparison isn't perfectly like-for-like.
4. **Front-extra parity.** Check that `prepare_job.py`'s re-implementation matches `make_pattern.py`, so the two drapes
   used the identical pattern. Diff `jobs/tee_long_f11_warp/tee_long_f11_warp_specification.json` against
   `out/tee_long_f11/tee_long_f11_specification.json`.
5. **Hem.** Both drapes hang above the pattern hem; Warp's is closer. Is the bust room still right?
6. **Motion poke-through.** It's all on the right side (shoulder.R, armpit.R) for Warp and mostly the left for Blender.
   This could be skinning or seam placement rather than drape.
7. **Integration.** `run.py` (recipes, compare sheet, `--accept`) only knows `drape_blender.py`. The proposal is a
   `drape: {engine: warp}` option in the recipe, with Blender kept as a fallback. Colab must be driven through the
   browser for each run; the Drive sync covers the file transfer.
8. **Skinning** is still your nearest-body-vertex method and was not changed. The fitting importer re-derives weights
   from the body anyway (`--weights body`).

## Proposal from the owner's side

Stop tuning the Blender cloth simulation. Keep the pattern, measurements, fit findings and Blender as the GLB/preview
exporter. Make the Warp drape the default once the open questions above check out.
