"""Saguna Mono: the Latin letters that need their own drawing (Æ Ø ß Ł ŋ ...), currency, maths and
typographic signs, then the code set (cells.py: arrows, box drawing, blocks and shapes)."""

from kit import ASC, CAP, DSC, MATH, W, XH, merge, se, tf
from pen import se_point


def extend(G, K, env):
    e = type('E', (), env)
    a, b, w, osl, osc = K.a, K.b, K.w, K.os, K.osc
    o, vl, hl, D, DD, ring, along, dot = K.o, K.vl, K.hl, K.D, K.DD, K.ring, K.along, K.dot
    fin, tp = K.fin, K.taper
    S = e.S
    T, XT, AT, yt, yb = e.T, e.XT, e.AT, e.yt, e.yb
    L, R, OL, OR, CL, CR = e.L, e.R, e.OL, e.OR, e.CL, e.CR
    xl, xr, xs, km = e.xl, e.xr, e.xs, e.km
    from glyphs import BR_B, BR_T
    dw = w - 80
    rd = K.dr
    G[' '] = dict(s=[], p=[])

    def sub(ch, sx, sy, dx, dy, k):
        return tf(G[ch], sx, sy, dx, dy, k)

    def plus(ch, strokes=(), fills=()):
        return merge(G[ch], dict(s=list(strokes), p=list(fills)))

    # ------------------------------------------------------------ Latin letters
    G['¡'] = tf(G['!'], 1, -1, 0, XH)
    G['¿'] = tf(G['?'], -1, -1, W, XH)
    sl = lambda x0, y0, x1, y1: D((x0, y0), (x1, y1), k=0.9)
    G['Ø'] = plus('O', [DD((CL - 10, -40), (CR + 10, CAP + 40), 1, -1, (0, -40, W, CAP + 40), k=0.9)])
    G['ø'] = plus('o', [DD((OL + 10, -50), (OR - 10, XH + 50), 1, -1, (0, -50, W, XH + 50), k=0.9)])
    G['Ł'] = plus('L', [sl(xs - 50, 300, xs + 170, 450)])
    G['ł'] = plus('l', [sl(G['l'].get('stem', e.xL) - 110, 200, G['l'].get('stem', e.xL) + 110, 330)])
    G['Đ'] = plus('D', [hl(CAP / 2, CL - 30, xs + 130)])
    G['Ð'] = G['Đ']
    G['đ'] = plus('d', [hl(ASC - 130, xr - 130, xr + 80)])
    G['Ħ'] = plus('H', [hl(540, CL - 30, CR + 30)])
    # in the italic the bar runs right from the stem only: across the entry hook it closed a pinhole
    G['ħ'] = plus('h', [hl(ASC - 130, xl - (0.3 * a if 'italic' in env and env['italic'] else 90), xl + 150)])
    G['Ŧ'] = plus('T', [hl(360, W / 2 - 130, W / 2 + 130)])
    G['ŧ'] = plus('t', [hl(250, e.xf - 120, e.xf + 140)])
    G['Ŀ'] = plus('L', [], [dot(CR - 70, CAP / 2)])
    G['ŀ'] = plus('l', [], [dot(G['l'].get('stem', e.xL) + 236, 236)])
    for ch, x in (('ł', G['l'].get('stem', e.xL)), ('ŀ', G['l'].get('stem', e.xL)), ('ŧ', e.xf)):
        G[ch]['stem'] = x
    # Þ þ
    ymp = 484
    rp = (ymp - 150) / 2
    S('Þ', [vl(xs, 0, CAP), o([(xs, ymp), (CR - a - rp, ymp)] + se(CR - a - rp, ymp - rp, rp, rp, 90, -90) + [(xs, 150)])])
    S('þ', [vl(xl, DSC, ASC), e.bowl_l])
    # ß: a stem rising into two stacked bowls, open at the foot like a lowercase B
    yw = 486
    r1x, r1 = 140, (ASC + osl - b - yw) / 2
    S('ß', [o([(xl, 0), (xl, ASC + osl - b - r1)] + se(xl + r1x, ASC + osl - b - r1, r1x, r1, 180, -90) + [(xl + 70, yw)]),
            o([(xl + 70, yw), (xr - 110, yw)] + se(xr - 110, yw - (yw - yb) / 2, 110, (yw - yb) / 2, 90, -90) +
              [(xl + 2.2 * a + 30, yb)])])          # the foot stops clear of the stem, so no counter closes in Bold
    # ẞ: the stem's top runs right and drops as a diagonal (one stroke, cut level at the bowl's top bar); the bowl
    # starts on the diagonal's left edge, cut along it. The sharp corner under the diagonal (its left edge meeting
    # the bar's underside) keeps 14 units clear of the stem, or a counter closes there in Bold.
    r_ = 110
    xt = CR - 30
    ym = 422
    rx2 = 118
    cx2 = CR - a - rx2
    xm = cx2 - 40
    for _ in range(6):
        hx_ = K.hx((xt, T), (xm, ym), 1.0)
        tip = xm - hx_ - b * (xt - xm) / (T - ym)
        xm = max(cx2 - 40, xm + (xs + a + 14 - tip))
    hx_ = K.hx((xt, T), (xm, ym), 1.0)
    S('ẞ', [o([(xs, 0), (xs, T - r_)] + se(xs + r_, T - r_, r_, r_, 180, 90) + [(xt, T), (xm, ym)], caps=('f', ('y', ym))),
            o([(xm - hx_, ym)] + se(cx2, (ym - osc + b) / 2, rx2, (ym + osc - b) / 2, 90, -90) + [(xs + 90, -osc + b)],
              caps=(('L', xm - hx_, ym, xm - xt, ym - T), 'f'))])
    # ð: a bowl, and a stroke that rises from its right side and curls over to the left; a short bar crosses it
    cxo, cyo, rxo, ryo = K.bowl(OL, OR, -osl, XH * 1.02 + osl)
    cxa_ = 230
    rxa_, rya_ = OR - a - cxa_, ASC - cyo - b
    px, py = se_point(cxa_, cyo, rxa_, rya_, 66)
    S('ð', [ring(cxo, cyo, rxo, ryo), o(se(cxa_, cyo, rxa_, rya_, 4, 104, fin(None, 1))),
            D((px - 100, py - 40), (px + 100, py + 40), k=0.9)])
    # ĸ: a small-capital K
    arm = D((R - 0.4 * a, XH), (xl, 0.30 * XH), (0, 0, W, XH))
    S('ĸ', [vl(xl, 0, XH), arm, D((xl + 0.44 * (R - xl), 0.30 * XH + 0.44 * 0.70 * XH), (R - 0.2 * a, 0), (0, 0, W, XH),
                                caps=(along(arm), 'f'))])
    # ŋ Ŋ: the right stem runs into a hook
    rj, yh, ra = e.rj, e.yh, e.ra
    rx = (xr - xl) / 2
    S('ŋ', [vl(xl, 0, XH), o(se(xl + rx, yt - ra, rx, ra, 180, 0, tp(0, None)) + [(xr, yh + rj * 0.92)] +
                            se(xr - rj, yh + rj * 0.92, rj, rj * 0.92, 0, -158, fin(None, 1, 0.84)))])
    rN = 0.42 * (CR - CL - 2 * a)
    xN = (CR - a - xs) / 2
    S('Ŋ', [vl(xs, 0, CAP), o(se(xs + xN, T - rN, xN, rN, 180, 0, tp(0, None)) + [(CR - a, -40)] +
                             se(CR - a - 110, -40, 110, 150 - b, 0, -150, fin(None, 1, 0.84)))])
    # ſ: f without its bar; ƒ: the florin, descending with a tail
    S('ſ', [o([(e.xf, 0), (e.xf, AT - e.rf)] + se(e.xf + e.rf, AT - e.rf, e.rf, e.rf, 180, 90) + [(500, AT, 0.9)]), hl(b, 106, 420)])
    rfl = 0.30 * (R - L)
    xfl = 310
    S('ƒ', [o(se(xfl - rfl, DSC - osl + b + rfl, rfl, rfl, -160, 0, fin(0, None, 0.84)) + [(xfl, AT - rfl)] +
              se(xfl + rfl, AT - rfl, rfl, rfl, 180, 90) + [(540, AT, 0.9)]), hl(XT, 170, 450)])
    # Ĳ ĳ: two letters in one cell
    rJ = 120
    S('Ĳ', [vl(135, 0, CAP), o([(465, CAP), (450, -osc + b + rJ)] + se(465 - rJ, -osc + b + rJ, rJ, rJ, 0, -132, fin(None, 1)))])
    rjj = 100
    S('ĳ', [vl(170, 0, XH), o([(430, XH), (430, yh + rjj)] + se(430 - rjj, yh + rjj, rjj, rjj * 0.92, 0, -160, fin(None, 1, 0.84)))],
      [dot(170, e.yd), dot(430, e.yd)])
    # Æ Œ: two letters sharing a stem, on the lighter pen of the wide letters
    kk = min(km, 90 / w)                 # Æ Œ æ œ: two letters in one cell, on a pen that stops growing (but late: they matched Light in Bold)
    xm = W / 2 + 20
    lA = DD((CL - 22, 0), (xm, CAP), 1, None, (0, 0, W, CAP), k=K.kd * kk)
    S('Æ', [lA, vl(xm, 0, CAP, k=kk), hl(T, xm, CR + 10, k=kk), hl(377, xm, CR - 20, k=kk), hl(b, xm, CR + 10, k=kk),
            o([(CL + 70, 220), (xm, 220)], k=kk, caps=(along(lA), 'f'))])
    cxO, cyO, rxO, ryO = K.bowl(CL - 30, xm + 80, -osc, CAP + osc)
    S('Œ', [ring(cxO, cyO, rxO, ryO, k=kk), vl(xm + 20, 0, CAP, k=kk), hl(T, xm + 20, CR + 20, k=kk),
            hl(377, xm + 20, CR, k=kk), hl(b, xm + 20, CR + 20, k=kk)])
    G['æ'] = merge(sub('a', 0.56, 1, 16, 0, kk), dict(s=e.e_strokes(272, 560, kk), p=[]))
    G['œ'] = merge(sub('o', 0.56, 1, 6, 0, kk), dict(s=e.e_strokes(272, 560, kk), p=[]))
    S('µ', [vl(xl, DSC, XH), o([(xl, XH)] + se(xl + rx, yb + ra, rx, ra, 180, 360, tp(None, 1))), vl(xr, 0, XH)])
    G['ª'] = merge(sub('a', 0.62, 0.62, 120, 380, min(0.78, 64 / w)), dict(s=[hl(290, 160, 440, k=min(0.78, 64 / w))], p=[]))
    G['º'] = merge(sub('o', 0.62, 0.62, 114, 380, min(0.78, 70 / w)), dict(s=[hl(290, 160, 440, k=min(0.78, 70 / w))], p=[]))

    # ------------------------------------------------------------ figures: superiors and fractions
    # small figures and letters: the pen stops growing, or their counters close in Bold
    kf_ = min(0.78, 70 / w)

    def fig(ch, s, dx, dy, k=kf_):
        return sub(ch, s, s, dx, dy, k)
    for ch, f_ in (('¹', '1'), ('²', '2'), ('³', '3')):
        G[ch] = fig(f_, 0.56, W / 2 - 0.56 * W / 2, 340)
    G['²'] = dict(s=e.two(W / 2 - 0.56 * (W / 2 - e.FL), W / 2 + 0.56 * (e.FR - W / 2), 340, 340 + 0.56 * CAP, kf_), p=[])
    slash = dict(s=[D((90, 0), (510, CAP), (0, 0, W, CAP), k=0.8)], p=[])
    for ch, (n, d) in (('¼', ('1', '4')), ('½', ('1', '2')), ('¾', ('3', '4'))):
        kq = min(0.72, 60 / w)
        den = dict(s=e.two(290 + 0.44 * e.FL, 290 + 0.44 * e.FR, 0, 0.44 * CAP, kq), p=[]) if d == '2' else fig(d, 0.44, 290, 0, kq)
        G[ch] = merge(fig(n, 0.44, -10, 380, kq), den, slash)
    G['⁄'] = dict(s=[D((60, 0), (540, CAP), (0, 0, W, CAP))], p=[])

    # ------------------------------------------------------------ currency
    cx, cy, rx_, ry_ = K.bowl(OL + 20, OR - 20, -osl - 10, XH + osl + 10)
    S('¢', [o(se(cx, cy + 90, rx_, ry_, K.term(rx_, ry_, 0), K.term(rx_, ry_, 3), fin(0, 1))), vl(W / 2 + 10, -60, XH + 230)])
    hs, rxl = 190, 150
    S('£', [o(se(hs + rxl, T - 170, rxl, 170, 26, 180) + [(hs, b)]), hl(b, 110, 500), hl(330, 110, 380)])
    yY = 330
    S('¥', [DD((CL - 10, CAP), (W / 2, yY), 1, None, (0, 0, W, CAP)), DD((CR + 10, CAP), (W / 2, yY), -1, None, (0, 0, W, CAP)),
            vl(W / 2, 0, yY + a), hl(yY - 10, 150, 450, k=0.9), hl(yY - 160, 150, 450, k=0.9)])
    cxe, cye, rxe, rye = K.bowl(CL + 40, CR + 20, -osc, CAP + osc)
    S('€', [o(se(cxe, cye, rxe, rye, K.term(rxe, rye, 0), K.term(rxe, rye, 3))), hl(410, 40, 360, k=0.9), hl(270, 40, 340, k=0.9)])
    S('₹', [hl(T, 100, 500), hl(T - 150, 100, 500),
            o([(100, T), (250, T)] + se(250, T - 150, 170, 150, 90, -90) + [(120, T - 300)]),
            D((150, T - 300), (450, 0), (0, 0, W, CAP), caps=('f', ('y', 0)))])
    cr, rc = 300, 140
    kc_ = min(1.0, 84 / w)                        # the ring keeps a real counter in Bold
    S('¤', [ring(cr, MATH, rc - a * kc_, rc - b * kc_, k=kc_)] +
      [D((cr + sx * (rc + 50), MATH + sy * (rc + 50)), (cr + sx * rc * 0.55, MATH + sy * rc * 0.55), k=kc_) for sx in (-1, 1) for sy in (-1, 1)])

    # ------------------------------------------------------------ signs
    S('¦', [vl(W / 2, BR_B, 250), vl(W / 2, 430, BR_T)])
    # §: an S-curve and the same curve turned half round, overlapping in the middle (a squashed s tightened its
    # curves until they stepped)
    yt_s, yb_s = CAP + osc - b, 130
    ym_s = (yt_s + yb_s) / 2 + 10
    ur, lr = (yt_s - ym_s) / 2, (ym_s - yb_s) / 2
    urx, lrx = 160 - a, 168 - a
    sp_ = se(W / 2, ym_s + ur, urx, ur, K.term(urx, ur, 0), 270) + se(W / 2, ym_s - lr, lrx, lr, 90, K.term(lrx, lr, 2) - 360)[1:]
    upper = dict(s=[o(sp_)], p=[])
    G['§'] = merge(upper, tf(upper, -1, -1, W, yt_s + yb_s - (yt_s - yb_s) / 2))      # the turned copy sits one bowl lower
    kr_ = min(0.8, 92 / w)                           # the ring stops growing, so R and C keep room inside it in Bold
    rR = 280 - a * kr_
    S('©', [ring(W / 2, 360, rR, rR + 20, k=kr_),
            o(se(W / 2, 360, 120 - a * 0.7, 140 - b * 0.7, K.term(120, 140, 0), K.term(120, 140, 3)), k=0.7)])
    kR = min(0.66, 58 / w)
    S('®', [ring(W / 2, 360, rR, rR + 20, k=kr_), vl(225, 190, 530, k=kR),
            o([(225, 530 - b * kR), (325, 530 - b * kR)] + se(325, 455, 75, 75 - b * kR, 90, -90) + [(225, 380)], k=kR),
            D((330, 380), (400, 190), (0, 190, W, 530), k=kR)])
    kd_ = min(0.8, 60 / w)
    S('°', [ring(W / 2, CAP - 126, 126 - a * kd_, 126 - b * kd_, k=kd_)])
    S('±', [hl(MATH + 60, 86, 514), vl(W / 2, MATH - 140, MATH + 260), hl(MATH - 220, 86, 514)])
    S('×', [D((150, MATH - 150), (450, MATH + 150)), D((150, MATH + 150), (450, MATH - 150))])
    S('÷', [hl(MATH, 80, 520)], [dot(W / 2, MATH + 200, rd * 0.95), dot(W / 2, MATH - 200, rd * 0.95)])     # as wide as + and =
    S('¬', [o([(100, MATH + 80), (500 - a, MATH + 80), (500 - a, MATH - 110)])])
    S('−', [hl(MATH, 80, 520)])
    S('«', [o([(300, MATH + 170), (140, MATH), (300, MATH - 170)], k=0.95), o([(490, MATH + 170), (330, MATH), (490, MATH - 170)], k=0.95)])
    S('»', [o([(110, MATH + 170), (270, MATH), (110, MATH - 170)], k=0.95), o([(300, MATH + 170), (460, MATH), (300, MATH - 170)], k=0.95)])
    S('‹', [o([(390, MATH + 170), (230, MATH), (390, MATH - 170)], k=0.95)])
    S('›', [o([(210, MATH + 170), (370, MATH), (210, MATH - 170)], k=0.95)])
    S('†', [vl(W / 2, -150, CAP + 20), hl(CAP - 200, 140, 460)])
    S('‡', [vl(W / 2, -150, CAP + 20), hl(CAP - 200, 140, 460), hl(60, 140, 460)])
    S('•', [], [dot(W / 2, MATH, 120 + 0.2 * dw)])
    S('′', [D((W / 2 - 30, 470), (W / 2 + 40, CAP + 20), k=0.9)])
    S('″', [D((W / 2 - 120, 470), (W / 2 - 50, CAP + 20), k=0.9), D((W / 2 + 60, 470), (W / 2 + 130, CAP + 20), k=0.9)])
    # ¶: a filled bowl on two stems
    yb6 = CAP - 340
    S('¶', [vl(330, -120, CAP), vl(470, -120, CAP), hl(T, 200, 470)],
      [K.fill(se(330, (T + yb6) / 2, 220, (T - yb6) / 2 + b, 90, 270) + [(330 + a, yb6 - b), (330 + a, T + b)])])
    kp = min(0.7, 62 / w)
    pr = 80
    pr = 72
    S('‰', [ring(125, CAP + osc - 120, pr - a * kp, 120 - b * kp, k=kp), ring(345, 120 - osc, pr - a * kp, 120 - b * kp, k=kp),
            ring(510, 120 - osc, pr - a * kp, 120 - b * kp, k=kp), DD((170, 0), (470, CAP), 1, -1, (0, 0, W, CAP), k=0.8)])
    S('™', [hl(CAP - b * 0.7, 20, 230, k=0.7), vl(125, 400, CAP, k=0.7), vl(315, 400, CAP, k=0.7), vl(570, 400, CAP, k=0.7),
            D((315, CAP), (442, 470), (0, 470, W, CAP), k=0.62), D((570, CAP), (442, 470), (0, 470, W, CAP), k=0.62)])

    # ------------------------------------------------------------ maths
    S('≤', [o([(490, MATH + 270), (120, MATH + 100), (490, MATH - 70)]), hl(MATH - 230, 110, 490)])
    S('≥', [o([(110, MATH + 270), (480, MATH + 100), (110, MATH - 70)]), hl(MATH - 230, 110, 490)])
    G['≈'] = merge(tf(G['~'], 1, 1, 0, 90), tf(G['~'], 1, 1, 0, -90))
    S('≠', [hl(MATH - 112, 86, 514), hl(MATH + 112, 86, 514), D((200, MATH - 260), (400, MATH + 260))])
    ki_ = min(0.85, 94 / w)                          # a pen that stops growing: the loops filled in in Bold
    S('∞', [ring(192, MATH, 122 - a * ki_, 98 - b * ki_, k=ki_), ring(408, MATH, 122 - a * ki_, 98 - b * ki_, k=ki_)])    # the loops overlap
    S('√', [o([(50, MATH + 20), (150, MATH + 60), (290, -20), (540, BR_T)])])
    rt = 110
    S('∫', [o(se(300 + rt, BR_T - b - rt, rt, rt, 15, 180) + se(300 - rt, BR_B + b + rt, rt, rt, 0, -165))])
    S('∂', [ring(*K.bowl(OL, OR - 20, -osc, 0.66 * CAP + osc)),
            o(se(W / 2 - 40, 0.33 * CAP, OR - 20 - a - (W / 2 - 40), CAP + osc - b - 0.33 * CAP, 0, 140, fin(None, 1)))])
    S('∆', [K.closed([(CL - 10, b), (W / 2, CAP - a), (CR + 10, b)])])
    S('∏', [hl(T, 50, 550), vl(150, BR_B, T), vl(450, BR_B, T)])
    S('∑', [hl(T, 90, 510), hl(BR_B + b, 90, 520), o([(110, T), (330, 300), (110, BR_B + b)])])
    S('◊', [K.closed([(W / 2, b + 10), (500, CAP / 2), (W / 2, CAP - b - 10), (100, CAP / 2)], k=0.9)])
    arc = se(W / 2, 400, 250 - a, 300 - b, -40, 220)
    S('Ω', [o([(CR + 20, b), (arc[0].x + 20, b)] + arc + [(arc[-1].x - 20, b), (CL - 20, b)])])

    import cells
    cells.extend(G, K, env)
