"""Netherlands Explained — explainer Short generator.
Usage: python3 make_short.py script.json out.mp4
script.json: {"voice":"af_heart","slides":[{"kicker":"STEP 1","big":"...","small":"...","say":"..."}]}
Each slide: voice line -> duration; text animates in; progress bar; brand look (navy/orange/cream).
"""
import json, sys, os, subprocess, tempfile, math
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont
from kokoro_onnx import Kokoro

W, H, FPS = 1080, 1920, 30
NV, OR, CR, MUT = (20, 33, 61), (255, 106, 19), (255, 247, 236), (150, 165, 195)
BEBAS, MONT = '/tmp/bebas.ttf', '/tmp/m800.ttf'

def font(p, s): return ImageFont.truetype(p, s)

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def ease(t): return 1 - (1 - min(max(t, 0), 1)) ** 3

def frame(sl, t, idx, n, global_p):
    im = Image.new('RGB', (W, H), NV); d = ImageDraw.Draw(im)
    for i in range(-H, W, 140):  # diagonal texture
        d.line([(i, H), (i + H * 0.35, 0)], fill=(27, 43, 79), width=34)
    # header
    d.rounded_rectangle([60, 120, 60 + 520, 200], radius=40, fill=OR)
    d.text((90, 132), 'NETHERLANDS EXPLAINED', font=font(BEBAS, 62), fill=NV)
    # kicker
    a = ease(t / 0.35)
    if sl.get('kicker'):
        d.text((80, 470 + (1 - a) * 40), sl['kicker'], font=font(MONT, 52), fill=OR)
    # big text
    fb = font(BEBAS, sl.get('size', 150))
    y = 560
    for k, line in enumerate(wrap(d, sl['big'], fb, W - 160)):
        ak = ease((t - 0.08 * k) / 0.4)
        d.text((80, y + (1 - ak) * 60), line, font=fb, fill=CR if ak > 0.05 else NV)
        y += int(fb.size * 0.95)
    # small text
    if sl.get('small'):
        fs = font(MONT, 50); y += 40
        as_ = ease((t - 0.35) / 0.4)
        for line in wrap(d, sl['small'], fs, W - 160):
            col = tuple(int(NV[c] + (CR[c] - NV[c]) * as_) for c in range(3))
            d.text((80, y), line, font=fs, fill=col); y += 66
    # footer: disclaimer + progress
    d.text((80, H - 230), 'General info, not legal advice. Sources in description.', font=font(MONT, 30), fill=MUT)
    d.rounded_rectangle([80, H - 160, W - 80, H - 140], radius=10, fill=(40, 58, 98))
    d.rounded_rectangle([80, H - 160, 80 + int((W - 160) * global_p), H - 140], radius=10, fill=OR)
    return im

def main(spec_path, out):
    spec = json.load(open(spec_path))
    k = Kokoro('/root/models/kokoro-v1.0.onnx', '/root/models/voices-v1.0.bin')
    voice, speed = spec.get('voice', 'af_heart'), spec.get('speed', 1.08)
    tmp = tempfile.mkdtemp()
    audio, durs, sr = [], [], 24000
    for sl in spec['slides']:
        s, sr = k.create(sl['say'], voice=voice, speed=speed, lang='en-us')
        pad = np.zeros(int(sr * 0.25), dtype=s.dtype)
        clip = np.concatenate([np.zeros(int(sr * 0.1), dtype=s.dtype), s, pad])
        audio.append(clip); durs.append(len(clip) / sr)
    wav = np.concatenate(audio); sf.write(f'{tmp}/vo.wav', wav, sr)
    total = sum(durs)
    # frames piped to ffmpeg
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-i', f'{tmp}/vo.wav', '-af', 'loudnorm=I=-15:TP=-1.5', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '30',
           '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-shortest', '-movflags', '+faststart', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    el = 0.0
    for i, (sl, dur) in enumerate(zip(spec['slides'], durs)):
        nf = int(round(dur * FPS))
        for f in range(nf):
            t = f / FPS
            p.stdin.write(frame(sl, t, i, len(durs), (el + t) / total).tobytes())
        el += dur
    p.stdin.close(); p.wait()
    print(out, round(total, 1), 's', os.path.getsize(out) // 1024, 'KB')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
