#!/bin/bash
# Usage: SPEC=/abs/path/spec.json OUT=/abs/path/out.mp4 bash make_short.sh
set -e
cd "$(dirname "$0")"
[ -f kokoro.onnx ] || curl -sSL -o kokoro.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -f voices.bin ] || curl -sSL -o voices.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
python3 -c "import kokoro_onnx" 2>/dev/null || pip install --break-system-packages -q kokoro-onnx soundfile scipy
rm -f b*.wav durs.json mix.wav video_only.mp4
python3 voice.py && python3 audio.py && python3 render3.py
ffmpeg -v error -y -i video_only.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest "$OUT.tmp.mp4" && mv "$OUT.tmp.mp4" "$OUT"
echo "done $OUT"
