"""Saguna Mono italic: cursive lowercase, drawn upright and sheared with the rest by generate.py.

The hand: stems start with a small entry stroke and end in an exit flick to the right; the l is a loop
(ℓ), while b h k keep plain ascenders (a loop there collided with their bowls and arches); f descends with a tail; a is single storey; x is two bowls back to back;
y is a u with a descending tail; z ends in a swash. c e g o s t and the diagonals v w keep their upright
shapes: in code, u v and w must never be confused, so v and w stay pointed.
"""

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
        return cy, o(se(x + rL, cy, rL, rLy, 180, -80, fin(None, 1, 0.86)) + [(x - 84, cy - rLy - 70, 0.84)],
                     caps=(J(('y', cy)), 'f'))

    def stem_to(x, cy):
        return o([(x, 0), (x, cy)], caps=('f', J(('y', cy))))

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
    xi = W / 2 - 20
    S('i', [o(entry(xi) + flick(xi))], [dot(xi, yd)])
    S('ı', [o(entry(xi) + flick(xi))])
    xj = e.xj
    rj, yh = e.rj, e.yh
    jt = se(xj - rj, yh + rj * 0.92, rj, rj * 0.92, 0, -158, fin(None, 1, 0.84))
    S('j', [o(entry(xj) + [(xj, yh + rj * 0.92)] + jt)], [dot(xj, yd)])
    S('ȷ', [o(entry(xj) + [(xj, yh + rj * 0.92)] + jt)])
    xL = W / 2 - 40
    cyL, lpL = loop(xL)
    S('l', [o([(xL, cyL)] + flick(xL), caps=(J(('y', cyL)), 'f')), lpL])
    for ch, x in (('i', xi), ('ı', xi), ('j', xj), ('ȷ', xj), ('l', xL)):
        G[ch]['stem'] = x
    # a d q: a bowl on the right stem; a and d end in a flick
    bowl_r, bowl_l = e.bowl_r, e.bowl_l
    S('a', [bowl_r, o([(xr, XH)] + flick(xr))])
    S('d', [bowl_r, o([(xr, ASC)] + flick(xr))])
    S('q', [bowl_r, vl(xr, DSC, XH)])
    # b p: an entry stroke, then the bowl
    S('b', [o(entry(xl, ASC) + [(xl, 0)]), bowl_l])
    S('p', [o(entry(xl) + [(xl, DSC)]), bowl_l])
    # k: an entry stroke, a small bowl for the arm and a leg that flicks out
    ya, yk = 0.30 * XH, 0.88 * XH
    S('k', [o(entry(xl, ASC) + [(xl, 0)]),
            o(se(xl, (ya + yk) / 2, 190, (yk - ya) / 2, -90, 90), caps=(J(('x', xl)), J(('x', xl)))),
            o([(xl + 110, ya + 20)] + se(R - 60 + rf, yb + rf, rf, rf, 240, 305, fin(None, 1, 0.84)))])     # the flick leaves at the leg's own slope
    # r: an entry stroke and a soft arm
    xs_r = e.xs_r
    S('r', [o(entry(xs_r) + [(xs_r, 0)]),
            o(se(xs_r + e.rxr, yt - ra * 0.92, e.rxr, ra * 0.92, 180, 90, e.kr) + [(470, yt - 10, 0.88)])])
    # f: descends below the baseline and curls left; a crossbar at the x-height
    xf, rff = 300, 0.28 * (R - L)
    S('f', [o(se(xf - rff, DSC - osl + b + rff, rff, rff, -160, 0, fin(0, None, 0.84)) + [(xf, AT - rff)] +
              se(xf + rff, AT - rff, rff, rff, 180, 90) + [(510, AT, 0.9)]), hl(XT, 150, 450)])
    # x: two bowls back to back, ɔ and c
    ry = (XH + osl - b - yb) / 2
    cyx = (XH + osl - b + yb) / 2
    S('x', [o(se(W / 2 - 160, cyx, 160 - 6, ry, 104, -104, fin(0, 1))), o(se(W / 2 + 160, cyx, 160 - 6, ry, 76, 284, fin(0, 1)))])
    # y: a u whose right stem runs on below the baseline into a tail
    S('y', [o(entry(xl) + se(xl + rxu, yb + ra, rxu, ra, 180, 360, tp(None, 1))),
            o([(xr, XH), (xr, yh + rj * 0.92)] + se(xr - rj * 1.2, yh + rj * 0.92, rj * 1.2, rj * 0.92, 0, -158, fin(None, 1, 0.84)))])
    # z: a top bar, a diagonal, and a foot that swings down into a swash
    zb = e.zbars(500, XH, 96, 0, 100, 400)          # the upright z's shared corners, then the foot runs on into a swash
    foot = zb[2]
    rz = max(96.0, 1.3 * a)                        # a true circle, wider than the pen (a squarish curve folded in Bold)
    zb[2] = o(foot.items + K.circle(400, b - rz, rz, 90, -55), caps=foot.caps)
    S('z', zb)
