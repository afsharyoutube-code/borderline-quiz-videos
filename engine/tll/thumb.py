import sys; sys.path.insert(0,'.')
from draw import *
def thumb(words, out, seed, bg=(225,220,210)):
    W,H=1280,720; img=paper(W,H); u=H/1080; p=Pen(img,seed,u)
    # dark sea band for contrast
    p.d.rectangle([0,H*0.62,W,H],fill=(70,72,74))
    ship(p,W*0.72,H*0.32,H*0.75,'torn')
    # huge character face
    character(p,W*0.2,H*0.62,H*1.25,'shock')
    p.d.text((W*0.66,H*0.86),words[0],font=font(160*u),fill=ORANGE,anchor='mm',stroke_width=7,stroke_fill=(25,25,25))
    img.save(out)
thumb(["NO ONE ABOARD"],'thumb_A.png',3)
def thumbB(out):
    W,H=1280,720; img=paper(W,H); u=H/1080; p=Pen(img,5,u)
    p.d.rectangle([0,H*0.62,W,H],fill=(70,72,74))
    ship(p,W*0.7,H*0.3,H*0.7,'torn'); boat(p,W*0.47,H*0.68,H*0.28,10)
    character(p,W*0.18,H*0.62,H*1.2,'scared')
    p.d.text((W*0.68,H*0.88),"WHERE'D THEY GO?",font=font(140*u),fill=ORANGE,anchor='mm',stroke_width=7,stroke_fill=(25,25,25))
    img.save(out)
thumbB('thumb_B.png')
