"""Regression checks for curved GarmentCode boundaries crossing the MD bridge."""
import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sion_pipeline.drape_marvelous import (
    ROOT, boundary_segment_counts, generate_md_script, sample_panel_md_points,
)


class BoundaryMappingTest(unittest.TestCase):
    def test_compiled_layer_boundaries_and_seams(self):
        for layer in ('layer_1_inner_turtleneck', 'layer_2_outer_oversized_tee'):
            spec = ROOT / 'sion_pipeline/out/layered_tops_test' / layer / f'{layer}_specification.json'
            data = json.loads(spec.read_text())['pattern']
            counts = boundary_segment_counts(data['panels'], data['stitches'])
            maps = {}
            for name, panel in data['panels'].items():
                points, maps[name] = sample_panel_md_points(name, panel, 0, 0, counts)
                self.assertEqual([j for ids in maps[name].values() for j in ids], list(range(len(points))))
                self.assertTrue(all(p[2] == 0 for p in points))
            expected_seams = 0
            for stitch in data['stitches']:
                a, b = stitch[:2]
                left, right = maps[a['panel']][a['edge']], maps[b['panel']][b['edge']]
                self.assertEqual(len(left), len(right))
                expected_seams += len(left)
            with tempfile.TemporaryDirectory() as tmp:
                script = Path(tmp) / 'drape.py'
                generate_md_script([spec], script, Path(tmp) / 'cloth.obj', Path(tmp) / 'cloth.zprj')
                source = script.read_text()
                compile(source, str(script), 'exec')
                self.assertEqual(source.count('assert pattern_api.AddSeamlinePairGroup('), expected_seams)


if __name__ == '__main__':
    unittest.main()
