import soundfile as sf, json
from kokoro_onnx import Kokoro
from script import SLIDES
k=Kokoro("kokoro.onnx","voices.bin"); d=[]
for si,s in enumerate(SLIDES):
    for ii,it in enumerate(s["items"]):
        a,sr=k.create(it["say"],voice="am_michael",speed=1.05,lang="en-us")
        sf.write(f"a_{si}_{ii}.wav",a,sr); d.append([si,ii,len(a)/sr])
json.dump(d,open("durs.json","w")); print(len(d),"clips",round(sum(x[2] for x in d)/60,2),"min")
