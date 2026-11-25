#!/bin/bash
# Guna (dari engine/lukisan): ./build.sh <A-imej.mp4> <B-klip.mp4> <suara.mp3> <dir kerja> [PREVIEW]
# A = 13 imej (1 saat setiap satu, 24 fps); B = klip v01 kemudian v08 (5.04 saat setiap satu). Dipecah dua kerana had attach 30 MB.
set -e; A=$1; B=$2; V=$3; W=$4; mkdir -p $W/in $W/tmp; HERE=$(cd "$(dirname "$0")" && pwd)
for i in $(seq 1 13); do n=$(printf %02d $i); ffmpeg -y -loglevel error -ss $((i-1)).5 -i "$A" -frames:v 1 $W/in/s$n.png; done
ffmpeg -y -loglevel error -i "$B" -t 5.0 -an -c:v libx264 -crf 12 -pix_fmt yuv420p $W/in/v01.mp4
ffmpeg -y -loglevel error -ss 5.0833 -i "$B" -t 4.95 -an -c:v libx264 -crf 12 -pix_fmt yuv420p $W/in/v08.mp4
ffmpeg -y -loglevel error -i "$V" -vn -c:a pcm_s16le -ar 44100 $W/voice.wav
python3 $HERE/tahun_gajah.py $W/in $HERE/../fonts_sub > $W/spec.json
if [ -n "$5" ]; then PREVIEW=$5 TMP=$W/tmp JOBS=2 python3 $HERE/comp.py $W/spec.json all; exit 0; fi
TMP=$W/tmp JOBS=2 python3 $HERE/comp.py $W/spec.json all
python3 $HERE/comp.py $W/spec.json events $W/ev.json && python3 $HERE/../sfx.py $W/ev.json $W/sfx.wav
ffmpeg -y -loglevel error -i $W/tmp/silent.mp4 -i $W/voice.wav -i $W/sfx.wav -filter_complex "[1:a]loudnorm=I=-16:TP=-1.5:LRA=11,apad[v];[2:a]volume=0.8[s];[v][s]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[a]" \
  -map 0:v -map "[a]" -c:v libx264 -crf 24 -preset medium -pix_fmt yuv420p -c:a aac -b:a 128k -ar 44100 -shortest -movflags +faststart $HERE/../../videos/el-zahra-sirah-tahun-gajah.mp4
echo siap
