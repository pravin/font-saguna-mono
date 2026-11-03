"""Saguna Mono: the letters, figures and punctuation, for one stem weight (kit.Kit).

Every glyph is a spec of pen strokes (pen.py) in the 600-unit cell. The rules:
- rounds are squarish superellipses (pen.EXP) and overshoot baseline, x-height and cap height;
- every stroke end is round (the pen's rounded mode), and dots are round;
- bars are a little lighter than stems; arches and bowls thin where they leave a stem;
- bowl terminals stop where the stroke runs at kit.PHI degrees, so c e s C G S 2 3 5 6 9 share one cut;
- narrow letters (i j l r f t 1 I) get arms, feet and tails so every cell looks equally full; wide ones
  (m w M W) use a lighter pen that stops growing, so they stay open in Bold;
- the hyphen, maths signs and arrows sit on kit.MATH, and brackets share one top and bottom.
italic.py replaces the lowercase with cursive forms; symbols.py adds the rest; compose.py the accents.
"""

import math

from kit import ASC, CAP, DSC, MATH, PHI_LONG, W, XH, Kit, se, tf
from pen import EXP, pen_half, se_point, se_tangent, slope_angle

BR_T, BR_B = 812, -176          # brackets, bars and slashes share this top and bottom


def make(K: Kit, italic=False):
    a, b, w, osl, osc = K.a, K.b, K.w, K.os, K.osc
    o, vl, hl, D, DD, ring, J, along = K.o, K.vl, K.hl, K.D, K.DD, K.ring, K.J, K.along
    tp, fin, dot = K.taper, K.fin, K.dot
    dw = w - 80
    G = {}

    def S(ch, strokes=(), fills=(), box=None):
        sp = dict(s=list(strokes), p=list(fills))
        if box is not None:                     # drawn in its own box: centre the box in the cell
            sp = tf(sp, dx=W / 2 - (box[0] + box[1]) / 2)
        G[ch] = sp

    T, XT, AT = CAP - b, XH - b, ASC - b
    yt, yb = XH + osl - b, -osl + b             # centre lines of round strokes at x-height and baseline
    # straight lowercase sits in L..R, rounds in OL..OR; capitals in CL..CR; wide letters in WL..WR
    L, R = 86, 514                              # (the cell is 600: these leave about the side room JetBrains Mono does)
    OL, OR = 70, 530
    CL, CR = 76, 524
    WL, WR = 40, 560
    km = min(0.9, (50 + 0.45 * w) / w)          # the pen of m w M W: lighter, and it stops growing
    xl, xr = L + a, R - a
    ra = 0.42 * (R - L)                         # arch: vertical radius
    rdot = K.dr
    yd = XH + 70 + rdot                         # the i and j dot

    def zbars(xt, yt_, xb, yb_, top_bar, bot_bar, k=None):
        """A diagonal from a top bar to a bottom bar (Z z 7 2): its outer edges land exactly on the bars' ends,
        (xt, yt_) and (xb, yb_); it is cut on the bars' centre lines, so its ends hide inside them; and each bar's
        end is cut along the diagonal's edge. The bar and the diagonal then share one corner: no foot poking
        out past the diagonal, no notch beside it."""
        dg = DD((xt, yt_), (xb, yb_), -1 if top_bar else None, 1 if bot_bar else None, k=k,
                caps=(J(('y', yt_ - b)) if top_bar else 'f', J(('y', yb_ + b)) if bot_bar else ('y', yb_)))
        (px, py), (qx, qy) = dg.items[0], dg.items[-1]
        d = (px - qx, py - qy)
        out = [dg]
        if top_bar:
            out.append(o([(top_bar, yt_ - b), (xt, yt_ - b)], caps=('f', ('L', xt, yt_, d[0], d[1], 'JR'))))   # its lower corner lies on the diagonal's edge
        if bot_bar:
            out.append(o([(xb, yb_ + b), (bot_bar, yb_ + b)], caps=(('L', xb, yb_, d[0], d[1], 'JL'), 'f')))   # its upper corner lies on the diagonal's edge
        return out

    def arch(x0, x1, k=1.0, rav=ra, top=yt):
        rx = (x1 - x0) / 2
        return o(se(x0 + rx, top - rav, rx, rav, 180, 0, tp(0, None)) + [(x1, 0)], k=k)

    # ------------------------------------------------------------ lowercase
    S('n', [vl(xl, 0, XH), arch(xl, xr)])
    S('h', [vl(xl, 0, ASC), arch(xl, xr)])
    am = a * km
    m0, m2 = WL + am, WR - am
    m1 = (m0 + m2) / 2
    ram = 0.40 * (R - L)
    S('m', [vl(m0, 0, XH, k=km), arch(m0, m1, km, ram, XH + osl - b * km), arch(m1, m2, km, ram, XH + osl - b * km)])
    rxu = (xr - xl) / 2
    S('u', [o([(xl, XH)] + se(xl + rxu, yb + ra, rxu, ra, 180, 360, tp(None, 1))), vl(xr, 0, XH)])
    # r: the arm leaves the stem in a soft shoulder and ends level. No foot: beside JetBrains and SF Mono a footed
    # r read as a hook (err, str); the stem sits left of centre so the arm fills the cell, and rn stays apart from m
    xs_r = 148
    rxr = 0.42 * (R - L)
    tr_ = tp(0, None)
    kr = lambda f: min(tr_(f), 1 - 0.12 * min(1.0, max(0.0, (f - 0.35) / 0.65)) ** 2)
    S('r', [vl(xs_r, 0, XH),
            o(se(xs_r + rxr, yt - ra * 0.92, rxr, ra * 0.92, 180, 90, kr) + [(530, yt, 0.9)])])
    S('o', [ring(*K.bowl(OL, OR, -osl, XH + osl))])
    bcx, bcy, brx, bry = K.bowl(L, OR, -osl, XH + osl)
    bowl_l = o(se(bcx, bcy, brx, bry, 180, -180, tp(0, 1, None, 0.22)))
    dcx, dcy, drx, dry = K.bowl(OL, R, -osl, XH + osl)
    bowl_r = o(se(dcx, dcy, drx, dry, 0, 360, tp(0, 1, None, 0.22)))
    S('b', [vl(xl, 0, ASC), bowl_l])
    S('p', [vl(xl, DSC, XH), bowl_l])
    S('d', [bowl_r, vl(xr, 0, ASC)])
    S('q', [bowl_r, vl(xr, DSC, XH)])
    # a: double storey. The hook runs over the top and down into the stem; the bowl leaves the stem
    # as a bar, runs round and returns into the stem's centre line
    ryh = 0.30 * XH
    rxh = 0.47 * (R - L)
    cyh = yt - ryh
    hook = se(xr - rxh, cyh, rxh, ryh, K.term(rxh, ryh, 1), 0, fin(0, None))
    ybt = 0.56 * XH
    rxb = (xr - (OL + 8 + a)) / 2
    ryb = (ybt - yb) / 2
    S('a', [o(hook + [(xr, 0)]),
            o([(xr, ybt), (xr - rxb, ybt)] + se(xr - rxb, ybt - ryb, rxb, ryb, 90, 340, tp(None, 1, None, 0.25)))])
    # c, e, s
    cx, cy, rx, ry = K.bowl(OL + 4, OR + 6, -osl, XH + osl)
    S('c', [o(se(cx, cy, rx, ry, K.term(rx, ry, 0, 74), K.term(rx, ry, 3, 74), fin(0, 1)))])     # ends reach round, so ct is not gappy
    def e_strokes(x0, x1, k=1.0):
        """An e in the box x0..x1 on pen scale k: the bowl runs down to the bar's underside and is cut level
        with it, so its right side is one curve; the bar ends inside the bowl's stroke. (æ and œ draw a narrow
        one: a squashed full-width e lost those hidden joins.)"""
        ak, bk = a * k, b * k
        cx, cy, rx, ry = (x0 + x1) / 2, XH / 2, (x1 - x0) / 2 - ak, (XH + 2 * osl) / 2 - bk
        ybar = cy + 12

        def y_ang(y):
            v = (y - cy) / ry
            return math.degrees(math.asin(math.copysign(min(1.0, abs(v) ** (EXP / 2)), v)))
        yu = ybar - bk
        bs = se(cx, cy, rx, ry, y_ang(yu), K.term(rx, ry, 3) - 4, fin(None, 1))
        xe = se_point(cx, cy, rx, ry, y_ang(ybar))[0]
        return [o(bs, k=k, caps=(J(('y', yu)), 'f')), o([(x0 + ak * 0.6, ybar), (xe, ybar)], k=k)]
    S('e', e_strokes(OL, OR))
    ym = XH * 0.53
    sx = W / 2
    up_ry, lo_ry = (yt - ym) / 2, (ym - yb) / 2
    up_rx, lo_rx = 200 - a - 8, 206 - a
    sp1 = se(sx, ym + up_ry, up_rx, up_ry, K.term(up_rx, up_ry, 0), 270, fin(0, None))
    sp2 = se(sx, ym - lo_ry, lo_rx, lo_ry, 90, K.term(lo_rx, lo_ry, 2) - 360, fin(None, 1))
    S('s', [o(sp1 + sp2[1:])])
    # f and t: the stem a little left of centre, a wide crossbar, the hook / tail reaching the right side. The narrow
    # letters fill their cells like JetBrains' and SF Mono's (ct, rt, ti, fl looked gappy)
    xf = 250
    rf = 0.30 * (R - L)
    S('f', [o([(xf, 0), (xf, AT - rf)] + se(xf + rf, AT - rf, rf, rf, 180, 90) + [(528, AT, 0.9)]),
            hl(XT, 72, 506), hl(b, 90, 430)])
    rt = 0.34 * (R - L)
    S('t', [o([(xf, 650), (xf, yb + rt)] + se(xf + rt, yb + rt, rt, rt, 180, 290, fin(None, 1, 0.84)),
              caps=(('L', xf, 650, 1.0, 0.42), 'f')),
            hl(XT, 72, 506)])
    # i j l: arms and feet fill the cell; l ends in a tail so it never reads as 1 or I
    xi = W / 2 + 10
    S('i', [vl(xi, 0, XH), hl(XT, 110, xi, caps=('f', 'FJ')), hl(b, 84, 516)], [dot(xi, yd)])
    S('ı', [vl(xi, 0, XH), hl(XT, 110, xi, caps=('f', 'FJ')), hl(b, 84, 516)])
    xj = 380
    rj = 0.40 * (R - L) * 0.62
    yh = DSC - osl * 0.5 + b
    jtail = se(xj - rj, yh + rj * 0.92, rj, rj * 0.92, 0, -158, fin(None, 1, 0.84))
    S('j', [o([(xj, XH), (xj, yh + rj * 0.92)] + jtail), hl(XT, 92, xj, caps=('f', 'FJ'))], [dot(xj, yd)])
    S('ȷ', [o([(xj, XH), (xj, yh + rj * 0.92)] + jtail), hl(XT, 92, xj, caps=('f', 'FJ'))])
    xL = 250
    rl = 0.44 * (R - L)
    S('l', [o([(xL, ASC), (xL, yb + rl)] + se(xL + rl, yb + rl, rl, rl, 180, 290, fin(None, 1, 0.84))),
            hl(AT, 86, xL, caps=('f', 'FJ'))])
    for ch, x in (('i', xi), ('ı', xi), ('j', xj), ('ȷ', xj), ('l', xL), ('t', xf)):
        G[ch]['stem'] = x                       # accents and marks below sit over the stem, not the ink's middle
    # k: a straight arm into the stem and a leg off the arm
    yk = 0.30 * XH
    arm = D((R - 0.4 * a, XH), (xl, yk), (0, 0, W, XH), k=K.kd)
    pa = (xl + 0.44 * (R - 0.4 * a - xl), yk + 0.44 * (XH - yk))
    S('k', [vl(xl, 0, ASC), arm, D(pa, (R - 0.2 * a, 0), (0, 0, W, XH), caps=(along(arm), 'f'))])
    # v w x y z
    cl = (0, 0, W, XH)
    S('v', [DD((70, XH), (W / 2, 0), 1, None, cl), DD((W - 70, XH), (W / 2, 0), -1, None, cl)])
    p1, p2, p3 = 0.25 * (WR - WL) + WL, W / 2, 0.75 * (WR - WL) + WL
    kw = K.kd * km / 0.96
    S('w', [DD((WL - 6, XH), (p1, 0), 1, None, cl, k=kw), D((p1, 0), (p2, XH * 0.80), (0, 0, W, XH * 0.80), k=kw),
            D((p2, XH * 0.80), (p3, 0), (0, 0, W, XH * 0.80), k=kw), DD((p3, 0), (WR + 6, XH), None, -1, cl, k=kw)])
    S('x', [DD((80, 0), (W - 80, XH), 1, -1, cl), DD((80, XH), (W - 80, 0), 1, -1, cl)])
    # y: the right arm runs on below the baseline and curls left
    WV = 460
    Q0 = (WV * 0.30, DSC)
    Py = K.edge((WV, XH), Q0, -1)
    ddx, ddy = Q0[0] - Py[0], Q0[1] - Py[1]
    rr = max(0.17 * WV, 1.55 * a)
    phi_d = math.degrees(math.atan2(abs(ddy), abs(ddx)))
    ay0 = -slope_angle(rr, rr, 0.5, 89.5, phi_d)
    cyr = DSC - osl * 0.5 + b + rr
    sx0, sy0 = se_point(0, cyr, rr, rr, ay0)
    xdiag = Py[0] + (sy0 - Py[1]) * ddx / ddy
    tail = se(xdiag - sx0, cyr, rr, rr, ay0, -170, fin(None, 1, 0.8))
    yr = o([Py] + tail, clip=(-500, DSC - 200, WV, XH))
    xjn = Py[0] + (0 - Py[1]) * ddx / ddy
    S('y', [yr, DD((0, XH), (xjn, 0), 1, None, (0, 0, WV, XH), caps=('f', J(('L', Py[0], Py[1], ddx, ddy))))],
      box=(0, WV))
    S('z', zbars(500, XH, 96, 0, 100, 504))
    # g: single storey, the tail swings round under the bowl
    rg = 0.36 * (R - OL)
    S('g', [bowl_r, o([(xr, XH), (xr, yh + rg * 0.92)] + se(xr - rg, yh + rg * 0.92, rg, rg * 0.92, 0, -152, fin(None, 1, 0.8)))])

    if italic:
        import italic as it
        it.cursive(G, K, locals())

    # ------------------------------------------------------------ capitals
    cl = (CL - 10, 0, CR + 10, CAP)
    lA, rA = DD((CL - 12, 0), (W / 2, CAP), 1, None, cl), DD((CR + 12, 0), (W / 2, CAP), -1, None, cl)
    x0A = lA.items[0][0]
    xA = x0A + (W / 2 - x0A) * 218 / CAP
    S('A', [lA, rA, o([(xA, 218), (W - xA, 218)], caps=(along(lA), along(rA)))])
    xs = CL + a
    ymB = 384
    rt_, rb_ = (T - ymB) / 2, (ymB - b) / 2
    S('B', [vl(xs, 0, CAP), o([(xs, T), (CR - 20 - a - rt_, T)] + se(CR - 20 - a - rt_, T - rt_, rt_, rt_, 90, -90) + [(xs, ymB)], caps=('FJ', 'f')),
            o([(xs, ymB), (CR - a - rb_, ymB)] + se(CR - a - rb_, ymB - rb_, rb_, rb_, 90, -90) + [(xs, b)], caps=('f', 'FJ'))])
    cx, cy, rx, ry = K.bowl(CL - 4, CR + 12, -osc, CAP + osc)
    S('C', [o(se(cx, cy, rx, ry, K.term(rx, ry, 0), K.term(rx, ry, 3)))])
    rD = (T - b) / 2
    xD = CR - a - rD * 1.02
    S('D', [vl(xs, 0, CAP), o([(xs, T), (xD, T)] + se(xD, CAP / 2, CR - a - xD, rD, 90, -90) + [(xs, b)], caps=('FJ', 'FJ'))])
    S('E', [vl(xs, 0, CAP), hl(T, xs, CR, caps=('FJ', 'f')), hl(377, xs, CR - 40, caps=('FJ', 'f')), hl(b, xs, CR + 6, caps=('FJ', 'f'))])
    S('F', [vl(xs, 0, CAP), hl(T, xs, CR, caps=('FJ', 'f')), hl(367, xs, CR - 40, caps=('FJ', 'f'))])
    cx, cy, rx, ry = K.bowl(CL - 6, CR + 4, -osc, CAP + osc)
    yg = 0.47 * CAP
    ag = 360 + math.degrees(math.asin(-(((cy - yg) / ry) ** (EXP / 2))))
    S('G', [o(se(cx, cy, rx, ry, K.term(rx, ry, 0), ag, fin(0, None)) + [(cx + 0.04 * W, yg)])])
    S('H', [vl(xs, 0, CAP), vl(CR - a, 0, CAP), hl(377, xs, CR - a, caps=('FJ', 'FJ'))])
    S('I', [vl(W / 2, 0, CAP), hl(T, 130, 470), hl(b, 130, 470)])
    rJ = 0.42 * (CR - CL)
    xJ = CR - 10 - a
    S('J', [o([(xJ, CAP), (xJ, -osc + b + rJ)] + se(xJ - rJ, -osc + b + rJ, rJ, rJ, 0, -180 + 25, fin(None, 1))),
            hl(T, 230, xJ, caps=('f', 'FJ'))])
    cl = (0, 0, CR + 12, CAP)
    arm = DD((xs, CAP * 0.36), (CR + 12, CAP), None, -1, cl, k=K.kd, caps=(J(('x', xs)), 'f'))
    S('K', [vl(xs, 0, CAP), arm, DD((xs + 0.30 * (CR - CL), CAP * 0.36 + 0.30 * (CR - CL) * 0.95), (CR + 12, 0), None, -1, cl,
                                   caps=(along(arm), 'f'))])
    S('L', [vl(xs + 20, 0, CAP), hl(b, xs + 20, CR + 6, caps=('FJ', 'f'))])
    am_ = a * km
    yv = 170
    # M: each diagonal's outer edge starts on its stem's outer edge, so stem and diagonal share one top
    # (two rounded tops side by side made a double bump)
    S('M', [vl(WL + 10 + am_, 0, CAP, k=km), vl(WR - 10 - am_, 0, CAP, k=km),
            DD((WL + 10, CAP), (W / 2, yv), 1, None, (0, yv, W, CAP), k=km * 0.96),
            DD((WR - 10, CAP), (W / 2, yv), -1, None, (0, yv, W, CAP), k=km * 0.96)])
    ni = 0.3 * a
    S('N', [vl(xs, 0, CAP), vl(CR - a, 0, CAP), DD((CL + ni, CAP), (CR - ni, 0), 1, -1, (0, 0, W, CAP))])
    S('O', [ring(*K.bowl(OL - 4, OR + 4, -osc, CAP + osc))])
    ymp = 310
    rp = (T - ymp) / 2
    S('P', [vl(xs, 0, CAP), o([(xs, T), (CR - a - rp, T)] + se(CR - a - rp, T - rp, rp, rp, 90, -90) + [(xs, ymp)], caps=('FJ', 'FJ'))])
    cxo, cyo, rxo, ryo = K.bowl(OL - 4, OR + 4, -osc, CAP + osc)
    S('Q', [ring(cxo, cyo, rxo, ryo), D((W * 0.56, 190), (W * 0.84, -150), caps=('f', ('y', -150)))])
    S('R', [vl(xs, 0, CAP), o([(xs, T), (CR - a - rp - 10, T)] + se(CR - a - rp - 10, T - rp, rp, rp, 90, -90) + [(xs, ymp)], caps=('FJ', 'FJ')),
            D((CR - a - rp - 40, ymp), (CR + 4, 0), (0, 0, W, CAP), caps=('f', 'f'))])
    ymS = 388
    up_ry, lo_ry = (CAP + osc - b - ymS) / 2, (ymS - (-osc + b)) / 2
    up_rx, lo_rx = 210 - a - 12, 218 - a
    # the ends run on past the shoulders to the sides of the bowls and are cut level, so the S reads as one sweep
    S('S', [o(se(W / 2, ymS + up_ry, up_rx, up_ry, 0, 270, fin(0, None)) +
              se(W / 2, ymS - lo_ry, lo_rx, lo_ry, 90, -180, fin(None, 1))[1:])])
    S('T', [hl(T, CL - 18, CR + 18), vl(W / 2, 0, T)])
    ru = (CR - CL - w) / 2
    S('U', [o([(xs, CAP), (xs, -osc + b + ru)] + se(W / 2, -osc + b + ru, ru, ru, 180, 360) + [(CR - a, CAP)])])
    cl = (0, 0, W, CAP)
    S('V', [DD((CL - 22, CAP), (W / 2, 0), 1, None, cl), DD((CR + 22, CAP), (W / 2, 0), -1, None, cl)])
    q1, q3 = WL + 0.25 * (WR - WL), WL + 0.75 * (WR - WL)
    S('W', [DD((WL - 4, CAP), (q1, 0), 1, None, cl, k=kw), D((q1, 0), (W / 2, CAP * 0.78), (0, 0, W, CAP * 0.78), k=kw),
            D((W / 2, CAP * 0.78), (q3, 0), (0, 0, W, CAP * 0.78), k=kw), DD((q3, 0), (WR + 4, CAP), None, -1, cl, k=kw)])
    S('X', [DD((CL - 14, 0), (CR + 14, CAP), 1, -1, cl), DD((CL - 14, CAP), (CR + 14, 0), 1, -1, cl)])
    yj = 320
    yl_ = DD((CL - 18, CAP), (W / 2, yj), 1, None, cl)
    yr_ = DD((CR + 18, CAP), (W / 2, yj), -1, None, cl)
    S('Y', [DD((CL - 18, CAP), (W / 2, yj), 1, None, cl, caps=('f', along(yr_))),
            DD((CR + 18, CAP), (W / 2, yj), -1, None, cl, caps=('f', along(yl_))), o([(W / 2, 0), (W / 2, yj + 0.8 * a)], caps=('f', 'FJ'))])
    S('Z', zbars(CR, CAP, CL, 0, CL + 4, CR + 4))

    # ------------------------------------------------------------ figures (cap height, one width)
    FL, FR = 90, 510
    cx = W / 2
    ytc, ybc = CAP + osc - b, -osc + b
    # 0: an oval with a round dot inside, so it never reads as O
    zx, zy, zrx, zry = K.bowl(FL, FR, -osc, CAP + osc)
    S('0', [ring(zx, zy, zrx, zry)], [dot(zx, zy, 0.55 * rdot + 6)])
    x1 = 318
    S('1', [vl(x1, 0, CAP), DD((x1 - 175, 0.74 * CAP), (x1 + a, CAP), None, -1, (-500, 0, x1 + a, CAP), k=0.94),
            hl(b, 140, 470)])
    r2 = 0.29 * CAP
    rx2 = cx - FL - a
    def two(x0, x1, y0, y1, k=1.0):
        """A 2 in the box x0..x1, y0..y1 on pen scale k. The bowl runs into the diagonal, whose outer edge lands
        on the foot's left end; the foot is cut along that edge, so they share one corner. (The superior and
        fraction 2s draw their own: scaled down, the edges no longer met.)"""
        ak, bk = a * k, b * k
        c_ = (x0 + x1) / 2
        rx_, ry_ = c_ - x0 - ak, 0.29 * (y1 - y0)
        arc = se(c_, y1 + osc - bk - ry_, rx_, ry_, K.term(rx_, ry_, 1, PHI_LONG), -40)
        p = (arc[-1].x, arc[-1].y)
        q = K.edge((x0, y0), p, 1, k=k, skewed=True)     # skewed: the stroke is drawn with k, no italic compensation
        d = (p[0] - q[0], p[1] - q[1])
        return [o(arc + [q], k=k, caps=('f', J(('y', y0 + bk)))),
                o([(q[0], y0 + bk), (x1 + 4, y0 + bk)], k=k, caps=(('L', x0, y0, d[0], d[1], 'JL'), 'f'))]
    S('2', two(FL, FR, 0, CAP))
    ym3 = 400
    kf = 1 - 0.0013 * max(dw, 0)
    r3u, r3l = (ytc - ym3) / 2, (ym3 - ybc) / 2
    rx3u, rx3l = cx - FL - a - 20, cx - FL - a + 4
    S('3', [o(se(cx - 6, ym3 + r3u, rx3u, r3u, K.term(rx3u, r3u, 1), -90), k=kf),
            o(se(cx, ym3 - r3l, rx3l, r3l, 90, K.term(rx3l, r3l, 2) - 360), k=kf),
            hl(ym3, cx - 70, cx + 0.5 * a, k=1.04)])
    x4 = FR - 92
    d4 = DD((x4 + a, CAP), (FL - 10, 225 - b), -1, 1, caps=(('y', CAP), ('y', 225 - b)))
    (dx0, dy0), (dx1, dy1) = d4.items[0], d4.items[-1]
    ex = dx1 - K.hx((dx0, dy0), (dx1, dy1))
    xb4 = ex + (dx0 - dx1) * (b / (dy0 - dy1))
    S('4', [vl(x4, 0, CAP), d4, o([(xb4, 225), (FR + 10, 225)], caps=(('L', ex, 225 - b, dx0 - dx1, dy0 - dy1), 'f'))])
    r5 = 0.30 * CAP
    rx5 = cx - FL - a + 4
    p5 = se(cx, ybc + r5, rx5, r5, 136, K.term(rx5, r5, 2, PHI_LONG) - 360, tp(0, None, 0.97, 0.15))
    x5 = p5[0].x + 0.02 * a
    q5 = p5[0]
    n5 = (q5.ty, -q5.tx) if q5.tx > 0 else (-q5.ty, q5.tx)
    h5 = pen_half(a, b, *n5) * q5.k
    y5 = min(q5.y - 0.12 * w, q5.y + n5[1] * h5 - 2)
    S('5', [o([(FR - a * 0.4, T), (x5, T), (x5, y5)]), o(p5)])
    r6 = 0.29 * CAP
    rx6 = cx - FL - a
    cy6 = ybc + r6
    ry6 = ytc - cy6
    S('6', [o(se(cx, cy6, rx6, ry6, K.term(rx6, ry6, 0, PHI_LONG) + 5, 180) + se(cx, cy6, rx6, r6, 180, 535)[1:], k=kf)])
    G['9'] = tf(G['6'], -1, -1, W, CAP)
    S('7', zbars(FR + 6, CAP, FL + 0.30 * (FR - FL), 0, FL, None))
    Hh = (ytc - ybc) / 2
    r8u, r8l = 0.465 * Hh, 0.535 * Hh
    S('8', [ring(cx, ytc - r8u, rx6 - 26, r8u, k=kf), ring(cx, ybc + r8l, rx6, r8l, k=kf)])

    # ------------------------------------------------------------ punctuation
    rd = rdot
    py = rd                                 # the full stop sits on the baseline
    cm = K.comma
    S('.', [], [dot(W / 2, py)])
    S(',', [], [cm(W / 2 + 10, py)])
    S(':', [], [dot(W / 2, py), dot(W / 2, XH - rd)])
    S(';', [], [cm(W / 2 + 10, py), dot(W / 2 + 10, XH - rd)])
    S('!', [o([(W / 2, CAP), (W / 2, 2 * rd + 90, 0.62)], k=1.08)], [dot(W / 2, py)])
    rq = 160
    q0 = K.term(185 - a, rq, 1)
    S('?', [o(se(W / 2, ytc - rq, 185 - a, rq, q0, -72, fin(0, None, 0.8)) + [(W / 2 + 0.12 * (185 - a), 2 * rd + 70, 0.8)], k=1.04)],
      [dot(W / 2 + 12, py)])
    S('-', [hl(MATH, 140, 460)])
    S('–', [hl(MATH, 60, 540)])
    S('—', [hl(MATH, 0, 600)])
    S('_', [hl(-110, 40, 560)])
    hx = K.hx((0, BR_B), (1, BR_T))
    S('/', [D((120 + hx, BR_B), (480 - hx, BR_T), (0, BR_B, W, BR_T))])
    S('\\', [D((480 - hx, BR_B), (120 + hx, BR_T), (0, BR_B, W, BR_T))])
    pr = (BR_T - BR_B) / 2
    S('(', [o(se(470, (BR_T + BR_B) / 2, 250 - a, pr - b + 46, 112, 248))])     # tips reach the brackets' top and bottom
    S(')', [o(se(130, (BR_T + BR_B) / 2, 250 - a, pr - b + 46, 68, -68))])
    S('[', [o([(430, BR_T - b), (220 + a, BR_T - b), (220 + a, BR_B + b), (430, BR_B + b)])])
    S(']', [o([(170, BR_T - b), (380 - a, BR_T - b), (380 - a, BR_B + b), (170, BR_B + b)])])
    S('|', [vl(W / 2, BR_B, BR_T)])
    # maths signs fill the cell as in JetBrains Mono and SF Mono, so operators read at a glance in code
    S('+', [hl(MATH, 80, 520), vl(W / 2, MATH - 220, MATH + 220)])
    S('=', [hl(MATH - 112, 86, 514), hl(MATH + 112, 86, 514)])
    S('<', [o([(500, MATH + 240), (104 + a * 1.3, MATH), (500, MATH - 240)])])
    S('>', [o([(100, MATH + 240), (496 - a * 1.3, MATH), (100, MATH - 240)])])
    ka = 0.8
    ca, ra_ = (W / 2, 400), 210                     # big and near the maths axis, so a * b and **argv read clearly
    arms = []
    for ang in (90, 210, 330):
        t = math.radians(ang)
        arms.append(D((ca[0] - ra_ * math.cos(t), ca[1] - ra_ * math.sin(t)), (ca[0] + ra_ * math.cos(t), ca[1] + ra_ * math.sin(t)), k=ka))
    S('*', arms)
    S("'", [vl(W / 2, 470, CAP + 20)])
    S('"', [vl(W / 2 - 90, 470, CAP + 20), vl(W / 2 + 90, 470, CAP + 20)])
    yq = CAP - rd
    tq = rd + 2 * rd * 0.6 + 30
    S('’', [], [cm(W / 2 + 10, yq)])
    S('‘', [], [cm(W / 2 - 10, yq - tq, turned=True)])
    S('”', [], [cm(W / 2 - 110, yq), cm(W / 2 + 130, yq)])
    S('“', [], [cm(W / 2 - 130, yq - tq, turned=True), cm(W / 2 + 110, yq - tq, turned=True)])
    S('‚', [], [cm(W / 2 + 10, py)])
    S('„', [], [cm(W / 2 - 110, py), cm(W / 2 + 130, py)])
    S('·', [], [dot(W / 2, MATH)])
    S('…', [], [dot(100, py, rd * 0.92), dot(W / 2, py, rd * 0.92), dot(500, py, rd * 0.92)])
    # #: cap height, the uprights a third of the cell apart and the bars well apart, with a pen that stops
    # growing, so the middle stays an open square in Bold (it closed to a pinhole)
    kh = min(0.9, 92 / w)
    yh0, yh1 = MATH - 128, MATH + 128
    S('#', [hl(yh0, 62, 538, k=kh), hl(yh1, 62, 538, k=kh),
            D((180, 0), (240, CAP), (0, 0, W, CAP), k=kh), D((360, 0), (420, CAP), (0, 0, W, CAP), k=kh)])
    # %: two lighter rings and a slash
    kp = 0.78 - 0.0022 * max(0.0, dw)
    prx, pry = 102 + 0.3 * dw, 138 + 0.3 * dw
    S('%', [ring(52 + prx, CAP + osc - pry, prx - a * kp, pry - b * kp, k=kp),
            ring(W - 52 - prx, pry - osc, prx - a * kp, pry - b * kp, k=kp),
            DD((70, 0), (530, CAP), 1, -1, (0, 0, W, CAP), k=0.88)])
    # &: a loop, a bowl and a straight leg
    rxo = 118 + 0.4 * max(0.0, dw)
    cnt = 54 - 10 * dw / 48
    kl = min(1.0, (rxo - cnt) / 2 / a)
    S('&', [ring(262, 540, rxo - a * kl, 150 - b * kl, k=kl),
            o(se(290, 214 - osc / 2, 212 - a, 214 + osc / 2 - b, 118, 378)),
            D((176, 420), (540, 0), (0, 0, W, CAP), caps=('f', ('y', 0)))])
    # @: an 'a' inside an open ring; the a's stem runs down onto the ring, which starts there. Many strokes
    # share one cell, so the pen is lighter and stops growing (in Bold the inner bowl filled in)
    kat = min(0.86, (44 + 0.34 * w) / w)            # lighter than a stem: at 13 px a full-weight @ filled in
    aa, ba = a * kat, b * kat
    cxa, cya = W / 2, 320                             # as tall as the capitals and the descender, like JetBrains' @
    Rx, Ry = 278 - aa, 400 - ba
    irx, iry = 122 - aa, 192 - ba                    # a narrow inner bowl, so the ring has room round it at 13 px
    icx = cxa - 22
    xsa = icx + irx
    cmm = ((xsa - cxa) / Rx) ** (EXP / 2)
    amm = -math.degrees(math.acos(min(1.0, cmm)))
    ym_ = cya - Ry * math.sin(math.radians(-amm)) ** (2 / EXP)
    arc = se(cxa, cya, Rx, Ry, amm, amm + 318)
    t0 = (arc[0].tx, arc[0].ty)
    S('@', [ring(icx, cya, irx, iry, k=kat),
            o([(xsa, cya + iry + ba), (xsa, ym_)], k=kat, caps=('f', J(('L', xsa, ym_, t0[0], t0[1])))),
            o(arc, k=kat, caps=(J(('x', xsa - aa)), 'f'))])
    S('^', [o([(130, 430), (W / 2, CAP), (470, 430)])])
    S('~', [o(K.wave(86, 514, MATH, 62))])
    S('`', [D((235, CAP + 150), (335, CAP - 10), k=0.86)])
    # {: true circles wider than the pen (rule 4.2.1): a squarish corner's tight spot folded in Bold
    mid = (BR_T + BR_B) / 2
    cr = K.circle
    S('{', [o([(460, BR_T - b), (390, BR_T - b)] + cr(390, BR_T - b - 100, 100, 90, 180) +
              [(290, mid + 100)] + cr(190, mid + 100, 100, 0, -90) + [(150, mid)]),
            o([(460, BR_B + b), (390, BR_B + b)] + cr(390, BR_B + b + 100, 100, -90, -180) +
              [(290, mid - 100)] + cr(190, mid - 100, 100, 0, 90) + [(150, mid)])])
    G['}'] = tf(G['{'], -1, 1, W, 0)
    # $: an S on a stroke that stops short of the bowls
    S('$', [o(se(W / 2, 390 + 154, 185 - a - 10, 154, 0, 270, fin(0, None)) +      # ends as the S
              se(W / 2, 390 - 174, 192 - a, 174, 90, -180, fin(None, 1))[1:]),
            vl(W / 2, -110, -osc + 1.4 * b), vl(W / 2, CAP + osc - 1.4 * b, CAP + 110)])     # the stem's ends run well into the bowls

    import symbols
    symbols.extend(G, K, locals())
    return G
