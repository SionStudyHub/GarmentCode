"""Diagnose why shirt weights look bad. Run in your OPEN .blend with shirt selected.
Paste the full console output back here.
"""
import bpy
from mathutils import Vector

ignore = {"Body", "Face"}
a = bpy.context.active_object
cands = []
if a and a.type == 'MESH' and a.name not in ignore and "Collider" not in a.name:
    cands = [a]
else:
    cands = [o for o in bpy.context.selected_objects if o.type == 'MESH' and o.name not in ignore and "Collider" not in o.name]
    if not cands:
        cands = [o for o in bpy.data.objects if o.type == 'MESH' and o.name not in ignore and "Collider" not in o.name and len(o.data.vertices) > 500][:5]

body = bpy.data.objects.get("Body")
print("=== SHIRT WEIGHT DIAGNOSIS ===")
print(f"Body present: {body is not None}, verts: {len(body.data.vertices) if body else 0}")
for g in cands:
    print(f"\n--- Object: '{g.name}' ---")
    print(f"  verts: {len(g.data.vertices)}, polys: {len(g.data.polygons)}, groups: {len(g.vertex_groups)}")
    print(f"  parent: {g.parent.name if g.parent else None}, location: {list(g.location)}, scale: {list(g.scale)}")
    print(f"  shape_keys: {g.data.shape_keys is not None}, materials: {len(g.data.materials)}")
    for m in g.modifiers:
        tgt = getattr(m, 'object', None)
        print(f"  mod: {m.type} '{m.name}' -> {tgt.name if tgt else ''} show_vp={getattr(m,'show_viewport', '?')}")
    # weight stats
    if g.vertex_groups:
        totals = {}
        for v in g.data.vertices:
            for grp in v.groups:
                totals[grp.group] = totals.get(grp.group, 0.0) + grp.weight
        idx2name = {vg.index: vg.name for vg in g.vertex_groups}
        ranked = sorted(totals.items(), key=lambda x: -x[1])[:15]
        print(f"  TOP BONES by total weight:")
        for idx, tot in ranked:
            print(f"    {idx2name.get(idx, '?')} : total={tot:.1f} avg={tot/len(g.data.vertices):.3f}")
        # rigid vs blended
        rigid = blended = single = 0
        maxinf = 0
        for v in g.data.vertices:
            n = sum(1 for grp in v.groups if grp.weight > 0.01)
            n001 = sum(1 for grp in v.groups if grp.weight > 0.001)
            maxinf = max(maxinf, n001)
            top = max([grp.weight for grp in v.groups], default=0)
            if top > 0.99:
                rigid += 1
            if n >= 2:
                blended += 1
            if n001 == 0:
                single += 1
        print(f"  rigid(>0.99): {rigid} ({100*rigid/len(g.data.vertices):.1f}%), blended(2+ bones): {blended} ({100*blended/len(g.data.vertices):.1f}%), ZERO-weight verts: {single}, maxInf: {maxinf}")
        # active group check (why weight paint looks empty)
        try:
            print(f"  active group idx: {g.vertex_groups.active_index}, name: {g.vertex_groups.active.name if len(g.vertex_groups) else 'none'}")
        except Exception as e:
            print(f"  active group err: {e}")
    # distance to Body (explains wrong transfer if shirt floats far)
    if body:
        import math
        bverts = [body.matrix_world @ v.co for v in body.data.vertices]
        # sample 200 garment verts for speed, brute force vs every 10th body vert
        samp = list(g.data.vertices)[::max(1, len(g.data.vertices)//200)]
        bsub = bverts[::10]
        dists = []
        for v in samp:
            co = g.matrix_world @ v.co
            d = min((co - b).length for b in bsub)
            dists.append(d)
        dists.sort()
        print(f"  DIST to Body (sampled, approx): min={dists[0]*1000:.1f}mm median={dists[len(dists)//2]*1000:.1f}mm max={dists[-1]*1000:.1f}mm")
        print(f"  (if median > 20mm the shirt floats far — nearest-point transfer WILL pick wrong bones at armpits)")
print("\n=== HOW TO SEE WEIGHT PAINT ===")
print("1. Select ONLY the shirt, go Weight Paint mode.")
print("2. In Properties > Object Data > Vertex Groups, click different groups (e.g. J_Bip_L_UpperArm) — red = fully driven by that bone.")
print("3. If all blue: no weights on that group (pruned or transfer missed).")
print("=== END ===")
