import sys, json, subprocess, math, numpy as np, soundfile as sf
sys.path.insert(0, '/home/claude/L07')
from scenes import compose
from PIL import Image
# usage: build.py script.py auddir W H out.mp4 [gap]
mod, aud, W, H, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
GAP = float(sys.argv[6]) if len(sys.argv) > 6 else 0.3
SHORT = H > W
ns = {}; exec(open(mod).read(), ns); S = ns['S']
SR = 24000; FPS = 10
segs = []; t = 0.0; voice = []
for i, (v, tx) in enumerate(S):
    if tx:
        a, sr = sf.read(f'{aud}/'+__import__('hashlib').md5(tx.encode()).hexdigest()[:12]+'.wav'); assert sr == SR
        d = len(a) / SR + GAP
        voice.append((t, a))
    else:
        d = 1.6
    segs.append((t, d, v, tx)); t += d
total = t + 0.6
N = int(total * SR)
vo = np.zeros(N, np.float32)
for st, a in voice:
    s0 = int(st * SR); vo[s0:s0 + len(a)] += a.astype(np.float32)
# music bed: soft minor pad + slow pulse (own synth, no copyright)
tt = np.arange(N) / SR
chords = [(110.0, 130.81, 164.81), (98.0, 116.54, 146.83), (87.31, 110.0, 130.81), (82.41, 98.0, 123.47)]
mus = np.zeros(N, np.float32)
cl = 8.0
for k in range(int(total / cl) + 1):
    s0 = int(k * cl * SR); s1 = min(N, int((k + 1) * cl * SR + SR));
    if s0 >= N: break
    seg = tt[s0:s1] - k * cl
    env = np.minimum(1, seg / 2.0) * np.minimum(1, np.maximum(0, (cl + 1 - seg)) / 2.0)
    for f in chords[k % 4]:
        mus[s0:s1] += (np.sin(2 * np.pi * f * seg) + 0.3 * np.sin(2 * np.pi * 2 * f * seg + 0.5)) * env * 0.05
mus += 0.012 * np.sin(2 * np.pi * 55 * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * tt / 4))
# whoosh on cards
rng = np.random.default_rng(1)
for st, d, v, tx in segs:
    if not tx:
        s0 = int(st * SR); n = int(1.0 * SR); e = np.sin(np.linspace(0, np.pi, n)) ** 2
        noise = np.convolve(rng.normal(0, 1, n), np.ones(40) / 40, 'same') * e * 0.25
        mus[s0:s0 + n] += noise[:max(0, min(n, N - s0))]
mix = vo + mus * (0.35 if not SHORT else 0.3)
mix = mix / max(1e-6, np.abs(mix).max()) * 0.9
sf.write(out + '.wav', mix, SR)
# captions (ASS)
def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f'{h}:{m:02d}:{s:05.2f}'
fs = 64 if not SHORT else 72
mv = 70 if not SHORT else 330
ass = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "", "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       f"Style: D,Patrick Hand,{fs},&H00FFFFFF,&H00FFFFFF,&H001E2022,&H64000000,0,0,0,0,100,100,0,0,1,5,0,2,80,80,{mv},1",
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for st, d, v, tx in segs:
    if not tx: continue
    words = tx.split(); spk = d - GAP
    chunk = 7 if not SHORT else 4
    groups = [words[i:i + chunk] for i in range(0, len(words), chunk)]
    if len(groups) > 1 and len(groups[-1]) <= 2: groups[-2] += groups[-1]; groups.pop()
    wc = len(words); c = 0
    for g in groups:
        a = st + spk * c / wc; c += len(g); b = st + spk * c / wc
        ass.append(f"Dialogue: 0,{ts(a)},{ts(b)},D,,0,0,0,,{' '.join(g)}")
open(out + '.ass', 'w').write('\n'.join(ass))
# video frames piped
cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
       '-i', out + '.wav', '-vf', f"fps=30,subtitles={out}.ass:fontsdir=/home/claude/fonts", '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p',
       '-c:a', 'aac', '-b:a', '160k', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-shortest', out]
pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
frames_done = 0
for k, (st, d, v, tx) in enumerate(segs):
    var = [compose(v, tx, W, H, 1000 * k + j) for j in range(3)]
    n = int(round((st + d) * FPS)) - frames_done
    if k == len(segs) - 1: n = int(round(total * FPS)) - frames_done
    zin = (k % 2 == 0)
    shots = 1 if not SHORT else max(1, int(d // 2.5))  # shorts: new framing every ~2.5 s
    for f in range(n):
        im = var[(f // 2) % 3]
        shot = min(shots - 1, f * shots // max(1, n))
        prog = f / max(1, n - 1)
        z = 1.0 + 0.05 * (prog if zin else 1 - prog)
        if SHORT and shots > 1: z += 0.08 * (shot % 2)
        if z > 1.001:
            cw, ch = W / z, H / z
            ox = (W - cw) * (0.5 + (0.2 if (shot % 3 == 1) else -0.2 if (shot % 3 == 2) else 0)); oy = (H - ch) / 2
            im = im.resize((W, H), Image.BILINEAR, box=(ox, oy, ox + cw, oy + ch))
        pr.stdin.write(im.tobytes())
    frames_done += n
    print(k, round(st, 1), flush=True)
pr.stdin.close(); pr.wait()
json.dump([(s[0], s[1], s[2]) for s in segs], open(out + '.segs.json', 'w'))
print('DONE', total)
