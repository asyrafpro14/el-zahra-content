# Potong suara pada jeda senyap, mux dengan SFX dan video senyap, mampat ke videos/el-zahra-<slug>.mp4
# Guna (dari engine/): python3 batch/finalize.py <dir kerja> <a.mp3> <b.mp3> [slug...]   |   SRC_C=<c.mp3> python3 batch/finalize.py <dir> - - <slug...>
import json, subprocess, sys, re, os
W, SRC = sys.argv[1], {"a": sys.argv[2], "b": sys.argv[3]}
C = json.load(open("batch/cuts.json")); OUT = os.path.join("..", "videos")
def sil(f):
    e = subprocess.run(["ffmpeg", "-i", f, "-af", "silencedetect=noise=-38dB:d=0.12", "-f", "null", "-"], capture_output=True, text=True).stderr
    return list(zip([float(x) for x in re.findall(r"silence_start: ([\d.]+)", e)], [float(x) for x in re.findall(r"silence_end: ([\d.]+)", e)]))
def dur(f): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))
if os.environ.get("SRC_C"): SRC["c"] = os.environ["SRC_C"]   # rakaman ketiga dan seterusnya: SRC_C=<c.mp3> (a dan b boleh diisi "-")
SRC = {k: v for k, v in SRC.items() if os.path.exists(v)}; SIL = {k: sil(v) for k, v in SRC.items()}; DUR = {k: dur(v) for k, v in SRC.items()}
def snap(src, t, last=False):
    # jeda senyap paling hampir dengan sempadan t (dalam 0.6 s); pulangkan (tamat klip sebelum, mula klip selepas)
    best = None
    for a, b in SIL[src]:
        d = 0 if a <= t <= b else min(abs(a - t), abs(b - t))
        if d <= 0.6 and (best is None or (b - a) > (best[1] - best[0])): best = (a, b)
    return best
slugs = list(C); rep = []; ONLY = set(sys.argv[4:])   # pilihan: senarai slug selepas dua fail mp3
for i, s in enumerate(slugs):
    if ONLY and s not in ONLY: continue
    c = C[s]; src = c["src"]; wt = json.load(open("words/%s.json" % s)); st = c["start"]; pad = c["pad"]
    first = i == 0 or C[slugs[i - 1]]["src"] != src; last = i == len(slugs) - 1 or C[slugs[i + 1]]["src"] != src
    b0 = snap(src, st); b1 = snap(src, c["end"])
    a0 = 0.0 if first else (max(b0[0], b0[1] - 0.12) if b0 else st)          # mula audio: sedikit sebelum suara bermula
    a1 = DUR[src] if last else (min(b1[1], b1[0] + 0.35) if b1 else c["end"])  # tamat audio: sedikit selepas suara tamat
    w0, w1 = wt[0][0] - pad + st, wt[-1][1] - pad + st
    rep.append((s, round(w0 - a0, 2), round(a1 - w1, 2), None if b0 is None else round(b0[1] - b0[0], 2), None if b1 is None else round(b1[1] - b1[0], 2)))
    vd = dur("%s/%s.silent.mp4" % (W, s)); delay = int(round((pad + a0 - st) * 1000))
    fc = ("[1:a]atrim=%.3f:%.3f,asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st=%.3f:d=0.05,loudnorm=I=-16:TP=-1.5:LRA=11,adelay=%d:all=1,apad[v];"
          "[2:a]volume=0.8[s];[v][s]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[a]") % (a0, a1, a1 - a0 - 0.05, max(0, delay))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "%s/%s.silent.mp4" % (W, s), "-i", SRC[src], "-i", "%s/%s.sfx.wav" % (W, s), "-filter_complex", fc,
                    "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "26", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
                    "-t", "%.3f" % vd, "-movflags", "+faststart", "%s/el-zahra-%s.mp4" % (OUT, s)], check=True)
for r in rep: print("%-38s lead=%s tail=%s jeda_mula=%s jeda_tamat=%s" % r)
