# Handoff: test the staged Modelista prompts on the difficult gown

Date: 2026-10-21
Repository: `/Users/vaz/Desktop/antigravity_apps/GarmentCode`

## User objective and sequence

Test the human-pattern-maker workflow on the more difficult gown discussed in the
previous work (the handoff calls it the **Emerald Couture Gown**). Start with the
existing, previously tested semantic deconstruction prompt. Then **create and test
the four drafting prompts one by one**. This is an experiment in staged garment
interpretation and pattern drafting, not a request to implement the entire automated
service or to draft all the prompts before trying them.

The user's latest instruction:

> create a handoff, we are going to test the 4 prompt pipeline in the more difficult gown, starting iwht the prompt we already tested, and creating the next prompts one by one

## What has actually been tested

- The standalone Stage 0 prompt exists in
  `sion_pipeline/STAGE_0_DECONSTRUCTION_PROMPT.md`. The previous handoff records
  standalone tests on the two-layer shirt and the Emerald Couture Gown (reported
  as three physical layers). This is documentary evidence, not a recovered model
  transcript. Do not assume the old layer inventory is correct without the image.
- The layered shirt was subsequently built using manually authored GarmentCode
  parameters in `sion_pipeline/test_compile_shirt_layers.py`, followed by real
  pattern compilation, MD draping, EveryWear rigging, and Sion avatar import.
- That shirt exercise **did not execute the proposed four drafting prompts**.
  There is no `sion_pipeline/image_to_pattern/` implementation, staged pattern
  progression, or prompt-driven critic report in the current repository.
- The shirt's visible movement issue has since been repaired in sibling repo
  `/Users/vaz/Desktop/antigravity_apps/sion-avatar`, notably commit
  `b7fdfda8925833c468e20b1e2c3542b209095637`. The owner reports no visible motion
  clipping. Recorded coverage tests retain small edge artifacts; universal zero
  triangle intersections have not been established. See the updated
  `sion_pipeline/HANDOFF_LAYERED_SHIRT_PIPELINE.md` for scope and evidence.

## First action: recover the exact gown input

The original gown image and its standalone deconstruction response were not found
among the named gown/deconstruction artifacts in `sion_pipeline/` during this
handoff. Recover them from available conversation context or known local files.
If they cannot be recovered, ask the user for the original reference image and,
if available, the earlier response. Do not substitute an invented gown or fabricate
its prior output. Save a stable copy of the reference and record its source.

Read these sources before starting:

1. `AGENTS.md`, including the Sion avatar override in section 0.
2. `sion_pipeline/STAGE_0_DECONSTRUCTION_PROMPT.md` — the actual existing prompt.
3. `/Users/vaz/Downloads/IMAGE_TO_FANTASY_GOWN_IMPLEMENTATION_PLAN.md` — original
   stage responsibilities, proposed parameter ownership, and progression artifacts.
4. `DIGITAL_TAILORING_AND_FITTING_GUIDE.md` and `sion_pipeline/FINDINGS.md` before
   designing/fitting. Old `new_base_female` dimensions are method references only.
5. Relevant GarmentCode implementations and `assets/design_params/default.yaml`
   before specifying each drafting prompt's allowed parameters.

## Experimental workflow

Keep the existing Stage 0 prompt unchanged for the first run, so the experiment
starts from the prompt the user already tested. Save the exact input, response,
and any review notes. If the historical response is available, preserve it too;
label any fresh run separately. Review independent physical layers, seam versus
fold interpretation, silhouette, materials, and explicit assumptions about unseen
construction. A single front view does not establish a unique sewing pattern.

Then author **only drafting prompt 1**. Run it against the gown deconstruction,
compile its proposed parameters, inspect the actual 2D patterns, and record what
worked or failed. Refine that prompt as needed. Only after its result is usable,
author and test prompt 2, and repeat through prompt 4. For a multi-layer gown,
exercise each prompt on the relevant layers and preserve their separate identities.

| Prompt | Human drafting decision | Expected visible checkpoint |
| --- | --- | --- |
| Existing Stage 0 | Read the image: physical layers, base families, construction, landmarks, fabrics, assumptions | Saved technical deconstruction, no YAML/code |
| Drafting 1 | Choose calibrated base blocks and proportions: bodice/skirt families, lengths, rise, fit/ease | Base-pattern PNG and design YAML per layer |
| Drafting 2 | Shape the blocks: fitted/darted construction, neckline, armholes, straps/strapless edges, asymmetry | Contoured-pattern PNG and updated YAML |
| Drafting 3 | Add volume: flare, circle fullness, gores, godets, tiers, gathers, sleeve fullness | Volume-pattern PNG and updated YAML |
| Drafting 4 | Draft dependent details: collars, cuffs, waistbands, slits; assign component fabrics/colors | Final-pattern PNG, YAML, specification, material/layer metadata |

Each drafting prompt receives the reference image, accepted deconstruction,
current design, and previous pattern image (except prompt 1, which has no previous
checkpoint). Give it verified parameter definitions and a bounded ownership scope.
It should return a small structured parameter patch, not custom garment geometry.
Validate the old plan's suggested keys against the actual engine: it is a proposal,
not proof that every listed control has the claimed effect.

The plan also describes a **sixth prompt role**, a final visual critic after
Stage 0 + four drafting stages. Keep this distinct from the four drafting prompts.
Use agent/user inspection at every checkpoint now; implement and test a separate
critic prompt after the four stages if continuing the original plan. Do not claim
that critic has been tested simply because an agent looked at the patterns.

## Compilation, evidence, and corrections

Use `BodyParameters('sion_pipeline/kit/sion_female_default.yaml')` and authentic
GarmentCode `MetaGarment(...).assembly()` / pattern serialization. Match the Sion
A-pose calibration where relevant. Start from an explicit saved baseline: the
current `assets/design_params/default.yaml` has shirt/sleeve defaults and must not
silently introduce unwanted gown components.

A small local compilation helper is appropriate if needed. Avoid building a
multi-provider client, full CLI, or automated retry system before this staged test
establishes what each prompt needs. `sion_pipeline/make_pattern.py` and the shirt
compiler are implementation references; their existence is not evidence that the
new prompt sequence works.

For each stage and layer save:

- Exact prompt version and model identity when known, supplied context, and raw response.
- Proposed patch, accepted patch, merged design YAML, compiled specification JSON,
  and actual rendered pattern PNG. Keep previous checkpoints unchanged.
- Compiler failures and inspection findings; record retries and reasons.
- Any agent/manual intervention as a separate correction. Do not quietly repair
  model output and report the repaired result as unassisted prompt success.
- Panel inventory, proportions, expected shaping/volume/details, and unresolved
  uncertainties. A successful compile proves structural validity, not image fidelity.

Suggested locations: `sion_pipeline/modelista_gown_test/` for versioned prompts
and experiment notes; `sion_pipeline/out/modelista_gown_test/` for reference,
responses, per-layer/per-stage outputs, and a final progression sheet. Record the
actual chosen paths. Preserve physical layer IDs independently of material colors
and names, including intended overlap and exposed regions.

For a failed check about appearance, inspect the relevant rendered property before
concluding the garment is wrong. Distinguish a defective test, a parameter mapping
problem, a compiler limitation, and a prompt interpretation error. Report unsupported
construction honestly instead of silently replacing it with an easier silhouette.

## Completion for this experiment and later work

Success means the **actual gown reference** has passed through the existing
Stage 0 prompt and four incrementally authored/tested drafting prompts, producing
inspectable GarmentCode patterns and a documented progression for every physical
layer. List assumptions, fidelity gaps, retries, and manual interventions. The gown
must not be reported as reproduced merely because all stages compiled.

The immediate focus is image interpretation → 2D patterns. MD draping, 3D reference
comparison, EveryWear rigging, and runtime body/motion checks follow once the 2D
bundle is usable; they remain necessary before claiming a finished wearable gown.

If proceeding to MD, read `MARVELOUS_DESIGNER_PYTHON_API_GUIDE.md` first. The old
implementation plan's `point_type=1` curve strategy was disproved on the installed
build. Use the tested explicit type-0 curve sampling and original-edge → MD segment
mapping in `sion_pipeline/drape_marvelous.py`, with its boundary-mapping test.
Do not revive the obsolete curve strategy or assume shirt-specific arrangement
rules already generalize to every gown panel.
