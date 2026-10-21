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
await save('catalog','stored',null,0,mesh.positions);
const shapes={default:defaultShape(catalog),chest06:{...defaultShape(catalog),'chest-size':.6}};
for(const [shape,values] of Object.entries(shapes)) {
 const shaped=shaper.shape(values,[key]), P=shaped.items.get(key).positions;
 const d=dresser.dress({shown:keys,shaped,labels,rules}).get(key);
 await save(shape,'shaped',null,0,P); await save(shape,'dressed',null,0,d.positions);
 for(const c of poser.clips) {
  const times=c.static?[0]:[.125,.375,.625,.875].map(f=>f*c.duration);
  for(const time of times) {
   const M=poser.pose(shaped,c.name,time);
   for(const [stage,R] of [['shaped',P],['dressed',d.positions]]) await save(shape,stage,c.name,time,skin(R,null,mesh.joints,mesh.weights,M).positions);
  }
 }
}
const prims=catalog.json.meshes[mesh.meshIndex].primitives.map((p,i)=>({name:catalog.json.materials[p.material]?.name,material:catalog.json.materials[p.material],indices:Array.from(mesh.indices[i])}));
await fs.writeFile(path.join(output,'manifest.json'),JSON.stringify({key,vertexCount:mesh.vertexCount,extras:catalog.json.meshes[mesh.meshIndex].extras,clips:poser.clips,prims,frames,joints:Array.from(mesh.joints),weights:Array.from(mesh.weights),bones:catalog.skeleton.skinJoints.map(n=>catalog.json.nodes[n].name)}));
console.log(JSON.stringify({vertexCount:mesh.vertexCount,frames:frames.length,prims:prims.map(({name,material,indices})=>({name,color:material.pbrMetallicRoughness.baseColorFactor,triangles:indices.length/3})),clips:poser.clips,extras:catalog.json.meshes[mesh.meshIndex].extras},null,2));
