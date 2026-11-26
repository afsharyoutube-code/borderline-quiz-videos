import sys, json, soundfile as sf, numpy as np
sys.path.insert(0,'/home/claude/L07')
from kokoro_onnx import Kokoro
k=Kokoro('/home/claude/tts/kokoro-v1.0.onnx','/home/claude/tts/voices-v1.0.bin')
mod=sys.argv[1]; out=sys.argv[2]; speed=float(sys.argv[3])
ns={}; exec(open(mod).read(),ns); S=ns['S']
import os; os.makedirs(out,exist_ok=True); d=[]
for i,(v,t) in enumerate(S):
    f=f'{out}/'+__import__('hashlib').md5(t.encode()).hexdigest()[:12]+'.wav'
    if t:
        if not os.path.exists(f):
            a,sr=k.create(t,voice='af_heart',speed=speed,lang='en-us'); sf.write(f,a,sr)
        a,sr=sf.read(f); d.append(len(a)/sr)
    else: d.append(0)
    print(i,round(d[-1],2),flush=True)
json.dump(d,open(out+'/dur.json','w'))
print('TOTAL',sum(d))
