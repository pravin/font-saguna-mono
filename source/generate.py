"""Draw Saguna Mono: build UFO masters and let the foundry compile them.

Contract: `generate.py <out>` writes raw TTFs into <out>. foundry.ufo.build_family does that from
compatible masters (same glyphs and point structure in each): a weight-axis variable font plus every
static style in font.toml, instanced from it. The font's name comes from font.toml, never from here.

Every glyph is drawn as pen strokes (pen.py) in the 600-unit cell. The Regular master records how many
pieces each arc is cut into and the other masters replay it, so the outlines interpolate. The italic is
the same drawing with cursive lowercase forms (italic.py), sheared by ITALIC_ANGLE about the middle of
the x-height.
"""

import math
import sys
from pathlib import Path

from fontTools.agl import UV2AGL

from foundry.ufo import build_family, load_spec, new_master

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kit import BOT, CAP, TOP, W, XH, Kit            # noqa: E402
from pen import STYLE, Pen, Plan                     # noqa: E402
import compose                                        # noqa: E402
import glyphs                                         # noqa: E402

# wght axis: user value -> stem width. The Regular is light and open, like a book weight.
STEMS = {300: 60, 400: 86, 700: 134}
ITALIC_ANGLE = 10.0
METRICS = dict(ascender=TOP, descender=BOT, x_height=XH, cap_height=CAP)


def gname(key):
    if len(key) == 1:
        u = ord(key)
        return UV2AGL.get(u) or f'uni{u:04X}'
    return key


def shear(contours, k):
    if not k:
        return contours
    piv = XH / 2
    return [[(x + k * (y - piv), y, on) for x, y, on in c] for c in contours]


def put(font, name, contours, uni=None):
    g = font.newGlyph(name)
    g.width = W
    if uni is not None:
        g.unicodes = [uni]
    pen = g.getPointPen()
    for c in contours:
        if len(c) < 3:
            continue
        i0 = next((i for i, p in enumerate(c) if p[2]), None)
        pen.beginPath()
        if i0 is None:                      # all off-curve: a closed quadratic loop
            for x, y, _ in c:
                pen.addPoint((round(x), round(y)), None)
        else:
            pts = c[i0:] + c[:i0]
            prev_on = pts[-1][2]
            for x, y, on in pts:
                pen.addPoint((round(x), round(y)), ('line' if prev_on else 'qcurve') if on else None)
                prev_on = on
        pen.endPath()


def master(spec, weight, italic, mode):
    w = STEMS[weight]
    STYLE.skew = math.tan(math.radians(ITALIC_ANGLE)) if italic else 0.0
    K = Kit(w)
    P = Pen(w, rounded=True)
    Plan.start('glyphs' + ('-it' if italic else ''), mode)
    G = glyphs.make(K, italic)
    Plan.stop()
    # a spec with 'raw' carries finished outlines (box drawing, blocks: sharp, so cells join seamlessly)
    cont = {key: (sp['raw'] if 'raw' in sp else P.glyph(sp)) for key, sp in G.items()}
    cont.update(compose.accented(K, P, G, cont, italic, mode))
    f = new_master(spec, weight, **METRICS, italic_angle=ITALIC_ANGLE if italic else 0)
    put(f, '.notdef', notdef(w))
    f.glyphOrder = ['.notdef']
    for key in sorted(cont, key=lambda k: (len(k) != 1, ord(k) if len(k) == 1 else 0, k)):
        k = 0.0 if G.get(key, {}).get('upright') else STYLE.skew     # box drawing and blocks stay upright in the italic
        put(f, gname(key), shear(cont[key], k), ord(key) if len(key) == 1 else None)
    for alias, key in compose.ALIASES.items():
        if key in cont:
            put(f, gname(alias), shear(cont[key], STYLE.skew), ord(alias))
    f.features.text = compose.features(set(cont))
    STYLE.skew = 0.0
    return f


def notdef(w):
    k = w * 0.7
    o = [(90, 0, True), (90, CAP, True), (510, CAP, True), (510, 0, True)]
    i = [(90 + k, k, True), (510 - k, k, True), (510 - k, CAP - k, True), (90 + k, CAP - k, True)]
    return [o, i]


def main():
    spec = load_spec()
    out = Path(sys.argv[1])
    fam = spec.families[0]
    for italic in (False, True):
        ms = {400: master(spec, 400, italic, 'record')}
        for wt in (300, 700):
            ms[wt] = master(spec, wt, italic, 'replay')
        build_family(spec, fam, ms, out, italic=italic, clearance=None)


if __name__ == '__main__':
    main()
