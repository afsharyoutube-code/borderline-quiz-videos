# Hand-drawn grayscale + orange renderer (Tiny Life Lessons STYLE-V2)
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT = '/home/claude/fonts/PatrickHand-Regular.ttf'
INK = (34, 32, 30); GRAY = (150, 146, 140); LIGHT = (205, 200, 192); DARK = (95, 92, 88)
ORANGE = (236, 120, 38); WHITE = (252, 250, 246); PAPER = (238, 233, 223)
_font = {}
def font(sz):
    sz = int(sz)
    if sz not in _font: _font[sz] = ImageFont.truetype(FONT, sz)
    return _font[sz]

_paper = {}
def paper(W, H, seed=0):
    k = (W, H)
    if k not in _paper:
        r = np.random.default_rng(7)
        base = np.ones((H, W, 3), np.float32) * np.array(PAPER, np.float32)
        n = r.normal(0, 5, (H // 4 + 1, W // 4 + 1)).astype(np.float32)
        n = np.kron(n, np.ones((4, 4), np.float32))[:H, :W]
        fine = r.normal(0, 3, (H, W)).astype(np.float32)
        yy, xx = np.mgrid[0:H, 0:W]
        v = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
        vig = 1 - 0.13 * v
        base = base * vig[..., None] + (n + fine)[..., None]
        _paper[k] = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    return _paper[k].copy()

class Pen:
    def __init__(self, img, seed, u):
        self.img = img; self.d = ImageDraw.Draw(img); self.r = random.Random(seed); self.u = u
    def j(self, a=1.0): return self.r.uniform(-a, a) * self.u
    def wob(self, pts, amp=2.2, step=14):
        out = []
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            L = math.hypot(x1 - x0, y1 - y0); n = max(1, int(L / (step * self.u)))
            for i in range(n):
                t = i / n; out.append((x0 + (x1 - x0) * t + self.j(amp), y0 + (y1 - y0) * t + self.j(amp)))
        out.append((pts[-1][0] + self.j(amp), pts[-1][1] + self.j(amp)))
        return out
    def line(self, pts, w=4, col=INK, passes=2, amp=2.2):
        for p in range(passes):
            q = self.wob(pts, amp)
            self.d.line(q, fill=col, width=max(1, int(w * self.u * (1 if p == 0 else 0.6))), joint='curve')
    def poly(self, pts, fill=None, w=4, col=INK, hatch=None):
        if fill is not None:
            self.d.polygon(self.wob(pts + [pts[0]], 1.2), fill=fill)
        if hatch: self.hatch(pts, hatch)
        self.line(pts + [pts[0]], w, col)
    def hatch(self, pts, gap=14, col=DARK):
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        m = Image.new('L', self.img.size, 0); ImageDraw.Draw(m).polygon(pts, fill=255)
        lay = Image.new('L', self.img.size, 0); ld = ImageDraw.Draw(lay)
        g = gap * self.u; k = x0 - (y1 - y0)
        while k < x1:
            ld.line([(k + self.j(2), y1 + self.j(2)), (k + (y1 - y0) + self.j(2), y0 + self.j(2))], fill=110, width=max(1, int(1.6 * self.u)))
            k += g
        from PIL import ImageChops
        lay = ImageChops.multiply(lay, m)
        self.img.paste(Image.new('RGB', self.img.size, col), (0, 0), lay)
    def ellipse(self, cx, cy, rx, ry, fill=None, w=4, col=INK, n=40):
        pts = [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]
        if fill is not None: self.d.polygon(pts, fill=fill)
        self.line(pts + [pts[0], pts[1]], w, col, amp=1.6)
    def arc(self, cx, cy, rx, ry, a0, a1, w=4, col=INK, n=16):
        pts = [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
        self.line(pts, w, col, amp=1.2)
    def text(self, s, cx, cy, sz, col=INK, anchor='mm', maxw=None):
        f = font(sz * self.u)
        lines = [s]
        if maxw:
            words = s.split(); lines = []; cur = ''
            for wd in words:
                t = (cur + ' ' + wd).strip()
                if self.d.textlength(t, font=f) > maxw * self.u and cur: lines.append(cur); cur = wd
                else: cur = t
            lines.append(cur)
        lh = sz * self.u * 1.1; y = cy - lh * (len(lines) - 1) / 2
        for ln in lines:
            self.d.text((cx + self.j(1), y + self.j(1)), ln, font=f, fill=col, anchor=anchor)
            y += lh

# ---------------- elements: draw(p, cx, cy, s, **kw) with s = element size in px
def character(p, cx, cy, s, emo='curious', pose=None):
    hr = s * 0.2; hx, hy = cx, cy - s * 0.18
    # body (orange shirt)
    bw, bh = s * 0.34, s * 0.32; by = hy + hr * 0.95
    body = [(hx - bw * 0.36, by), (hx + bw * 0.36, by), (hx + bw * 0.5, by + bh), (hx - bw * 0.5, by + bh)]
    # legs
    p.line([(hx - bw * 0.2, by + bh), (hx - bw * 0.24, by + bh + s * 0.2)], 5)
    p.line([(hx + bw * 0.2, by + bh), (hx + bw * 0.24, by + bh + s * 0.2)], 5)
    p.poly(body, fill=ORANGE, w=4)
    # arms by pose
    sl, sr = (hx - bw * 0.42, by + bh * 0.2), (hx + bw * 0.42, by + bh * 0.2)
    pose = pose or {'shock': 'up', 'scared': 'hug', 'think': 'chin', 'point': 'point', 'happy': 'open', 'sad': 'down', 'curious': 'hip'}.get(emo, 'down')
    L = s * 0.26
    if pose == 'up':
        p.line([sl, (sl[0] - L * 0.6, sl[1] - L * 0.9)], 5); p.line([sr, (sr[0] + L * 0.6, sr[1] - L * 0.9)], 5)
    elif pose == 'hug':
        p.line([sl, (hx - bw * 0.1, by + bh * 0.5)], 5); p.line([sr, (hx + bw * 0.1, by + bh * 0.45)], 5)
    elif pose == 'chin':
        p.line([sl, (sl[0] - L * 0.3, sl[1] + L * 0.8)], 5); p.line([sr, (sr[0] + L * 0.25, sr[1] + L * 0.15), (hx + hr * 0.35, hy + hr * 0.95)], 5)
    elif pose == 'point':
        p.line([sl, (sl[0] - L * 0.3, sl[1] + L * 0.8)], 5); p.line([sr, (sr[0] + L * 1.1, sr[1] - L * 0.35)], 5)
    elif pose == 'open':
        p.line([sl, (sl[0] - L * 0.9, sl[1] - L * 0.2)], 5); p.line([sr, (sr[0] + L * 0.9, sr[1] - L * 0.2)], 5)
    elif pose == 'hip':
        p.line([sl, (sl[0] - L * 0.4, sl[1] + L * 0.4), (sl[0] - L * 0.05, sl[1] + L * 0.75)], 5); p.line([sr, (sr[0] + L * 0.3, sr[1] + L * 0.8)], 5)
    else:
        p.line([sl, (sl[0] - L * 0.25, sl[1] + L * 0.85)], 5); p.line([sr, (sr[0] + L * 0.25, sr[1] + L * 0.85)], 5)
    # head
    p.ellipse(hx, hy, hr, hr * 0.97, fill=WHITE, w=5)
    ex = hr * 0.36; ey = hy - hr * 0.05; d = p.d; u = p.u
    def dot(x, y, r): d.ellipse([x - r, y - r, x + r, y + r], fill=INK)
    if emo in ('shock', 'scared'):
        for sx in (-1, 1):
            p.ellipse(hx + sx * ex, ey, hr * 0.17, hr * 0.2, fill=WHITE, w=3); dot(hx + sx * ex, ey + hr * 0.02, hr * 0.06)
            p.line([(hx + sx * ex - hr * 0.15, ey - hr * 0.38 - (sx * hr * 0.04 if emo == 'scared' else 0)), (hx + sx * ex + hr * 0.15, ey - hr * 0.42 + (sx * hr * 0.06 if emo == 'scared' else 0))], 3)
        if emo == 'shock': p.ellipse(hx, hy + hr * 0.45, hr * 0.13, hr * 0.17, fill=INK, w=3)
        else:
            pts = [(hx - hr * 0.3 + i * hr * 0.1, hy + hr * 0.48 + (hr * 0.05 if i % 2 else -hr * 0.05)) for i in range(7)]
            p.line(pts, 3)
            p.line([(hx + hr * 1.05, hy - hr * 0.5), (hx + hr * 1.12, hy - hr * 0.3)], 3); p.ellipse(hx + hr * 1.12, hy - hr * 0.25, hr * 0.06, hr * 0.08, fill=WHITE, w=2)
    elif emo == 'happy':
        for sx in (-1, 1): p.arc(hx + sx * ex, ey + hr * 0.05, hr * 0.13, hr * 0.12, 200, 340, 4)
        p.arc(hx, hy + hr * 0.25, hr * 0.38, hr * 0.32, 20, 160, 4)
        for sx in (-1, 1): d.ellipse([hx + sx * hr * 0.62 - hr * 0.1, hy + hr * 0.22 - hr * 0.06, hx + sx * hr * 0.62 + hr * 0.1, hy + hr * 0.22 + hr * 0.06], fill=(240, 190, 170))
    elif emo == 'sad':
        for sx in (-1, 1):
            dot(hx + sx * ex, ey + hr * 0.08, hr * 0.065)
            p.line([(hx + sx * ex - sx * hr * 0.14, ey - hr * 0.2), (hx + sx * ex + sx * hr * 0.14, ey - hr * 0.3)], 3)
        p.arc(hx, hy + hr * 0.62, hr * 0.26, hr * 0.18, 200, 340, 4)
        p.ellipse(hx - ex - hr * 0.05, ey + hr * 0.35, hr * 0.05, hr * 0.08, fill=(200, 215, 225), w=2)
    elif emo == 'think':
        dot(hx - ex, ey, hr * 0.065); dot(hx + ex, ey - hr * 0.03, hr * 0.065)
        p.line([(hx - ex - hr * 0.14, ey - hr * 0.25), (hx - ex + hr * 0.14, ey - hr * 0.25)], 3)
        p.line([(hx + ex - hr * 0.14, ey - hr * 0.33), (hx + ex + hr * 0.14, ey - hr * 0.42)], 3)
        p.line([(hx - hr * 0.2, hy + hr * 0.45), (hx + hr * 0.25, hy + hr * 0.4)], 4)
    else:  # curious / point
        for sx in (-1, 1): dot(hx + sx * ex, ey, hr * 0.07)
        p.line([(hx - ex - hr * 0.14, ey - hr * 0.25), (hx - ex + hr * 0.14, ey - hr * 0.3)], 3)
        p.line([(hx + ex - hr * 0.14, ey - hr * 0.36), (hx + ex + hr * 0.14, ey - hr * 0.3)], 3)
        p.arc(hx + hr * 0.05, hy + hr * 0.3, hr * 0.22, hr * 0.15, 30, 150, 4)

def sea(p, x0, x1, y, s, rows=3):
    for k in range(rows):
        yy = y + k * s * 0.06; pts = []
        x = x0
        while x < x1:
            pts.append((x, yy + math.sin(x / (s * 0.05) + k) * s * 0.012)); x += s * 0.02
        p.line(pts, 3, GRAY if k else DARK, passes=1)

def ship(p, cx, cy, s, state='normal', flag=None):
    hw = s * 0.42; hy = cy + s * 0.3
    hull = [(cx - hw, hy), (cx + hw * 1.05, hy - s * 0.02), (cx + hw * 0.8, hy + s * 0.14), (cx - hw * 0.85, hy + s * 0.14)]
    for mx, mh in ((-0.18, 0.62), (0.2, 0.68)):
        x = cx + mx * s; top = hy - mh * s
        p.line([(x, hy), (x, top)], 5)
        for k, (a, b) in enumerate(((0.06, 0.24), (0.28, 0.46))):
            sy0, sy1 = top + a * s, top + b * s; w0, w1 = s * 0.13, s * 0.16
            sail = [(x - w0, sy0), (x + w0, sy0), (x + w1 + s * 0.02, sy1), (x - w1 + s * 0.02, sy1)]
            if state == 'torn' and k == 0:
                sail = [(x - w0, sy0), (x + w0 * 0.2, sy0), (x - w0 * 0.1, sy0 + s * 0.08), (x + w1 * 0.4, sy1), (x - w1, sy1)]
            p.poly(sail, fill=WHITE if state != 'ghost' else (225, 222, 216), w=3)
            p.line([(x - w0 * 0.8, sy0 + s * 0.06), (x + w0 * 0.8, sy0 + s * 0.06)], 2, GRAY, passes=1)
        p.line([(x - s * 0.1, top + s * 0.06), (x + s * 0.1, top + s * 0.06)], 4)
    p.line([(cx + hw * 1.05, hy - s * 0.02), (cx + hw * 1.4, hy - s * 0.12)], 4)  # bowsprit
    p.line([(cx + hw * 1.4, hy - s * 0.12), (cx + 0.2 * s, hy - 0.62 * s)], 2, GRAY, passes=1)
    p.poly(hull, fill=(120, 116, 110), w=5, hatch=10)
    p.line([(cx - hw * 0.95, hy + s * 0.05), (cx + hw, hy + s * 0.04)], 2, LIGHT, passes=1)
    if flag:
        x = cx + 0.2 * s; top = hy - 0.68 * s
        p.poly([(x, top), (x + s * 0.12, top + s * 0.04), (x, top + s * 0.08)], fill=INK, w=2)
    sea(p, cx - s * 0.7, cx + s * 0.75, hy + s * 0.13, s)

def qmark(p, cx, cy, s, col=ORANGE):
    p.text('?', cx, cy, s / p.u, col)

def label(p, txt, cx, cy, sz=56, col=INK, maxw=None):
    p.text(txt, cx, cy, sz, col, maxw=maxw)

def person(p, cx, cy, s, col=WHITE, body=GRAY):
    p.line([(cx, cy), (cx - s * 0.12, cy + s * 0.45)], 3); p.line([(cx, cy), (cx + s * 0.12, cy + s * 0.45)], 3)
    p.poly([(cx - s * 0.14, cy - s * 0.35), (cx + s * 0.14, cy - s * 0.35), (cx + s * 0.18, cy + s * 0.05), (cx - s * 0.18, cy + s * 0.05)], fill=body, w=3)
    p.ellipse(cx, cy - s * 0.52, s * 0.17, s * 0.17, fill=col, w=3)

def people(p, cx, cy, s, n=10, faded=0):
    cols = min(n, 5); rows = math.ceil(n / cols); gap = s * 0.22
    k = 0
    for r in range(rows):
        cnt = min(cols, n - r * cols)
        for c in range(cnt):
            x = cx + (c - (cnt - 1) / 2) * gap; y = cy + (r - (rows - 1) / 2) * s * 0.42
            person(p, x, y, s * 0.3, WHITE if k >= faded else LIGHT, GRAY if k >= faded else LIGHT); k += 1

def boat(p, cx, cy, s, n=10, dots=True):
    p.poly([(cx - s * 0.4, cy), (cx + s * 0.4, cy), (cx + s * 0.3, cy + s * 0.12), (cx - s * 0.3, cy + s * 0.12)], fill=(130, 126, 120), w=4, hatch=9)
    if dots:
        for i in range(n):
            x = cx - s * 0.33 + i * s * 0.073
            p.ellipse(x, cy - s * 0.05, s * 0.03, s * 0.03, fill=WHITE, w=2)
    p.line([(cx + s * 0.05, cy), (cx + s * 0.45, cy - s * 0.2)], 3)  # oar
    sea(p, cx - s * 0.6, cx + s * 0.6, cy + s * 0.12, s * 0.8, 2)

def barrel(p, cx, cy, s, fill=(170, 160, 150)):
    w, h = s * 0.3, s * 0.4
    p.poly([(cx - w * 0.42, cy - h / 2), (cx + w * 0.42, cy - h / 2), (cx + w / 2, cy), (cx + w * 0.42, cy + h / 2), (cx - w * 0.42, cy + h / 2), (cx - w / 2, cy)], fill=fill, w=4)
    for f in (-0.3, 0.3): p.line([(cx - w * 0.47, cy + f * h), (cx + w * 0.47, cy + f * h)], 3)
    p.line([(cx - w * 0.15, cy - h * 0.48), (cx - w * 0.17, cy + h * 0.48)], 2, GRAY, passes=1)
    p.line([(cx + w * 0.15, cy - h * 0.48), (cx + w * 0.17, cy + h * 0.48)], 2, GRAY, passes=1)

def barrels(p, cx, cy, s, rows=3, cols=6, empty=()):
    k = 0
    for r in range(rows):
        for c in range(cols):
            x = cx + (c - (cols - 1) / 2) * s * 0.17; y = cy + (r - (rows - 1) / 2) * s * 0.2
            barrel(p, x, y, s * 0.5, (235, 225, 215) if k in empty else (170, 160, 150)); k += 1

ATL_NA = [(0.05, 0.05), (0.2, 0.12), (0.23, 0.25), (0.3, 0.3), (0.24, 0.38), (0.2, 0.45), (0.12, 0.55), (0.1, 0.7), (0.05, 0.8)]
ATL_EU = [(0.62, 0.05), (0.66, 0.15), (0.7, 0.22), (0.72, 0.3), (0.74, 0.38), (0.72, 0.46), (0.76, 0.5), (0.82, 0.48), (0.9, 0.45), (0.95, 0.4)]
ATL_AF = [(0.73, 0.52), (0.7, 0.6), (0.66, 0.7), (0.65, 0.82), (0.7, 0.95)]
PLACES = {'New York': (0.22, 0.33), 'Azores': (0.5, 0.4), 'Santa Maria': (0.53, 0.43), 'Gibraltar': (0.73, 0.49), 'Genoa': (0.92, 0.36)}

def amap(p, cx, cy, s, mode='route'):
    W, H = s * 1.5, s * 0.9; x0, y0 = cx - W / 2, cy - H / 2
    P = lambda q: (x0 + q[0] * W, y0 + q[1] * H)
    p.poly([P((0, 0)), P((1, 0)), P((1, 1)), P((0, 1))], fill=(228, 224, 214), w=4)
    for coast in (ATL_NA, ATL_EU, ATL_AF):
        p.line([P(q) for q in coast], 5, DARK)
    for k in range(4):
        yy = 0.2 + k * 0.2; p.line([P((0.35, yy)), P((0.38, yy - 0.01)), P((0.41, yy))], 2, GRAY, passes=1)
    for isl in ((0.47, 0.39), (0.5, 0.4), (0.53, 0.43)):
        x, y = P(isl); p.ellipse(x, y, s * 0.012, s * 0.008, fill=DARK, w=2)
    def pin(name, col=INK, big=False):
        x, y = P(PLACES[name]); r = s * (0.025 if big else 0.015)
        p.ellipse(x, y, r, r, fill=col, w=3); p.text(name, x, y - s * 0.05, 34 * s / 700, INK)
    if mode in ('route', 'full'):
        pts = [P(q) for q in ((0.22, 0.33), (0.4, 0.38), (0.53, 0.43), (0.73, 0.49))]
        for a, b in zip(pts, pts[1:]):
            n = 6
            for i in range(n):
                t0, t1 = i / n, (i + 0.5) / n
                p.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0), (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)], 4, ORANGE, passes=1)
        pin('New York'); pin('Gibraltar'); pin('Genoa')
    if mode in ('azores', 'island', 'full'):
        pin('Santa Maria', ORANGE, True)
        if mode == 'island':
            x, y = P((0.43, 0.43)); p.ellipse(x, y, s * 0.02, s * 0.02, fill=WHITE, w=3); p.text('where he thought he was', x - s * 0.05, y + s * 0.07, 30 * s / 700, DARK)
    if mode == 'found':
        pin('Azores'); x, y = P((0.64, 0.44)); p.text('X', x, y, 70 * s / 700, ORANGE); p.text('found here', x, y + s * 0.07, 32 * s / 700)

def slate(p, cx, cy, s, lines):
    w, h = s * 0.9, s * 0.6
    p.poly([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)], fill=(150, 140, 125), w=6)
    p.poly([(cx - w * 0.44, cy - h * 0.4), (cx + w * 0.44, cy - h * 0.4), (cx + w * 0.44, cy + h * 0.4), (cx - w * 0.44, cy + h * 0.4)], fill=(70, 72, 72), w=3)
    for i, t in enumerate(lines):
        p.text(t, cx, cy - h * 0.22 + i * h * 0.2, 44 * s / 600, (235, 235, 230))

def clockface(p, cx, cy, s, hands=(10, 2), col=WHITE):
    r = s * 0.3; p.ellipse(cx, cy, r, r, fill=col, w=6)
    for i in range(12):
        a = math.radians(i * 30); p.line([(cx + r * 0.82 * math.cos(a), cy + r * 0.82 * math.sin(a)), (cx + r * 0.92 * math.cos(a), cy + r * 0.92 * math.sin(a))], 3, passes=1)
    for hv, ln in ((hands[0] / 12, 0.5), (hands[1] / 12, 0.75)):
        a = math.radians(hv * 360 - 90); p.line([(cx, cy), (cx + r * ln * math.cos(a), cy + r * ln * math.sin(a))], 5)

def calendar(p, cx, cy, s, n=9):
    for i in range(n):
        x = cx + (i % 5 - 2) * s * 0.2; y = cy + (i // 5 - 0.5) * s * 0.26
        p.poly([(x - s * 0.08, y - s * 0.1), (x + s * 0.08, y - s * 0.1), (x + s * 0.08, y + s * 0.1), (x - s * 0.08, y + s * 0.1)], fill=WHITE, w=3)
        p.text(str(i + 1), x, y + s * 0.01, 46 * s / 600)
        p.line([(x - s * 0.06, y - s * 0.07), (x + s * 0.06, y + s * 0.07)], 3, ORANGE, passes=1)

def book(p, cx, cy, s, title='', sub=''):
    w, h = s * 0.55, s * 0.72
    p.poly([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)], fill=(110, 106, 100), w=5)
    p.line([(cx - w * 0.4, cy - h / 2), (cx - w * 0.4, cy + h / 2)], 3, LIGHT, passes=1)
    p.text(title, cx + w * 0.04, cy - h * 0.15, 46 * s / 600, WHITE, maxw=w * 0.8 / p.u)
    if sub: p.text(sub, cx + w * 0.04, cy + h * 0.25, 30 * s / 600, LIGHT)

def letter(p, cx, cy, s):
    w, h = s * 0.6, s * 0.4
    p.poly([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)], fill=WHITE, w=4)
    p.line([(cx - w / 2, cy - h / 2), (cx, cy + h * 0.05), (cx + w / 2, cy - h / 2)], 3)
    p.ellipse(cx, cy + h * 0.05, s * 0.04, s * 0.04, fill=ORANGE, w=2)

def spyglass(p, cx, cy, s):
    p.poly([(cx - s * 0.35, cy + s * 0.08), (cx + s * 0.3, cy - s * 0.12), (cx + s * 0.33, cy - s * 0.02), (cx - s * 0.32, cy + s * 0.16)], fill=(160, 150, 140), w=4, hatch=12)
    p.ellipse(cx + s * 0.32, cy - s * 0.07, s * 0.03, s * 0.06, fill=WHITE, w=3)

def circleview(p, cx, cy, s, inner):
    r = s * 0.45; p.ellipse(cx, cy, r, r, fill=(228, 226, 220), w=8); inner(p, cx, cy, s * 0.55)

def wheel(p, cx, cy, s):
    r = s * 0.28; p.ellipse(cx, cy, r, r, w=8); p.ellipse(cx, cy, r * 0.2, r * 0.2, fill=GRAY, w=4)
    for i in range(8):
        a = math.radians(i * 45 + 10); p.line([(cx, cy), (cx + r * 1.3 * math.cos(a), cy + r * 1.3 * math.sin(a))], 6)

def crate(p, cx, cy, s, txt=''):
    w = s * 0.3
    p.poly([(cx - w / 2, cy - w / 2), (cx + w / 2, cy - w / 2), (cx + w / 2, cy + w / 2), (cx - w / 2, cy + w / 2)], fill=(185, 175, 160), w=4)
    p.line([(cx - w / 2, cy - w / 2), (cx + w / 2, cy + w / 2)], 3); p.line([(cx + w / 2, cy - w / 2), (cx - w / 2, cy + w / 2)], 3)
    if txt: p.text(txt, cx, cy - w * 0.72, 30 * s / 500)

def jug(p, cx, cy, s):
    p.poly([(cx - s * 0.08, cy - s * 0.15), (cx + s * 0.08, cy - s * 0.15), (cx + s * 0.13, cy + s * 0.15), (cx - s * 0.13, cy + s * 0.15)], fill=(200, 210, 215), w=4)
    p.ellipse(cx, cy - s * 0.17, s * 0.06, s * 0.025, fill=WHITE, w=3)

def boot(p, cx, cy, s):
    p.poly([(cx - s * 0.05, cy - s * 0.2), (cx + s * 0.07, cy - s * 0.2), (cx + s * 0.07, cy + s * 0.05), (cx + s * 0.2, cy + s * 0.08), (cx + s * 0.2, cy + s * 0.14), (cx - s * 0.05, cy + s * 0.14)], fill=(90, 86, 82), w=4)

def sewing(p, cx, cy, s):
    p.poly([(cx - s * 0.25, cy + s * 0.05), (cx + s * 0.25, cy + s * 0.05), (cx + s * 0.25, cy + s * 0.12), (cx - s * 0.25, cy + s * 0.12)], fill=GRAY, w=4)
    p.line([(cx - s * 0.18, cy + s * 0.05), (cx - s * 0.18, cy - s * 0.15), (cx + s * 0.15, cy - s * 0.15), (cx + s * 0.15, cy - s * 0.02)], 8)
    p.line([(cx + s * 0.15, cy - s * 0.02), (cx + s * 0.15, cy + s * 0.05)], 3)

def missing(p, cx, cy, s, kind):
    # dashed outline of a missing object
    if kind == 'sextant':
        pts = [(cx, cy - s * 0.18), (cx - s * 0.16, cy + s * 0.12), (cx + s * 0.16, cy + s * 0.12)]
    else:
        pts = [(cx - s * 0.16, cy - s * 0.12), (cx + s * 0.16, cy - s * 0.12), (cx + s * 0.16, cy + s * 0.12), (cx - s * 0.16, cy + s * 0.12)]
    ring = pts + [pts[0]]
    for a, b in zip(ring, ring[1:]):
        for i in range(5):
            t0, t1 = i / 5, (i + 0.55) / 5
            p.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0), (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)], 3, GRAY, passes=1)
    p.text('?', cx, cy, 70 * s / 400, ORANGE)

def hold(p, cx, cy, s, level=0.3, rising=False):
    w, h = s * 1.0, s * 0.55
    hull = [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w * 0.4, cy + h / 2), (cx - w * 0.4, cy + h / 2)]
    p.poly(hull, fill=(225, 220, 210), w=6)
    wy = cy + h / 2 - h * level
    p.poly([(cx - w * 0.4 - w * 0.1 * (1 - level), wy), (cx + w * 0.4 + w * 0.1 * (1 - level), wy), (cx + w * 0.4, cy + h / 2), (cx - w * 0.4, cy + h / 2)], fill=(175, 185, 190), w=3)
    for i in range(5): barrel(p, cx + (i - 2) * s * 0.16, wy - s * 0.06, s * 0.35)
    if rising:
        for x in (-0.3, 0.3): p.line([(cx + x * w, wy - s * 0.12), (cx + x * w, wy - s * 0.25)], 4, ORANGE); p.line([(cx + x * w - s * 0.03, wy - s * 0.21), (cx + x * w, wy - s * 0.25), (cx + x * w + s * 0.03, wy - s * 0.21)], 4, ORANGE)
    p.text('3.5 ft of water', cx, cy + h / 2 + s * 0.08, 40 * s / 600, DARK)

def pump(p, cx, cy, s, clog=False):
    p.poly([(cx - s * 0.06, cy - s * 0.3), (cx + s * 0.06, cy - s * 0.3), (cx + s * 0.06, cy + s * 0.25), (cx - s * 0.06, cy + s * 0.25)], fill=GRAY, w=4, hatch=10)
    p.line([(cx, cy - s * 0.3), (cx + s * 0.25, cy - s * 0.4)], 6)
    for i, (dx, dy) in enumerate(((0.22, 0.15), (0.3, 0.05), (-0.25, 0.12))):
        p.poly([(cx + dx * s - s * 0.04, cy + dy * s - s * 0.02), (cx + dx * s + s * 0.04, cy + dy * s - s * 0.02), (cx + dx * s + s * 0.04, cy + dy * s + s * 0.02), (cx + dx * s - s * 0.04, cy + dy * s + s * 0.02)], fill=LIGHT, w=3)
    if clog:
        for i in range(18):
            x = cx + p.r.uniform(-0.05, 0.05) * s; y = cy + p.r.uniform(0.0, 0.24) * s
            p.d.ellipse([x - 4 * p.u, y - 4 * p.u, x + 4 * p.u, y + 4 * p.u], fill=INK)
        p.text('coal dust', cx, cy + s * 0.36, 36 * s / 500, DARK)

def rod(p, cx, cy, s):
    p.line([(cx - s * 0.02, cy - s * 0.35), (cx + s * 0.02, cy + s * 0.35)], 7)
    for i in range(6): p.line([(cx - s * 0.03, cy - s * 0.25 + i * s * 0.1), (cx + s * 0.05, cy - s * 0.25 + i * s * 0.1)], 3, passes=1)

def court(p, cx, cy, s):
    p.poly([(cx - s * 0.6, cy), (cx + s * 0.6, cy), (cx + s * 0.6, cy + s * 0.3), (cx - s * 0.6, cy + s * 0.3)], fill=(120, 112, 104), w=5, hatch=12)
    person(p, cx, cy - s * 0.08, s * 0.35, WHITE, (60, 58, 56))
    p.line([(cx + s * 0.3, cy - s * 0.04), (cx + s * 0.42, cy - s * 0.12)], 6); p.poly([(cx + s * 0.38, cy - s * 0.18), (cx + s * 0.48, cy - s * 0.1), (cx + s * 0.44, cy - s * 0.05), (cx + s * 0.34, cy - s * 0.13)], fill=DARK, w=3)
    for x in (-0.45, 0.45): p.line([(cx + x * s, cy - s * 0.55), (cx + x * s, cy)], 6)
    p.line([(cx - s * 0.55, cy - s * 0.55), (cx + s * 0.55, cy - s * 0.55)], 6)

def sword(p, cx, cy, s):
    p.poly([(cx - s * 0.4, cy + s * 0.02), (cx + s * 0.3, cy - s * 0.02), (cx + s * 0.4, cy), (cx + s * 0.3, cy + s * 0.04), (cx - s * 0.4, cy + s * 0.05)], fill=(220, 220, 218), w=4)
    p.line([(cx - s * 0.4, cy - s * 0.08), (cx - s * 0.4, cy + s * 0.14)], 7); p.line([(cx - s * 0.4, cy + s * 0.03), (cx - s * 0.55, cy + s * 0.03)], 9)
    for x in (0.0, 0.12): p.ellipse(cx + x * s, cy + s * 0.02, s * 0.025, s * 0.012, fill=GRAY, w=1)

def coins(p, cx, cy, s):
    r = s * 0.3; p.ellipse(cx, cy, r, r, fill=WHITE, w=5)
    pts = [(cx, cy)] + [(cx + r * math.cos(math.radians(-90 + a)), cy + r * math.sin(math.radians(-90 + a))) for a in range(0, 61, 6)]
    p.poly(pts, fill=ORANGE, w=4)
    p.text('1/6', cx + r * 0.55, cy - r * 1.15, 50 * s / 500, ORANGE)

def pirateflag(p, cx, cy, s):
    p.line([(cx - s * 0.2, cy + s * 0.4), (cx - s * 0.2, cy - s * 0.4)], 6)
    p.poly([(cx - s * 0.2, cy - s * 0.4), (cx + s * 0.3, cy - s * 0.38), (cx + s * 0.3, cy - s * 0.05), (cx - s * 0.2, cy - s * 0.05)], fill=INK, w=3)
    p.ellipse(cx + s * 0.05, cy - s * 0.24, s * 0.06, s * 0.06, fill=WHITE, w=2)
    p.line([(cx - s * 0.05, cy - s * 0.12), (cx + s * 0.15, cy - s * 0.1)], 4, WHITE, passes=1); p.line([(cx - s * 0.05, cy - s * 0.1), (cx + s * 0.15, cy - s * 0.13)], 4, WHITE, passes=1)

def tentacles(p, cx, cy, s):
    for k in range(4):
        x0 = cx + (k - 1.5) * s * 0.22; pts = []
        for i in range(14):
            t = i / 13; pts.append((x0 + math.sin(t * 5 + k) * s * 0.08, cy + s * 0.4 - t * s * (0.55 + 0.1 * k)))
        p.line(pts, 12 - 6 * 0, DARK, passes=1)
    sea(p, cx - s * 0.6, cx + s * 0.6, cy + s * 0.38, s, 2)

def cup(p, cx, cy, s):
    p.poly([(cx - s * 0.16, cy - s * 0.1), (cx + s * 0.16, cy - s * 0.1), (cx + s * 0.12, cy + s * 0.12), (cx - s * 0.12, cy + s * 0.12)], fill=WHITE, w=4)
    p.arc(cx + s * 0.18, cy, s * 0.06, s * 0.06, -90, 90, 4)
    p.ellipse(cx, cy + s * 0.14, s * 0.24, s * 0.04, fill=LIGHT, w=3)
    for x in (-0.06, 0.04):
        p.line([(cx + x * s, cy - s * 0.15), (cx + x * s + s * 0.03, cy - s * 0.25), (cx + x * s, cy - s * 0.35)], 3, GRAY, passes=1)

def vapor(p, cx, cy, s):
    for k in range(5):
        x = cx + (k - 2) * s * 0.18; pts = [(x + math.sin(i * 0.9 + k) * s * 0.04, cy + s * 0.2 - i * s * 0.05) for i in range(10)]
        p.line(pts, 3, GRAY, passes=1)

def burst(p, cx, cy, s, col=ORANGE):
    pts = []
    for i in range(24):
        r = s * (0.38 if i % 2 == 0 else 0.22); a = 2 * math.pi * i / 24
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    p.poly(pts, fill=col, w=4)
    p.text('BOOM?', cx, cy, 60 * s / 500, WHITE)

def rope(p, x0, y0, x1, y1, snap=False):
    mx = (x0 + x1) / 2
    if snap:
        p.line([(x0, y0), (mx - 30 * p.u, (y0 + y1) / 2 + 30 * p.u)], 4, DARK)
        p.line([(mx + 30 * p.u, (y0 + y1) / 2 + 30 * p.u), (x1, y1)], 4, DARK)
        burst_small(p, mx, (y0 + y1) / 2 + 20 * p.u)
    else:
        pts = [(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + math.sin(t * math.pi) * 40 * p.u) for t in [i / 10 for i in range(11)]]
        p.line(pts, 4, DARK)

def burst_small(p, cx, cy):
    for i in range(8):
        a = 2 * math.pi * i / 8; p.line([(cx + 14 * p.u * math.cos(a), cy + 14 * p.u * math.sin(a)), (cx + 34 * p.u * math.cos(a), cy + 34 * p.u * math.sin(a))], 4, ORANGE, passes=1)

def cubes(p, cx, cy, s):
    w, h = s * 0.9, s * 0.5
    p.poly([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)], fill=(232, 228, 220), w=5)
    for r in range(2):
        for c in range(5):
            x = cx - w * 0.36 + c * w * 0.18; y = cy + h * 0.25 - r * h * 0.3
            p.poly([(x - s * 0.05, y - s * 0.05), (x + s * 0.05, y - s * 0.05), (x + s * 0.05, y + s * 0.05), (x - s * 0.05, y + s * 0.05)], fill=WHITE, w=3)

def fire(p, cx, cy, s):
    for k, (sc, col) in enumerate(((1.0, (150, 175, 205)), (0.7, (110, 140, 185)), (0.4, ORANGE))):
        pts = []
        for i in range(17):
            a = math.pi * i / 16; r = s * 0.35 * sc * (1 + (0.35 if i % 2 else 0))
            pts.append((cx - math.cos(a) * r * 0.7, cy - math.sin(a) * r * 1.3))
        p.poly(pts, fill=col, w=3)

def island(p, cx, cy, s):
    p.poly([(cx - s * 0.45, cy), (cx - s * 0.2, cy - s * 0.2), (cx + s * 0.05, cy - s * 0.28), (cx + s * 0.3, cy - s * 0.15), (cx + s * 0.45, cy)], fill=(140, 136, 128), w=5, hatch=12)
    sea(p, cx - s * 0.7, cx + s * 0.7, cy, s, 2)

def reef(p, cx, cy, s):
    p.poly([(cx - s * 0.5, cy + s * 0.15), (cx - s * 0.3, cy + s * 0.05), (cx - s * 0.1, cy + s * 0.12), (cx + s * 0.15, cy + s * 0.02), (cx + s * 0.5, cy + s * 0.15)], fill=(110, 105, 100), w=4, hatch=8)

def heart(p, cx, cy, s, col=ORANGE):
    pts = [(cx + s * 0.16 * (16 * math.sin(t) ** 3) / 16, cy - s * 0.16 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16) for t in [i * 2 * math.pi / 40 for i in range(40)]]
    p.poly(pts, fill=col, w=4)

def bubble(p, cx, cy, s, txt='?'):
    p.ellipse(cx, cy, s * 0.4, s * 0.25, fill=WHITE, w=5)
    p.poly([(cx - s * 0.15, cy + s * 0.2), (cx - s * 0.25, cy + s * 0.38), (cx - s * 0.02, cy + s * 0.24)], fill=WHITE, w=4)
    p.text(txt, cx, cy, 60 * s / 500, INK, maxw=s * 0.7 / p.u)

def lighthouse(p, cx, cy, s):
    p.poly([(cx - s * 0.1, cy - s * 0.3), (cx + s * 0.1, cy - s * 0.3), (cx + s * 0.16, cy + s * 0.35), (cx - s * 0.16, cy + s * 0.35)], fill=WHITE, w=5)
    for f in (-0.1, 0.12): p.line([(cx - s * 0.13, cy + f * s), (cx + s * 0.13, cy + f * s)], 8, DARK, passes=1)
    p.poly([(cx - s * 0.08, cy - s * 0.45), (cx + s * 0.08, cy - s * 0.45), (cx + s * 0.08, cy - s * 0.3), (cx - s * 0.08, cy - s * 0.3)], fill=ORANGE, w=4)
    p.poly([(cx - s * 0.12, cy - s * 0.45), (cx, cy - s * 0.58), (cx + s * 0.12, cy - s * 0.45)], fill=DARK, w=4)
    island(p, cx, cy + s * 0.42, s * 0.9)

def city(p, cx, cy, s):
    x = cx - s * 0.6
    for i, hgt in enumerate((0.25, 0.4, 0.3, 0.5, 0.35, 0.28, 0.45)):
        w = s * 0.16
        p.poly([(x, cy), (x, cy - hgt * s), (x + w, cy - hgt * s), (x + w, cy)], fill=(170 - i * 8, 165 - i * 8, 158 - i * 8), w=4)
        for r in range(int(hgt * 10)):
            p.d.rectangle([x + w * 0.3, cy - hgt * s + s * 0.05 + r * s * 0.08, x + w * 0.45, cy - hgt * s + s * 0.08 + r * s * 0.08], fill=LIGHT)
        x += w + s * 0.01
    sea(p, cx - s * 0.7, cx + s * 0.7, cy + s * 0.02, s, 2)

def captain(p, cx, cy, s, name, sub=''):
    person(p, cx, cy, s * 0.9, WHITE, (70, 68, 66))
    p.poly([(cx - s * 0.2, cy - s * 0.58), (cx + s * 0.2, cy - s * 0.58), (cx + s * 0.12, cy - s * 0.68), (cx - s * 0.12, cy - s * 0.68)], fill=INK, w=3)
    p.text(name, cx, cy + s * 0.55, 46 * s / 500)
    if sub: p.text(sub, cx, cy + s * 0.7, 32 * s / 500, DARK)
