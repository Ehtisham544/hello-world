#!/bin/bash
# Usage: LSPEC=/abs/long_spec.json OUT=/abs/out.mp4 THUMB=/abs/thumb.jpg bash make_long.sh
set -e
cd "$(dirname "$0")"
[ -f kokoro.onnx ] || curl -sSL -o kokoro.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -f voices.bin ] || curl -sSL -o voices.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
python3 -c "import kokoro_onnx" 2>/dev/null || pip install --break-system-packages -q kokoro-onnx soundfile scipy
rm -f a_*.wav durs.json part*.mp4 mix_long.wav
python3 voice_long.py
N=$(nproc); [ "$N" -gt 4 ] && N=4; [ "$N" -lt 1 ] && N=1
for i in $(seq 0 $((N-1))); do python3 render_long.py $i $N & done
python3 audio_long.py
wait
for i in $(seq 0 $((N-1))); do [ -f part$i.mp4 ] || { echo "render part $i failed"; exit 1; }; echo "file part$i.mp4"; done > parts.txt
ffmpeg -v error -y -f concat -i parts.txt -c copy vid_long.mp4
ffmpeg -v error -y -i vid_long.mp4 -i mix_long.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest "$OUT.tmp.mp4" && mv "$OUT.tmp.mp4" "$OUT"
python3 thumb.py "$THUMB"
python3 chapters.py > chapters.txt
echo "done $OUT"; cat chapters.txt
