"""Run inside headless MD after the two-layer drape has passed visual review.

Uses the validated 188-bone EveryWear bridge, restoring exact draped vertices
following the one solver step needed to initialize the rigging interface.
"""
import ctypes
import json
from pathlib import Path
import traceback
import ApiTypes
import import_api
import export_api
import pattern_api
import utility_api

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'sion_pipeline/out/layered_tops_test'
REFERENCE = ROOT.parent / 'REA-MARVELOUS/output/antony-price-macaw-dress/everywear-probe'
STEM = 'layered_tops_both'


def run():
    report = {}
    report_path = OUT / f'{STEM}_rigging.json'
    try:
        utility_api.NewProject()
        opt = ApiTypes.ImportZPRJOption()
        opt.bLoadAvatar = False
        opt.bLoadGarment = True
        assert import_api.ImportZprj(str(OUT / f'{STEM}_draped.zprj'), opt)
        coords = []
        for line in (OUT / f'{STEM}_draped.obj').read_text().splitlines():
            if line.startswith('v '):
                coords.extend(map(float, line.split()[1:4]))
        expected = len(coords) // 3
        assert expected > 0

        op = ApiTypes.ImportExportOption()
        op.ImportObjectType = 0
        op.scale = 10.0
        op.bAutoTranslate = False
        op.bMoveGarment = False
        op.bAdd = False
        op.bAutoCreateFittingSuit = False
        assert import_api.ImportFBX(str(REFERENCE / 'sion-female-full-188-rigged-fixed.fbx'), op)
        lib = ctypes.CDLL(str(REFERENCE / 'everywear_bridge.dylib'))
        for name in ('ew_avatar_count', 'ew_joint_count', 'ew_has_skin_controller'):
            fn = getattr(lib, name)
            fn.argtypes = []
            fn.restype = ctypes.c_int
        report['avatars'] = lib.ew_avatar_count()
        report['joints'] = lib.ew_joint_count()
        assert report['avatars'] == 1 and report['joints'] == 188
        assert lib.ew_has_skin_controller()
        for pid in range(pattern_api.GetPatternCount()):
            pattern_api.SetPatternFreeze(pid, False)
            pattern_api.SetPatternStrengthen(pid, False)
        utility_api.SetSimulationGravity(0)
        utility_api.Simulate(1)
        utility_api.SetSimulationGravity(-9800)
        lib.ew_transfer_weights.argtypes = [ctypes.c_int]
        lib.ew_transfer_weights.restype = ctypes.c_int
        report['transfer'] = lib.ew_transfer_weights(8)
        assert report['transfer'] == 1
        lib.ew_set_exact_positions.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_int]
        lib.ew_set_exact_positions.restype = ctypes.c_int
        report['expected_vertices'] = expected
        report['restored_vertices'] = lib.ew_set_exact_positions((ctypes.c_float * len(coords))(*coords), expected)
        assert report['restored_vertices'] == expected
        lib.ew_export_fbx.argtypes = [ctypes.c_char_p]
        lib.ew_export_fbx.restype = ctypes.c_int
        report['export_fbx'] = lib.ew_export_fbx(str(OUT / f'{STEM}_everywear.fbx').encode())
        assert report['export_fbx'] == 1
        opt_out = ApiTypes.ImportExportOption()
        opt_out.bExportGarment = True
        opt_out.bExportAvatar = False
        assert export_api.ExportOBJ(str(OUT / f'{STEM}_everywear.obj'), opt_out)
        # Keep the two layer colors through the unwelded per-pattern OBJ converter.
        obj_path = OUT / f'{STEM}_everywear.obj'
        obj_lines, current = [], None
        for line in obj_path.read_text().splitlines():
            if line.startswith('g '):
                current = line[2:].strip()
                assert current.startswith(('l0_', 'l1_')), current
            if line.startswith('usemtl ') and current:
                line = 'usemtl ' + ('InnerLightBlue' if current.startswith('l0_') else 'OuterCharcoal')
            obj_lines.append(line)
        obj_path.write_text('\n'.join(obj_lines) + '\n')
        obj_path.with_suffix('.mtl').write_text(
            'newmtl InnerLightBlue\nKd 0.55 0.72 0.88\n'
            'newmtl OuterCharcoal\nKd 0.045 0.045 0.055\n')
        export_api.ExportZPrj(str(OUT / f'{STEM}_everywear.zprj'), False)
        report['success'] = True
    except Exception:
        report['success'] = False
        report['error'] = traceback.format_exc()
        traceback.print_exc()
    report_path.write_text(json.dumps(report, indent=2))
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    run()
