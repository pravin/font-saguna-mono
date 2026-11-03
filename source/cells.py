"""Saguna Mono: the code set. Arrows and check marks are pen strokes like the letters. Box drawing, block
elements and the filled shapes are finished outlines ('raw'): sharp-cornered, the same in every weight,
upright in the italic, and drawn edge to edge over the whole line (kit.BOT..kit.TOP), so they join
seamlessly from cell to cell and line to line."""

import math

from kit import BOT, MATH, TOP, W, se

CX, CY = W / 2, (TOP + BOT) / 2
LT, HV = 84, 168                 # light and heavy line thickness
GAP = 66                         # half the distance between the two lines of a double line


def rect(x0, y0, x1, y1):
    """A clockwise rectangle."""
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    return [(x0, y0, True), (x0, y1, True), (x1, y1, True), (x1, y0, True)]


def poly(pts):
    """A closed polygon made clockwise."""
    a = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
    if a > 0:
        pts = pts[::-1]
    return [(x, y, True) for x, y in pts]


def raw(cs):
    return dict(s=[], p=[], raw=cs, upright=True)


# ---------------------------------------------------------------- box drawing table: (L, R, U, D)
# 0 none, 1 light, 2 heavy, 3 double
BOX = {0x2500: (1, 1, 0, 0), 0x2501: (2, 2, 0, 0), 0x2502: (0, 0, 1, 1), 0x2503: (0, 0, 2, 2)}
_c = 0x250C
for r_, d_ in ((1, 1), (2, 1), (1, 2), (2, 2)):
    BOX[_c] = (0, r_, 0, d_); _c += 1
for l_, d_ in ((1, 1), (2, 1), (1, 2), (2, 2)):
    BOX[_c] = (l_, 0, 0, d_); _c += 1
for r_, u_ in ((1, 1), (2, 1), (1, 2), (2, 2)):
    BOX[_c] = (0, r_, u_, 0); _c += 1
for l_, u_ in ((1, 1), (2, 1), (1, 2), (2, 2)):
    BOX[_c] = (l_, 0, u_, 0); _c += 1
for u_, d_, r_ in ((1, 1, 1), (1, 1, 2), (2, 1, 1), (1, 2, 1), (2, 2, 1), (2, 1, 2), (1, 2, 2), (2, 2, 2)):
    BOX[_c] = (0, r_, u_, d_); _c += 1
for u_, d_, l_ in ((1, 1, 1), (1, 1, 2), (2, 1, 1), (1, 2, 1), (2, 2, 1), (2, 1, 2), (1, 2, 2), (2, 2, 2)):
    BOX[_c] = (l_, 0, u_, d_); _c += 1
for l_, r_, d_ in ((1, 1, 1), (2, 1, 1), (1, 2, 1), (2, 2, 1), (1, 1, 2), (2, 1, 2), (1, 2, 2), (2, 2, 2)):
    BOX[_c] = (l_, r_, 0, d_); _c += 1
for l_, r_, u_ in ((1, 1, 1), (2, 1, 1), (1, 2, 1), (2, 2, 1), (1, 1, 2), (2, 1, 2), (1, 2, 2), (2, 2, 2)):
    BOX[_c] = (l_, r_, u_, 0); _c += 1
for l_, r_, u_, d_ in ((1, 1, 1, 1), (2, 1, 1, 1), (1, 2, 1, 1), (2, 2, 1, 1), (1, 1, 2, 1), (1, 1, 1, 2), (1, 1, 2, 2),
                       (2, 1, 2, 1), (1, 2, 2, 1), (2, 1, 1, 2), (1, 2, 1, 2), (2, 2, 2, 1), (2, 2, 1, 2), (2, 1, 2, 2),
                       (1, 2, 2, 2), (2, 2, 2, 2)):
    BOX[_c] = (l_, r_, u_, d_); _c += 1
assert _c == 0x254C
# double lines 2550..256C
DOUBLE = {0x2550: (3, 3, 0, 0), 0x2551: (0, 0, 3, 3),
          0x2552: (0, 3, 0, 1), 0x2553: (0, 1, 0, 3), 0x2554: (0, 3, 0, 3),
          0x2555: (3, 0, 0, 1), 0x2556: (1, 0, 0, 3), 0x2557: (3, 0, 0, 3),
          0x2558: (0, 3, 1, 0), 0x2559: (0, 1, 3, 0), 0x255A: (0, 3, 3, 0),
          0x255B: (3, 0, 1, 0), 0x255C: (1, 0, 3, 0), 0x255D: (3, 0, 3, 0),
          0x255E: (0, 3, 1, 1), 0x255F: (0, 1, 3, 3), 0x2560: (0, 3, 3, 3),
          0x2561: (3, 0, 1, 1), 0x2562: (1, 0, 3, 3), 0x2563: (3, 0, 3, 3),
          0x2564: (3, 3, 0, 1), 0x2565: (1, 1, 0, 3), 0x2566: (3, 3, 0, 3),
          0x2567: (3, 3, 1, 0), 0x2568: (1, 1, 3, 0), 0x2569: (3, 3, 3, 0),
          0x256A: (3, 3, 1, 1), 0x256B: (1, 1, 3, 3), 0x256C: (3, 3, 3, 3)}
BOX.update(DOUBLE)
# half lines 2574..257F
BOX.update({0x2574: (1, 0, 0, 0), 0x2575: (0, 0, 1, 0), 0x2576: (0, 1, 0, 0), 0x2577: (0, 0, 0, 1),
            0x2578: (2, 0, 0, 0), 0x2579: (0, 0, 2, 0), 0x257A: (0, 2, 0, 0), 0x257B: (0, 0, 0, 2),
            0x257C: (1, 2, 0, 0), 0x257D: (0, 0, 1, 2), 0x257E: (2, 1, 0, 0), 0x257F: (0, 0, 2, 1)})
DASH = {0x2504: (0, 3, 1), 0x2505: (0, 3, 2), 0x2506: (1, 3, 1), 0x2507: (1, 3, 2), 0x2508: (0, 4, 1), 0x2509: (0, 4, 2),
        0x250A: (1, 4, 1), 0x250B: (1, 4, 2), 0x254C: (0, 2, 1), 0x254D: (0, 2, 2), 0x254E: (1, 2, 1), 0x254F: (1, 2, 2)}


def box(arms):
    L_, R_, U_, D_ = arms
    th = {1: LT, 2: HV, 3: LT}
    cs = []
    vmax = max(th.get(U_, 0) if U_ != 3 else 0, th.get(D_, 0) if D_ != 3 else 0)
    hmax = max(th.get(L_, 0) if L_ != 3 else 0, th.get(R_, 0) if R_ != 3 else 0)
    vdbl, hdbl = 3 in (U_, D_), 3 in (L_, R_)
    # horizontal arms
    for side, s in (('L', L_), ('R', R_)):
        if not s:
            continue
        edge = 0 if side == 'L' else W
        sg = -1 if side == 'L' else 1
        if s == 3:
            for yy, partner in ((CY + GAP, U_), (CY - GAP, D_)):
                other = D_ if partner is U_ else U_
                if partner == 3:
                    x0 = CX + sg * GAP
                elif other == 3:
                    x0 = CX - sg * GAP
                elif U_ or D_:
                    x0 = CX - sg * vmax / 2
                else:
                    x0 = CX - sg * LT / 2
                cs.append(rect(x0 - sg * LT / 2 * (partner == 3 or other == 3), yy - LT / 2, edge, yy + LT / 2))
        else:
            t = th[s]
            if vdbl:
                both = (L_ in (1, 2)) and (R_ in (1, 2))
                x0 = CX - sg * (GAP + LT / 2) if both else CX + sg * (GAP - LT / 2)
            else:
                x0 = CX - sg * (vmax / 2 if vmax else t / 2)
            cs.append(rect(x0, CY - t / 2, edge, CY + t / 2))
    # vertical arms
    for side, s in (('U', U_), ('D', D_)):
        if not s:
            continue
        edge = TOP if side == 'U' else BOT
        sg = 1 if side == 'U' else -1
        if s == 3:
            for xx, partner in ((CX + GAP, R_), (CX - GAP, L_)):
                other = L_ if partner is R_ else R_
                if partner == 3:
                    y0 = CY + sg * GAP
                elif other == 3:
                    y0 = CY - sg * GAP
                elif L_ or R_:
                    y0 = CY - sg * hmax / 2
                else:
                    y0 = CY - sg * LT / 2
                cs.append(rect(xx - LT / 2, y0 - sg * LT / 2 * (partner == 3 or other == 3), xx + LT / 2, edge))
        else:
            t = th[s]
            if hdbl:
                both = (U_ in (1, 2)) and (D_ in (1, 2))
                y0 = CY - sg * (GAP + LT / 2) if both else CY + sg * (GAP - LT / 2)
            else:
                y0 = CY - sg * (hmax / 2 if hmax else t / 2)
            cs.append(rect(CX - t / 2, y0, CX + t / 2, edge))
    return cs


def dashes(vertical, n, heavy):
    t = HV if heavy else LT
    span = (TOP - BOT) if vertical else W
    step = span / n
    seg = step * 0.62
    cs = []
    for i in range(n):
        p0 = (BOT if vertical else 0) + i * step + (step - seg) / 2
        if vertical:
            cs.append(rect(CX - t / 2, p0, CX + t / 2, p0 + seg))
        else:
            cs.append(rect(p0, CY - t / 2, p0 + seg, CY + t / 2))
    return cs


def corner(q):
    """╭ ╮ ╯ ╰: a light line turning through a quarter circle of radius W/2 about a cell corner point."""
    r = W / 2
    hx = {0: 1, 1: -1, 2: -1, 3: 1}[q]          # which way the horizontal arm runs (to the right edge or the left)
    vy = {0: -1, 1: -1, 2: 1, 3: 1}[q]          # which way the vertical arm runs (down or up)
    ccx, ccy = CX + hx * r, CY + vy * r          # the arc's centre
    pts_o, pts_i = [], []
    n = 12
    for i in range(n + 1):
        t = i / n * math.pi / 2
        ux, uy = -hx * math.cos(t), -vy * math.sin(t)
        pts_o.append((ccx + ux * (r + LT / 2), ccy + uy * (r + LT / 2)))
        pts_i.append((ccx + ux * (r - LT / 2), ccy + uy * (r - LT / 2)))
    # the arc runs from (CX, ccy) to (ccx, CY) = the side edge; the vertical arm runs on to the top or bottom
    ey = TOP if vy == 1 else BOT
    return [poly(pts_o + pts_i[::-1]), rect(CX - LT / 2, ccy, CX + LT / 2, ey)]


def diag(kind):
    t = LT * 1.05
    cs = []
    for (x0, y0, x1, y1) in ({'/': [(0, BOT, W, TOP)], '\\': [(0, TOP, W, BOT)], 'x': [(0, BOT, W, TOP), (0, TOP, W, BOT)]}[kind]):
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        nx, ny = -dy / L * t / 2, dx / L * t / 2
        ext = 40
        ux, uy = dx / L * ext, dy / L * ext
        cs.append(poly([(x0 - ux + nx, y0 - uy + ny), (x1 + ux + nx, y1 + uy + ny), (x1 + ux - nx, y1 + uy - ny), (x0 - ux - nx, y0 - uy - ny)]))
    return cs


def blocks():
    H8 = (TOP - BOT) / 8
    B = {}
    B[0x2580] = [rect(0, CY, W, TOP)]
    for i in range(1, 9):                        # ▁ .. █: lower eighths
        B[0x2580 + i] = [rect(0, BOT, W, BOT + i * H8)]
    for i in range(1, 8):                        # ▉ .. ▏: left seven-eighths .. one-eighth
        B[0x2588 + i] = [rect(0, BOT, W * (8 - i) / 8, TOP)]
    B[0x2590] = [rect(CX, BOT, W, TOP)]
    sq = 100                                     # shades: a grid of 100-unit squares tiles the 600 x 1200 cell
    nx, ny = int(W / sq), int((TOP - BOT) / sq)
    for cp, keep in ((0x2591, lambda i, j: i % 2 == 0 and j % 2 == 0), (0x2592, lambda i, j: (i + j) % 2 == 0),
                     (0x2593, lambda i, j: not (i % 2 == 0 and j % 2 == 0))):
        B[cp] = [rect(i * sq, BOT + j * sq, (i + 1) * sq, BOT + (j + 1) * sq) for i in range(nx) for j in range(ny) if keep(i, j)]
    B[0x2594] = [rect(0, TOP - H8, W, TOP)]
    B[0x2595] = [rect(W * 7 / 8, BOT, W, TOP)]
    qd = {'ll': rect(0, BOT, CX, CY), 'lr': rect(CX, BOT, W, CY), 'ul': rect(0, CY, CX, TOP), 'ur': rect(CX, CY, W, TOP)}
    for cp, qs in ((0x2596, 'll'), (0x2597, 'lr'), (0x2598, 'ul'), (0x2599, 'ul ll lr'), (0x259A, 'ul lr'), (0x259B, 'ul ur ll'),
                   (0x259C, 'ul ur lr'), (0x259D, 'ur'), (0x259E, 'ur ll'), (0x259F, 'ur ll lr')):
        B[cp] = [qd[q] for q in qs.split()]
    return B


def extend(G, K, env):
    o, D, hl, vl, ring, dot = K.o, K.D, K.hl, K.vl, K.ring, K.dot
    a = K.a
    # arrows: a shaft and an open head, on the maths axis
    hd = 170

    def arrow(ang, x0, y0, x1, y1):
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        px, py = -uy, ux
        tip = (x1, y1)
        h1 = (x1 - ux * hd + px * hd, y1 - uy * hd + py * hd)
        h2 = (x1 - ux * hd - px * hd, y1 - uy * hd - py * hd)
        return [o([(x0, y0), (x1 - ux * a * 0.8, y1 - uy * a * 0.8)]), o([h1, tip, h2])]
    G['→'] = dict(s=arrow(0, 70, MATH, 530, MATH), p=[])
    G['←'] = dict(s=arrow(0, 530, MATH, 70, MATH), p=[])
    G['↑'] = dict(s=arrow(0, W / 2, MATH - 300, W / 2, MATH + 300), p=[])
    G['↓'] = dict(s=arrow(0, W / 2, MATH + 300, W / 2, MATH - 300), p=[])
    G['↔'] = dict(s=[o([(70 + a, MATH), (530 - a, MATH)]), o([(70 + hd, MATH + hd), (70, MATH), (70 + hd, MATH - hd)]),
                     o([(530 - hd, MATH + hd), (530, MATH), (530 - hd, MATH - hd)])], p=[])
    G['↕'] = dict(s=[o([(W / 2, MATH - 300 + a), (W / 2, MATH + 300 - a)]),
                     o([(W / 2 - hd, MATH + 300 - hd), (W / 2, MATH + 300), (W / 2 + hd, MATH + 300 - hd)]),
                     o([(W / 2 - hd, MATH - 300 + hd), (W / 2, MATH - 300), (W / 2 + hd, MATH - 300 + hd)])], p=[])
    g2 = 92
    G['⇒'] = dict(s=[hl(MATH + g2, 60, 420), hl(MATH - g2, 60, 420), o([(330, MATH + 220), (540, MATH), (330, MATH - 220)])], p=[])
    G['⇐'] = dict(s=[hl(MATH + g2, 180, 540), hl(MATH - g2, 180, 540), o([(270, MATH + 220), (60, MATH), (270, MATH - 220)])], p=[])
    # box drawing, dashes, rounded corners, diagonals and blocks
    for cp, arms in BOX.items():
        G[chr(cp)] = raw(box(arms))
    for cp, (v, n, h) in DASH.items():
        G[chr(cp)] = raw(dashes(bool(v), n, h == 2))
    for cp, q in ((0x256D, 0), (0x256E, 1), (0x256F, 2), (0x2570, 3)):
        G[chr(cp)] = raw(corner(q))
    G['╱'], G['╲'], G['╳'] = raw(diag('/')), raw(diag('\\')), raw(diag('x'))
    for cp, cs in blocks().items():
        G[chr(cp)] = raw(cs)
    # geometric shapes: filled ones are outlines; open ones are pen strokes
    s_, m_ = 230, 130
    G['■'] = raw([rect(CX - s_, MATH - s_, CX + s_, MATH + s_)])
    G['▪'] = raw([rect(CX - m_, MATH - m_, CX + m_, MATH + m_)])
    ks = min(1.0, 62 / K.w)                       # open shapes keep their counters in Bold
    aq = a * ks
    G['□'] = dict(s=[K.closed([(CX - s_ + aq, MATH - s_ + aq), (CX - s_ + aq, MATH + s_ - aq), (CX + s_ - aq, MATH + s_ - aq), (CX + s_ - aq, MATH - s_ + aq)], k=ks)], p=[])
    G['▫'] = dict(s=[K.closed([(CX - m_ + aq, MATH - m_ + aq), (CX - m_ + aq, MATH + m_ - aq), (CX + m_ - aq, MATH + m_ - aq), (CX + m_ - aq, MATH - m_ + aq)], k=ks)], p=[])
    tr = 250
    G['▲'] = raw([poly([(CX - tr, MATH - tr * 0.85), (CX, MATH + tr), (CX + tr, MATH - tr * 0.85)])])
    G['▼'] = raw([poly([(CX - tr, MATH + tr * 0.85), (CX + tr, MATH + tr * 0.85), (CX, MATH - tr)])])
    G['►'] = raw([poly([(CX - tr * 0.85, MATH + tr), (CX + tr, MATH), (CX - tr * 0.85, MATH - tr)])])
    G['◄'] = raw([poly([(CX + tr * 0.85, MATH + tr), (CX + tr * 0.85, MATH - tr), (CX - tr, MATH)])])
    G['◆'] = raw([poly([(CX, MATH + 260), (CX + 220, MATH), (CX, MATH - 260), (CX - 220, MATH)])])
    G['◇'] = dict(s=[K.closed([(CX, MATH + 260 - a * 1.3), (CX + 220 - a * 1.3, MATH), (CX, MATH - 260 + a * 1.3), (CX - 220 + a * 1.3, MATH)])], p=[])
    rc = 240
    G['○'] = dict(s=[ring(CX, MATH, rc - a, rc - a)], p=[])
    n = 32
    G['●'] = raw([poly([(CX + rc * math.cos(2 * math.pi * i / n), MATH + rc * math.sin(2 * math.pi * i / n)) for i in range(n)])])
    G['✓'] = dict(s=[o([(90, MATH + 10), (240, MATH - 180), (520, 700)])], p=[])
    G['✗'] = dict(s=[D((120, MATH - 240), (480, MATH + 260)), D((120, MATH + 260), (480, MATH - 240))], p=[])
