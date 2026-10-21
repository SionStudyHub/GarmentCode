"""Stretch-knit torso panels: GarmentCode's simple shirt panels (tee.py) with a side seam shaped to the body.

GarmentCode's Shirt panel is a trapezoid: its side seam runs straight from the hem up to the armhole. Cut tight,
that line crosses the bust about 24% smaller than the body (the hem is narrow and the bust sits low on the line),
so on the sion body the tank slid down under the breasts (FINDINGS.md). These panels put the side seam through
three body levels instead, each with its own fit (split between front and back as at the bust):

    waist      design['knit']['waist']       x body waist
    underbust  design['knit']['underbust']   x body underbust, at underbust_level of the way from waist to bust
    bust       design['knit']['bust']        x body bust; straight up from there to the shoulder

and the front panel's centre hem drops by front_room x (front-over-bust length - back length), curving up to the side
seam: room for the bust in the middle of the front, with the side seams still matching. No darts.

With design['knit']['side_curve'] > 0 the seam is instead one smooth S-curve from the waist width to the bust width,
leaving the waist and reaching the bust going straight up (cubic, control points side_curve and (1 + side_curve) / 2 of
the way up; the underbust level is not used). The sion body's girth rises late and levels off at the bust, and the
polyline's sharp turn at the bust poked out as a small point at the side, ~4 cm under the armpit, once sewn: the side
of the body hardly widens there, the girth grows in front (FINDINGS.md).

With design['knit']['armhole_scoop'] and sleeve.armhole_shape: ArmholeKnit, the armhole is cut deeper in its lower
half, scoop x its width past the strap line: the sion body has a deep hollow at the front of the armpit, and
GarmentCode's ArmholeCurve edge stretched straight across it, ~2 cm off the skin (FINDINGS.md).

With design['knit']['armhole_drop'] the armhole bottom sits that many cm lower. Even with matched seams, the side
seam from waist to armhole is ~1 cm longer than the body is tall there (its 2D slant shapes the girth, which grows in
front, not at the side). Pinned at the waist by the tight fit and at the armpit by the armhole, that extra bowed out
as a small point at the side of the bust (FINDINGS.md).

With design['knit']['side_match'] the front's side seam is cut as long as the back's, up to the bust: its side hem
point is lifted (the front hem curving down to the middle), so the front's extra length over the bust sits in the
middle rather than in the seam. The same split at every level makes the front seam slant more than the back's, ~0.8 cm
longer on the sion body; sewn to the shorter back seam, that extra bunched into a small point at the side of the bust
(FINDINGS.md). A sewn pattern walks its seams to the same length; a woven one puts the difference in a bust dart.

Used when a design has a 'knit' section (warp/prepare_job.py calls install(design)).
"""
import functools

import numpy as np
import pygarment as pyg

from assets.garment_programs import bodice, sleeves, tee
from assets.garment_programs.base_classes import BaseBodicePanel


def _profile(body, design, back):
    """Side seam points (x, y) from the hem (y = 0) up to the bust, x negative (towards the side)."""
    k = design['knit']
    h_bust = body['waist_line'] - body['vert_bust_line']          # bust line above the waist
    levels = [  # (height above the waist, full girth)
        (0.0, k['waist']['v'] * body['waist']),
        (k['underbust_level']['v'] * h_bust, k['underbust']['v'] * body['underbust']),
        (h_bust, k['bust']['v'] * body['bust']),
    ]
    # Same front/back split at every level (the bust's, as tee.py): the front and back side seams then bend in
    # proportion, so GarmentCode can sew them edge to edge. A split that follows the body at each level makes the
    # front seam's bend much bigger than the back's, and GarmentCode cuts the seams into sub-centimetre pieces
    # that BoxMesh can't mesh (StitchingError).
    share = body['back_width'] / body['bust'] / 2
    share = share if back else 0.5 - share
    xy = np.array([[-share * girth, h] for h, girth in levels])
    hem = body['waist_line'] * (1 - design['shirt']['length']['v'])  # hem height above the waist (< 0: below it)
    above = xy[xy[:, 1] > hem]
    hem_x = np.interp(hem, xy[:, 1], xy[:, 0])                   # below the waist: the waist width, straight down
    return [[hem_x, 0.0]] + [[x, y - hem] for x, y in above]


def hem_up(body, design):
    """The waist's height above the hem (0 if the hem is at or above the waist)"""
    return max(0.0, -body['waist_line'] * (1 - design['shirt']['length']['v']))


def _side(body, design, back, length, lift=0.0):
    """Side seam from the hem (its first point lifted by lift) up to the bust: points, and its edges"""
    side = [p for p in _profile(body, design, back) if p[1] < length - 1]
    a = design['knit'].get('side_curve', {}).get('v', 0)
    if a > 0:  # waist (or hem, if above it) -> bust in one S-curve: drop the underbust point
        side = [p for p in side if p[1] <= hem_up(body, design) + 1e-6] + side[-1:]
    side[0] = [side[0][0], side[0][1] + lift]
    edges = pyg.EdgeSeqFactory.from_verts(*side)
    if a > 0:
        e = edges[-1]
        (x0, y0), (x1, y1) = e.start, e.end
        cps = [[x0, y0 + a * (y1 - y0)], [x1, y0 + (1 + a) / 2 * (y1 - y0)]]
        edges.substitute(e, pyg.CurveEdge(e.start, e.end, cps, relative=False))
    return side, edges


def _front_lift(body, design, length):
    """How far to lift the front's side hem point so its side seam is as long as the back's, up to the bust"""
    back_len = _side(body, design, True, design['shirt']['length']['v'] * body['waist_line'])[1].length()
    lo, hi = 0.0, 5.0
    if _side(body, design, False, length)[1].length() <= back_len:
        return 0.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _side(body, design, False, length, mid)[1].length() > back_len else (lo, mid)
    return lo


def _build(panel, body, design, length, shoulder_incl, top_x, drop, back):
    lift = 0.0
    if not back and design['knit'].get('side_match', {}).get('v', False):
        lift = _front_lift(body, design, length)
    side, side_edges = _side(body, design, back, length, lift)
    top = [top_x, length]
    verts = [[0, -drop]] + side + [top] + [[0, length + shoulder_incl]]
    panel.edges = pyg.EdgeSeqFactory.from_verts(*verts, loop=True)
    for i, e in enumerate(side_edges):
        if isinstance(e, pyg.CurveEdge):
            panel.edges.substitute(panel.edges[1 + i], e)
    if drop > 0 or lift > 0:  # front hem: low across the middle, curving up to the side seam
        e = panel.edges[0]
        curve = pyg.CurveEdge(e.start, e.end, [[0.55 * e.end[0], -drop]], relative=False)
        panel.edges.substitute(e, curve)
    n = len(panel.edges)
    outside = pyg.EdgeSequence(*[panel.edges[i] for i in range(1, n - 2)])
    bottom_ref = body['waist_back_width'] / 2 if back else (body['waist'] - body['waist_back_width']) / 2
    panel.interfaces = {
        'outside': pyg.Interface(panel, outside),
        'inside': pyg.Interface(panel, panel.edges[-1]),
        'shoulder': pyg.Interface(panel, panel.edges[-2]),
        'bottom': pyg.Interface(panel, panel.edges[0], ruffle=panel.edges[0].length() / bottom_ref),
        'shoulder_corner': pyg.Interface(panel, [panel.edges[-3], panel.edges[-2]]),
        'collar_corner': pyg.Interface(panel, [panel.edges[-2], panel.edges[-1]]),
    }
    panel.translate_by([0, body['height'] - body['head_l'] - length - shoulder_incl, 0])


class KnitFrontHalf(BaseBodicePanel):
    def __init__(self, name, body, design) -> None:
        super().__init__(name, body, design)
        k = design['knit']
        frac = (body['bust'] - body['back_width']) / 2 / body['bust']
        self.width = frac * k['bust']['v'] * body['bust']
        sh_tan = np.tan(np.deg2rad(body['_shoulder_incl']))
        length = design['shirt']['length']['v'] * body['waist_line']
        length -= sh_tan * (frac - (0.5 - frac)) * body['bust']   # as tee.py: front is shorter by the shoulder slope
        drop = k['front_room']['v'] * (body['waist_over_bust_line'] - body['waist_line'])
        _build(self, body, design, length, sh_tan * self.width, -self.width, drop, back=False)

    def get_width(self, level):
        return super().get_width(level) + self.width - self.body['shoulder_w'] / 2


class KnitBackHalf(BaseBodicePanel):
    def __init__(self, name, body, design) -> None:
        super().__init__(name, body, design)
        k = design['knit']
        frac = body['back_width'] / 2 / body['bust']
        self.width = frac * k['bust']['v'] * body['bust']
        sh_tan = np.tan(np.deg2rad(body['_shoulder_incl']))
        length = design['shirt']['length']['v'] * body['waist_line']
        _build(self, body, design, length, sh_tan * self.width, -self.width, 0.0, back=True)

    def get_width(self, level):
        return super().get_width(level) + self.width - self.body['shoulder_w'] / 2


def armhole_knit(incl, width, angle, invert=True, scoop=0.0, **kwargs):
    """Sleeveless armhole for sleeves.Sleeve, in its frame: from the side seam (0, 0), level at first, to the strap
    (incl, width), bowing scoop x incl past the strap line on the way (0: no further in than the strap)"""
    assert not invert, 'ArmholeKnit is for sleeveless designs'
    edge = pyg.CurveEdge([0, 0], [incl, width], [[0.9 * incl, 0], [(1 + scoop) * incl, 0.35 * width]], relative=False)
    return pyg.EdgeSequence(edge), None


def install(design):
    """Make GarmentCode's Shirt (meta.upper: Shirt) use these panels, offer sleeve.armhole_shape: ArmholeKnit, and
    lower the armhole by design['knit']['armhole_drop'] cm"""
    tee.TorsoFrontHalfPanel = KnitFrontHalf
    tee.TorsoBackHalfPanel = KnitBackHalf
    sleeves.ArmholeKnit = functools.partial(armhole_knit, scoop=design['knit'].get('armhole_scoop', {}).get('v', 0.0))
    drop = design['knit'].get('armhole_drop', {}).get('v', 0.0)
    if drop and not getattr(bodice.BodiceHalf, '_knit_drop', False):
        base = bodice.BodiceHalf.eval_dep_params

        def eval_dep_params(self, body, design):
            # GarmentCode caps the armhole depth at the last side edge's length - 1 cm, here bust -> armhole: it can't
            # go below that. The cut still lands on that edge as long as the drop stays under its slack above the bust.
            base(self, body, design)
            design['sleeve']['connecting_width']['v'] += design['knit']['armhole_drop']['v']

        bodice.BodiceHalf.eval_dep_params = eval_dep_params
        bodice.BodiceHalf._knit_drop = True
