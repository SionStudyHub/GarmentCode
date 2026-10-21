"""Triangle-level stage isolation; materials select physical layer for this diagnostic only."""
import array, json, sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(sys.argv[sys.argv.index('--')+1]); m=json.loads((root/'manifest.json').read_text())
# Explicit evidence mapping: pale blue vs charcoal. No runtime layer inference.
faces=[[],[]]; partfaces=[[],[]]
for p in m['prims']:
    k=0 if p['material']['pbrMetallicRoughness']['baseColorFactor'][0]>.2 else 1
    ix=p['indices']; ff=[ix[i:i+3] for i in range(0,len(ix),3)]
    faces[k]+=ff; partfaces[k]+=[p['name']]*len(ff)
def read(f):
    a=array.array('f'); a.frombytes((root/f['file']).read_bytes()); return [Vector(a[i:i+3]) for i in range(0,len(a),3)]
rows=[]
for f in m['frames']:
    P=read(f); trees=[BVHTree.FromPolygons(P,F,all_triangles=True,epsilon=0) for F in faces]
    hits=trees[0].overlap(trees[1]); pairs={}; vertices=set()
    for a,b in hits:
        name=f'{partfaces[0][a]}/{partfaces[1][b]}'; pairs[name]=pairs.get(name,0)+1
        vertices.update(faces[0][a]); vertices.update(faces[1][b])
    rows.append({**f,'trianglePairs':len(hits),'affectedVertices':len(vertices),'panels':pairs})
report={'method':'Blender BVHTree actual triangle overlaps between explicitly mapped physical layers; zero epsilon; no body-height proxy','rows':rows}
(root/'intersections.json').write_text(json.dumps(report,indent=2))
for r in rows:
    if r['stage']=='dressed' or not r['clip']:
        print(r['shape'],r['stage'],r['clip'],round(r['time'],3),r['trianglePairs'],flush=True)
