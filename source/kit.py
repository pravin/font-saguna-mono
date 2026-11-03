"""Drawing vocabulary for Saguna Mono, for one stem weight w.

The vertical and horizontal system, the pen, overshoot, terminal angle and the stroke helpers live
here, so every glyph module draws with the same hand. Units are 1/1000 em.
"""

import math

from pen import P, STYLE, Fill, N, Stroke, contrast, merge, pen_half, se, slope_angle, tf

CAP, XH, ASC, DSC = 710, 540, 760, -225   # x-height and caps as tall as JetBrains Mono's, relative to the cell
W = 600               # the cell: every glyph has this advance
TOP, BOT = 980, -260  # the line (typo ascender/descender): box drawing fills it exactly; accents fit under TOP
MATH = 352            # the maths axis: + - = < > and arrows, and the hyphen, so -> and => line up
PHI = 64.0            # bowl terminals stop where the stroke runs at this slope: steep enough that c C e s reach well round (at 40 the
                      # squarish rounds cut them off early and c read as a bracket)
PHI_LONG = 68.0       # the longer terminals of 2 5 6 9 (S and $ run on further, to the sides of their bowls): they curl further round, so the figures look complete


class Kit:
    def __init__(self, w):
        self.w = w
        self.a = w / 2                     # half stem (vertical strokes)
        self.b = w / 2 * contrast(w)       # half bar (horizontal strokes)
        self.os = (9 + 0.02 * w) * P('os')     # overshoot, lowercase
        self.osc = (10 + 0.02 * w) * P('os')    # overshoot, capitals and figures
        self.phi = PHI
        self.dr = 0.52 * w + 16               # round dot radius (i, j, full stop, colon): a little over the stem
        self.trap = 0.70 - 0.0026 * (w - 80)   # ink-trap pen scale where arches leave stems (deeper in Bold)
        self.dm = 0.52 * w + 16            # the dieresis dot radius
        self.kd = 0.96 * (1 - 0.0016 * max(w - 80, 0))   # pen scale of diagonals: thinner in Bold, where a mono's v w x y k M N clot

    # ------------------------------------------------------------ primitives
    def o(self, pts, k=1.0, clip=None, caps=('f', 'f')):
        return Stroke(pts, caps=caps, k=k, clip=clip)

    def vl(self, x, y0, y1, k=1.0, caps=('f', 'f')):
        return Stroke([(x, y0), (x, y1)], k=k, caps=caps)

    def hl(self, y, x0, x1, k=1.0, caps=('f', 'f')):
        """A bar. An end hidden inside a stem takes the cap 'FJ': unrounded, or its rounded corner and the stem's
        leave a 1-2 unit dent in the edge they share."""
        return Stroke([(x0, y), (x1, y)], k=k, caps=caps)

    @staticmethod
    def kskew(p, q, k):
        """Pen scale for a diagonal in an italic master. Shearing the drawing keeps a stroke's horizontal thickness,
        so a diagonal that is steepened by the slant grows thicker across its width and one that is flattened
        grows thinner (about 5% and 6% on a v): the pen is scaled by the change in the stroke's length."""
        if not STYLE.skew:
            return k
        dx, dy = q[0] - p[0], q[1] - p[1]
        L = math.hypot(dx, dy)
        if L < 1e-6:
            return k
        return k * min(1.12, max(0.88, math.hypot(dx + STYLE.skew * dy, dy) / L))

    def D(self, p, q, clip=None, e0=0.0, e1=0.0, k=None, caps=('f', 'f'), skewed=False):
        """A straight stroke; with a clip box its ends are cut along the box edges."""
        k = self.kd if k is None else k
        if not skewed:
            k = self.kskew(p, q, k)
        dx, dy = q[0] - p[0], q[1] - p[1]
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        return Stroke([(p[0] - ux * e0, p[1] - uy * e0), (q[0] + ux * e1, q[1] + uy * e1)], caps=caps, k=k, clip=clip)

    def hx(self, p, q, k=None, skewed=False):
        """Half the horizontal cross-section of a straight stroke from p to q."""
        k = self.kd if k is None else k
        if not skewed:
            k = self.kskew(p, q, k)
        dx, dy = q[0] - p[0], q[1] - p[1]
        L = math.hypot(dx, dy)
        nx, ny = -dy / L, dx / L
        perp = pen_half(self.a * k, self.b * k, nx, ny)
        return perp / max(abs(dy / L), 1e-6)

    def edge(self, e, other, side, k=None, skewed=False):
        """Centre-line point at height e[1] whose outer edge lies exactly on x = e[0].
        side=+1: the ink lies to the right of e (left edge on it); -1: to the left.
        Diagonals that meet a box edge or a stem then end flush, with no spur."""
        k = self.kd if k is None else k
        if not skewed:
            k = self.kskew(e, other, k)
        x = e[0] + side * self.a
        for _ in range(4):
            x = e[0] + side * self.hx((x, e[1]), other, k, skewed=True)
        return (x, e[1])

    def DD(self, p, q, sp=None, sq=None, clip=None, k=None, caps=('f', 'f')):
        """A diagonal whose ends, where sp/sq is given, are edge points: the stroke's
        outer edge (not its centre line) lands on them, so it ends flush with a stem,
        the side bearing box or another stroke."""
        k = self.kskew(p, q, self.kd if k is None else k)
        P, Q = p, q
        for _ in range(3):
            if sp:
                P = self.edge(p, Q, sp, k, skewed=True)
            if sq:
                Q = self.edge(q, P, sq, k, skewed=True)
        return self.D(P, Q, clip, k=k, caps=caps, skewed=True)

    @staticmethod
    def along(stroke):
        """A joined cap that cuts along another straight stroke's centre line (its corners
        hide inside that stroke, so the Rounded family leaves them sharp)."""
        (x0, y0), (x1, y1) = stroke.items[0], stroke.items[-1]
        return ('L', x0, y0, x1 - x0, y1 - y0, 'J')

    @staticmethod
    def J(cap):
        """Mark a cut cap as a join: hidden inside another stroke, never rounded."""
        return tuple(cap) + ('J',)

    @staticmethod
    def circle(cx, cy, r, a0, a1, step=15.0):
        """A circular arc from a0 to a1 (degrees) as curve nodes, in a fixed number of pieces (masters stay
        compatible). A circle's tightest radius is r; a superellipse's is 0.71 of its own."""
        n = max(2, math.ceil(abs(a1 - a0) / step))
        sg = 1 if a1 > a0 else -1
        out = []
        for i in range(n + 1):
            t = math.radians(a0 + (a1 - a0) * i / n)
            out.append(N(cx + r * math.cos(t), cy + r * math.sin(t), -math.sin(t) * sg, math.cos(t) * sg))
        return out

    def ring(self, cx, cy, rx, ry, k=1.0, kf=None):
        pts = se(cx, cy, rx, ry, 0, 360, kf)[:-1]
        return Stroke(pts, k=k, closed=True)

    def closed(self, pts, k=1.0):
        return Stroke(pts, k=k, closed=True)

    def dot(self, cx, cy, r=None):
        """A round dot: a filled circle drawn as curve nodes (a fixed number of pieces)."""
        r = self.dr if r is None else r
        return Fill(se(cx, cy, r, r, 0, 360)[:-1])

    def comma(self, cx, cy, r=None, turned=False, tail=None):
        """The comma: a round dot that runs out into a curved, tapering tail."""
        r = self.dr if r is None else r
        L = (1.5 * r + 46) if tail is None else tail
        top = se(cx, cy, r, r, -30, 200)
        pts = top + [(cx - 0.55 * r - 0.25 * L, cy - r - L)]
        if turned:
            pts = [N(2 * cx - p.x, 2 * cy - p.y, -p.tx, -p.ty, p.k) if isinstance(p, N) else (2 * cx - p[0], 2 * cy - p[1])
                   for p in pts]
        return Fill(pts)

    def wave(self, x0, x1, y, amp, n=8):
        """A tilde's wave from x0 to x1 about height y: one sine period as curve nodes (a fixed number), so it
        is a single smooth stroke with no joins to fold in Bold."""
        out = []
        for i in range(n + 1):
            t = i / n
            x = x0 + (x1 - x0) * t
            yy = y + amp * math.sin(2 * math.pi * t)
            dx, dy = (x1 - x0), amp * 2 * math.pi * math.cos(2 * math.pi * t)
            L = math.hypot(dx, dy)
            out.append(N(x, yy, dx / L, dy / L))
        return out

    def fill(self, pts):
        return Fill(pts)

    def spec(self, strokes=(), fills=()):
        return dict(s=list(strokes), p=list(fills))

    # ------------------------------------------------------------ geometry helpers
    def bowl(self, x0, x1, y0, y1):
        """Centre-line superellipse for a round whose outer ink spans the given box."""
        return ((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 - self.a, (y1 - y0) / 2 - self.b)

    def term(self, rx, ry, quadrant, phi=None):
        """Terminal angle on a bowl: where its tangent slope is PHI (or phi), in quadrant 0..3. A steeper phi
        runs the stroke further round before it is cut: a longer terminal."""
        a = slope_angle(rx, ry, 0.5, 89.5, self.phi if phi is None else phi)
        return {0: a, 1: 180 - a, 2: 180 + a, 3: 360 - a}[quadrant]

    def taper(self, f0=0.0, f1=1.0, k0=None, span=0.3):
        """Pen scale along an arc: thin (k0) at the ends that join a stem, full in between.
        f0/f1 say which ends join: 0 = start, 1 = end."""
        k0 = self.trap if k0 is None else k0

        def kf(f):
            k = 1.0
            if f0 is not None and f < span:
                t = f / span
                k = min(k, k0 + (1 - k0) * (3 * t * t - 2 * t ** 3))
            if f1 is not None and f > 1 - span:
                t = (1 - f) / span
                k = min(k, k0 + (1 - k0) * (3 * t * t - 2 * t ** 3))
            return k
        return kf


    @staticmethod
    def fin(f0=None, f1=1, k0=0.84, span=0.22):
        """Terminal shaping: a free end tapers slightly, like a brush lifting."""
        def kf(f):
            k = 1.0
            if f0 is not None and f < span:
                t = f / span
                k = min(k, k0 + (1 - k0) * t)
            if f1 is not None and f > 1 - span:
                t = (1 - f) / span
                k = min(k, k0 + (1 - k0) * t)
            return k
        return kf


__all__ = ['Kit', 'CAP', 'XH', 'ASC', 'DSC', 'W', 'TOP', 'BOT', 'MATH', 'PHI', 'PHI_LONG', 'se', 'merge', 'tf', 'N', 'Stroke', 'Fill']
