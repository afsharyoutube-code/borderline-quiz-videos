#!/usr/bin/env python3
"""What-if geography long-video engine (16:9, 1920x1080).
Usage: python3 whatif.py spec.json out.mp4 [--thumb thumb.jpg]
Scenes: map (world/region, sea level static or animated), bars, timeline, card.
Elevation: ETOPO20 (NOAA ETOPO5-derived, 20 arc-min) at /root/elev/etopo20.npz.
Borders: historical-basemaps world_2010.geojson (thin lines only)."""
import json, sys, os, subprocess, tempfile, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import map_coordinates

W, H, FPS = 1920, 1080, 24
NAVY = (12, 22, 46); ORANGE = (255, 106, 19); CREAM = (250, 244, 230); YEL = (255, 210, 63)
F = lambda p, s: ImageFont.truetype(p, s)
BEBAS, M900, M800, LG = '/tmp/bebas.ttf', '/tmp/m900.ttf', '/tmp/m800.ttf', '/tmp/lg.ttf'

E = np.load('/root/elev/etopo20.npz'); Z = E['z']; LAT = E['lat']; LON = E['lon']
# roll lon 20..380 -> -180..180
LONr = np.where(LON > 180, LON - 360, LON); order = np.argsort(LONr)
Z = Z[:, order]; LONr = LONr[order]
# known ETOPO5 artefact: false below-sea pixels inland in the Ganges-Brahmaputra delta
_m = (LAT[:, None] > 21.9) & (LAT[:, None] < 25.0) & (LONr[None, :] > 88.3) & (LONr[None, :] < 91.5)
Z = np.where(_m & (Z <= 0), 5.0, Z)
GEO = json.load(open('/root/historical-basemaps/geojson/world_2010.geojson'))

def sample(box, w, h):
    lo0, lo1, la0, la1 = box
    lons = np.linspace(lo0, lo1, w); lats = np.linspace(la1, la0, h)
    gx = (lons - LONr[0]) / (LONr[1] - LONr[0]); gy = (lats - LAT[0]) / (LAT[1] - LAT[0])
    GX, GY = np.meshgrid(gx, gy)
    return map_coordinates(Z, [GY, GX], order=1, mode='nearest')

def colorize(z, sea, shade):
    out = np.zeros(z.shape + (3,), np.float32)
    ocean = z <= 0
    d = np.clip(-z / 6000, 0, 1)[..., None]
    out[:] = (np.array([28, 62, 112]) * (1 - d) + np.array([10, 26, 58]) * d)
    stops = [(0, (86, 140, 74)), (300, (150, 160, 90)), (1000, (170, 140, 95)), (2500, (130, 100, 80)), (4000, (235, 232, 225))]
    zl = np.clip(z, 0, 6000)
    land = np.zeros_like(out)
    for (a, ca), (b, cb) in zip(stops, stops[1:] + [(9000, (245, 245, 245))]):
        m = (zl >= a) & (zl < b); t = ((zl - a) / (b - a))[..., None]
        land = np.where(m[..., None], np.array(ca) * (1 - t) + np.array(cb) * t, land)
    land = land * shade[..., None]
    out = np.where(ocean[..., None], out, land)
    if sea > 0:
        fl = (~ocean) & (z <= sea)
        out = np.where(fl[..., None], np.array([46, 150, 222]) * 0.85 + land * 0.15, out)
    return np.clip(out, 0, 255).astype(np.uint8)

def hillshade(z):
    gy, gx = np.gradient(z.astype(np.float32))
    s = 1 - 0.0018 * (gx - gy); return np.clip(s, 0.75, 1.15)

def proj(box, rect):
    lo0, lo1, la0, la1 = box; x0, y0, x1, y1 = rect
    return lambda lon, lat: (x0 + (lon - lo0) / (lo1 - lo0) * (x1 - x0), y0 + (la1 - lat) / (la1 - la0) * (y1 - y0))

def draw_borders(img, box, rect, highlight=()):
    dr = ImageDraw.Draw(img, 'RGBA'); P = proj(box, rect)
    lo0, lo1, la0, la1 = box
    def rings(g):
        if g['type'] == 'Polygon': return g['coordinates']
        if g['type'] == 'MultiPolygon': return [r for p in g['coordinates'] for r in p]
        return []
    for f in GEO['features']:
        name = f['properties'].get('NAME') or ''
        hl = name in highlight
        for r in rings(f['geometry']):
            xs = [p[0] for p in r]; ys = [p[1] for p in r]
            if max(xs) < lo0 or min(xs) > lo1 or max(ys) < la0 or min(ys) > la1: continue
            pts = [P(x, y) for x, y in r]
            if len(pts) > 2:
                dr.line(pts + [pts[0]], fill=(255, 106, 19, 255) if hl else (255, 255, 255, 70), width=4 if hl else 1)

def text_box(dr, xy, txt, font, fg=NAVY, bg=CREAM, pad=12, anchor='la'):
    b = dr.textbbox(xy, txt, font=font, anchor=anchor)
    dr.rounded_rectangle((b[0] - pad, b[1] - pad, b[2] + pad, b[3] + pad), 10, fill=bg)
    dr.text(xy, txt, font=font, fill=fg, anchor=anchor)

def chrome(img, sc, chapter):
    dr = ImageDraw.Draw(img, 'RGBA')
    dr.rectangle((0, 0, W, 150), fill=NAVY + (235,))
    if chapter: dr.text((60, 30), chapter.upper(), font=F(M800, 30), fill=ORANGE)
    if sc.get('title'): dr.text((60, 68), sc['title'], font=F(BEBAS, 72), fill=CREAM)
    dr.text((W - 60, 40), 'BORDERLINE QUIZ', font=F(BEBAS, 44), fill=CREAM, anchor='ra')
    if sc.get('tag'):
        text_box(dr, (60, H - 50), sc['tag'], F(M800, 24), fg=CREAM, bg=(12, 22, 46, 220), anchor='ls')
    if sc.get('note', True) and sc['type'] == 'map':
        dr.text((W - 60, H - 50), 'Simplified: sea raised evenly · elevation NOAA ETOPO', font=F(M800, 20), fill=(255, 255, 255, 190), anchor='rs')

def map_frame(sc, sea, cache):
    box = tuple(sc.get('box', [-180, 180, -58, 84]))
    key = box
    if key not in cache:
        rect = (0, 150, W, H)
        bw, bh = W, H - 150
        z = sample(box, bw, bh)
        cache[key] = (z, hillshade(z), rect)
    z, sh, rect = cache[key]
    img = Image.new('RGB', (W, H), NAVY)
    img.paste(Image.fromarray(colorize(z, sea, sh)), (0, 150))
    draw_borders(img, box, rect, sc.get('highlight', ()))
    dr = ImageDraw.Draw(img, 'RGBA'); P = proj(box, rect)
    for p in sc.get('pins', []):
        x, y = P(p['lon'], p['lat'])
        dr.ellipse((x - 11, y - 11, x + 11, y + 11), fill=ORANGE, outline=CREAM, width=4)
        dx = p.get('dx', 24); anc = 'lm' if dx >= 0 else 'rm'
        text_box(dr, (x + dx, y + p.get('dy', 0)), p['label'], F(M800, 30), anchor=anc)
    if sc.get('big'):
        text_box(dr, (W // 2, H - 130), sc['big'], F(BEBAS, 84), fg=NAVY, bg=YEL, pad=18, anchor='mm')
    if sc.get('counter', True) and sea > 0:
        text_box(dr, (W - 60, 210), f'SEA LEVEL +{sea:.0f} m', F(BEBAS, 64), fg=CREAM, bg=(46, 150, 222), pad=16, anchor='ra')
    return img

def bars_frame(sc, t):
    img = Image.new('RGB', (W, H), NAVY); dr = ImageDraw.Draw(img, 'RGBA')
    rows = sc['rows']; mx = sc.get('max') or max(r[1] for r in rows)
    n = len(rows); top = 260; gap = (H - top - 160) / n
    for i, r in enumerate(rows):
        y = top + i * gap; bh = min(90, gap * 0.6)
        g = min(1, max(0, t * 1.6 - i * 0.25)); g = 1 - (1 - g) ** 3
        bw = (W - 1180) * (r[1] / mx) * g
        dr.text((80, y + bh / 2), r[0], font=F(M800, 38), fill=CREAM, anchor='lm')
        dr.rounded_rectangle((560, y, 560 + max(bw, 6), y + bh), 12, fill=tuple(r[3]) if len(r) > 3 else ORANGE)
        dr.text((580 + bw, y + bh / 2), r[2], font=F(BEBAS, 60), fill=YEL, anchor='lm')
    return img

def card_frame(sc, t):
    img = Image.new('RGB', (W, H), NAVY); dr = ImageDraw.Draw(img, 'RGBA')
    dr.text((W // 2, H // 2 - 40), sc['big'], font=F(BEBAS, sc.get('size', 150)), fill=YEL, anchor='mm')
    if sc.get('small'):
        for j, line in enumerate(sc['small'].split('\n')):
            dr.text((W // 2, H // 2 + 90 + j * 56), line, font=F(M800, 42), fill=CREAM, anchor='mm')
    return img

def timeline_frame(sc, t):
    img = Image.new('RGB', (W, H), NAVY); dr = ImageDraw.Draw(img, 'RGBA')
    pts = sc['points']; n = len(pts); y = 600
    dr.line((160, y, W - 160, y), fill=CREAM, width=6)
    for i, p in enumerate(pts):
        x = 160 + i * (W - 320) / (n - 1)
        on = t * (n + 0.5) > i
        dr.ellipse((x - 22, y - 22, x + 22, y + 22), fill=ORANGE if on else (80, 90, 120))
        dr.text((x, y - 70), p[0], font=F(BEBAS, 64), fill=YEL if on else (120, 130, 160), anchor='ms')
        if on:
            for j, line in enumerate(p[1].split('\n')):
                dr.text((x, y + 70 + j * 44), line, font=F(M800, 32), fill=CREAM, anchor='mt')
    return img

def render_scene(sc, chapter, t, cache):
    ty = sc['type']
    if ty == 'map':
        s = sc.get('sea', 65)
        if isinstance(s, list): s = s[0] + (s[1] - s[0]) * min(1, t * 1.15)
        img = map_frame(sc, s, cache)
    elif ty == 'bars': img = bars_frame(sc, t)
    elif ty == 'timeline': img = timeline_frame(sc, t)
    else: img = card_frame(sc, t)
    chrome(img, sc, chapter)
    return img

def animated(sc):
    return (sc['type'] == 'map' and isinstance(sc.get('sea'), list)) or sc['type'] in ('bars', 'timeline')

def main():
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]
    tmp = tempfile.mkdtemp(prefix='wi_'); cache = {}
    if '--thumb' in sys.argv:
        th = spec['thumb']; img = map_frame(th, th['sea'], cache)
        dr = ImageDraw.Draw(img, 'RGBA'); dr.rectangle((0, 0, W, 150), fill=NAVY)
        text_box(dr, (W // 2, 560), th['text'], F(BEBAS, 260), fg=NAVY, bg=YEL, pad=30, anchor='mm')
        img.crop((0, 0, W, H)).resize((1280, 720), Image.LANCZOS).save(sys.argv[sys.argv.index('--thumb') + 1], quality=90)
        print('thumb ok'); return
    from kokoro_onnx import Kokoro
    k = Kokoro('/root/models/kokoro-v1.0.onnx', '/root/models/voices-v1.0.bin')
    voice = spec.get('voice', 'am_michael'); speed = spec.get('speed', 1.0)
    audio = []; clips = []; chapters = []; tcur = 0.0; sr = 24000
    for ci, ch in enumerate(spec['chapters']):
        chapters.append((tcur, ch['name']))
        for si, sc in enumerate(ch['scenes']):
            s, sr = k.create(sc['say'], voice=voice, speed=speed, lang='en-us')
            pad = np.zeros(int(sr * sc.get('gap', 0.45)), np.float32)
            seg = np.concatenate([s.astype(np.float32), pad]); audio.append(seg)
            dur = len(seg) / sr; nf = max(1, round(dur * FPS)); tcur += nf / FPS
            clip = f'{tmp}/c{ci:02d}_{si:02d}.mp4'; label = ch.get('label', ch['name'])
            enc = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22', '-pix_fmt', 'yuv420p', '-r', str(FPS)]
            if animated(sc):
                p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-'] + enc + [clip], stdin=subprocess.PIPE)
                anim_n = min(nf, int(FPS * sc.get('anim_s', 6))); last = None
                for f in range(nf):
                    if f <= anim_n or last is None:
                        last = render_scene(sc, label, f / max(1, anim_n), cache).tobytes()
                    p.stdin.write(last)
                p.stdin.close(); p.wait()
            else:
                png = clip.replace('.mp4', '.png'); render_scene(sc, label, 1, cache).save(png)
                subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-framerate', str(FPS), '-i', png, '-frames:v', str(nf)] + enc + [clip], check=True)
            clips.append(clip)
            print(f'{ci}.{si} {dur:.1f}s', flush=True)
    a = np.concatenate(audio); n = len(a); tt = np.arange(n) / sr
    bed = sum(np.sin(2 * np.pi * f * tt) * w for f, w in ((110, .5), (164.8, .35), (220, .25), (277.2, .15)))
    bed *= (0.6 + 0.4 * np.sin(2 * np.pi * tt / 9)); bed = bed / np.abs(bed).max() * 0.035
    mix = np.clip(a * 0.95 + bed, -1, 1)
    import wave
    with wave.open(f'{tmp}/a.wav', 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((mix * 32767).astype(np.int16).tobytes())
    open(f'{tmp}/list.txt', 'w').write(''.join(f"file '{c}'\n" for c in clips))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{tmp}/list.txt', '-i', f'{tmp}/a.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', out], check=True)
    with open(out + '.chapters.txt', 'w') as fch:
        for t0, nm in chapters: fch.write(f'{int(t0 // 60)}:{int(t0 % 60):02d} {nm}\n')
    print('done', out, f'{tcur / 60:.1f} min')

if __name__ == '__main__':
    main()
