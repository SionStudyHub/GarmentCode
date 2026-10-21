"""Make one garment from its recipe: pattern -> drape -> pictures and numbers next to the accepted version.

    ./.venv/bin/python sion_pipeline/run.py garments/tee.yaml            make it and compare (changes nothing else)
    ./.venv/bin/python sion_pipeline/run.py garments/tee.yaml --accept   make it the accepted version and import it
                                                                         into the fitting app, then check it there

A recipe (sion_pipeline/garments/<name>.yaml) holds everything that decides the garment: the GarmentCode design,
the body, the pattern options, the fabric preset (fabrics.json) and how the fitting app imports it. Same recipe,
same garment: the cloth simulation is deterministic.

Writes sion_pipeline/out/<name>/: the pattern and drape outputs (make_pattern.py, drape_blender.py), drape_log.txt,
metrics.json, and compare.png (accepted version on top, new one below, with the numbers).
--accept copies the GLB, pictures, numbers, recipe and fabric settings to sion_pipeline/accepted/<name>/ (the
version it replaces moves to accepted/<name>/history/<time>/), runs the fitting app's import (fitting:import,
fitting:prepare) and its checks (fitting:check at the default, smallest and largest shapes, and --motion), and
saves their output in accepted/<name>/fitting_check.txt.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PY = ROOT / '.venv/bin/python'
BLENDER = '/Applications/Blender.app/Contents/MacOS/Blender'
SION = ROOT.parent / 'sion-avatar'
VIEWS = ('front', 'side', 'back')


def sh(cmd, log=None, cwd=ROOT, may_fail=False):
    """Run a command; stop with its last lines if it fails (unless may_fail: then note it). Returns its output."""
    print('$', ' '.join(str(c) for c in cmd), flush=True)
    r = subprocess.run([str(c) for c in cmd], cwd=cwd, capture_output=True, text=True)
    out = r.stdout + r.stderr
    if log:
        Path(log).write_text(out)
    if r.returncode and may_fail:
        return f'$ {" ".join(str(c) for c in cmd)}\n(exit code {r.returncode}: FAILED)\n' + out
    if r.returncode:
        sys.exit(f'failed ({r.returncode}):\n' + '\n'.join(out.splitlines()[-25:]))
    return out


def metrics(log):
    """The numbers drape_blender.py prints, from its log."""
    m = {}
    for stage in ('sew', 'settle'):
        rows = re.findall(rf'{stage} frame\s+(\d+)\s+seam gap mean\s+([\d.]+) mm\s+max\s+([\d.]+) mm', log)
        if rows:
            m[f'{stage}_frames'], m[f'{stage}_gap_mean_mm'], m[f'{stage}_gap_max_mm'] = int(rows[-1][0]), float(rows[-1][1]), float(rows[-1][2])
    if r := re.search(r'stretch vs pattern: median ([-\d.]+)%\s+95th ([-\d.]+)%\s+max ([-\d.]+)%', log):
        m['stretch_median_pct'], m['stretch_95th_pct'], m['stretch_max_pct'] = map(float, r.groups())
    if r := re.search(r'fit: hem ([-\d.]+) cm above floor \(pattern ([-\d.]+)\); cloth to skin median ([-\d.]+) cm, '
                      r'90th ([-\d.]+) cm; (\d+) points inside the body', log):
        m['hem_cm'], m['hem_pattern_cm'], m['skin_gap_median_cm'], m['skin_gap_90th_cm'] = map(float, r.groups()[:4])
        m['points_inside_body'] = int(r.group(5))
    if r := re.search(r'welded: (\d+) vertices, (\d+) triangles', log):
        m['vertices'], m['triangles'] = map(int, r.groups())
    if r := re.search(r'^fabric: (\S+)', log, re.M):
        m['fabric'] = r.group(1)
    return m


ROWS = [('fabric', 'fabric', '{}'), ('hem_cm', 'hem above floor', '{:.1f} cm'),
        ('skin_gap_median_cm', 'cloth to skin, median', '{:.1f} cm'), ('skin_gap_90th_cm', 'cloth to skin, 90%', '{:.1f} cm'),
        ('stretch_median_pct', 'stretch vs pattern, median', '{:.1f}%'), ('stretch_95th_pct', 'stretch, 95%', '{:.1f}%'),
        ('settle_gap_max_mm', 'widest seam gap', '{:.1f} mm'), ('points_inside_body', 'points inside body', '{}')]


def compare_sheet(name, new_dir, new_stem, new_m, acc_dir, acc_m, out):
    W, H, PAD = 350, 450, 36
    font = ImageFont.load_default(size=22)
    small = ImageFont.load_default(size=18)
    rows = [('accepted', acc_dir, acc_m)] if acc_dir else []
    rows.append(('new', new_dir, new_m))
    table_w = 430
    sheet = Image.new('RGB', (W * 3 + table_w, (H + PAD) * len(rows)), 'white')
    d = ImageDraw.Draw(sheet)
    for r, (label, folder, m) in enumerate(rows):
        y = r * (H + PAD)
        stem = new_stem if label == 'new' else (json.loads((folder / 'accepted.json').read_text())['stem'])
        d.text((10, y + 6), f'{label}: {name}' + (f" ({m.get('fabric', 'old settings')})"), fill='black', font=font)
        for c, v in enumerate(VIEWS):
            png = folder / f'{stem}_{v}.png'
            if png.exists():
                sheet.paste(Image.open(png).convert('RGB').resize((W, H)), (c * W, y + PAD))
        for k, (key, title, fmt) in enumerate(ROWS):
            val = m.get(key)
            d.text((W * 3 + 14, y + PAD + 10 + k * 30), f'{title}: ' + ('-' if val is None else fmt.format(val)),
                   fill='black', font=small)
    sheet.save(out)


def fitting_import(glb, imp, log_lines):
    """fitting:import + prepare + checks in sion-avatar; returns the check output."""
    listing = json.loads(sh(['npm', 'run', '--silent', 'fitting:import', '--', glb, '--list', '--json'], cwd=SION))
    ids = [str(p['id']) for p in listing['parts']]
    if len(ids) != 1:
        sys.exit(f'expected one garment part in {glb}, found {ids}')
    cmd = ['npm', 'run', '--silent', 'fitting:import', '--', glb, '--part', ids[0], '--as', imp['as']]
    for k in ('slot', 'gender', 'name', 'outfit', 'weights', 'pose'):
        if k in imp:
            cmd += [f'--{k}', imp[k]]
    log_lines.append(sh(cmd, cwd=SION))
    log_lines.append(sh(['npm', 'run', '--silent', 'fitting:prepare'], cwd=SION))
    outfit = imp.get('check_outfit', imp['as'].split(':')[0])
    for gender in (['female', 'male'] if imp.get('gender') == 'both' else [imp.get('gender', 'female')]):
        for extra in (['--shape', 'default'], ['--shape', 'smallest'], ['--shape', 'largest'], ['--motion']):
            log_lines.append(sh(['npm', 'run', '--silent', 'fitting:check', '--', gender, '--outfit', outfit, *extra],
                                cwd=SION, may_fail=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('recipe')
    ap.add_argument('--accept', action='store_true', help='make this the accepted version and import it into the fitting app')
    ap.add_argument('--skip-make', action='store_true', help='reuse the last pattern and drape (e.g. to --accept it)')
    a = ap.parse_args()
    path = Path(a.recipe)
    if not path.is_absolute() and not path.exists():
        path = HERE / a.recipe
    rec = yaml.safe_load(path.read_text())
    name = rec['name']
    out = HERE / 'out' / name
    pat = rec.get('pattern', {})
    drape = rec.get('drape', {})
    t0 = time.time()
    if not a.skip_make:
        cmd = [PY, HERE / 'make_pattern.py', name, '--design', HERE / rec['design'], '--res', pat.get('res', 1.0)]
        if 'body' in rec:
            cmd += ['--body', HERE / rec['body']]
        for k in ('arm_angle', 'front_extra'):
            if k in pat:
                cmd += [f"--{k.replace('_', '-')}", pat[k]]
        sh(cmd)
        cmd = [BLENDER, '--background', '--factory-startup', '--python', HERE / 'drape_blender.py', '--', name,
               '--fabric', rec['fabric']]
        for k, v in drape.items():
            cmd += [f"--{k.replace('_', '-')}"] + ([] if v is True else [v])
        log = sh(cmd, log=out / 'drape_log.txt')
    log = (out / 'drape_log.txt').read_text()
    m = metrics(log)
    m['seconds'] = round(time.time() - t0)
    (out / 'metrics.json').write_text(json.dumps(m, indent=2) + '\n')
    acc = HERE / 'accepted' / name
    acc_m = json.loads((acc / 'metrics.json').read_text()) if (acc / 'metrics.json').exists() else {}
    compare_sheet(name, out, name, m, acc if acc.exists() else None, acc_m, out / 'compare.png')
    print('\n'.join(f'  {t:28s} {"-" if m.get(k) is None else f.format(m[k]):>12s}   accepted: '
                    f'{"-" if acc_m.get(k) is None else f.format(acc_m[k])}' for k, t, f in ROWS))
    print('compare:', out / 'compare.png')
    if not a.accept:
        return
    if acc.exists():
        hist = acc / 'history' / time.strftime('%Y%m%d-%H%M%S')
        hist.mkdir(parents=True)
        for f in acc.iterdir():
            if f.name != 'history':
                shutil.move(str(f), hist / f.name)
    acc.mkdir(parents=True, exist_ok=True)
    for f in [out / f'{name}.glb', out / 'metrics.json', out / 'drape_log.txt', out / f'{name}_pattern.png'] + \
             [out / f'{name}_{v}.png' for v in VIEWS]:
        if f.exists():
            shutil.copy2(f, acc / f.name)
    shutil.copy2(path, acc / 'recipe.yaml')
    fab = json.loads((HERE / 'fabrics.json').read_text())['presets'][rec['fabric']]
    (acc / 'accepted.json').write_text(json.dumps({'stem': name, 'when': time.strftime('%Y-%m-%d %H:%M'),
                                                   'fabric': {rec['fabric']: fab}}, indent=2) + '\n')
    if 'fitting' in rec:
        lines = []
        fitting_import(acc / f'{name}.glb', rec['fitting'], lines)
        (acc / 'fitting_check.txt').write_text('\n'.join(lines))
        print('fitting app: imported and checked, see', acc / 'fitting_check.txt')
    print('accepted:', acc)


if __name__ == '__main__':
    main()
