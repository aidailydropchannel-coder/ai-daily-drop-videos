#!/usr/bin/env bash
# One-time setup per session: downloads the Kokoro voice model + pronunciation data (data files only).
set -e
D="$(cd "$(dirname "$0")" && pwd)/tts_data"
mkdir -p "$D"; cd "$D"
[ -f kokoro-v1.0.onnx ] || curl -sSL -o kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -f voices-v1.0.bin ] || curl -sSL -o voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
if [ ! -f config.json ]; then
  git clone -q --depth 1 https://github.com/thewh1teagle/kokoro-onnx /tmp/kokoro-src && cp /tmp/kokoro-src/src/kokoro_onnx/config.json .
fi
if [ ! -f us_gold.json ]; then
  git clone -q --depth 1 https://github.com/hexgrad/misaki /tmp/misaki-src && cp /tmp/misaki-src/misaki/data/{us,gb}_{gold,silver}.json .
fi
ls -la "$D"
