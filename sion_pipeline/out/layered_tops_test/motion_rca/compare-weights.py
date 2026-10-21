import array,json,sys,statistics
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
r=Path(sys.argv[sys.argv.index('--')+1]);m=json.loads((r/'manifest.json').read_text());s=json.loads((r/'source-weights.json').read_text());bones=m['bones']
def read(f):
 a=array.array('f');a.frombytes((r/f['file']).read_bytes());return [Vector(a[i:i+3]) for i in range(0,len(a),3)]
def frame(clip=None,time=None):return next(f for f in m['frames'] if f['shape']=='default' and f['stage']=='shaped' and f['clip']==clip and (time is None or abs(f['time']-time)<.01))
P=read(frame('A-Pose')); W=[]
for v in range(m['vertexCount']):W.append({bones[m['joints'][v*4+k]]:m['weights'][v*4+k] for k in range(4) if m['weights'][v*4+k]>1e-7})
def norm(w):
 d={n:v for n,v in w if v>1e-7};t=sum(d.values());return {n:v/t for n,v in d.items()}
def l1(a,b):return sum(abs(a.get(n,0)-b.get(n,0)) for n in a.keys()|b.keys())
Q=[Vector((-x,z,y))for x,y,z in s['positions_blender']];kds={}
for slot,name in enumerate(s['patterns']):
 verts=sorted({v for i,f in enumerate(s['faces']) if s['slots'][i]==slot for v in f});kd=KDTree(len(verts))
 for v in verts:kd.insert(Q[v],v)
 kd.balance();kds[name]=kd
D=[];matches=[]
for p in m['prims']:
 name=p['name'].split('_top_')[-1] if '_top_' in p['name'] else p['name'].split('layered-shirt:top_')[-1]
 kd=kds[name]
 for v in set(p['indices']):
  _,u,d=kd.find(P[v]);D.append(d);matches.append((v,u));
changed=[l1(W[v],norm(s['filtered'][u])) for v,u in matches]
rawchanged=[l1(norm(s['raw'][u]),norm(s['filtered'][u])) for v,u in matches]
inner=sorted({v for p in m['prims'] if '_l0_' in p['name'] for v in p['indices']});outer=sorted({v for p in m['prims'] if '_l1_' in p['name'] for v in p['indices']})
kd=KDTree(len(inner))
for v in inner:kd.insert(P[v],v)
kd.balance();pairs=[]
for v in outer:
 _,u,d=kd.find(P[v])
 if d<=.012:pairs.append((v,u,d,l1(W[v],W[u])))
F=read(frame('Model Pose',5.279));delta=sorted((((F[v]-F[u])-(P[v]-P[u])).length*1000 for v,u,_,_ in pairs))
report={'source_mapping_nearest_distance_mm':{'p50':statistics.median(D)*1000,'max':max(D)*1000},'converter_raw8_vs_filtered4':{'verticesL1Over01':sum(d>.1 for d in rawchanged),'maxL1':max(rawchanged)},'filtered4_vs_imported':{'verticesL1Over01':sum(d>.1 for d in changed),'maxL1':max(changed)},'near_layer_vertex_pairs_12mm':{'count':len(pairs),'weightsL1Over02':sum(d>.2 for _,_,_,d in pairs),'meanWeightL1':statistics.mean(d for _,_,_,d in pairs),'maxWeightL1':max(d for _,_,_,d in pairs),'relativeVectorChangeAtModelPoseMm':{'median':statistics.median(delta),'p95':delta[int(.95*len(delta))],'max':max(delta)}}}
(r/'weight-comparison.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
