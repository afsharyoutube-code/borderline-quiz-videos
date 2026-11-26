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

def compose(key, text, W, H, seed):
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
