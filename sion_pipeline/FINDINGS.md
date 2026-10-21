# What we learned draping GarmentCode clothes for sion-avatar (raw notes for the do/don't guide)

Each entry: what went wrong, why, what fixed it, and the run that showed it (`out/<name>/`).

## Pose
- **Drape in the fitting app's A-pose and let its importer un-pose** (`drape_blender.py --pose a`, import with
  `--weights body --pose a`). Turning the garment back to the T-pose ourselves tore the armpits.

## Sewing
- **Pull the seams fully shut** (`--sewing-force 0`, the default now). With a force cap of 10 the right underarm
  seam stayed 17 mm open in the A-pose (`tee_apose`), because the arm squeezes the cloth there.
- Gravity while sewing doesn't help: it left the seams more open (`tee_apose` tags `g1`, `g03`).

## Length: the hem ends up about 7 cm higher than GarmentCode places it
- **Why:** GarmentCode puts the front and back panels at shoulder height, one in front of the body and one
  behind. Sewing the shoulder seam pulls them together over the top of the shoulder, which uses about 7 cm of
  each panel (on this body the pattern is 12-14 cm short of hem -> over the shoulder -> hem). The bust takes a
  little more from the front.
- It is not the sleeves pulling up: a sleeveless tee rose just as much (`tee_sleeveless`), and a shallower
  armhole made it worse (`tee_apose_shallow`).
- It is not the length: a longer pattern rises the same amount (`tee_long`). So choose `shirt.length` for where
  the hem should *end*: `tee_long` (length 1.44 instead of 1.2) lands at the hip like a normal tee.
- `make_pattern.py --front-extra 2.5` gives the front its bust room so front and back hems come out level.

## Hips wider than the bust
- sion bodies have hips of 74 cm and a bust of 67 cm. GarmentCode's plain tee is cut straight down from the bust,
  so a hem at hip level is tighter than the hips. Use `shirt.flare` 1.1 so the hem has room (`tee_long_f11`).
  This mattered less than expected for the rise, but the flared run also stopped a sleeve getting caught in the
  armpit.

## Neckline
- The neckline that stood up like a collar was a symptom of the rise. Once the length was right it lies flat.
- **Don't widen the neck much on these narrow shoulders:** `collar.width` 0.6 (14 cm opening) left only about
  4 cm of shoulder seam, and the shirt slid off the shoulders into a tube top (`tee_long_n06`).

## Fabric: use calibrated presets, never tune knobs per garment
- **The owner judged `tee_long_f11` (bending 60, longer, flared) worse than `tee_apose` (bending 2, sewing force
  10).** Tuning stiffness by eye on one garment made it look like card. Lesson: cloth settings come from a fabric
  preset that was measured on test pieces, the way Marvelous Designer ships fabric presets, and a new drape is
  always compared side by side with the accepted one before it replaces it (`run.py`, `compare.png`).
- `fabrics.json` holds 11 presets (chiffon to canvas). Each has the real fabric's numbers (weight, stretch, drape
  coefficient) and the Blender settings that reproduce them. `fabric_tests.py --calibrate` finds the Blender
  settings with the same three tests a textile lab uses, on test pieces meshed exactly like garments
  (`fabric_specimens.py`: GarmentCode + BoxMesh, 1 cm):
  - stretch: a hanging strip under 20x gravity (sets tension);
  - drape: a 30 cm disc on an 18 cm stand, the Cusick drape test (sets bending);
  - bending length: a strip pushed off a ledge (ASTM D1388). Reported only, see below.
- **Why Blender cloth draped like card at real settings** (each found with `fabric_tests.py --sweep`):
  - Shear stiffness does nothing on our meshes. Blender only adds shear springs across quads, and GarmentCode
    meshes are all triangles.
  - With compression = tension the triangle mesh locks: a disc can't fold over the stand without squeezing
    in-plane, so it stays flat like card at any bending. **Compression 3% of tension** lets it fold
    (`tests.compression_ratio`). It is the stand-in for the missing shear.
  - Real wovens barely stretch (chiffon 3% under the test load means tension about 17000 per kg). That stiff,
    the drape number jumped around 0.4-0.5 whatever the bending. **Stretch floor 0.5%**
    (`tests.min_hang_stretch_pct`): no preset is stiffer in tension than that. Cost: wovens stretch a little more
    than real when pulled tight.
  - Drape is chaotic: the same settings with the cloth started 0.3 mm differently give drape numbers 0.05-0.08
    apart. Calibration averages 3 starts (`tests.drape_runs`).
- **The cantilever and the drape test disagree in Blender.** Settings that drape right make a strip that folds
  sharply at the ledge edge and hangs nearly straight down (bending length 0.7-2.6 cm instead of 1.7-5.5). A disc
  can only drape by bending in two directions at once, which also squeezes the cloth, so the drape test measures
  bending and compression together, as a garment does. We calibrate by the drape and only report the cantilever.
- Calibrated drape (real -> Blender): chiffon 0.28 -> 0.22 (floppiest, the one miss), satin 0.35 -> 0.31,
  jersey 0.42 -> 0.44, rib 0.45 -> 0.44, poplin 0.62 -> 0.59, wool 0.66 -> 0.65, fleece 0.60 -> 0.58,
  linen 0.74 -> 0.74, denim 0.80 -> 0.81, leather 0.82 -> 0.83, canvas 0.88 -> 0.88 (`out/fabrics/`).
- Settings depend on mass per vertex (gsm x 0.15/160), so presets carry over only at the same mesh size (1 cm).
- Older notes, still true: a longer settle doesn't remove ripples, neither does less friction; ripples don't show
  up as stretch, so look at renders, not only numbers.

## Result
- Accepted (`accepted/tee/`): the owner's preferred `tee_apose`, made before recipes with the old settings.
- In the fitting app `gc:shirt` is still `tee_long_f11`, which the owner disliked. The next `run.py --accept`
  replaces it.

## Blender with the calibrated presets: the tee collapses (unsolved)
- `run.py garments/tee.yaml` (cotton_jersey preset) shrank the tee from the shoulders to a band at the waist. It
  happened while the seams were being pulled shut, with gravity off (`out/tee/tee_states.npz`: top of the shirt
  1.43 m at the start, 1.18 m after sewing). Caught by `compare.png` before anything was replaced.
- Not the low compression: compression 156 (= tension), 47 and 16 all collapsed the same way (`out/tee` tags
  `c156`, `c47`, `c16`). Still to test: the preset's higher tension (156 vs the old 40) and bending (73 vs 2).
- Lesson: a preset that drapes a disc right can still fail on a garment. A garment run must be part of accepting
  a preset.

## GarmentCode's own simulator (Warp, on Colab): see warp/HANDOFF.md
- Skin-tight tank top (`designs/tank_tight.yaml`: FittedShirt, cut to the body with darts, no added room,
  sleeveless, scoop neck 0.8, back scoop 0.3, neck width 0.25 gives 4.5 cm straps), 2026-10-13:
  - drape 5 s on the T4, 0 body or self intersections; cloth to skin median 0.5 cm, 90th 1.3 cm.
  - fitting app `gcwarp-tank:top`: no poke-through at the default, smallest and largest shapes;
    `--motion` 16 points, mostly the left strap (shoulder.L), up to 7.5 mm.
- Each import set is one outfit in the fitting app. Importing into an existing set (first try: `gcwarp:tank`) made
  the app wear it together with `gcwarp:shirt` and mixed their check results. Give each test garment its own set.

## Skin-tight tank, round 2 (2026-10-13): why it isn't skin tight and why it's spiky
- Owner's feedback on `gcwarp-tank:top`: not skin tight, spiky at the biggest and smallest bust.
- Three causes, in order of how much they show:
  1. The avatar itself. Its bust slider (the legacy procedural field in `fitting/src/core/shape.mjs`) leaves a
     hard crease along the bottom and inner side of the breasts at the biggest bust, and small points and ridges
     at the smallest bust. Clothes follow the skin, so they copy these. The bare body shows it
     (scratch render `lumps/body.png`).
  2. The fitting app's follow and push-out make uneven spots worse. Each piece of cloth is tied to its nearest
     skin triangle with a fixed offset that doesn't turn with the skin. Then the push-out moves single spots
     by up to 3 cm.
  3. The drape: FittedShirt's big darts leave slack folds under the bust.
- Simple smoothing of the bust slider's change (scratch `bodysmooth.mjs`) is not the fix. At the biggest bust
  the breasts got droopier, and at the smallest a new bump appeared. A fix needs to soften only the crease edge,
  or treat small and large busts separately. It is fitting-app code: ask the owner before changing it.
- Tighter versions (the owner approved cutting about 10% smaller than the body for this test only; CLAUDE.md
  says no negative ease):
  - FittedShirt on a body 10% smaller (`kit/sion_female_tight10*.yaml`): smooth over the bust, but a band of
    folds stays under it.
  - Plain front with no darts, 10% smaller (`designs/tank_knit.yaml`): hugs the waist, but slides down under the
    breasts. Extra front length (`--front-extra 3`) and a 2 mm gap didn't stop it. A stretchy top with no
    shaping needs room at the bust and tightness only below it.
- Warp keeps the cloth about 4 mm off the skin (body collision 0.25 cm plus fabric 0.1 cm).
  `warp/sim_props_tight.yaml` (collision 0.1 cm) brings the median to about 2.6 mm.
- A deep scoop neck (fc_depth 0.8) on the no-dart front breaks GarmentCode's mesher (degenerate triangles);
  0.65 works.
- Why the no-dart tank slid: GarmentCode's Shirt side seam is one straight line from the hem to the armhole, so
  cut 10% under at the hem it crossed the bust about 24% under the bust measurement (51 cm on a 67 cm bust).
  Fix: `knit_panels.py` (used when a design has a `knit` section) bends the side seam through the waist, underbust
  and bust widths. `designs/tank_knit2.yaml`: 0.95 x bust, 0.9 x underbust and waist, 2 mm gap props. It stays up
  and covers the bust (scratch render `drapes/compare3.png`). Cloth to skin about 2.5-3 mm at the waist and
  underbust; about 10 mm at the 90th percentile over the bust, where it bridges the cleavage.
  - Variants: 1.0 x bust is a little looser over the bust, otherwise the same. With no centre-front hem drop
    (front_room 0) the hem stays level and nothing else changes much.
  - Front and back must use the same width split at every level: a split that follows the body puts a much
    bigger bend in the front seam than the back, GarmentCode cuts the seams into sub-centimetre pieces to match
    them, and BoxMesh fails (StitchingError).
- `designs/tank_knit3.yaml` (the owner's pick: level hem, plus "cover up a little more": scoop 0.5 instead of
  0.65), imported as its own outfit `gcwarp-tank3:top` ("Tank top 3 (GarmentCode Warp)"). Checks: no
  poke-through at the default, smallest and largest shapes, and none in `--motion` (the first tank had 16 points).
  In the app it is smoother than `gcwarp-tank:top` at both bust extremes: the dents and the fold band are gone.
  What's left comes mostly from the avatar: a crease under the breasts at the biggest bust, small wrinkles at the
  armpits, and a faint line down the centre-front seam at the smallest bust. `gcwarp-tank:top` is still there,
  unchanged.
- `designs/tank_knit4.yaml` (owner: "neck higher still", and "too much fabric at the armpits, making a little
  spike"): neckline fc_depth 0.4. Imported as its own outfit `gcwarp-tank4:top` ("Tank top 4 (GarmentCode
  Warp)"); `gcwarp-tank3:top` is unchanged.
  - Armpit fabric: the sion body has a deep hollow at the front of the armpit, and GarmentCode's ArmholeCurve
    edge stretched straight across it, about 2 cm off the skin. Fix: `sleeve.armhole_shape: ArmholeKnit` with
    `knit.armhole_scoop: 0.4` cuts the lower half of the armhole deeper. Loose points at the front armpit went
    from 47 (tank 3) to 7.
  - Making the armpit narrower barely helped. It also had side effects (GarmentCode's armhole-depth cap came
    off, the neckline rose), so it was removed.
  - The point at the side of the bust, about 4 cm under the armpit:
    - Bulging the side seam outward to round the bust (`bust_round`, removed) made it worse: wider under the
      bust, and a sharper turn at the underbust.
    - A smooth S-curve seam (`knit.side_curve: 0.5`) and front/back seams cut to the same length
      (`knit.side_match`; the front was about 0.8 cm longer) each helped a little. Neither removed the point.
      `side_match` on the straight-segment seam (side_curve 0) gives a StitchingError: the front and back edge
      fractions no longer match, and GarmentCode splits the edges into sub-cm pieces.
    - Root cause: the side seam from the waist to the armhole is about 1 cm longer than the body's side is tall
      there. Its 2D slant shapes the girth, but on this body the girth grows in front and back, not at the side
      (the side moves out only 8.8 -> 10.2 cm between 112 and 120 cm high). The tight waist holds the seam at
      the bottom and the armhole holds it at the top, so the extra length bows out at bust height (119-121 cm),
      about 14 mm.
    - Fix: end the armhole 2.5 cm lower (`knit.armhole_drop: 2.5`). `knit_panels.install` adds it to
      GarmentCode's armhole depth (`BodiceHalf.eval_dep_params`), past the cap of "last side edge - 1 cm".
      1.5 cm left a smaller point. The seam bump at 119-121 cm is now 9-10 mm, vs tank 3's 10-14 mm (the body's
      own shape there).
  - Drape: median 2.7 mm off the skin, nothing inside the body. Fitting checks: no poke-through at the default,
    smallest and largest shapes, or in `--motion` (Spin).
  - In the app, the biggest bump (mm) on the cloth:

    |        | bust 0 | bust 1 | smallest | largest |
    |--------|--------|--------|----------|---------|
    | tank 4 | 10.1   | 11.7   | 9.9      | 11.6    |
    | tank 3 | 13.0   | 15.4   | 12.2     | 15.7    |

    The 99th percentile is about the same for both, 6.2-7.3 mm. At the biggest bust tank 4 no longer gaps at the
    cleavage or folds under the bust. At the smallest bust both still wrinkle at the centre front and armpits;
    that comes from the avatar's bust slider (see above), not the pattern.
  - Rule for knit tops pinned tight at the waist: the side seam must not be longer than the body's side path
    from the waist to the armpit. Measure it on the body and lower the armhole (or shorten the seam) to match.

## Male body: flat chest
- `measure_body.py` found the bust as the most forward point off the centre line. A male chest has no point
  standing out past the breastbone, so it picked a spot near the waist (bust 62 cm, below the underbust).
- **Fix:** if nothing stands out past the breastbone by 0.5 cm, place the bust points as GarmentCode's male average
  does, scaled to the height, and look for the underbust only a few centimetres lower. Male now: bust 74 cm at
  121 cm, underbust 71 cm, waist 62 cm. The female numbers did not change.
