import soundfile as sf, json
from kokoro_onnx import Kokoro
from beats import BEATS, STYLE
k = Kokoro("kokoro.onnx", "voices.bin"); d = []
for i, s in enumerate(BEATS):
    a, sr = k.create(s["say"], voice=STYLE["voice"], speed=STYLE["speed"], lang="en-us")
    sf.write(f"b{i}.wav", a, sr); d.append(len(a) / sr)
json.dump(d, open("durs.json", "w")); print("voice", round(sum(d), 1), "s")
