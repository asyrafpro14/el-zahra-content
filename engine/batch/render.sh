#!/bin/bash
# Guna: batch/render.sh <dir kerja> <slug>...   (dari folder engine). Hasil: <dir>/<slug>.silent.mp4 dan <dir>/<slug>.sfx.wav
W=$1; shift
for s in "$@"; do
  SLUG=$s EVENTS=$W/$s.ev.json python3 tips_batch.py > $W/$s.log 2>&1
  python3 sfx.py $W/$s.ev.json $W/$s.sfx.wav >> $W/$s.log 2>&1
  SLUG=$s OUT=$W/$s.silent.mp4 python3 tips_batch.py >> $W/$s.log 2>&1 && echo "siap $s"
done
