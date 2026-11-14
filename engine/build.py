#!/usr/bin/env python3
"""Borderline Quiz builder.
Usage: python3 tools/build.py specs/<id>.json [--render]
Reads a spec, writes voice lines + mixed audio to public/audio/<id>.wav,
writes props to out/<id>.props.json, and (with --render) renders out/<id>.mp4.
Spec format: see specs/README.md
"""
import json, sys, os, random, subprocess, math
import numpy as np, soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = json.load(open('data/countries.json'))
TIERS = json.load(open('data/tiers.json'))
SR = 24000
_K = None

def kokoro():
    global _K
    if _K is None:
        from kokoro_onnx import Kokoro
        m = os.path.expanduser('~/models')
        _K = Kokoro(f'{m}/kokoro-v1.0.onnx', f'{m}/voices-v1.0.bin')
    return _K

def tts(text, voice, speed):
    s, sr = kokoro().create(text, voice=voice, speed=speed, lang='en-us')
    idx = np.where(np.abs(s) > 0.01)[0]
    s = s[max(0, idx[0] - 500): idx[-1] + 1500]
    return s

def say_num(n):
    words = ['zero','one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen','twenty']
    return words[n] if n < len(words) else str(n)

REF = [('Portugal', 92212), ('Greece', 131990), ('the UK', 242495), ('Italy', 301336), ('Germany', 357114), ('Japan', 377930), ('Spain', 505992), ('France', 551695), ('Egypt', 1002450), ('Mexico', 1964375), ('India', 3287590)]

def fact(c, rnd):
    """Deterministic, data-backed facts only (no invented trivia)."""
    opts = []
    if c['capital']:
        opts.append((f"Its capital is {c['capital']}.", f"Capital: {c['capital']}"))
    b = c['borders']
    if c['landlocked']:
        opts.append(("It has no coastline at all!", "Landlocked: no coastline"))
    if len(b) == 0:
        opts.append(("It shares no land border with any country!", "No land borders"))
    elif len(b) == 1:
        opts.append((f"Its only land neighbor is {b[0]}.", f"Only neighbor: {b[0]}"))
    elif len(b) >= 6:
        opts.append((f"It borders {say_num(len(b))} countries!", f"Borders {len(b)} countries"))
    a = c['area']
    bigger = [r for r in REF if r[1] < a * 0.92 and r[0].replace('the ', '') != c['name']]
    smaller = [r for r in REF if r[1] > a * 1.08 and r[0].replace('the ', '') != c['name']]
    if bigger and a < 4000000:
        r = bigger[-1]; opts.append((f"It's bigger than {r[0]}.", f"Bigger than {r[0].replace('the ', 'the ')}"))
    elif smaller and a > 50000:
        r = smaller[0]; opts.append((f"It's smaller than {r[0]}.", f"Smaller than {r[0]}"))
    return rnd.choice(opts) if opts else (None, None)

HOOKS = {
    'shape': ["Only one percent of people can name all five of these countries, just from their shape.",
              "Can you name these five countries by their shape? Most people get stuck on number four.",
              "Name all five countries from their outline, and you're a geography genius."],
    'flag': ["Can you name all five of these flags? Only true geography nerds get number five.",
             "Five flags, three seconds each. How many can you name?",
             "Most people fail this flag quiz. Let's see how you do."],
    'capital': ["Can you name the capital of all five countries? Number five is brutal.",
                "Five countries, four options each. Can you pick the right capital?",
                "Most people only get three of these capitals right. Let's go."],
    'emoji': ["Can you guess the country from just three emojis? Number five is tricky.",
              "Three emojis, one country. How many can you get?",
              "Guess the country from the emojis. Only real travelers get all five."],
    'size': ["Maps lie to you. Can you tell which country is actually bigger?",
             "Which country is bigger? Your eyes will fool you on these.",
             "Guess which country is bigger. The answers might surprise you."],
}
BIGS = {'shape': ['ONLY 1%', 'GENIUS TEST', 'BET YOU CAN\'T'], 'flag': ['FLAG MASTER?', 'ONLY 2%', 'NO GOOGLING'], 'capital': ['TOO EASY?', 'ONLY 3%', 'TRICKY ONES'], 'size': ['MAPS LIE', 'YOUR EYES LIE', 'TRUST ISSUES'], 'emoji': ['3 EMOJIS', 'EMOJI QUIZ', 'NO GOOGLING']}
QLINES = ["Number one.", "Number two.", "Number three.", "Number four.", "Last one."]
DIFFS = ['EASY', 'EASY', 'MEDIUM', 'HARD', 'EXPERT']

def build(spec_path, render=False):
    spec = json.load(open(spec_path))
    vid = spec['id']; typ = spec['type']; fmt = spec.get('format', 'short')
    rnd = random.Random(vid)
    voice = spec.get('voice', 'am_michael'); speed = spec.get('speed', 1.12)
    cd = spec.get('countdown', 3.0 if fmt == 'short' else 5.0)
    lines = []  # (key, text)
    scenes = []
    hook = spec.get('hook') or rnd.choice(HOOKS[typ if typ in HOOKS else 'shape'])
    lines.append(('hook', hook))
    items = spec['items']
    for i, it in enumerate(items):
        q = {'i': i}
        if typ in ('shape', 'flag', 'emoji'):
            c = C[it['iso2']]
            q.update(iso2=c['iso2'], name=c['name'], diff=it.get('diff') or (DIFFS[i] if fmt == 'short' else ''))
            if typ == 'emoji':
                assert len(it['emojis']) == 3, it
                q.update(emojis=it['emojis'])
            if fmt == 'short':
                qt = QLINES[i] if i < 5 else f"Number {i+1}."
                if i == 2: qt += " Getting harder."
                if i == len(items) - 1: qt = "Last one. Only experts get this."
            else:
                qt = f"Number {i+1}." if rnd.random() < 0.6 else rnd.choice([f"Number {i+1}.", f"Here's number {i+1}.", f"Next up, number {i+1}."])
            at = rnd.choice([f"It's {c['name']}!", f"{c['name']}!", f"That's {c['name']}!"])
            ft, fc = fact(c, rnd)
            q.update(fact=fc)
        elif typ == 'capital':
            c = C[it['iso2']]
            opts = it['options']; assert c['capital'] in opts, (c['name'], opts)
            q.update(iso2=c['iso2'], name=c['name'], options=opts, answer=c['capital'], diff=DIFFS[i] if i < 5 else '')
            qt = f"What's the capital of {c['name']}?"
            at = rnd.choice([f"It's {c['capital']}!", f"{c['capital']}!"])
            ft, fc = fact(c, rnd)
            if ft and ft.startswith('Its capital'):
                ft, fc = None, None
            q.update(fact=fc)
        elif typ == 'size':
            a, b = C[it['a']], C[it['b']]
            big, small = (a, b) if a['area'] >= b['area'] else (b, a)
            ratio = big['area'] / small['area']
            q.update(a=a['iso2'], b=b['iso2'], nameA=a['name'], nameB=b['name'], areaA=a['area'], areaB=b['area'], bigger=big['iso2'], diff='')
            qt = f"{a['name']} or {b['name']}?"
            if ratio < 1.15:
                at = f"{big['name']}, but only just!"
            else:
                r = round(ratio, 1) if ratio < 3 else round(ratio)
                at = f"{big['name']} is about {r} times bigger!"
            ft, fc = None, None
        if spec.get('facts') == 'last' and i != len(spec['items']) - 1:
            ft, fc = None, None; q['fact'] = None
        if spec.get('facts', True) is False:
            ft, fc = None, None; q['fact'] = None
        lines += [(f'q{i}', qt), (f'a{i}', at)]
        if ft: lines.append((f'f{i}', ft))
        scenes.append(q)
    outro = spec.get('outro') or ("How many did you get? Comment your score!" if typ != 'size' else "How many did you get right? Comment your score!")
    lines.append(('outro', outro))

    # --- voice
    os.makedirs(f'out/{vid}', exist_ok=True)
    audio = {}; dur = {}
    for k, t in lines:
        s = tts(t, voice, speed); audio[k] = s; dur[k] = len(s) / SR
    text = dict(lines)

    # --- timeline
    t = 0.25
    hookT = dict(start=0.0, voice=0.25); t = 0.25 + dur['hook'] + 0.35; hookT['end'] = t
    levelCards = []
    for i, q in enumerate(scenes):
        if fmt == 'long' and spec.get('levels') and i % spec['levels']['size'] == 0:
            lv = i // spec['levels']['size']
            levelCards.append(dict(start=t, end=t + 2.2, level=lv, name=spec['levels']['names'][lv]))
            t += 2.2
        q['start'] = t; q['qVoice'] = t + 0.15
        q['countdown'] = q['qVoice'] + dur[f'q{i}'] + 0.1
        q['reveal'] = q['countdown'] + cd
        q['aVoice'] = q['reveal'] + 0.12
        e = q['aVoice'] + dur[f'a{i}'] + 0.4
        if f'f{i}' in dur:
            q['fVoice'] = q['aVoice'] + dur[f'a{i}'] + 0.15; e = q['fVoice'] + dur[f'f{i}'] + 0.6
        if typ == 'size': e = max(e, q['reveal'] + 2.8)
        q['end'] = e; t = e
    outroT = dict(start=t, voice=t + 0.2, end=t + 0.2 + dur['outro'] + 2.4)
    total = outroT['end']

    # --- mix
    n = int(total * SR) + SR; out = np.zeros(n)
    def place(sig, at, g=1.0):
        i = int(at * SR); seg = sig[:max(0, n - i)]; out[i:i + len(seg)] += g * seg
    tt = lambda d: np.arange(int(d * SR)) / SR
    x = tt(0.06); tick = np.sin(2 * np.pi * 1800 * x) * np.exp(-x * 90) * 0.5
    x = tt(1.0); ding = (np.sin(2*np.pi*880*x) + .6*np.sin(2*np.pi*1320*x) + .3*np.sin(2*np.pi*1760*x)) * np.exp(-x*4) * .28
    d = .45; x = tt(d); whoosh = np.convolve(np.random.RandomState(1).randn(len(x)), np.ones(8)/8, 'same') * np.sin(np.pi*x/d)**2 * .18
    x = tt(.12); pop = np.sin(2*np.pi*(300+2000*x)*x) * np.exp(-x*35) * .35
    place(audio['hook'], hookT['voice']); place(pop, 0.05)
    for lc in levelCards: place(whoosh, lc['start']); place(pop, lc['start'] + 0.1)
    for i, q in enumerate(scenes):
        place(whoosh, q['start']); place(audio[f'q{i}'], q['qVoice'])
        for k in range(int(cd)): place(tick, q['countdown'] + k)
        place(ding, q['reveal']); place(audio[f'a{i}'], q['aVoice'])
        if 'fVoice' in q: place(audio[f'f{i}'], q['fVoice'])
    place(whoosh, outroT['start']); place(audio['outro'], outroT['voice'])
    # music: key/tempo vary per video
    bpm = rnd.choice([100, 106, 112, 118]); beat = 60 / bpm; bar = beat * 4
    root = rnd.choice([196, 207.65, 220, 233.08])
    prog = rnd.choice([[0, -2, -4, -2], [0, -5, -3, -4], [0, 3, -2, -4]])
    m = np.zeros(n); rs = np.random.RandomState(rnd.randint(0, 9999))
    for bi in range(int(total / bar) + 2):
        x = tt(bar); f0 = root * 2 ** (prog[bi % 4] / 12)
        ch = [f0, f0 * 2 ** (4/12 if bi % 4 != 1 else 3/12), f0 * 2 ** (7/12)]
        pad = sum(np.sin(2*np.pi*f*x) + .3*np.sin(4*np.pi*f*x) for f in ch) * .05 * (1 - np.exp(-x*6)) * np.exp(-x*.4)
        i0 = int(bi * bar * SR); seg = pad[:max(0, n - i0)]; m[i0:i0+len(seg)] += seg
        for k in range(4):
            xk = tt(.25); kick = np.sin(2*np.pi*(55+90*np.exp(-xk*30))*xk) * np.exp(-xk*12) * .35
            j = int((bi*bar + k*beat) * SR); seg = kick[:max(0, n-j)]; m[j:j+len(seg)] += seg
            xh = tt(.05); hat = rs.randn(len(xh)) * np.exp(-xh*120) * .05
            j = int((bi*bar + k*beat + beat/2) * SR); seg = hat[:max(0, n-j)]; m[j:j+len(seg)] += seg
    env = np.convolve(np.abs(out), np.ones(2400)/2400, 'same'); duck = 1 - .55*np.clip(env*12, 0, 1)
    fade = np.ones(n); fl = int(1.5*SR); fade[-fl:] = np.linspace(1, 0, fl)
    mix = (out + m*duck*.55) * fade; mix = mix / np.max(np.abs(mix)) * .89
    sf.write(f'public/audio/{vid}.wav', mix[:int(total*SR)], SR)

    props = dict(id=vid, type=typ, format=fmt, fps=30, total=total, cd=cd, title=spec.get('screenTitle'),
                 hook=hookT, scenes=scenes, levels=levelCards, outro=outroT, text=text, dur=dur,
                 countries={k: C[k] for k in set(sum([[q.get('iso2'), q.get('a'), q.get('b')] for q in scenes], [])) if k},
                 scoreboard=spec.get('scoreboard'), hookBig=spec.get('hookBig') or (rnd.choice(BIGS.get(typ, [None])) if fmt == 'short' else None), hookSmall=spec.get('hookSmall'))
    pp = f'out/{vid}.props.json'; json.dump(props, open(pp, 'w'))
    print(f'{vid}: {total:.1f}s, {len(scenes)} items')
    if render:
        comp = 'Long' if fmt == 'long' else 'Short'
        cmd = ['npx', 'remotion', 'render', 'src/index.jsx', comp, f'out/{vid}.raw.mp4', f'--props={pp}',
               '--browser-executable=/usr/bin/google-chrome', '--concurrency=2', '--crf=20', '--log=error']
        subprocess.run(cmd, check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'out/{vid}.raw.mp4', '-c:v', 'copy', '-af',
                        'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', f'out/{vid}.mp4'], check=True)
        os.remove(f'out/{vid}.raw.mp4')
        print('rendered', f'out/{vid}.mp4')

if __name__ == '__main__':
    build(sys.argv[1], '--render' in sys.argv)
