"""Facebook photo-quiz stills (1080x1350) in the Borderline look.
usage: python3 tools/fb_still.py <out.jpg> <kind> <iso2> [layout]
kind: flag  -> "Which country's flag is this?"
layout: 0..2 varies background/badge so posts don't look templated."""
import sys, subprocess, json, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
out, kind, iso = sys.argv[1], sys.argv[2], sys.argv[3]
lay = int(sys.argv[4]) if len(sys.argv) > 4 else 0
W, H = 1080, 1350
NV, YE, WH = (11, 42, 74), (255, 210, 63), (255, 255, 255)
bgs = [(11, 42, 74), (20, 24, 48), (8, 58, 70)]
im = Image.new('RGB', (W, H), bgs[lay % 3]); d = ImageDraw.Draw(im)
for x in range(0, W, 90): d.line([(x, 0), (x, H)], fill=tuple(min(255, c + 10) for c in bgs[lay % 3]), width=2)
for y in range(0, H, 90): d.line([(0, y), (W, y)], fill=tuple(min(255, c + 10) for c in bgs[lay % 3]), width=2)
fb = ImageFont.truetype('/tmp/lg.ttf', 92); fm = ImageFont.truetype('/tmp/m900.ttf', 44); fs = ImageFont.truetype('/tmp/m900.ttf', 34)
titles = ["WHICH COUNTRY?", "NAME THIS FLAG", "GUESS THE FLAG"]
t = titles[lay % 3]; w = d.textlength(t, font=fb)
d.text(((W - w) / 2 + 5, 125), t, font=fb, fill=(0, 0, 0)); d.text(((W - w) / 2, 120), t, font=fb, fill=YE)
# flag
png = f'/tmp/flag_{iso}.png'
subprocess.run(['rsvg-convert', '-w', '760', f'public/flags/{iso}.svg', '-o', png], check=True)
fl = Image.open(png).convert('RGBA'); fl = fl.resize((760, int(760 * fl.height / fl.width)))
x, y = (W - fl.width) // 2, 330 + (570 - fl.height) // 2
sh = Image.new('RGBA', (fl.width + 40, fl.height + 40), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([20, 20, fl.width + 20, fl.height + 20], fill=(0, 0, 0, 150))
sh = sh.filter(ImageFilter.GaussianBlur(14)); im.paste(sh, (x - 14, y - 6), sh)
d.rectangle([x - 8, y - 8, x + fl.width + 8, y + fl.height + 8], fill=WH); im.paste(fl, (x, y), fl)
s = "Comment your answer 👇".replace(' 👇', '')
w = d.textlength(s, font=fm); d.rounded_rectangle([(W - w) / 2 - 40, 1010, (W + w) / 2 + 40, 1090], radius=40, fill=YE)
d.text(((W - w) / 2, 1026), s, font=fm, fill=NV)
s2 = "Answer tomorrow in the comments"; w = d.textlength(s2, font=fs); d.text(((W - w) / 2, 1130), s2, font=fs, fill=WH)
s3 = "BORDERLINE QUIZ"; w = d.textlength(s3, font=fs); d.text(((W - w) / 2, 1250), s3, font=fs, fill=YE)
im.save(out, quality=90); print(out)
