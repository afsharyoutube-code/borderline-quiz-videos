import sys; sys.path.insert(0,'.')
from draw import *
from scenes import compose
C={1:("THEY JUST VANISHED","ship:empty"),2:("THE TEA WAS FAKE","tea:cup"),3:("9 EMPTY BARRELS","barrels:nine"),4:("IT WASN'T SINKING","ship:float")}
for k,(t,v) in C.items():
    img=compose(v,'',1080,1920,77); p=Pen(img,9,1)
    p.d.rectangle([0,1280,1080,1560],fill=(40,40,42))
    p.d.text((540,1420),t,font=font(118),fill=ORANGE,anchor='mm',stroke_width=6,stroke_fill=(15,15,15))
    img.save(f'cover{k}.png')
