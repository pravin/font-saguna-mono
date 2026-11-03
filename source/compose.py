"""Saguna Mono: the marks, the accented letters built from them, aliases and OpenType features.

Marks are lighter than letters (stroke 24 + 0.42 x stem: lighter still in Bold, where short arms turned to blobs) and have round ends like every stroke. They are
drawn about x = 0 with their foot on y = 0 (marks above) or their top near y = 0 (marks below), then
placed over the middle of the base letter's top (or foot) and composed into one outline, so the italic
shear tilts letter and mark together. Capitals take flatter `.case` marks. Letters whose mark must sit
over a stem rather than the ink's middle (i j l t) say where in their spec: G[ch]['stem'].
"""

import unicodedata

from fontTools.agl import UV2AGL

from foundry.charsets import GF, LATIN
from kit import ASC, CAP, W, XH, se
from pen import Plan, band, bounds

ALIASES = {' ': ' ', '­': '-', 'Ω': 'Ω'}
ABOVE = {0x300: 'grave', 0x301: 'acute', 0x302: 'circumflex', 0x303: 'tilde', 0x304: 'macron', 0x306: 'breve',
         0x307: 'dot', 0x308: 'dieresis', 0x30A: 'ring', 0x30B: 'hungarumlaut', 0x30C: 'caron'}
BELOW = {0x327: 'cedilla', 0x328: 'ogonek', 0x326: 'commabelow'}
LATVIAN = set('ĢĶĻŅŖķļņŗ')          # their cedilla is drawn as a comma below (ģ: a turned comma above)
CARON_ALT = set('ďľťĽ')              # a caron beside a tall stem is a small apostrophe-like stroke
ASCENDERS = set('bdfhklĸ')
SPACING = {'´': 'acute', '¨': 'dieresis', '¯': 'macron', '¸': 'cedilla', 'ˆ': 'circumflex', 'ˇ': 'caron',
           '˘': 'breve', '˙': 'dot', '˚': 'ring', '˛': 'ogonek', '˜': 'tilde', '˝': 'hungarumlaut'}
GAP_LC, GAP_UC = 62, 54              # mark foot above the x-height / ascender, and above the cap height


def marks(K, case=False):
    a, b, w = K.a, K.b, K.w
    km = min(1.0, (24 + 0.42 * w) / w)              # the mark pen
    am, bm = a * km, b * km
    o, D, ring, dot = K.o, K.D, K.ring, K.dot
    h = 132 if case else 158                         # height of acute, grave, circumflex, caron
    M = {}

    def sp(strokes=(), fills=()):
        return dict(s=list(strokes), p=list(fills))
    M['acute'] = sp([D((-52, am), (58, h - am), k=km)])
    M['grave'] = sp([D((52, am), (-58, h - am), k=km)])
    aw = 136 if not case else 144
    M['circumflex'] = sp([D((-aw + am, am), (0, h - am), k=km), D((aw - am, am), (0, h - am), k=km)])
    M['caron'] = sp([D((-aw + am, h - am), (0, am), k=km), D((aw - am, h - am), (0, am), k=km)])
    dep = (92 if case else 108) - bm
    M['breve'] = sp([o(se(0, dep + bm, 116 - am, dep, 196, 344), k=km)])     # ends short of level: they left a step in Bold Italic
    amp = 34 if case else 40
    M['tilde'] = sp([o(K.wave(-128, 128, amp + bm, amp), k=km)])
    M['macron'] = sp([K.hl(bm + 12, -128, 128, k=km)])
    rd = K.dm
    M['dieresis'] = sp([], [dot(-108, rd, rd), dot(108, rd, rd)])
    M['dot'] = sp([], [dot(0, rd * 1.05, rd * 1.05)])
    rr = 82 if case else 88                          # big enough, on a lighter pen, that its counter stays open in Bold
    M['ring'] = sp([ring(0, rr, rr - am * 0.78, rr - bm * 0.78, k=km * 0.78)])
    M['hungarumlaut'] = sp([D((-122, am), (-28, h - am), k=km), D((28, am), (122, h - am), k=km)])
    # below: the cedilla hooks out of the letter's foot; the ogonek curls from its right foot
    kc = min(1.0, km * 1.08)
    M['cedilla'] = sp([o([(0, 50), (0, -82)] + K.circle(0, -82 - 64, 64, 90, -150), k=kc)])      # clear of the foot; a true circle, wider than the pen
    # the ogonek runs down out of the foot, round the bottom on the left and off to the right, thinning
    M['ogonek'] = sp([o([(0, 60)] + se(58, -40, 70, 78, 168, 330, K.fin(None, 1, 0.8)), k=kc)])
    M['commabelow'] = sp([], [K.comma(0, -rd * 1.05 - 62, rd * 1.05, tail=58)])
    M['commaturned'] = sp([], [K.comma(0, rd * 1.05 + 52, rd * 1.05, turned=True, tail=58)])
    M['caronalt'] = sp([], [K.comma(0, -rd * 1.05, rd * 1.05, tail=62)])
    return M


def decompose(ch):
    d = unicodedata.decomposition(ch)
    if not d or d.startswith('<'):
        return None
    parts = [chr(int(x, 16)) for x in d.split()]
    base, mks = parts[0], parts[1:]
    while True:
        dd = unicodedata.decomposition(base)
        if not dd or dd.startswith('<'):
            break
        p = [chr(int(x, 16)) for x in dd.split()]
        base, mks = p[0], p[1:] + mks
    return base, [ord(m) for m in mks]


def accented(K, P, G, cont, italic, mode):
    Plan.start('marks' + ('-it' if italic else ''), mode)
    Ms = {False: {k: P.glyph(v) for k, v in marks(K).items()}, True: {k: P.glyph(v) for k, v in marks(K, True).items()}}
    Plan.stop()
    out = {}

    def shifted(cs, dx, dy):
        return [[(x + dx, y + dy, on) for x, y, on in c] for c in cs]

    def centre(key, bc, y0, y1):
        st = G.get(key, {}).get('stem')
        if st is not None:
            return st
        x0, x1 = band(bc, y0, y1)
        return (x0 + x1) / 2

    for u in sorted(LATIN | GF):
        ch = chr(u)
        if ch in cont or ch in out:
            continue
        r = decompose(ch)
        if not r:
            continue
        base, mks = r
        upper = base.isupper()
        bkey = {'i': 'ı', 'j': 'ȷ'}.get(base, base) if any(m in ABOVE for m in mks) else base
        if bkey not in cont:
            continue
        bc = cont[bkey]
        cs = [list(c) for c in bc]
        top = CAP if upper else (ASC if base in ASCENDERS else XH)
        y = top + (GAP_UC if upper else GAP_LC)
        for m in mks:
            if m in ABOVE:
                if ch in CARON_ALT:
                    x0, x1 = band(bc, top - 160, top + 5)
                    if base == 't':
                        cs += shifted(Ms[False]['caronalt'], x1 + 30, 600)
                    else:
                        cs += shifted(Ms[False]['caronalt'], x1 + K.dm * 1.05 + 28, top + 10)    # clear of the stem
                    continue
                mc = Ms[upper][ABOVE[m]]
                cs += shifted(mc, centre(bkey, bc, top - 120, top + 20), y)
                mb = bounds(mc)
                y += (mb[3] - mb[1]) + 26                # a second mark stacks above the first
            elif m in BELOW:
                name = BELOW[m]
                if ch in LATVIAN:
                    if ch == 'ģ':
                        cs += shifted(Ms[False]['commaturned'], centre(bkey, bc, XH - 120, XH + 20), XH + GAP_LC - 30)
                        continue
                    name = 'commabelow'
                x0, x1 = band(bc, 0, 90)
                st = G.get(bkey, {}).get('stem')
                if name == 'ogonek':
                    cx = x1 - K.a - 12 if st is None else st + 30
                elif st is not None:
                    cx = st
                else:
                    cx = (x0 + x1) / 2
                cs += shifted(Ms[False][name], cx, 0)
        out[ch] = cs

    for ch, name in SPACING.items():                 # spacing marks, centred in the cell
        mc = Ms[False][name]
        out[ch] = shifted(mc, W / 2, 0 if name in ('cedilla', 'ogonek') else XH + GAP_LC)
    # combining marks: zero width, drawn back over the previous cell, so a mark ccmp cannot compose still lands on
    # its letter (generate.py gives them no advance)
    for m, name in {**ABOVE, **BELOW}.items():
        out[chr(m)] = shifted(Ms[False][name], -W / 2, 0 if m in BELOW else XH + GAP_LC)
    return out


def combining(ch):
    return 0x300 <= ord(ch) <= 0x36F if len(ch) == 1 else False


def _gn(ch):
    return UV2AGL.get(ord(ch)) or f'uni{ord(ch):04X}'


def features(names):
    """ccmp: a letter followed by combining marks becomes the precomposed letter, which has the marks placed for
    it (decomposed text, as in NFD, then looks like composed text). GDEF marks the combining marks."""
    rules = []
    for ch in sorted(n for n in names if len(n) == 1):
        d = unicodedata.decomposition(ch)
        if not d or d.startswith('<'):
            continue
        parts = [chr(int(x, 16)) for x in d.split()]
        if len(parts) < 2 or not all(p in names for p in parts) or not all(combining(p) for p in parts[1:]):
            continue
        rules.append(f'    sub {" ".join(_gn(p) for p in parts)} by {_gn(ch)};')
        r = decompose(ch)                           # the fully decomposed spelling too (ǻ = a + ring + acute)
        if r and len(r[1]) > len(parts) - 1 and r[0] in names and all(chr(m) in names for m in r[1]):
            rules.append(f'    sub {_gn(r[0])} {" ".join(_gn(chr(m)) for m in r[1])} by {_gn(ch)};')
    marks = ' '.join(_gn(n) for n in sorted(names) if combining(n))
    if not rules:
        return ''
    return ('feature ccmp {\n    lookup compose {\n' + '\n'.join('    ' + r for r in dict.fromkeys(rules)) +
            '\n    } compose;\n} ccmp;\n\n'
            f'@CombiningMarks = [{marks}];\ntable GDEF {{\n    GlyphClassDef , , @CombiningMarks, ;\n}} GDEF;\n')
