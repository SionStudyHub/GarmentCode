"""One picture of the fabric library: each preset draped on the round stand, with its numbers.

    ./.venv/bin/python sion_pipeline/fabric_sheet.py

Reads fabrics.json and the drape pictures from fabric_tests.py (out/fabrics/<preset>_drape.png).
Writes sion_pipeline/out/fabrics/fabric_library.png.
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / 'out' / 'fabrics'


def main():
    lib = json.loads((HERE / 'fabrics.json').read_text())['presets']
    names = sorted(lib, key=lambda n: lib[n]['physical']['drape_coefficient'])  # floppiest first
    cols, W, TXT = 4, 360, 96
    rows = -(-len(names) // cols)
    sheet = Image.new('RGB', (cols * W, rows * (W + TXT)), 'white')
    d = ImageDraw.Draw(sheet)
    big, small = ImageFont.load_default(size=20), ImageFont.load_default(size=16)
    for i, n in enumerate(names):
        p = lib[n]
        x, y = (i % cols) * W, (i // cols) * (W + TXT)
        png = OUT / f'{n}_drape.png'
        if png.exists():
            sheet.paste(Image.open(png).convert('RGB').resize((W, W)), (x, y))
        phys, m = p['physical'], p.get('measured', {})
        d.text((x + 10, y + W + 6), p['label'], fill='black', font=big)
        d.text((x + 10, y + W + 32), f"{phys['weight_gsm']} g/m2   stretch {phys['stretch_pct']:g}%   name: {n}",
               fill='#444', font=small)
        dc = m.get('drape_coefficient')
        line = f"drape: real {phys['drape_coefficient']:.2f}, Blender " + ('-' if dc is None else f'{dc:.2f}')
        if p.get('note'):
            line += '  (out of reach)'
        d.text((x + 10, y + W + 54), line, fill='#a00' if p.get('note') else '#444', font=small)
        if not p.get('calibrated'):
            d.text((x + 10, y + W + 74), 'not calibrated', fill='#a00', font=small)
    sheet.save(OUT / 'fabric_library.png')
    print('wrote', OUT / 'fabric_library.png')


if __name__ == '__main__':
    main()
