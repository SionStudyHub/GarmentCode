// Export a sion-avatar body exactly as the fitting app's importer sees it (default slider shape), for draping.
//   node sion_pipeline/export_sion_body.mjs [female|male] [sion-avatar dir] [--pose a]
// Writes sion_pipeline/kit/<gender>_default_body.json: body+face mesh (metres, Y up, facing -Z, avatar's left at -X),
// per-vertex weights on humanoid J_Bip_* bones, and the humanoid joint positions with their parents.
// --pose a: the body and joints standing in the importer's A-pose fit pose (the catalog's A-Pose clip), written to
// kit/<gender>_apose_body.json; garments draped on it are imported with --pose a.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2), at = argv.indexOf('--pose');
const pose = at >= 0 ? argv.splice(at, 2)[1] : 't';
const gender = argv[0] || 'female';
const sion = path.resolve(argv[1] || path.join(here, '../../sion-avatar'));
const core = (m) => import(pathToFileURL(path.join(sion, 'fitting/src/core', m)).href);
const { loadCatalog } = await core('catalog.mjs');
const { importTarget } = await core('import-vrm.mjs');

// The VRoid avatars are the ones the fitting app uses; the older r26 avatars only when those aren't built.
const vrm = ['generated/vroid/catalogs', 'generated/r26/catalogs'].map((d) => path.join(sion, d, `${gender}-catalog.vrm`)).find((f) => fs.existsSync(f));
if (!vrm) throw new Error(`No ${gender}-catalog.vrm in ${sion}/generated; run npm run fitting:vroid -- all there`);
const buf = fs.readFileSync(vrm);
const catalog = loadCatalog(buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength));
const target = importTarget(catalog, { pose });
const json = catalog.json, nodes = json.nodes;

const parent = new Int32Array(nodes.length).fill(-1);
nodes.forEach((n, i) => (n.children || []).forEach((c) => (parent[c] = i)));
const humanBones = json.extensions.VRM.humanoid.humanBones.filter((h) => h.node >= 0);
const boneOfNode = new Map(humanBones.map((h) => [h.node, h.bone]));
const humanAncestor = (n) => { for (let k = n; k >= 0; k = parent[k]) if (boneOfNode.has(k)) return k; return -1; };

// Skin joint index -> name of the nearest humanoid node at or above it (spring/adjust bones fold into it).
const jointName = catalog.skeleton.skinJoints.map((n) => { const h = humanAncestor(n); return h >= 0 ? nodes[h].name : null; });

const s = target.skin, nv = s.positions.length / 3;
const groups = [];
for (let v = 0; v < nv; v++) {
  const w = new Map();
  for (let c = 0; c < 4; c++) {
    const name = jointName[s.joints[v * 4 + c]], x = s.weights[v * 4 + c];
    if (name && x > 0) w.set(name, (w.get(name) || 0) + x);
  }
  groups.push([...w].map(([n, x]) => [n, +x.toFixed(4)]));
}

const joints = humanBones.map((h) => {
  const up = humanAncestor(parent[h.node]);
  return { name: nodes[h.node].name, bone: h.bone, parent: up >= 0 ? nodes[up].name : null, pos: target.jointPos(h.bone).map((x) => +x.toFixed(5)) };
});

const round = (a, d = 5) => Array.from(a, (x) => +x.toFixed(d));
const out = {
  gender, pose, source: `sion-avatar ${path.relative(sion, vrm)}, default slider shape${pose === 't' ? '' : `, ${pose}-pose fit pose`}`,
  frame: 'metres, Y up, avatar faces -Z, avatar left is -X',
  floor: json.extras.muse.fit.floor || 0, scale: target.scale, bodyVertexCount: target.bodyVertexCount,
  positions: round(s.positions), triangles: Array.from(s.triangles), groups, joints,
};
fs.mkdirSync(path.join(here, 'kit'), { recursive: true });
const file = path.join(here, 'kit', `${gender}_${pose === 't' ? 'default' : pose + 'pose'}_body.json`);
fs.writeFileSync(file, JSON.stringify(out));
let mn = [1e9, 1e9, 1e9], mx = [-1e9, -1e9, -1e9];
for (let v = 0; v < target.bodyVertexCount; v++) for (let k = 0; k < 3; k++) { mn[k] = Math.min(mn[k], s.positions[v * 3 + k]); mx[k] = Math.max(mx[k], s.positions[v * 3 + k]); }
console.log(`${file}: ${nv} verts (${target.bodyVertexCount} body), ${s.triangles.length / 3} tris, ${joints.length} joints, floor ${out.floor}, scale ${target.scale}`);
console.log('body bbox min', mn.map((x) => x.toFixed(3)), 'max', mx.map((x) => x.toFixed(3)));
