"""Saguna Mono outline engine: skeletons + an elliptical pen -> quadratic contours.

Ported from Dimple Sans (shape.py), rounded mode only. Every glyph is a spec: dict(s=[Stroke...],
p=[Fill...]). A Stroke is a skeleton (corner points and superelliptic curve samples) drawn with an
elliptical pen: half-width a = w/2 across vertical strokes, b = CONTRAST * a across horizontal ones.
Each node may scale the pen (k). The point structure of every contour depends only on the skeleton,
never on the weight, so the masters of the weight axis are compatible; cap corners and outer mitres
become quadratic arcs with fixed point counts.
"""

import math

from types import SimpleNamespace

CONTRAST = 0.84       # bar thickness / stem thickness: a mono reads best with gentle contrast

# One optical size: the parameters the engine reads (see Dimple Sans for the axis version).
OPSZ = {14: dict(dw=0, sp=1.0, os=1.0, dot=1.0, con=0.0, phi=0.0, kern=1.0)}
OPSZ_DEFAULT = 14
STYLE = SimpleNamespace(opsz=OPSZ_DEFAULT, skew=0.0)     # skew: tan of the italic angle while an italic master is drawn


def P(name):
    """The optical-size parameter for the master being drawn."""
    return OPSZ[STYLE.opsz][name]


def contrast(w):
    """Bar/stem ratio: rises a little towards Light, where bars would turn to hairlines on screen."""
    return CONTRAST + 0.003 * max(0.0, min(20.0, 80 - w)) - 0.0008 * max(0.0, w - 80)
TILT = 0.0            # pen angle (degrees): upright stress, as a mono wants


def pen_half(a, b, nx, ny):
    """Half the stroke width across unit normal n for the tilted elliptical pen."""
    c, s = math.cos(math.radians(TILT)), math.sin(math.radians(TILT))
    ux, uy = nx * c + ny * s, -nx * s + ny * c
    return math.sqrt((a * ux) ** 2 + (b * uy) ** 2) or 1e-9
MITRE = 3.2           # mitre length limit, in pen half-widths
MAXSTEP = 15.0        # degrees per quadratic piece on a superellipse
INNER = 0.44                      # corner radius (x stem) on the inside of a bent round end: full, so the edge runs round without a tooth
ROUND_LO, ROUND_HI = 0.26, 0.985   # end tangents between about 15 and 80 degrees from horizontal
EXP = 2.6             # superellipse exponent: squarish, flat-sided rounds


class N:
    """A curve sample: position, unit tangent (direction of travel), pen scale."""
    __slots__ = ('x', 'y', 'tx', 'ty', 'k')

    def __init__(self, x, y, tx, ty, k=1.0):
        self.x, self.y, self.tx, self.ty, self.k = x, y, tx, ty, k

    def __getitem__(self, i):
        return (self.x, self.y)[i]

    def __iter__(self):
        return iter((self.x, self.y))

    def __len__(self):
        return 2


class Plan:
    """Keeps arc subdivisions identical across masters.

    Terminal angles depend slightly on the weight, so the number of quadratic pieces on
    an arc could differ between masters. The Regular master records the piece counts
    of every arc in drawing order; the other masters replay them."""
    mode = None
    seq = {}
    key = None
    i = 0

    @classmethod
    def start(cls, key, mode):
        cls.key, cls.mode, cls.i = key, mode, 0
        if mode == 'record':
            cls.seq[key] = []

    @classmethod
    def stop(cls):
        cls.mode = None


def _angles(a0, a1):
    sgn = 1 if a1 >= a0 else -1
    lo, hi = min(a0, a1), max(a0, a1)
    inner = []
    m = math.floor(lo / 90) * 90 + 90
    while m < hi - 1e-6:
        if m > lo + 1e-6:
            inner.append(m)
        m += 90
    if sgn < 0:
        inner.reverse()
    marks = [a0] + inner + [a1]
    counts = [max(1, math.ceil(abs(q - p) / MAXSTEP - 1e-9)) for p, q in zip(marks, marks[1:])]
    if Plan.mode == 'record':
        Plan.seq[Plan.key].append(counts)
    elif Plan.mode == 'replay':
        rec = Plan.seq[Plan.key][Plan.i]
        Plan.i += 1
        if len(rec) != len(counts):
            raise ValueError(f'arc {a0:.1f}..{a1:.1f} crosses a quadrant differently from the Regular master')
        counts = rec
    out = [marks[0]]
    for (p, q), n in zip(zip(marks, marks[1:]), counts):
        out += [p + (q - p) * i / n for i in range(1, n + 1)]
    return out


def se_point(cx, cy, rx, ry, deg):
    p = 2 / EXP
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    return (cx + rx * math.copysign(abs(c) ** p, c), cy + ry * math.copysign(abs(s) ** p, s))


def se_tangent(rx, ry, deg, sgn=1):
    p = 2 / EXP
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    ac, as_ = max(abs(c), 1e-7), max(abs(s), 1e-7)
    dx = -rx * p * ac ** (p - 1) * s
    dy = ry * p * as_ ** (p - 1) * c
    L = math.hypot(dx, dy) or 1.0
    return dx / L * sgn, dy / L * sgn


def se(cx, cy, rx, ry, a0, a1, k=None):
    """Superellipse arc from angle a0 to a1 (degrees) as curve nodes.

    k: None, a number, or f(fraction along the arc) -> pen scale."""
    sgn = 1 if a1 >= a0 else -1
    out = []
    for a in _angles(a0, a1):
        x, y = se_point(cx, cy, rx, ry, a)
        tx, ty = se_tangent(rx, ry, a, sgn)
        f = (a - a0) / (a1 - a0) if a1 != a0 else 0
        kk = k(f) if callable(k) else (1.0 if k is None else k)
        out.append(N(x, y, tx, ty, kk))
    return out


def slope_angle(rx, ry, q0, q1, phi):
    """The angle within [q0, q1] (inside one quadrant) where the tangent is phi degrees
    from horizontal. Terminals end where the stroke runs at the same slope, so every
    terminal cut has the same angle."""
    def f(a):
        tx, ty = se_tangent(rx, ry, a)
        return math.degrees(math.atan2(abs(ty), abs(tx))) - phi
    lo, hi = q0, q1
    flo = f(lo)
    for _ in range(50):
        mid = (lo + hi) / 2
        fm = f(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return (lo + hi) / 2


class Stroke:
    def __init__(self, items, caps=('f', 'f'), k=1.0, clip=None, closed=False):
        self.items = list(items)
        self.caps = list(caps)
        self.k = k
        self.clip = clip
        self.closed = closed

    def tf(self, sx, sy, dx, dy, kk):
        def P(it):
            if isinstance(it, N):
                tx, ty = it.tx * sx, it.ty * sy
                L = math.hypot(tx, ty) or 1
                return N(it.x * sx + dx, it.y * sy + dy, tx / L, ty / L, it.k)
            if len(it) == 3:
                return (it[0] * sx + dx, it[1] * sy + dy, it[2])
            return (it[0] * sx + dx, it[1] * sy + dy)

        def C(c):
            if isinstance(c, tuple) and c[0] == 'L':
                return ('L', c[1] * sx + dx, c[2] * sy + dy, c[3] * sx, c[4] * sy) + c[5:]
            if isinstance(c, tuple):
                return ((c[0], c[1] * sx + dx) if c[0] == 'x' else (c[0], c[1] * sy + dy)) + c[2:]
            return c
        clip = None
        if self.clip:
            a = (self.clip[0] * sx + dx, self.clip[1] * sy + dy)
            b = (self.clip[2] * sx + dx, self.clip[3] * sy + dy)
            clip = (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))
        return Stroke([P(i) for i in self.items], [C(c) for c in self.caps], self.k * kk, clip, self.closed)


class Fill:
    """A filled shape from corner points and/or curve nodes (diamonds, the pilcrow bowl)."""

    def __init__(self, items):
        self.items = list(items)

    def tf(self, sx, sy, dx, dy, kk):
        return Fill(Stroke(self.items).tf(sx, sy, dx, dy, 1).items)


def tf(spec, sx=1.0, sy=1.0, dx=0.0, dy=0.0, k=1.0):
    return dict(s=[s.tf(sx, sy, dx, dy, k) for s in spec['s']], p=[p.tf(sx, sy, dx, dy, k) for p in spec['p']])


def merge(*specs):
    return dict(s=[x for sp in specs for x in sp['s']], p=[x for sp in specs for x in sp['p']])


def _unit(x, y):
    L = math.hypot(x, y)
    return (x / L, y / L) if L > 1e-12 else (1.0, 0.0)


def _cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def _isect(p, d, q, e):
    den = _cross(d, e)
    if abs(den) < 1e-9:
        return None
    w = (q[0] - p[0], q[1] - p[1])
    s = _cross(w, e) / den
    t = _cross(w, d) / den
    return (p[0] + s * d[0], p[1] + s * d[1]), s, t


class Pen:
    def __init__(self, w, rounded=False):
        self.a = w / 2
        self.b = w / 2 * contrast(w)
        self.w = w
        self.rounded = rounded
        self.r = 0.36 * w

    def off(self, t, k):
        """Left offset for unit tangent t: along the normal, by the pen's half-width there."""
        nx, ny = -t[1], t[0]
        h = pen_half(self.a * k, self.b * k, nx, ny)
        return (nx * h, ny * h)

    def nodes(self, st):
        nodes, segs = [], []
        for it in st.items:
            if isinstance(it, N):
                x, y, tan, k, cur = it.x, it.y, (it.tx, it.ty), it.k * st.k, True
            else:
                x, y = it[0], it[1]
                k = (it[2] if len(it) == 3 else 1.0) * st.k
                tan, cur = None, False
            if nodes and math.hypot(x - nodes[-1][0], y - nodes[-1][1]) < 0.5:
                if cur and not nodes[-1][4]:
                    nodes[-1][2], nodes[-1][3], nodes[-1][4] = tan, k, True
                continue
            if nodes:
                segs.append('q' if (cur and nodes[-1][4]) else 'l')
            nodes.append([x, y, tan, k, cur])
        if st.closed:
            if math.hypot(nodes[0][0] - nodes[-1][0], nodes[0][1] - nodes[-1][1]) < 0.5:
                nodes.pop()
                segs.pop()
            segs.append('q' if (nodes[-1][4] and nodes[0][4]) else 'l')
        n = len(nodes)
        tin, tout = [None] * n, [None] * n
        for i in range(n):
            P = nodes[i]
            if i > 0 or st.closed:
                j = (i - 1) % n
                tin[i] = P[2] if (segs[j] == 'q' and P[2]) else _unit(P[0] - nodes[j][0], P[1] - nodes[j][1])
            if i < n - 1 or st.closed:
                j = (i + 1) % n
                tout[i] = P[2] if (segs[i] == 'q' and P[2]) else _unit(nodes[j][0] - P[0], nodes[j][1] - P[1])
        if not st.closed:
            tin[0] = tout[0]
            tout[-1] = tin[-1]
        return nodes, segs, tin, tout

    def otan(self, t, k, turn, grow, s):
        """Unit tangent of the offset curve where the skeleton runs along t. The pen's half-width
        changes with direction (tilted ellipse) and scale, so the offset edge does not run parallel
        to the skeleton: turn (radians per unit length) and grow (pen scale per unit length) say
        how fast those change here."""
        e = 1e-4
        c, sn = math.cos(e), math.sin(e)
        o1 = self.off((t[0] * c - t[1] * sn, t[0] * sn + t[1] * c), k)
        o0 = self.off((t[0] * c + t[1] * sn, -t[0] * sn + t[1] * c), k)
        ok1, ok0 = self.off(t, k + e), self.off(t, k - e)
        dx = t[0] + s * ((o1[0] - o0[0]) / (2 * e) * turn + (ok1[0] - ok0[0]) / (2 * e) * grow)
        dy = t[1] + s * ((o1[1] - o0[1]) / (2 * e) * turn + (ok1[1] - ok0[1]) / (2 * e) * grow)
        if dx * t[0] + dy * t[1] <= 0.05:          # the edge would fold back (a cusp): keep the skeleton's direction
            return t
        return _unit(dx, dy)

    def rates(self, nodes, segs, tin, tout, closed):
        """Per node: how fast the skeleton turns and the pen scale changes, averaged over the
        curve pieces on either side, so both pieces leave the node along the same offset tangent."""
        n = len(nodes)
        seg = {}
        for i in range(n if closed else n - 1):
            if segs[i] != 'q':
                continue
            j = (i + 1) % n
            L = math.hypot(nodes[j][0] - nodes[i][0], nodes[j][1] - nodes[i][1]) or 1.0
            da = math.atan2(_cross(tout[i], tin[j]), tout[i][0] * tin[j][0] + tout[i][1] * tin[j][1])
            seg[i] = (da / L, (nodes[j][3] - nodes[i][3]) / L)
        out = []
        for i in range(n):
            near = [seg[x] for x in ((i - 1) % n, i) if x in seg and (x == i or i > 0 or closed)]
            out.append((sum(r[0] for r in near) / len(near), sum(r[1] for r in near) / len(near)) if near else (0.0, 0.0))
        return out, seg

    def side(self, nodes, segs, tin, tout, s, closed):
        """One offset side (s=+1 left, -1 right): (x, y, on, flag, din, dout)."""
        pts = []
        n = len(nodes)
        rate, seg = self.rates(nodes, segs, tin, tout, closed)

        def smooth(i):          # the node joins two curve pieces along one tangent
            return seg.get((i - 1) % n) is not None and (i > 0 or closed) and i in seg and abs(_cross(tin[i], tout[i])) < 2e-3
        for i in range(n):
            P = (nodes[i][0], nodes[i][1])
            k = nodes[i][3]
            oi, oo = self.off(tin[i], k), self.off(tout[i], k)
            Si = (P[0] + s * oi[0], P[1] + s * oi[1])
            So = (P[0] + s * oo[0], P[1] + s * oo[1])
            cr = _cross(tin[i], tout[i])
            dot = tin[i][0] * tout[i][0] + tin[i][1] * tout[i][1]
            if abs(cr) < 2e-3 and dot > 0:
                pts.append((So[0], So[1], True, None, tin[i], tout[i]))
            else:
                r = _isect(Si, tin[i], So, tout[i])
                X = r[0] if r else ((Si[0] + So[0]) / 2, (Si[1] + So[1]) / 2)
                d = math.hypot(X[0] - P[0], X[1] - P[1])
                lim = MITRE * self.a * k
                if d > lim:
                    X = (P[0] + (X[0] - P[0]) * lim / d, P[1] + (X[1] - P[1]) * lim / d)
                pts.append((X[0], X[1], True, 'outer' if s * cr < 0 else 'inner', tin[i], tout[i]))
            if (i < n - 1 or closed) and segs[i] == 'q':
                j = (i + 1) % n
                Q = (nodes[j][0], nodes[j][1])
                oq = self.off(tin[j], nodes[j][3])
                A_ = So
                B_ = (Q[0] + s * oq[0], Q[1] + s * oq[1])
                ra = rate[i] if smooth(i) else seg[i]
                rb = rate[j] if smooth(j) else seg[i]
                ta = self.otan(tout[i], nodes[i][3], ra[0], ra[1], s)
                tb = self.otan(tin[j], nodes[j][3], rb[0], rb[1], s)
                r = _isect(A_, ta, B_, tb)
                chord = math.hypot(B_[0] - A_[0], B_[1] - A_[1])
                if r and 0 < r[1] < 1.2 * chord + 1 and -1.2 * chord - 1 < r[2] < 0:
                    C = r[0]
                else:
                    C = ((A_[0] + B_[0]) / 2, (A_[1] + B_[1]) / 2)
                pts.append((C[0], C[1], False, None, None, None))
        return pts

    def cap(self, P, t, k, kind, s):
        o = self.off(t, k)
        S = (P[0] + s * o[0], P[1] + s * o[1])
        if kind in ('f', 'F', 'FJ', None):
            return S
        if kind[-1] in ('J', 'JL', 'JR'):   # a joined end: same cut, not rounded (JL / JR: only that side's corner)
            kind = kind[:-1]
        if kind[0] == 'L':
            # cut along a line (another stroke's centre line): the corners hide inside it
            _, px, py, ldx, ldy = kind
            den = _cross(t, (ldx, ldy))
            if abs(den) < 1e-6:
                return S
            u = _cross((px - S[0], py - S[1]), (ldx, ldy)) / den
            u = max(-6 * self.a, min(6 * self.a, u))
            return (S[0] + u * t[0], S[1] + u * t[1])
        axis, v = kind
        comp = t[1] if axis == 'y' else t[0]
        if abs(comp) < 0.08:
            return S
        u = (v - (S[1] if axis == 'y' else S[0])) / comp
        u = max(-6 * self.a, min(6 * self.a, u))
        return (S[0] + u * t[0], S[1] + u * t[1])

    def clip_caps(self, st, nodes, tin, tout):
        caps = list(st.caps)
        if not st.clip:
            return caps
        x0, y0, x1, y1 = st.clip
        for end in (0, 1):
            if caps[end] not in ('f', None):
                continue
            i = 0 if end == 0 else -1
            P = (nodes[i][0], nodes[i][1])
            d = (-tout[0][0], -tout[0][1]) if end == 0 else tin[-1]
            best = None
            for axis, val in (('x', x0), ('x', x1), ('y', y0), ('y', y1)):
                comp = d[0] if axis == 'x' else d[1]
                if abs(comp) < 1e-6:
                    continue
                u = (val - (P[0] if axis == 'x' else P[1])) / comp
                if u < -1e-6:
                    continue
                if best is None or u < best[0]:
                    best = (u, axis, val)
            if best and best[0] <= 0.6 * self.w:
                caps[end] = (best[1], best[2])
        return caps

    def stroke(self, st):
        nodes, segs, tin, tout = self.nodes(st)
        if st.closed:
            return [self.finish(self.side(nodes, segs, tin, tout, 1, True)),
                    self.finish(self.side(nodes, segs, tin, tout, -1, True))]
        caps = self.clip_caps(st, nodes, tin, tout)
        L = self.side(nodes, segs, tin, tout, 1, False)
        R = self.side(nodes, segs, tin, tout, -1, False)
        P0, P1 = (nodes[0][0], nodes[0][1]), (nodes[-1][0], nodes[-1][1])
        k0, k1 = nodes[0][3], nodes[-1][3]
        t0, t1 = tout[0], tin[-1]
        l0, r0 = self.cap(P0, t0, k0, caps[0], 1), self.cap(P0, t0, k0, caps[0], -1)
        l1, r1 = self.cap(P1, t1, k1, caps[1], 1), self.cap(P1, t1, k1, caps[1], -1)
        n_l = len(L)
        L[0] = (l0[0], l0[1], True, 'cap0', None, t0)
        L[-1] = (l1[0], l1[1], True, 'cap1', t1, None)
        R[0] = (r0[0], r0[1], True, 'cap0', None, t0)
        R[-1] = (r1[0], r1[1], True, 'cap1', t1, None)
        # the right side is walked backwards: its corner directions reverse too
        R = [(p[0], p[1], p[2], p[3], (-p[5][0], -p[5][1]) if p[5] else None, (-p[4][0], -p[4][1]) if p[4] else None)
             for p in R]
        ring = L + R[::-1]
        if not self.rounded:
            return [[(p[0], p[1], p[2]) for p in ring]]
        n = len(ring)
        corners = {}
        for i, p in enumerate(ring):
            if p[3] in ('cap0', 'cap1'):
                mark = (caps[0 if p[3] == 'cap0' else 1] or 'f')[-1]
                left = i in (0, n_l - 1)          # this corner is on the stroke's left side (s = +1)
                if mark == 'J' or (mark == 'JL' and left) or (mark == 'JR' and not left):
                    continue
            if p[3] in ('cap0', 'cap1'):
                if i == n_l - 1:      # left end -> across end cap
                    d1, d2 = t1, _unit(ring[i + 1][0] - p[0], ring[i + 1][1] - p[1])
                elif i == n_l:        # right end -> back along right side
                    d1, d2 = _unit(p[0] - ring[i - 1][0], p[1] - ring[i - 1][1]), (-t1[0], -t1[1])
                elif i == n - 1:      # right start -> across start cap
                    d1, d2 = (-t0[0], -t0[1]), _unit(ring[0][0] - p[0], ring[0][1] - p[1])
                else:                 # left start -> along left side
                    d1, d2 = _unit(p[0] - ring[-1][0], p[1] - ring[-1][1]), t0
                end = caps[0 if p[3] == 'cap0' else 1]
                t = t0 if p[3] == 'cap0' else t1
                # a free end cut across a slanted stroke is fully round: a squared-off corner
                # on a diagonal reads as a beak or nick, so only vertical and horizontal cuts keep one
                full = end in ('f', None) and ROUND_LO < abs(t[1]) < ROUND_HI
                lo_, ro_ = (l0, r0) if p[3] == 'cap0' else (l1, r1)
                rr = 0.49 * math.hypot(lo_[0] - ro_[0], lo_[1] - ro_[1]) if full else 0.0
                if full:                  # the corner on the inside of the bend stays tight, so the edge doesn't swell into an S
                    if p[3] == 'cap1':
                        left_inner = _cross(tout[-2], t1) > 0
                        inner = (i == n_l - 1) == left_inner
                    else:
                        left_inner = _cross(t0, tout[1]) > 0
                        inner = (i == 0) == left_inner
                    if inner:     # never past the middle of the cap: the two corners' trims would cross
                        rr = min(INNER * self.w, rr)
                corners[i] = (d1, d2, rr)
            elif p[3] == 'outer':
                corners[i] = (p[4], p[5], False)
        return [self._assemble(ring, corners)]

    def finish(self, pts):
        if not self.rounded:
            return [(p[0], p[1], p[2]) for p in pts]
        return self._assemble(pts, {i: (p[4], p[5], False) for i, p in enumerate(pts) if p[3] == 'outer'})

    def _assemble(self, ring, corners):
        """The ring with its corners rounded. A corner that follows or precedes a curve is
        rounded from the curve's own trimmed end (an exact sub-curve with the same tangent),
        so the round starts on the curve and no kink or nick is left where they meet."""
        n = len(ring)
        r = {}
        for i, c in corners.items():
            p, prv, nxt = ring[i], ring[(i - 1) % n], ring[(i + 1) % n]
            # a neighbouring curve is measured by its chord (it is trimmed exactly), a line by its length
            pv = prv if prv[2] else ring[(i - 2) % n]
            nx = nxt if nxt[2] else ring[(i + 2) % n]
            l1 = math.hypot(p[0] - pv[0], p[1] - pv[1])
            l2 = math.hypot(nx[0] - p[0], nx[1] - p[1])
            f1 = 0.48 if (prv[2] and prv[3] in ('cap0', 'cap1', 'outer')) else (0.85 if prv[2] else 0.5)
            f2 = 0.48 if (nxt[2] and nxt[3] in ('cap0', 'cap1', 'outer')) else (0.85 if nxt[2] else 0.5)
            r[i] = max(0.0, min(self.r, l1 * f1, l2 * f2))
            if c[2]:                  # a round end: the cap's two corners meet in the middle
                side = l1 if ring[(i + 1) % n][3] == ring[i][3] else l2    # the neighbour that is not the cap's other corner
                r[i] = max(0.0, min(c[2], 0.85 * side))
        ctrl, e_in, s_out = {}, {}, {}
        for j in range(n):
            if ring[j][2]:
                continue
            a, q = (j - 1) % n, (j + 1) % n
            S, C, E, tS, tE = _quad_trim(ring[a][:2], ring[j][:2], ring[q][:2], r.get(a, 0.0), r.get(q, 0.0))
            ctrl[j] = C
            if a in r:
                s_out[a] = (S, tS)
            if q in r:
                e_in[q] = (E, tE)
        out = []
        for i, p in enumerate(ring):
            if i in corners:
                d1, d2, _ = corners[i]
                E, tin = e_in.get(i, ((p[0] - d1[0] * r[i], p[1] - d1[1] * r[i]), d1))
                S, tout = s_out.get(i, ((p[0] + d2[0] * r[i], p[1] + d2[1] * r[i]), d2))
                X = (p[0], p[1])
                hit = _isect(E, tin, S, tout)
                if hit and hit[1] > -1e-6 and hit[2] < 1e-6 and math.hypot(hit[0][0] - p[0], hit[0][1] - p[1]) < 2.5 * r[i] + 1:
                    X = hit[0]
                out += [(E[0], E[1], True), (X[0], X[1], False), (S[0], S[1], True)]
            elif p[2]:
                out.append((p[0], p[1], True))
            else:
                out.append((ctrl[i][0], ctrl[i][1], False))
        return out

    def fill(self, f):
        st = Stroke(f.items, closed=True)
        nodes, segs, tin, tout = self.nodes(st)
        pts = []
        n = len(nodes)
        for i in range(n):
            P = (nodes[i][0], nodes[i][1])
            corner = abs(_cross(tin[i], tout[i])) > 2e-3
            pts.append((P[0], P[1], True, 'outer' if corner else None, tin[i], tout[i]))
            if segs[i] == 'q':
                j = (i + 1) % n
                Q = (nodes[j][0], nodes[j][1])
                r = _isect(P, tout[i], Q, tin[j])
                C = r[0] if r and r[1] > 0 and r[2] < 0 else ((P[0] + Q[0]) / 2, (P[1] + Q[1]) / 2)
                pts.append((C[0], C[1], False, None, None, None))
        return self.finish(pts)

    def glyph(self, spec):
        cs = []
        for st in spec['s']:
            parts = self.stroke(st)
            if len(parts) == 2:
                a0, a1 = abs(area(parts[0])), abs(area(parts[1]))
                outer, inner = (parts[0], parts[1]) if a0 >= a1 else (parts[1], parts[0])
                cs += [orient(outer, True), orient(inner, False)]
            else:
                cs.append(orient(parts[0], True))
        for f in spec['p']:
            cs.append(orient(self.fill(f), True))
        return cs


def _quad_trim(A, C, P, r0, r1):
    """The quadratic A-C-P with r0 trimmed off its start and r1 off its end (measured as
    straight distance): start, control, end, and the unit tangents at the new start and end."""
    def B(t):
        u = 1 - t
        return (u * u * A[0] + 2 * u * t * C[0] + t * t * P[0], u * u * A[1] + 2 * u * t * C[1] + t * t * P[1])

    def D(t):
        u = 1 - t
        return (2 * (u * (C[0] - A[0]) + t * (P[0] - C[0])), 2 * (u * (C[1] - A[1]) + t * (P[1] - C[1])))

    def solve(r, ref, rising):
        lo, hi = 0.0, 1.0
        for _ in range(40):
            m = (lo + hi) / 2
            q = B(m)
            d = math.hypot(q[0] - ref[0], q[1] - ref[1])
            if (d < r) == rising:
                lo = m
            else:
                hi = m
        return (lo + hi) / 2
    for _ in range(4):
        t0 = solve(r0, A, True) if r0 > 0 else 0.0
        t1 = solve(r1, P, False) if r1 > 0 else 1.0
        if t1 - t0 > 0.12:
            break
        r0, r1 = r0 * 0.6, r1 * 0.6
    else:
        t0, t1 = min(t0, 0.44), max(t1, 0.56)
    S, E, d0, d1 = B(t0), B(t1), D(t0), D(t1)
    ctrl = (S[0] + (t1 - t0) / 2 * d0[0], S[1] + (t1 - t0) / 2 * d0[1])
    return S, ctrl, E, _unit(*d0), _unit(*d1)


def area(pts):
    a = 0.0
    n = len(pts)
    for i in range(n):
        a += pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1]
    return a / 2


def orient(c, cw=True):
    """TrueType fills clockwise contours; holes run counter-clockwise."""
    if (area(c) < 0) != cw:
        c = c[::-1]
    for i, p in enumerate(c):
        if p[2]:
            return c[i:] + c[:i]
    return c


def flatten(contours, steps=6):
    out = []
    for c in contours:
        poly = []
        n = len(c)
        for i, p in enumerate(c):
            if p[2]:
                poly.append((p[0], p[1]))
            else:
                a, b = c[i - 1], c[(i + 1) % n]
                for j in range(1, steps):
                    t = j / steps
                    poly.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * p[0] + t * t * b[0],
                                 (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * p[1] + t * t * b[1]))
        out.append(poly)
    return out


def bounds(contours):
    pts = [q for poly in flatten(contours) for q in poly]
    if not pts:
        return (0.0, 0.0, 0.0, 0.0)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def band(contours, y0, y1):
    xs = []
    for poly in flatten(contours):
        n = len(poly)
        for i in range(n):
            (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n]
            if y0 <= ay <= y1:
                xs.append(ax)
            for yy in (y0, y1):
                if (ay - yy) * (by - yy) < 0:
                    xs.append(ax + (bx - ax) * (yy - ay) / (by - ay))
    return (min(xs), max(xs)) if xs else None
