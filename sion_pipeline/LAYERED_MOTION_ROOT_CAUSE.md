# Layered garment motion: root cause and pipeline requirements

Status update 2026-10-21: this report describes the **pre-repair** runtime.
`sion-avatar` commit `b7fdfda8925833c468e20b1e2c3542b209095637` now applies
posed surface bindings for authored inner cloth, shared by viewer and checks.
The owner reports the shirt no longer visibly clips in motion. Recorded visible
coverage validation shows substantial improvement with residual edge artifacts;
it is not a rerun of this report's triangle audit. See
[the handoff progress update](HANDOFF_LAYERED_SHIRT_PIPELINE.md) and the sibling
repository's `fitting/README.md` for current results and remaining limits.
The diagnosis, counts and proposed requirements below remain historical evidence.

2026-10-18. Investigated `layered-shirt:top` in the current local fitting app.

The pipeline currently guarantees a clean static drape, not that physical layers
remain ordered during animation. Independently skinned layers cross as joints move.
The failure already exists with the original EveryWear weights; conversion can
aggravate it. Runtime clearance and the old validator do not cover this failure.
The shirt is **not motion-ready**.

## Measured evidence

Exported the app's actual shaped and dressed positions, then ran the same CPU
skinning function used by its viewer. Compared real inner/outer triangle geometry
with Blender BVHs (zero epsilon). Tested four evenly spaced interior moments of
every moving clip, plus A/T poses, on the default body and chest-size 0.6.

| Stage / body | A-pose | T-pose | Idle, range over 4 moments | Model Pose, range over 4 moments |
|---|---:|---:|---:|---:|
| Original EveryWear weights, up to 8 influences | 0 | 0 | 774–1,100 | 1,353–1,667 |
| Original weights reduced to 4, no filtering | 0 | 0 | 744–1,091 | 1,313–1,647 |
| Converter's filtered 4 weights | 0 | 0 | 797–1,176 | 1,414–1,808 |
| Final app, default body | 0 | 0 | 880–1,181 | 1,420–1,816 |
| Final app, chest-size 0.6 | 0 | 0 | 897–1,258 | 1,461–1,827 |

Numbers count intersecting triangle pairs, **not holes, affected people, surface
area, penetration depth or severity**. Counts depend on tessellation. All six
moving clips have at least one failing sample with original source weights and
with the final imported garment. All 48 final dressed moving samples fail.
Default and chest-size 0.6 rest geometry have zero cross-layer intersections.
Shaped and dressed frame counts are identical: dressing is not repairing this.
The native MD static drape also has zero body/layer intersections.

For source isolation, used the exact unwelded OBJ and its per-pattern nearest
FBX weights, before the converter's arm/bust filtering. Replayed them on the target
skeleton, first taking the A-pose geometry back through its own blended inverse,
then applying each clip. Applied the same 180-degree facing conversion as import.
Raw-8/raw-4/filtered-4 use the same geometry and clips. These are controlled target
replays, not a claim that native MD ran an animated cloth simulation.

Calibrated source-to-app A-pose geometry by panel: median nearest distance
0.00054 mm; maximum 2.54 mm after fitting. The source replay and app differ slightly
because fitting/import changes the asset. The table localizes the failure without
pretending the stages have identical vertex order or final geometry.

Visually confirmed in the live viewer: Model Pose at about 5.28 s, chest-size 0.6,
shows blue through black on the back, shoulders and side. Screenshot:
`out/layered_tops_test/rca_model_pose.png`.

## Causal chain

1. **Static collision resolution ends at draping.** EveryWear supplies skeletal
   skin weights. Those weights do not encode an inner/outer contact constraint.
   Zero intersections at the draped pose does not establish collision-free motion.
2. **The layers use different local blends.** Of 9,651 outer vertices with an
   inner vertex within 12 mm at A-pose, 407 nearest pairs differ by more than 0.2
   in weight L1 distance (maximum 1.54). In Model Pose at 5.279 s, these pairs'
   relative vectors change by up to 30.4 mm (95th percentile 4.78 mm). This is a
   nearest-vertex diagnostic, not a contact correspondence or penetration-depth
   measurement. It demonstrates differential motion large enough to consume
   small layer gaps. Even matching nearby weights is not a universal collision
   guarantee under arbitrary joint motion or folds.
3. **Slider smoothing solves a different problem.** `shape-weights.mjs` explicitly
   couples nearby surfaces for slider deformation. `import-vrm.mjs:1168–1171`
   keeps the original motion J/W separately. Passing body-shape checks therefore
   says nothing about this motion failure.
4. **Contact happens before posing.** `app.mjs:266` calls `dresser.dress()`;
   `app.mjs:298–311` then skins its output and sends it straight to the viewer.
   There is no posed cross-layer contact pass. Rest piece carrying/lifting cannot
   enforce separation after independent skinning.
5. **Physical layer semantics do not survive as a usable contract.** The imported
   shirt is one item at layer 30 with 20 material primitives. Names retain `l0_`
   and `l1_`, but the runtime has no explicit relationship saying which surfaces
   belong to the two physical shells or which must remain outside. Connected
   panels, render materials, physical shells and catalog items are different
   concepts. Inferring shell order from connected-piece size is insufficient.
6. **The acceptance check cannot see the defect.** `fit-check.mjs:144–164` creates
   one coverage layer per catalog item and compares it with skin/other items.
   `layerOf()` uses an outermost-height coverage projection. It never compares
   this item's inner and outer surfaces. A fresh Idle run reports zero poke points
   at all four moments while the direct mesh check finds 880–1,181 intersections.
   Its global failure also includes unrelated stale-import warnings; these are
   not the layer-motion failure.

## Conversion is a contributor, not the primary cause

The converter redirects arm/shoulder weights based on panel arm-dominant share
and distance from sleeve panels, fades upward bust weights, then keeps four
influences. It modifies 5,436 vertices in this asset. The importer has a second,
similar heuristic. These decisions are made independently per surface; different
panel shapes can therefore change neighboring layers differently.

Raw eight-influence weights already fail. Four-influence reduction alone does
not explain the defect; the measured unfiltered reduction is similar and sometimes
slightly better. Filtering increases the worst sampled Model Pose count from
1,647 to 1,808. The importer is a smaller additional perturbation in this asset:
nearest same-panel weight comparisons have no L1 difference above 0.1, maximum
0.097. None of this justifies treating the current raw EveryWear output as a
motion-safe final asset or removing all filtering blindly.

## Pipeline changes required

The supported animation/body-shape envelope must be an explicit acceptance
boundary. Static A/T-pose, normalized weights, bone count and successful export
are structural checks, not animation acceptance.

1. **Preserve semantics from generation onward.** Carry physical shell IDs and
   inner/outer contact relationships, panel/seam identities and intentionally
   exposed regions through MD, GLB, import and catalog loading. They must be
   independent of material color/names and of whether the outfit is one item.
   Missing relationships must be reported as unchecked, never silently passed.
2. **Add a motion acceptance gate at each transformation.** Check original
   binding, conversion, import, shaping and final dressed animation geometry.
   Compare actual shell surfaces, including surfaces inside one item. Include
   body contact, open-boundary rules, thickness/gap tolerances, visibility and
   penetration area/depth, alongside intersection localization. Sample all
   supported clips/body shapes and refine near contact or rapid relative motion;
   retain a visual review of failing frames. Four samples were enough to diagnose
   this asset, not enough to certify every moment.
3. **Use a shared deformation model for overlapping shells.** Treat EveryWear
   weights as an initial binding. Build contact-aware correspondences/common
   deformation support at setup, preserving seam continuity and intentional
   free hems/cuffs. Fit the binding jointly across neighboring shells and the
   supported poses. Apply influence reduction once and revalidate afterward;
   independently stripping weights twice is not a layer-aware solution.
4. **Handle residual posed contact explicitly.** A common binding improves
   coherence but cannot guarantee separation for every fold or pose. For the
   current lightweight runtime, precompute pose-dependent contact correctives
   and validate their interpolation over the supported envelope. If arbitrary
   unseen animation must be supported with a stronger separation guarantee,
   an actual posed contact/cloth solver is needed. A fixed rest offset or a few
   saved corrections cannot provide that guarantee.

These are proposed architecture changes, not shipped repairs. Start with semantic
layer data and the acceptance gate so later binding/corrective work has a valid
success criterion. Do not enlarge only this tee, delete its hidden blue surface,
copy body weights blindly, or re-enable radial piece pushes as the pipeline fix.

## Added diagnostic and reproduction

`inspect_layer_motion.py` is a reusable offline triangle checker. It requires an
explicit `physicalLayer` on every primitive, validates the supplied frame buffers,
and reports its limited scope. It does not infer layers from colors or garment
names. The experiment assigns its 12 inner and 8 outer primitives in data.

```sh
/Users/vaz/.local/bin/blender -b -P sion_pipeline/inspect_layer_motion.py -- \
  sion_pipeline/out/layered_tops_test/motion_rca/manifest.json \
  --output sion_pipeline/out/layered_tops_test/motion_rca/layer-motion-check.json
```

The all-frame report has 109 geometry snapshots, with 96 failures (shaped and
dressed stages counted separately). The 13 rest/A/T control snapshots pass.
Both controls and the visible motion failure were checked; the failing check was
not accepted on its count alone.

Diagnostic scripts and full reports are in `out/layered_tops_test/motion_rca/`:
`dump-stages.mjs`, `dump-source.mjs`, `extract-source-weights.py`,
`source-weights.json`, `intersections.json`, `source-motion/intersections.json`,
`weight-comparison.json`, `old-check-idle.json`, `control-check.json`, and
`layer-motion-check.json`. Extraction reuses converter matching in a diagnostic
copy and stops before export. The garment, imported asset, app engine and catalog
were not modified during this investigation.
