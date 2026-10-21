"""Check native MD OBJ layer/body triangle intersections with Blender's BVH.

Blender -b -P inspect_md_drape.py -- cloth.obj body.obj --output report.json
Pattern names use l0_/l1_ prefixes; panels within one physical layer are grouped.
"""
import argparse
import json
from pathlib import Path
import sys
from mathutils.bvhtree import BVHTree


def read_obj(path):
    vertices, groups, current = [], {}, 'default'
    for line in path.read_text().splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == 'v':
            vertices.append(tuple(float(x) for x in parts[1:4]))
        elif parts[0] == 'g':
            current = parts[1]
        elif parts[0] == 'f':
            groups.setdefault(current, []).append([int(v.split('/')[0]) - 1 for v in parts[1:]])
    return vertices, groups


def inspect(cloth_path, body_path):
    vertices, groups = read_obj(cloth_path)
    body, body_groups = read_obj(body_path)
    body_tree = BVHTree.FromPolygons(body, [f for fs in body_groups.values() for f in fs])
    layers = {}
    body_hits = {}
    for name, faces in groups.items():
        prefix = name.split('_', 1)[0]
        layers.setdefault(prefix, []).extend(faces)
        hits = BVHTree.FromPolygons(vertices, faces).overlap(body_tree)
        if hits:
            body_hits[name] = len(hits)
    trees = {key: BVHTree.FromPolygons(vertices, faces) for key, faces in layers.items()}
    keys = list(trees)
    layer_hits = {f'{a}/{b}': len(trees[a].overlap(trees[b]))
                  for i, a in enumerate(keys) for b in keys[i + 1:]}
    return {'groups': len(groups), 'vertices': len(vertices),
            'body_intersections_by_panel': body_hits,
            'layer_triangle_intersections': layer_hits,
            'success': not body_hits and not any(layer_hits.values())}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('cloth', type=Path)
    parser.add_argument('body', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    report = inspect(args.cloth, args.body)
    result = json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(result)
    print(result, flush=True)
