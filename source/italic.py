"""Saguna Mono italic: cursive lowercase, drawn upright and sheared with the rest by generate.py.

The hand: stems start with an entry stroke and end in an exit flick to the right; the l is a loop (ℓ); f loops
below the baseline and crosses back at it; s rises from the left to a point and swings into its belly; e's stroke
rises across the bowl and runs round to an exit; z is ʒ; q's tail and k's leg flick out; r's arm curls over and
down; a is single storey; x is two bowls back to back (ɔc). b h k keep plain ascenders and g j y open tails: the
ascender and descender are too short for loops, which collided with bowls or read as knots. c o t and the
diagonals v w keep their upright shapes: in code, u v and w must never be confused, so v and w stay pointed.
"""

import math

from kit import ASC, DSC, W, XH, se


def cursive(G, K, env):
    e = type('E', (), env)
    a, b, osl = K.a, K.b, K.os
    o, vl, hl, D, J = K.o, K.vl, K.hl, K.D, K.J
    fin, tp, dot = K.fin, K.taper, K.dot
    S = e.S
    xl, xr, L, R = e.xl, e.xr, e.L, e.R
    yt, yb, ra, XT, AT = e.yt, e.yb, e.ra, e.XT, e.AT
    rf = 66                                         # exit flick radius
    yd = e.yd

    def flick(x, r=rf):
        """The stem's foot turns right and lifts: an exit stroke."""
        return [(x, yb + r)] + se(x + r, yb + r, r, r, 180, 305, fin(None, 1, 0.84))

    def entry(x, top=XH):
        """A short entry stroke into the top of a stem: a little hook that turns over and runs down into it, so
        there is no corner (a mitred corner poked above the zone and left needles in Bold Italic)."""
        r = max(56.0, 1.25 * a)                     # a true circle, clearly wider than half the stroke at every weight
        return K.circle(x - r, top - b - r, r, 140, 0)      # 140: the hook stays inside its cell

    def loop(x, top=ASC):
        """An ascender loop to the right of the stem at x: the stem rises into it, it turns over and comes
        back down across the stem, ending to the left. Two strokes, joined flat, so the join never shows."""
        rL, rLy = 46 + 1.0 * a, 140 + 0.5 * a            # the loop grows with the pen, so its counter stays open in Bold
        cy = top + osl - b - rLy
        return cy, o(se(x + rL, cy, rL, rLy, 180, -80, fin(None, 1, 0.86)) + [(x - 124, cy - rLy - 80, 0.84)],
                     caps=(J(('y', cy)), 'f'))

    def stem_to(x, cy):
        return o([(x, 0), (x, cy)], caps=('f', J(('y', cy))))

    def dloop(x, top=XH, reach=72, rise=92):
        """A looped descender, the ℓ loop turned over: the stem runs down into a loop to its left, which turns
        over and comes back up across the stem at the baseline, ending in an exit stroke to the right. Two strokes,
        joined flat. Returns the stem (from top) and the loop."""
        rD, rDy = 100 + 0.4 * a, 92 + 0.3 * a            # wide and shallow (the descender is short), growing with the pen
        cy = DSC - osl + b + rDy
        stem = o([(x, top), (x, cy)], caps=('f', J(('y', cy))))
        lp = o(se(x - rD, cy, rD, rDy, 0, -248, fin(None, 1, 0.86)) + [(x + reach, cy + rDy + rise, 0.84)],
               caps=(J(('y', cy)), 'f'))
        return stem, lp

    def arch(x0, x1, end):
        rx = (x1 - x0) / 2
        return o(se(x0 + rx, yt - ra, rx, ra, 180, 0, tp(0, None)) + end)

    # n m h u: entry strokes and exit flicks
    S('n', [o(entry(xl) + [(xl, 0)]), arch(xl, xr, flick(xr))])
    km, m0, m2, ram = e.km, e.m0, e.m2 - 34, e.ram     # the right stem comes in, so the exit flick stays clear of the next letter
    m1 = (m0 + m2) / 2
    ytm = XH + osl - b * km
    S('m', [o([(m0, XH), (m0, 0)], k=km),            # no entry: m fills its cell, and the stroke reached the letter before
            o(se((m0 + m1) / 2, ytm - ram, (m1 - m0) / 2, ram, 180, 0, tp(0, None)) + [(m1, 0)], k=km),
            o(se((m1 + m2) / 2, ytm - ram, (m2 - m1) / 2, ram, 180, 0, tp(0, None)) + flick(m2, 60), k=km)])
    S('h', [o(entry(xl, ASC) + [(xl, 0)]), arch(xl, xr, flick(xr))])
    rxu = (xr - xl) / 2
    S('u', [o(entry(xl) + se(xl + rxu, yb + ra, rxu, ra, 180, 360, tp(None, 1))), o([(xr, XH)] + flick(xr))])
    # i j l: an entry stroke and an exit flick; the l is a loop
    xi = W / 2 - 4                                  # the hook and the flick balance about the cell's centre
    ri = 112                                         # i's own hook and flick are larger, so it fills its cell (ti looked gappy)
    S('i', [o(K.circle(xi - ri, XH - b - ri, ri, 140, 0) + flick(xi, ri))], [dot(xi, yd)])
    S('ı', [o(K.circle(xi - ri, XH - b - ri, ri, 140, 0) + flick(xi, ri))])
    xj = e.xj
    rj, yh = e.rj, e.yh
    jt = se(xj - rj, yh + rj * 0.92, rj, rj * 0.92, 0, -158, fin(None, 1, 0.84))
    S('j', [o(entry(xj) + [(xj, yh + rj * 0.92)] + jt)], [dot(xj, yd)])     # g j y keep open tails: loops in a short descender read as knots
    S('ȷ', [o(entry(xj) + [(xj, yh + rj * 0.92)] + jt)])
    xL = W / 2 - 64
    cyL, lpL = loop(xL)
    S('l', [o([(xL, cyL)] + flick(xL), caps=(J(('y', cyL)), 'f')), lpL])
    for ch, x in (('i', xi), ('ı', xi), ('j', xj), ('ȷ', xj), ('l', xL)):
        G[ch]['stem'] = x
    # a d q: a bowl on the right stem; a and d end in a flick
    bowl_r, bowl_l = e.bowl_r, e.bowl_l
    S('a', [bowl_r, o([(xr, XH)] + flick(xr))])
    S('d', [bowl_r, o([(xr, ASC)] + flick(xr))])
    rq = max(62.0, 1.15 * a)                          # q's tail turns out to the right: a true circle, wider than half the pen
    cyq = DSC - osl + b + rq
    S('q', [bowl_r, o([(xr, XH), (xr, cyq)] + K.circle(xr + rq, cyq, rq, 180, 300))])
    # b p: an entry stroke, then the bowl
    S('b', [o(entry(xl, ASC) + [(xl, 0)]), bowl_l])
    S('p', [o(entry(xl) + [(xl, DSC)]), bowl_l])
    # k: an entry stroke into the ascender, the upright k's straight arm, and a leg that runs out into a flick
    # (a round arm leaving the stem at the x-height read as a closed h)
    ka_, pa = e.arm, e.pa
    rk = max(rf, 1.15 * a)                           # the flick: a true circle on the baseline, wider than half the pen
    cxk, cyk = R - 60 + rf * 0.2, yb + rk
    t0k = math.radians(230)
    for _ in range(6):                               # it starts where its tangent runs along the leg, so the join is smooth
        dx, dy = cxk + rk * math.cos(t0k) - pa[0], cyk + rk * math.sin(t0k) - pa[1]     # (a kink there left a pinhole)
        t0k = math.atan2(-dx, dy) % (2 * math.pi)
    S('k', [o(entry(xl, ASC) + [(xl, 0)]), ka_,
            o([pa] + K.circle(cxk, cyk, rk, math.degrees(t0k), 305), caps=(K.along(ka_), 'f'))])
    # r: an entry stroke and a soft arm
    xs_r = e.xs_r + 46                               # right of the upright r's stem: the entry hook needs room in the cell
    rxr_i, ryr_i = (528 - a - xs_r) / 2, 0.30 * XH
    S('r', [o(entry(xs_r) + [(xs_r, 0)]),
            o(se(xs_r + rxr_i, yt - ryr_i, rxr_i, ryr_i, 180, 28, fin(None, 1, 0.84)))])     # the arm curls over and down, as a pen would
    # f: descends below the baseline and curls left; a crossbar at the x-height
    xf, rff = 300, 0.28 * (R - L)
    st_f, lp_f = dloop(xf, AT - rff)
    S('f', [o([st_f.items[-1]] + [(xf, AT - rff)] + se(xf + rff, AT - rff, rff, rff, 180, 90) + [(520, AT, 0.9)],
              caps=(st_f.caps[1], 'f')), lp_f, hl(XT, 130, 470)])
    # e: the handwritten e: a stroke rises from the left side up across the bowl to the right, turns over the top and
    # runs round into an exit at the lower right; the eye is the space above the rising stroke
    cxe, cye, rxe, rye = K.bowl(e.OL, e.OR, -osl, XH + osl)
    ae0 = 24
    S('e', [o([(cxe - rxe + 0.15 * a, cye - 0.32 * rye)] + se(cxe, cye, rxe, rye, ae0, K.term(rxe, rye, 3), fin(None, 1)),
              caps=('FJ', 'f'))])
    # s: the handwritten s: a stroke rises from the left to a point at the top, then swings down into a belly on
    # the right and round to a tail at the lower left
    cxs_, cys_ = W / 2 + 8, 0.31 * XH                # the belly sits low, so the rising stroke is long and reads as s
    rxs_, rys_ = 186 - 0.8 * a, cys_ + osl - b
    ts_ = (W / 2 + 34, XH + osl - b)
    s0_ = (L + 4 + 0.4 * a, 0.30 * XH)                 # open at the lower left: the belly ends short of the stroke's start
    ks_ = min(1.0, 110 / K.w)                        # a pen that stops growing: in Bold the pointed top and the counter filled in
    S('s', [o([s0_, ts_], k=ks_, caps=('f', J(('y', ts_[1])))),
            o([ts_] + se(cxs_, cys_, rxs_, rys_, 66, -126, fin(None, 1)), k=ks_, caps=(J(('y', ts_[1])), 'f'))])
    # x: two bowls back to back, ɔ and c
    ry = (XH + osl - b - yb) / 2
    cyx = (XH + osl - b + yb) / 2
    S('x', [o(se(W / 2 - 160, cyx, 160 - 6, ry, 104, -104, fin(0, 1))), o(se(W / 2 + 160, cyx, 160 - 6, ry, 76, 284, fin(0, 1)))])
    # y: a u whose right stem runs on below the baseline into a tail
    S('y', [o(entry(xl) + se(xl + rxu, yb + ra, rxu, ra, 180, 360, tp(None, 1))),
            o([(xr, XH), (xr, yh + rj * 0.92)] + se(xr - rj * 1.2, yh + rj * 0.92, rj * 1.2, rj * 0.92, 0, -158, fin(None, 1, 0.84)))])
    # z: ʒ, the handwritten z: a top bar, a diagonal down to a sharp turn, and a bowl that swings below the baseline
    # and ends in a tail to the left
    ytz, ybz = 0.50 * XH, DSC - osl + b
    rxz, ryz = 196 - a * 0.9, (ytz - ybz) / 2
    cxz, cyz = W / 2 + 6, (ytz + ybz) / 2
    az = 118
    pz = se(cxz, cyz, rxz, ryz, az, az)[0]
    dgz, barz = e.zbars(504, XH, pz.x, pz.y, 104, None)        # the upright z's shared top corner
    # the bowl is its own stroke, starting just inside the diagonal's end (one stroke lost the diagonal's lighter,
    # skew-compensated pen, and the bar's cut no longer matched it: a step)
    S('z', [dgz, barz, o(se(cxz, cyz, rxz, ryz, az + 10, -158, fin(None, 1, 0.86)))])
