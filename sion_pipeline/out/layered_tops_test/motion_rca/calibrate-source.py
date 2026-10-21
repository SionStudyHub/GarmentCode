import array,json,sys
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
r=Path(sys.argv[sys.argv.index('--')+1]); m=json.loads((r/'manifest.json').read_text()); s=json.loads((r/'source-weights.json').read_text())
f=next(f for f in m['frames'] if f['shape']=='default' and f['stage']=='shaped' and f['clip']=='A-Pose')
a=array.array('f');a.frombytes((r/f['file']).read_bytes());P=[Vector(a[i:i+3]) for i in range(0,len(a),3)]
Q=[Vector((x,z,-y)) for x,y,z in s['positions_blender']]
for name,V in [('app',P),('source',Q)]:print(name,[(min(v[c] for v in V),max(v[c] for v in V))for c in range(3)])
for flip in [1,-1]:
 kd=KDTree(len(Q))
 for i,v in enumerate(Q):kd.insert((v.x*flip,v.y,v.z*flip),i)
 kd.balance();ds=sorted(kd.find(v)[2] for v in P);print('flip',flip,'nearest p50,p95,max',ds[len(ds)//2],ds[int(len(ds)*.95)],ds[-1])
