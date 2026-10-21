// Diagnostic only: exports the same shaping/dressing/skinning stages used by the app.
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
const [root, key, output] = process.argv.slice(2);
const mod = (p) => import(pathToFileURL(path.join(root,p)));
const { createCatalogStore, catalogDirs } = await mod('fitting/catalog-store.mjs');
const { loadCatalog } = await mod('fitting/src/core/catalog.mjs');
const { checkOverrides, createResolver } = await mod('fitting/src/core/labels.mjs');
const { checkRules, resolveRules } = await mod('fitting/src/core/rules.mjs');
const { listLabelFiles, listRulesFiles, createFitCache } = await mod('fitting/server.mjs');
const { decodeCache } = await mod('fitting/src/core/coverage.mjs');
const { createShaper, defaultShape } = await mod('fitting/src/core/shape.mjs');
const { createDresser } = await mod('fitting/src/core/dress.mjs');
const { createPoser, skin } = await mod('fitting/src/core/pose.mjs');
const store = createCatalogStore({catalogDir:catalogDirs(root),importsDir:path.join(root,'fitting/imports'),editsDir:path.join(root,'fitting/catalog-edits')});
const catalog=loadCatalog((await store.read('female')).buffer), mesh=catalog.byKey.get(key);
const lf=await checkOverrides(catalog,await listLabelFiles(path.join(root,'fitting/labels'),'female'));
const rf=await checkRules(catalog,await listRulesFiles(path.join(root,'fitting/rules'),'female'));
const {resolve}=createResolver(catalog), keys=['body','face',key];
const labels=new Map(keys.map(k=>[k,resolve(k,lf.saved).labels]));
const rules=new Map([[key,resolveRules(catalog,key,rf.saved.get(key)??null)]]);
const cache=decodeCache(JSON.parse((await createFitCache({store,derivedDir:path.join(root,'fitting/derived')}).get('female')).text),catalog);
const shaper=createShaper(catalog), dresser=createDresser(catalog,cache), poser=createPoser(catalog);
await fs.mkdir(output,{recursive:true});
let serial=0; const frames=[];
async function save(shape,stage,clip,time,P) {
 const file=`positions-${serial++}.bin`; await fs.writeFile(path.join(output,file),new Uint8Array(P.buffer,P.byteOffset,P.byteLength));
 frames.push({shape,stage,clip,time,file});
}

const source=JSON.parse(await fs.readFile(path.join(output,'../source-weights.json'),'utf8'));
const Q=Float32Array.from(source.positions_blender.flatMap(([x,y,z])=>[-x,z,y]));
const boneIndex=new Map(catalog.skeleton.skinJoints.map((n,j)=>[catalog.json.nodes[n].name,j]));
const shaped=shaper.shape(defaultShape(catalog),[key]), AM=poser.pose(shaped,'A-Pose',0);
function blend(weights,M){ const A=new Float64Array(12); for(const [j,w] of weights){ const o=j*16; for(let c=0;c<4;c++) for(let r=0;r<3;r++) A[c*3+r]+=w*M[o+c*4+r]; } return A; }
function solve(A,b){const a=[...Array(3)].map((_,r)=>[A[r],A[3+r],A[6+r],b[r]]); for(let k=0;k<3;k++){let p=k;for(let r=k+1;r<3;r++)if(Math.abs(a[r][k])>Math.abs(a[p][k]))p=r;[a[k],a[p]]=[a[p],a[k]];const z=a[k][k];if(Math.abs(z)<1e-10)throw Error('singular');for(let c=k;c<4;c++)a[k][c]/=z;for(let r=0;r<3;r++)if(r!==k){const f=a[r][k];for(let c=k;c<4;c++)a[r][c]-=f*a[k][c];}}return a.map(r=>r[3]);}
function move(P,W,M){return Float32Array.from(W.flatMap((w,v)=>{const A=blend(w,M),i=v*3; return [0,1,2].map(r=>A[r]*P[i]+A[3+r]*P[i+1]+A[6+r]*P[i+2]+A[9+r]);}));}
for(const mode of ['raw8','raw4','filtered4']){
 const W=source[mode==='filtered4'?'filtered':'raw'].map(w=>{w=w.filter(([n])=>boneIndex.has(n)).sort((a,b)=>b[1]-a[1]);if(mode!=='raw8')w=w.slice(0,4);const total=w.reduce((s,[,v])=>s+v,0);if(!total)throw Error('unmapped');return w.map(([n,v])=>[boneIndex.get(n),v/total]);});
 const P=Float32Array.from(W.flatMap((w,v)=>{const A=blend(w,AM);return solve(A,[0,1,2].map(r=>Q[v*3+r]-A[9+r]));}));
 await save('source',mode,'A-Pose',0,move(P,W,AM)); await save('source',mode,'T-Pose',0,P);
 for(const c of poser.clips.filter(c=>!c.static))for(const fraction of [.125,.375,.625,.875]){const time=c.duration*fraction;await save('source',mode,c.name,time,move(P,W,poser.pose(shaped,c.name,time)));}
}
const prims=source.patterns.map((name,k)=>({name,material:{pbrMetallicRoughness:{baseColorFactor:name.startsWith('l0_')?[.55,.72,.88,1]:[.045,.045,.055,1]}},indices:source.faces.filter((_,i)=>source.slots[i]===k).flat()}));
await fs.writeFile(path.join(output,'manifest.json'),JSON.stringify({vertexCount:Q.length/3,prims,frames}));
console.log('source frames',frames.length);
