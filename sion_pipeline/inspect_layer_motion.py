"""Inspect physical layers on actual exported runtime frames using Blender BVHs.

Usage: blender -b -P inspect_layer_motion.py -- manifest.json --output report.json
Manifest: vertexCount; prims[{physicalLayer, indices}];
frames[{file, ...description}]. Each file holds little-endian float32 XYZ positions
in metres, relative to the manifest. Physical layers must be explicitly assigned:
materials, disconnected panels and catalog items are not interchangeable with them.

This is an offline diagnostic, not a motion contact solver. It checks cross-layer
triangle intersections at the supplied frames; it does not certify unsampled times,
minimum cloth thickness, body clearance, or visibility masks.
"""
import argparse
import array
import json
import sys
from pathlib import Path
from mathutils.bvhtree import BVHTree


def inspect(manifest_path):
    manifest = json.loads(manifest_path.read_text())
    n = manifest['vertexCount']
    layers = {}
    for primitive in manifest['prims']:
        layer = primitive['physicalLayer']
        ix = primitive['indices']
        if len(ix) % 3 or any(v < 0 or v >= n for v in ix):
            raise ValueError('Invalid triangle indices')
        layers.setdefault(layer, []).extend(tuple(ix[i:i+3]) for i in range(0, len(ix), 3))
    if len(layers) < 2:
        raise ValueError('At least two explicitly assigned physical layers are required')
    rows = []
    for frame in manifest['frames']:
        values = array.array('f')
        values.frombytes((manifest_path.parent / frame['file']).read_bytes())
        if sys.byteorder != 'little':
            values.byteswap()
        if len(values) != n * 3:
            raise ValueError(f"Wrong position count in {frame['file']}")
        if any(not (-float('inf') < v < float('inf')) for v in values):
            raise ValueError('Non-finite positions')
        points = [tuple(values[i:i+3]) for i in range(0, len(values), 3)]
        trees = {k: BVHTree.FromPolygons(points, faces, all_triangles=True, epsilon=0)
                 for k, faces in layers.items()}
        names = list(layers)
        contacts = {f'{a}/{b}': len(trees[a].overlap(trees[b]))
                    for i, a in enumerate(names) for b in names[i+1:]}
        rows.append({**frame, 'trianglePairs': sum(contacts.values()), 'byLayerPair': contacts})
    return {'method': 'actual cross-layer triangle overlaps; zero BVH epsilon',
            'scope': 'supplied frames only; no body, visibility, thickness or continuous-time check',
            'frames': len(rows), 'failedFrames': sum(row['trianglePairs'] > 0 for row in rows),
            'success': bool(rows) and not any(row['trianglePairs'] for row in rows), 'rows': rows}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    report = inspect(args.manifest)
    if args.output:
        args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k != 'rows'}), flush=True)
    raise SystemExit(0 if report['success'] else 1)
