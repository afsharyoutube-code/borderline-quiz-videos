from draw import *

def L(W, H):
    v = H > W
    if v:
        return dict(v=True, P=(W * 0.5, H * 0.30, W * 0.82), C=(W * 0.5, H * 0.60, W * 0.62), M=(W * 0.5, H * 0.42, W * 0.9), T=(W * 0.5, H * 0.1))
    return dict(v=False, P=(W * 0.64, H * 0.47, H * 0.72), C=(W * 0.22, H * 0.52, H * 0.62), M=(W * 0.5, H * 0.46, H * 0.85), T=(W * 0.5, H * 0.1))

def prop(p, name, cx, cy, s):
    n = name
    if n == 'q': qmark(p, cx, cy, s * 0.8)
    elif n == 'map': amap(p, cx, cy, s * 0.85, 'route')
    elif n == 'book': book(p, cx, cy, s, 'Legends', 'vs facts')
    elif n == 'heart': heart(p, cx, cy, s * 1.2)
    elif n == 'letter': letter(p, cx, cy, s)
    elif n == 'spyglass': spyglass(p, cx, cy, s)
    elif n == 'ship': ship(p, cx, cy, s * 0.8)
    elif n == 'pirate': pirateflag(p, cx, cy, s)
    elif n == 'missing': missing(p, cx - s * 0.22, cy, s, 'sextant'); missing(p, cx + s * 0.22, cy, s, 'box')
    elif n == 'barrels': barrels(p, cx, cy, s, 3, 4)
    elif n == 'vapor': barrels(p, cx, cy + s * 0.15, s * 0.8, 2, 4); vapor(p, cx, cy - s * 0.2, s)
    elif n == 'boom': burst(p, cx, cy, s)
    elif n == 'rope': rope(p, cx - s * 0.4, cy, cx + s * 0.4, cy)
    elif n == 'boat': boat(p, cx, cy, s * 0.9)
    elif n == 'fire': fire(p, cx, cy + s * 0.2, s)
    elif n == 'clock': clockface(p, cx, cy, s)
    elif n == 'water': hold(p, cx, cy, s * 0.9, 0.35, True)
    elif n == 'rod': rod(p, cx, cy, s)
    elif n == 'comment': bubble(p, cx, cy, s, 'Stay or row?')
    elif n == 'lighthouse': lighthouse(p, cx, cy - s * 0.05, s)
    elif n == 'people0': people(p, cx, cy, s, 10, faded=10)

def compose0(key, text, W, H, seed):
    img = paper(W, H); u = min(W, H) / 1080
    p = Pen(img, seed, u); lay = L(W, H); v = lay['v']
    kind, _, arg = key.partition(':')
    Px, Py, Ps = lay['P']; Cx, Cy, Cs = lay['C']; Mx, My, Ms = lay['M']; Tx, Ty = lay['T']
    def head(t, col=INK, sz=64): p.text(t, Tx, Ty + (40 * u if v else 0), sz, col, maxw=(W / u) * 0.9)
    if kind == 'char':
        emo, _, pr = arg.partition('|')
        if pr: prop(p, pr, Px, Py, Ps)
        character(p, Cx if pr else W / 2, Cy if pr else H * 0.5, Cs * (1 if pr else 1.15), emo)
    elif kind == 'card':
        p.text(arg, W / 2, H * 0.44, 92 if not v else 80, INK, maxw=(W / u) * 0.85)
        p.line([(W * 0.3, H * 0.53), (W * 0.7, H * 0.53)], 6, ORANGE)
        character(p, W * 0.5, H * (0.72 if not v else 0.68), H * (0.28 if not v else 0.2), 'curious')
    elif kind == 'title':
        ship(p, Mx, My + (60 * u), Ms * 0.75, 'ghost')
        p.text(arg, W / 2, H * 0.12 if not v else H * 0.12, 110, INK, maxw=(W / u) * 0.9)
        p.text('1872', W / 2, H * 0.2 if not v else H * 0.18, 60, ORANGE)
    elif kind == 'ship':
        st = {'empty': 'torn', 'far': 'normal', 'away': 'torn', 'dei': 'normal', 'float': 'normal'}.get(arg, 'normal')
        if arg == 'far':
            sea(p, 0, W, H * 0.6, H * 0.6, 4); ship(p, W * 0.72, H * 0.52, H * 0.2, st); head('A ship on the horizon...')
            character(p, Cx, Cy + (0 if v else H * 0.08), Cs * 0.7, 'curious')
        elif arg == 'away':
            ship(p, W * 0.68, H * 0.42, Ms * 0.45, st); boat(p, W * 0.28, H * 0.68, Ms * 0.5)
            p.text('...alone', W * 0.68, H * 0.18, 60, DARK)
        elif arg == 'dei':
            ship(p, Mx, My + 40 * u, Ms * 0.8); head('The Dei Gratia', sz=72); p.text('"by the grace of God"', W / 2, H * 0.18 + (40 * u if v else 0), 44, DARK)
        elif arg == 'float':
            ship(p, Mx, My + 40 * u, Ms * 0.8); head('Still floating.', ORANGE, 80)
        else:
            ship(p, Mx, My + 40 * u, Ms * 0.85, st); head('Found: December 1872', sz=60)
    elif kind == 'map':
        mode = {'route': 'route', 'azores': 'azores', 'island': 'island'}[arg]
        amap(p, Mx, My + 20 * u, Ms * (0.95 if not v else 0.65), mode)
        head({'route': 'New York to Genoa', 'azores': 'Last entry: off Santa Maria', 'island': 'A wrong clock = a wrong position'}[arg])
    elif kind == 'city':
        city(p, Mx, My + Ms * 0.2, Ms * 0.9); head('New York, November 1872')
    elif kind == 'barrels':
        if arg == 'nine':
            barrels(p, Mx, My + 30 * u, Ms * 0.85, 3, 6, empty=(1, 4, 6, 9, 11, 12, 14, 16, 17)); head('9 barrels: EMPTY', ORANGE, 80)
        else:
            barrels(p, Mx, My + 40 * u, Ms * 0.85, 3, 6); head('1,701 barrels of alcohol', sz=72)
    elif kind == 'barrel':
        if arg == 'oak':
            barrel(p, W * 0.38, My, Ms * 0.9, (170, 160, 150)); barrel(p, W * 0.62, My, Ms * 0.9, (200, 150, 130))
            p.text('white oak', W * 0.38, My + Ms * 0.28, 44, DARK); p.text('red oak (leaks)', W * 0.62, My + Ms * 0.28, 44, ORANGE)
            vapor(p, W * 0.62, My - Ms * 0.35, Ms * 0.5)
        else:
            barrel(p, Px, Py, Ps * 1.2); character(p, Cx, Cy, Cs, 'sad'); p.text('undrinkable', Px, Py + Ps * 0.38, 48, DARK)
    elif kind == 'captain':
        nm = {'briggs': ('Capt. Benjamin Briggs', 'age 37 · careful'), 'morehouse': ('Capt. David Morehouse', 'the Dei Gratia')}[arg]
        captain(p, Px, Py, Ps * 0.9, nm[0], nm[1]); character(p, Cx, Cy, Cs, 'curious', 'point')
    elif kind == 'family':
        person(p, Mx - Ms * 0.3, My, Ms * 0.45, WHITE, (70, 68, 66)); person(p, Mx, My + Ms * 0.03, Ms * 0.4, WHITE, (150, 140, 135)); person(p, Mx + Ms * 0.24, My + Ms * 0.12, Ms * 0.22, WHITE, ORANGE)
        p.text('Benjamin', Mx - Ms * 0.3, My + Ms * 0.32, 44); p.text('Sarah', Mx, My + Ms * 0.32, 44); p.text('Sophia, 2', Mx + Ms * 0.3, My + Ms * 0.32, 44)
        heart(p, Mx, My - Ms * 0.42, Ms * 0.3)
    elif kind == 'people':
        n = int(arg); people(p, Mx, My, Ms * (0.8 if n > 5 else 0.9), n)
        head('+ 7 crew' if n == 7 else '10 people', ORANGE if n == 10 else INK, 80)
    elif kind == 'spyglass':
        circleview(p, Mx, My, Ms, lambda pp, x, y, s: ship(pp, x, y, s * 0.9, 'torn')); head('Something looks wrong')
    elif kind == 'boat':
        ship(p, W * 0.7, H * 0.42, Ms * 0.5); boat(p, W * 0.32, H * 0.62, Ms * 0.45, 3)
        if arg == 'island': island(p, W * 0.25, H * 0.5, Ms * 0.6); boat(p, W * 0.45, H * 0.7, Ms * 0.4)
        elif arg != 'island': p.text('Oliver Deveau goes aboard', W / 2, H * 0.12, 60)
    elif kind == 'deck':
        wheel(p, Px, Py, Ps * 0.9); p.text('lifeboat: GONE', Px, Py + Ps * 0.48, 52, ORANGE); character(p, Cx, Cy, Cs, 'scared')
    elif kind == 'food':
        for i, x in enumerate((-0.35, 0, 0.35)): crate(p, Mx + x * Ms, My + Ms * 0.15, Ms * 0.9)
        for x in (-0.18, 0.18): jug(p, Mx + x * Ms, My - Ms * 0.12, Ms * 0.7)
        head('Food & water for 6 months')
    elif kind == 'items':
        if arg == 'clothes':
            boot(p, Mx - Ms * 0.4, My, Ms); boot(p, Mx - Ms * 0.25, My, Ms); sewing(p, Mx + Ms * 0.25, My, Ms * 1.2)
            head('Everything left behind')
        else:
            missing(p, Mx - Ms * 0.35, My, Ms * 0.9, 'sextant'); missing(p, Mx, My, Ms * 0.9, 'box'); missing(p, Mx + Ms * 0.35, My, Ms * 0.9, 'box')
            for t, x in (('sextant', -0.35), ('chronometer', 0), ('papers', 0.35)): p.text(t, Mx + x * Ms, My + Ms * 0.24, 44, DARK)
            head('Missing', ORANGE, 84)
    elif kind == 'water':
        hold(p, Mx, My + 20 * u, Ms * 0.95, 0.3 if arg == 'hold' else 0.42, arg == 'rising')
    elif kind == 'pump':
        pump(p, Px, Py, Ps, arg == 'clog'); character(p, Cx, Cy, Cs, 'think')
        p.text('pump taken apart' if arg == 'broken' else 'clogged?', Px, Py - Ps * 0.5, 52, ORANGE)
    elif kind == 'rod':
        rod(p, Px, Py, Ps); character(p, Cx, Cy, Cs, 'curious', 'point'); p.text('sounding rod', Px, Py - Ps * 0.45, 52)
    elif kind == 'slate':
        slate(p, Mx, My, Ms, ['25 Nov 1872', '8 a.m.', 'Santa Maria Island']); head('The last entry')
    elif kind == 'clock':
        calendar(p, Mx, My + 20 * u, Ms); head('9+ days adrift', ORANGE, 80)
    elif kind == 'tow':
        ship(p, Mx, My + 30 * u, Ms * 0.7); p.text('Next stop: Gibraltar', W * 0.5, H * 0.14, 72, ORANGE)
    elif kind == 'court':
        court(p, Mx, My + Ms * 0.1, Ms * 0.9); head('Gibraltar, 1872: the hearing')
    elif kind == 'sword':
        sword(p, Px, Py, Ps * 1.1); character(p, Cx, Cy, Cs, 'curious'); p.text('tested: NOT blood', Px, Py + Ps * 0.3, 56, ORANGE)
    elif kind == 'coins':
        coins(p, Px, Py, Ps); character(p, Cx, Cy, Cs, 'think'); p.text('salvage reward', Px, Py + Ps * 0.42, 50)
    elif kind == 'pirate':
        ship(p, Mx, My + 30 * u, Ms * 0.75, 'normal', flag=True); head('Pirates? Nothing was stolen.')
    elif kind == 'monster':
        tentacles(p, Px, Py, Ps); character(p, Cx, Cy, Cs, 'scared'); head('Sea monster?!')
    elif kind == 'book':
        if arg == 'doyle': book(p, Px, Py, Ps, "J. Habakuk Jephson's Statement", '1884 · A. Conan Doyle'); character(p, Cx, Cy, Cs, 'curious', 'point')
        else: book(p, Px, Py, Ps, 'the "MARIE" Celeste', 'fiction'); character(p, Cx, Cy, Cs, 'think')
    elif kind == 'tea':
        cup(p, Px, Py, Ps * 1.2); p.text('FICTION', Px, Py - Ps * 0.42, 80, ORANGE); character(p, Cx, Cy, Cs, 'shock')
    elif kind == 'vapor':
        hold(p, Mx, My + 40 * u, Ms * 0.95, 0.15); vapor(p, Mx, My - Ms * 0.1, Ms * 0.9); head('Alcohol fumes building up')
    elif kind == 'rope':
        if arg == 'snap':
            ship(p, W * 0.7, H * 0.45, Ms * 0.5); boat(p, W * 0.25, H * 0.65, Ms * 0.45); rope(p, W * 0.33, H * 0.64, W * 0.55, H * 0.52, True)
            p.text('SNAP', W * 0.45, H * 0.3, 90, ORANGE)
        else:
            ship(p, W * 0.66, H * 0.45, Ms * 0.5); boat(p, W * 0.25, H * 0.65, Ms * 0.45); rope(p, W * 0.33, H * 0.64, W * 0.5, H * 0.52)
            head('Tied on, just in case?')
    elif kind == 'lab':
        cubes(p, Mx, My + 20 * u, Ms * 0.95); head('2006: a test at University College London', sz=56)
    elif kind == 'fire':
        cubes(p, Mx, My + Ms * 0.15, Ms * 0.9); fire(p, Mx, My + Ms * 0.1, Ms * 0.8); head('A wave of flame... no burns', ORANGE)
    elif kind == 'chrono':
        clockface(p, Px, Py, Ps); character(p, Cx, Cy, Cs, 'think'); p.text('wrong time = wrong place', Px, Py + Ps * 0.42, 48, ORANGE)
    elif kind == 'wreck':
        ship(p, Mx, My, Ms * 0.6, 'torn'); reef(p, Mx, My + Ms * 0.12, Ms * 0.9); head('1885: wrecked on purpose near Haiti')
    else:
        character(p, W / 2, H / 2, Cs, 'curious')
    return img

# ---- L08 additions: lighthouse / Flannan Isles kit ----
NIGHT = (58, 60, 64)
def beam(p, cx, cy, s, on=True):
    if not on: return
    for sg in (-1, 1):
        p.poly([(cx, cy), (cx + sg * s * 1.1, cy - s * 0.18), (cx + sg * s * 1.1, cy + s * 0.12)], fill=(250, 214, 170), w=2, col=ORANGE)
def lh(p, cx, cy, s, on=True):
    beam(p, cx, cy - s * 0.38, s, on)
    lighthouse(p, cx, cy, s)
    if not on:
        p.poly([(cx - s * 0.08, cy - s * 0.45), (cx + s * 0.08, cy - s * 0.45), (cx + s * 0.08, cy - s * 0.3), (cx - s * 0.08, cy - s * 0.3)], fill=(90, 90, 92), w=4)
def rain(p, W, H, n=70):
    for i in range(n):
        x = p.r.uniform(0, W); y = p.r.uniform(0, H * 0.85)
        p.line([(x, y), (x - 18 * p.u, y + 46 * p.u)], 2, GRAY, passes=1)
def bigwave(p, cx, cy, s):
    pts = [(cx - s * 0.7, cy + s * 0.3)]
    for i in range(25):
        t = i / 24; pts.append((cx - s * 0.7 + t * s * 1.3, cy + s * 0.3 - math.sin(t * math.pi) ** 1.5 * s * 0.75 - (s * 0.15 if t > 0.6 else 0) * math.sin((t - 0.6) / 0.4 * math.pi)))
    pts += [(cx + s * 0.6, cy + s * 0.3)]
    p.poly(pts, fill=(120, 130, 136), w=6, hatch=11)
    for k in range(5):
        x = cx + s * (0.05 + k * 0.08); y = cy - s * 0.42 + k * s * 0.03
        p.ellipse(x, y, s * 0.04, s * 0.025, fill=WHITE, w=2)
def cliff(p, cx, cy, s):
    p.poly([(cx - s * 0.6, cy + s * 0.35), (cx - s * 0.6, cy - s * 0.25), (cx - s * 0.1, cy - s * 0.3), (cx + s * 0.05, cy - s * 0.05), (cx + s * 0.15, cy + s * 0.35)], fill=(140, 136, 128), w=5, hatch=12)
    sea(p, cx - s * 0.1, cx + s * 0.7, cy + s * 0.25, s, 3)
def coat(p, cx, cy, s, col=(60, 62, 64)):
    p.line([(cx - s * 0.3, cy - s * 0.42), (cx + s * 0.3, cy - s * 0.42)], 7)
    p.poly([(cx - s * 0.06, cy - s * 0.4), (cx + s * 0.06, cy - s * 0.4), (cx + s * 0.2, cy + s * 0.32), (cx - s * 0.2, cy + s * 0.32)], fill=col, w=4)
    p.line([(cx, cy - s * 0.38), (cx, cy + s * 0.3)], 2, LIGHT, passes=1)
def hook(p, cx, cy, s):
    p.arc(cx, cy, s * 0.04, s * 0.05, 0, 180, 4)
def doc(p, cx, cy, s, lines, stamp=None):
    w, h = s * 0.62, s * 0.8
    p.poly([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)], fill=WHITE, w=5)
    for i, t in enumerate(lines): p.text(t, cx, cy - h * 0.32 + i * h * 0.14, 40 * s / 600, INK if i == 0 else DARK)
    for i in range(4): p.line([(cx - w * 0.38, cy + h * 0.15 + i * h * 0.07), (cx + w * 0.38, cy + h * 0.15 + i * h * 0.07)], 2, LIGHT, passes=1)
    if stamp:
        p.ellipse(cx + w * 0.18, cy + h * 0.28, s * 0.16, s * 0.08, None, 6, ORANGE); p.text(stamp, cx + w * 0.18, cy + h * 0.28, 52 * s / 600, ORANGE)
def bed(p, cx, cy, s):
    p.poly([(cx - s * 0.35, cy), (cx + s * 0.35, cy), (cx + s * 0.35, cy + s * 0.12), (cx - s * 0.35, cy + s * 0.12)], fill=(150, 140, 125), w=4)
    p.poly([(cx - s * 0.33, cy - s * 0.06), (cx + s * 0.1, cy - s * 0.1), (cx + s * 0.33, cy - s * 0.02), (cx - s * 0.2, cy + s * 0.02)], fill=WHITE, w=3)
    p.line([(cx - s * 0.35, cy - s * 0.2), (cx - s * 0.35, cy + s * 0.25)], 6); p.line([(cx + s * 0.35, cy - s * 0.1), (cx + s * 0.35, cy + s * 0.25)], 6)
def lamp(p, cx, cy, s):
    p.poly([(cx - s * 0.12, cy + s * 0.25), (cx + s * 0.12, cy + s * 0.25), (cx + s * 0.08, cy), (cx - s * 0.08, cy)], fill=(140, 136, 128), w=4)
    p.ellipse(cx, cy - s * 0.12, s * 0.1, s * 0.14, fill=(250, 214, 170), w=4)
    p.poly([(cx - s * 0.12, cy - s * 0.28), (cx + s * 0.12, cy - s * 0.28), (cx + s * 0.08, cy - s * 0.33), (cx - s * 0.08, cy - s * 0.33)], fill=DARK, w=3)
def gate(p, cx, cy, s):
    for i in range(7): p.line([(cx - s * 0.36 + i * s * 0.12, cy - s * 0.3), (cx - s * 0.36 + i * s * 0.12, cy + s * 0.3)], 6)
    for y in (-0.2, 0.2): p.line([(cx - s * 0.4, cy + y * s), (cx + s * 0.4, cy + y * s)], 6)
def steps(p, cx, cy, s):
    cliff(p, cx, cy, s)
    for i in range(10):
        x = cx - s * 0.05 - i * s * 0.05; y = cy + s * 0.28 - i * s * 0.055
        p.line([(x - s * 0.05, y), (x + s * 0.03, y)], 4, ORANGE, passes=1)
def scotland(p, cx, cy, s):
    p.poly([(cx + s * 0.05, cy + s * 0.4), (cx - s * 0.05, cy + s * 0.15), (cx + s * 0.02, cy - s * 0.05), (cx - s * 0.04, cy - s * 0.3), (cx + s * 0.1, cy - s * 0.42), (cx + s * 0.3, cy - s * 0.38), (cx + s * 0.28, cy - s * 0.1), (cx + s * 0.38, cy + s * 0.1), (cx + s * 0.3, cy + s * 0.4)], fill=(205, 198, 186), w=5, hatch=16)
    p.poly([(cx - s * 0.2, cy - s * 0.35), (cx - s * 0.1, cy - s * 0.38), (cx - s * 0.12, cy - s * 0.2), (cx - s * 0.2, cy - s * 0.12)], fill=(205, 198, 186), w=4)
    for dx, dy in ((-0.36, -0.3), (-0.34, -0.27), (-0.38, -0.26)): p.ellipse(cx + dx * s, cy + dy * s, s * 0.012, s * 0.01, fill=ORANGE, w=2)
    p.line([(cx - s * 0.33, cy - s * 0.28), (cx - s * 0.2, cy - s * 0.28)], 3, ORANGE, passes=1)
    p.text('Flannan Isles', cx - s * 0.36, cy - s * 0.36, 40 * s / 600, ORANGE); p.text('Lewis', cx - s * 0.06, cy - s * 0.42, 34 * s / 600, DARK)
    p.text('SCOTLAND', cx + s * 0.16, cy + s * 0.05, 40 * s / 600, DARK)

def compose(key, text, W, H, seed):
    kind, _, arg = key.partition(':')
    NEW = {'lh', 'hebmap', 'keepers', 'moore', 'hesperus', 'steps', 'door', 'stopclock', 'beds', 'lamp', 'oilskins', 'flag', 'storm', 'landing', 'wave', 'report', 'poem', 'fakelog', 'muirhead', 'cal', 'theory', 'calm', 'flare', 'slate', 'people'}
    if kind not in NEW and not (kind == 'char' and arg.split('|')[-1] in ('lh', 'wave', 'coat', 'storm', 'stop', 'fake')):
        return compose0(key, text, W, H, seed)
    img = paper(W, H); u = min(W, H) / 1080
    p = Pen(img, seed, u); lay = L(W, H); v = lay['v']
    Px, Py, Ps = lay['P']; Cx, Cy, Cs = lay['C']; Mx, My, Ms = lay['M']; Tx, Ty = lay['T']
    def head(t, col=INK, sz=64): p.text(t, Tx, Ty + (40 * u if v else 0), sz, col, maxw=(W / u) * 0.9)
    if kind == 'char':
        emo, _, pr = arg.partition('|')
        if pr == 'lh': lh(p, Px, Py + Ps * 0.05, Ps * 0.9)
        elif pr == 'wave': bigwave(p, Px, Py, Ps)
        elif pr == 'coat': coat(p, Px, Py, Ps * 0.8, ORANGE)
        elif pr == 'storm': rain(p, W, H); sea(p, 0, W, H * 0.8, H, 4)
        elif pr == 'stop': clockface(p, Px, Py, Ps, (3, 9))
        elif pr == 'fake': doc(p, Px, Py, Ps, ['Logbook?', '"storm... crying..."'], 'FAKE')
        character(p, Cx, Cy, Cs, emo)
    elif kind == 'lh':
        if arg in ('dark', 'night'):
            p.d.rectangle([0, 0, W, H * 0.62], fill=NIGHT)
        if arg == 'dark':
            lh(p, W * (0.5 if v else 0.62), H * 0.48, Ms * 0.75, False); ship(p, W * 0.2, H * 0.66, Ms * 0.25)
            p.text('15 Dec 1900: the light is OUT', Tx, Ty + (40 * u if v else 0), 60, ORANGE)
        elif arg == 'night':
            lh(p, Mx, My + 30 * u, Ms * 0.8, True); p.text('Every night, it must shine.', Tx, Ty + (40 * u if v else 0), 64, WHITE)
        else:
            lh(p, Mx, My + 40 * u, Ms * 0.8, arg != 'off'); head({'far': 'Eilean Mòr, Flannan Isles', 'new': 'New lighthouse, 1899', 'off': 'Silent'}.get(arg, 'The lighthouse'))
    elif kind == 'hebmap':
        scotland(p, Mx + Ms * 0.1, My + 90 * u, Ms * (1.0 if not v else 0.8)); head('20 miles west of the Isle of Lewis')
    elif kind == 'keepers':
        names = [('James Ducat', 'principal keeper'), ('Thomas Marshall', 'assistant'), ('Donald MacArthur', 'occasional keeper')]
        for i, (n, r) in enumerate(names):
            x = Mx + (i - 1) * Ms * (0.42 if not v else 0.32)
            person(p, x, My, Ms * 0.42, WHITE, (70, 68, 66) if i != 2 else ORANGE)
            p.text(n, x, My + Ms * 0.3, 42, INK); p.text(r, x, My + Ms * 0.38, 32, DARK)
        head('Three keepers', sz=72)
    elif kind == 'moore':
        captain(p, Px, Py, Ps * 0.9, 'Joseph Moore', 'relief keeper'); character(p, Cx, Cy, Cs, arg or 'curious')
    elif kind == 'muirhead':
        captain(p, Px, Py, Ps * 0.9, 'Robert Muirhead', 'superintendent'); character(p, Cx, Cy, Cs, 'think')
    elif kind == 'hesperus':
        ship(p, W * 0.66, H * 0.45, Ms * 0.6); lh(p, W * 0.24, H * 0.5, Ms * 0.45, False); head('The Hesperus · 26 December 1900', sz=60)
    elif kind == 'flare':
        p.d.rectangle([0, 0, W, H * 0.62], fill=NIGHT); ship(p, W * 0.62, H * 0.5, Ms * 0.55); lh(p, W * 0.22, H * 0.5, Ms * 0.4, False)
        burst(p, W * 0.62, H * 0.16, Ms * 0.18); p.text('No answer.', W * 0.3, H * 0.15, 70, WHITE)
    elif kind == 'steps':
        steps(p, Mx, My + 30 * u, Ms * 0.9); lh(p, Mx - Ms * 0.25, My - Ms * 0.33, Ms * 0.3); head('The climb up from the landing')
    elif kind == 'door':
        gate(p, Px, Py, Ps * 0.8); character(p, Cx, Cy, Cs, 'scared'); p.text('gate & door: shut', Px, Py - Ps * 0.42, 52, ORANGE)
    elif kind == 'stopclock':
        clockface(p, Px, Py, Ps, (3, 9)); character(p, Cx, Cy, Cs, 'shock'); p.text('the clock had stopped', Px, Py + Ps * 0.42, 52, ORANGE)
    elif kind == 'beds':
        bed(p, Mx - Ms * 0.25, My + Ms * 0.1, Ms * 0.5); bed(p, Mx + Ms * 0.25, My + Ms * 0.1, Ms * 0.5); head('Beds unmade. Fire cold.')
    elif kind == 'lamp':
        lamp(p, Px, Py, Ps * 1.1); character(p, Cx, Cy, Cs, 'think'); p.text('cleaned & refilled', Px, Py + Ps * 0.4, 52, ORANGE)
    elif kind == 'oilskins':
        My = My + Ms * 0.12
        hook(p, Mx - Ms * 0.3, My - Ms * 0.3, Ms); hook(p, Mx, My - Ms * 0.3, Ms); hook(p, Mx + Ms * 0.3, My - Ms * 0.3, Ms)
        coat(p, Mx + Ms * 0.3, My, Ms * 0.6, ORANGE); p.text('gone', Mx - Ms * 0.3, My, 60, GRAY); p.text('gone', Mx, My, 60, GRAY)
        head('One coat left behind', ORANGE, 72)
    elif kind == 'flag':
        p.line([(Px, Py + Ps * 0.4), (Px, Py - Ps * 0.45)], 7); character(p, Cx, Cy, Cs, 'curious'); p.text('no flag', Px + Ps * 0.15, Py - Ps * 0.35, 56, ORANGE)
    elif kind == 'storm':
        p.d.rectangle([0, 0, W, H * 0.6], fill=(150, 152, 156)); rain(p, W, H, 110); lh(p, Mx, My + 40 * u, Ms * 0.7, arg != 'off'); head({'gale': 'December gales', 'off': 'Wild weather'}.get(arg, 'Storm'), WHITE)
    elif kind == 'calm':
        lh(p, Mx, My + 40 * u, Ms * 0.75); head('Back to normal… almost')
    elif kind == 'landing':
        cliff(p, Mx, My + 30 * u, Ms * 0.95)
        for i in range(4): p.line([(Mx - Ms * 0.45 + i * Ms * 0.08, My - Ms * 0.18), (Mx - Ms * 0.4 + i * Ms * 0.09, My - Ms * 0.1 - (i % 2) * Ms * 0.06)], 5, ORANGE)
        p.text('railings bent · box of ropes gone · turf torn', Mx, My + Ms * 0.48, 46, ORANGE, maxw=(W / u) * 0.85); head('The west landing')
    elif kind == 'wave':
        cliff(p, W * 0.3, H * 0.55, Ms * 0.8); bigwave(p, W * 0.66, H * 0.5, Ms * 0.85)
        for i in range(2): person(p, W * (0.36 + i * 0.05), H * 0.36, Ms * 0.12, WHITE, (70, 68, 66))
        if arg != 'nopeople': person(p, W * 0.24, H * 0.3, Ms * 0.12, WHITE, ORANGE)
        head({'run': 'Did one of them run to warn them?', 'giant': 'A wave far bigger than the rest'}.get(arg, 'A freak wave?'), INK)
    elif kind == 'report':
        doc(p, Px, Py, Ps * 1.1, ['Report', 'R. Muirhead', '8 January 1901']); character(p, Cx, Cy, Cs, 'think', 'point')
    elif kind == 'poem':
        book(p, Px, Py, Ps, 'Flannan Isle', 'a poem · 1912'); character(p, Cx, Cy, Cs, 'curious'); p.text('beautiful… but fiction', Px, Py + Ps * 0.45, 48, ORANGE)
    elif kind == 'fakelog':
        doc(p, Px, Py, Ps * 1.1, ['"Log entries"', 'storm · crying · praying'], 'FAKE'); character(p, Cx, Cy, Cs, 'shock')
    elif kind == 'cal':
        calendar(p, Mx, My + 20 * u, Ms, int(arg)); head(f'{arg} days without a light', ORANGE, 76)
    elif kind == 'slate':
        slate(p, Mx, My + 20 * u, Ms, ['15 Dec 1900', 'morning', 'last notes']); head('The slate')
    elif kind == 'people':
        people(p, Mx, My + 40 * u, Ms * 0.9, int(arg)); lh(p, W * 0.85, H * 0.55, Ms * 0.4); head('Three men, alone at sea', sz=72)
    elif kind == 'theory':
        t = {'monster': ('Sea serpent?', lambda: tentacles(p, Px, Py, Ps)), 'spies': ('Foreign spies?', lambda: bubble(p, Px, Py, Ps, 'spies?')),
             'pirates': ('Ghost pirates?', lambda: pirateflag(p, Px, Py, Ps)), 'fight': ('A fight?', lambda: burst(p, Px, Py, Ps * 0.7))}[arg]
        t[1](); character(p, Cx, Cy, Cs, 'scared' if arg != 'fight' else 'sad'); head(t[0], ORANGE, 76)
    return img
