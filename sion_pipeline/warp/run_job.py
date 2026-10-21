"""Run one packed job (prepare_job.py) through GarmentCode's Warp simulator. Runs on Colab, from the GarmentCode root:

    cd /content/GarmentCode && MPLBACKEND=Agg PYTHONPATH=. /content/venv/bin/python <job>/run_job.py <job> [--tag t]

Writes <job>/out/: <name>_sim.obj (cm, GarmentCode frame), front/back renders, sim_props.yaml with the run stats,
and result.npz (garment vertices in cm, triangles) for warp_to_glb.py.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import trimesh

from pygarment.meshgen.boxmeshgen import BoxMesh
from pygarment.meshgen.simulation import run_sim
import pygarment.data_config as data_config
from pygarment.meshgen.sim_config import PathCofig

ap = argparse.ArgumentParser()
ap.add_argument('job')
ap.add_argument('--tag', default='')
a = ap.parse_args()

job = Path(a.job).resolve()
meta = json.loads((job / 'job.json').read_text())
name = meta['name']
body_name = 'sion_body'

# Body files where GarmentCode looks for them (system.json bodies_default_path), segmentation next to the job
bodies = Path(data_config.Properties('./system.json')['bodies_default_path'])
z = np.load(job / 'body.npz')
V, F, L = z['pos'].astype(np.float64) / 10000, z['tri'].astype(np.int64), z['labels']
trimesh.Trimesh(V, F, process=False).export(bodies / f'{body_name}.obj')
shutil.copy(job / 'body_measurements.yaml', bodies / f'{body_name}.yaml')
seg = {p: np.flatnonzero(L == k).tolist() for k, p in enumerate(meta['parts'])}
(job / 'body_segmentation.json').write_text(json.dumps(seg))

props = data_config.Properties(str(job / 'sim_props.yaml'))
props.set_section_stats('sim', fails={}, sim_time={}, spf={}, fin_frame={}, body_collisions={}, self_collisions={})
props.set_section_stats('render', render_time={})

out = job / ('out' + (f'_{a.tag}' if a.tag else ''))
shutil.rmtree(out, ignore_errors=True)
paths = PathCofig(in_element_path=job, out_path=out, in_name=name, body_name=body_name,
                  smpl_body=False, add_timestamp=False)
paths.body_seg = job / 'body_segmentation.json'

box = BoxMesh(paths.in_g_spec, props['sim']['config']['resolution_scale'])
box.load()
box.serialize(paths, store_panels=False, uv_config=props['render']['config']['uv_texture'])
props.serialize(paths.element_sim_props)
run_sim(box.name, props, paths, save_v_norms=False, store_usd=False, optimize_storage=False, verbose=False)
props.serialize(paths.element_sim_props)

sim = trimesh.load(paths.g_sim, process=False, force='mesh')
np.savez_compressed(out / 'result.npz', verts=np.asarray(sim.vertices, np.float32), faces=np.asarray(sim.faces, np.int32))
print('RESULT', out, len(sim.vertices), 'verts', len(sim.faces), 'faces')
