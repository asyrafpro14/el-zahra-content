import sys, json, wave
import numpy as np

SR = 44100
ev = json.load(open(sys.argv[1])); out = sys.argv[2]
N = int(ev["total"] * SR) + SR
mix = np.zeros((N, 2), dtype=np.float64)
rng = np.random.default_rng(5)

def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1.0 / SR)
    m = 1.0 / (1.0 + (lo / np.maximum(f, 1e-6)) ** 6) / (1.0 + (f / hi) ** 6)
    return np.fft.irfft(X * m, len(x))
def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i < 0: sig = sig[-i:]; i = 0
    n = min(len(sig), N - i)
    if n <= 0: return
    if sig.ndim == 1:
        l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
        mix[i:i + n, 0] += sig[:n] * gain * l * 1.414; mix[i:i + n, 1] += sig[:n] * gain * r * 1.414
    else: mix[i:i + n] += sig[:n] * gain
def norm(x): return x / (np.max(np.abs(x)) + 1e-9)

def whoosh(dur=0.75):
    n = int(dur * SR); t = np.arange(n) / SR; u = t / dur; x = rng.standard_normal(n)
    lo = band(x, 180, 700) * np.exp(-((u - 0.30) / 0.20) ** 2); mid = band(x, 700, 2600) * np.exp(-((u - 0.50) / 0.18) ** 2); hi = band(x, 2600, 9000) * np.exp(-((u - 0.66) / 0.16) ** 2)
    mono = norm(lo * 1.0 + mid * 0.8 + hi * 0.5); pan = np.linspace(-0.7, 0.7, n)
    return np.stack([mono * np.cos((pan + 1) * np.pi / 4), mono * np.sin((pan + 1) * np.pi / 4)], 1) * 1.2
def boom(dur=1.8):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 46 + 52 * np.exp(-t * 9); ph = 2 * np.pi * np.cumsum(f) / SR
    body = (np.sin(ph) + 0.55 * np.sin(2 * ph) + 0.28 * np.sin(3 * ph) + 0.14 * np.sin(4 * ph)) * np.exp(-t * 3.0)
    thud = band(rng.standard_normal(n), 90, 420) * np.exp(-t * 16) * 1.6
    tail = band(rng.standard_normal(n), 120, 900) * np.exp(-t * 2.2) * 0.12
    x = body + thud + tail; x[:int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR)); return norm(x)
def tick(k):
    n = int(0.09 * SR); t = np.arange(n) / SR; f0 = 1250 + 95 * k
    x = (np.sin(2 * np.pi * f0 * t) + 0.5 * np.sin(2 * np.pi * f0 * 2.01 * t)) * np.exp(-t * 55) + band(rng.standard_normal(n), 3000, 9000) * np.exp(-t * 300) * 0.5
    return norm(x)
def shimmer(dur=3.0):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros((n, 2))
    for j, fr in enumerate([1174.7, 1568.0, 1760.0, 2349.3, 2637.0, 3136.0, 3520.0]):
        on = 0.055 * j; e = np.where(t >= on, np.exp(-(t - on) * 1.7) * (1 - np.exp(-(t - on) * 180)), 0.0)
        s = np.sin(2 * np.pi * fr * t * (1 + 0.0009 * np.sin(2 * np.pi * 5 * t + j))) * e / (1 + 0.25 * j)
        p = -0.6 + 1.2 * (j / 6.0); x[:, 0] += s * np.cos((p + 1) * np.pi / 4); x[:, 1] += s * np.sin((p + 1) * np.pi / 4)
    return x / (np.max(np.abs(x)) + 1e-9)
def riser(dur=1.3):
    n = int(dur * SR); t = np.arange(n) / SR; u = t / dur
    f = 260 * (4.2 ** u); tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * u ** 2 * 0.5
    nz = band(rng.standard_normal(n), 900, 7000) * u ** 2.5
    x = tone + norm(nz) * 0.8; x[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR)); return norm(x)
def pop():
    n = int(0.14 * SR); t = np.arange(n) / SR; f = 520 + 520 * (t / 0.14)
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 26))
def water(dur=5.0):
    n = int(dur * SR); t = np.arange(n) / SR; x = band(rng.standard_normal(n), 1400, 7500)
    lfo = 0.55 + 0.45 * np.abs(band(rng.standard_normal(n), 3, 14)); lfo = lfo / np.max(lfo)
    env = np.minimum(1, t / 0.5) * np.minimum(1, (dur - t) / 1.6); return norm(x * lfo) * env
def bed(total):
    n = int(total * SR); t = np.arange(n) / SR; x = np.zeros((n, 2))
    for j, (fr, g) in enumerate([(73.42, 0.9), (110.0, 0.7), (146.83, 0.8), (220.0, 0.45), (293.66, 0.3), (440.0, 0.12)]):
        l = 0.6 + 0.4 * np.sin(2 * np.pi * (0.05 + 0.017 * j) * t + j); r = 0.6 + 0.4 * np.sin(2 * np.pi * (0.043 + 0.019 * j) * t + 2 * j + 1)
        s = np.sin(2 * np.pi * fr * t) + 0.3 * np.sin(2 * np.pi * fr * 1.003 * t)
        x[:, 0] += s * g * l; x[:, 1] += s * g * r
    wl = band(rng.standard_normal(n), 250, 1100) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t)); wr = band(rng.standard_normal(n), 250, 1100) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.06 * t + 2))
    x = x / np.max(np.abs(x)); x[:, 0] += norm(wl) * 0.35; x[:, 1] += norm(wr) * 0.35
    env = np.minimum(1, t / 1.5) * np.minimum(1, np.maximum(0, (total - t)) / 2.0); return x / np.max(np.abs(x)) * env[:, None]

add(bed(ev["total"]), 0.0, 0.05)
for i, t in enumerate(ev["whoosh"]): add(whoosh(), t - 0.42, 0.16)
for t, a in ev["boom"]: add(boom(), t - 0.01, 0.32 * (0.55 + 0.45 * a))
for k, t in enumerate(ev["ticks"]): add(tick(k), t, 0.14, pan=-0.5 + k / 6.0)
add(riser(), ev["riser_end"] - 1.3, 0.085); add(shimmer(), ev["shimmer"], 0.13); 
if ev.get("water", True): add(water(), ev["shimmer"] + 0.15, 0.035)
if "wind" in ev:
    t0, t1 = ev["wind"]; d = t1 - t0; n = int(d * SR); tt = np.arange(n) / SR
    for ch, sd in ((-0.6, 1), (0.6, 2)):
        r2 = np.random.default_rng(sd); x = band(r2.standard_normal(n), 180, 1500) + 0.5 * band(r2.standard_normal(n), 900, 4200)
        g = 0.45 + 0.55 * np.abs(band(r2.standard_normal(n), 0.3, 2.5)); g = g / np.max(g)
        e = np.minimum(1, tt / 1.0) * np.minimum(1, (d - tt) / 1.4)
        add(norm(x * g) * e, t0, 0.17, pan=ch)
for t in ev["pop"]: add(pop(), t - 0.05, 0.09)
pk = np.max(np.abs(mix)); print("peak", round(float(pk), 3), "rms_dB", round(float(20 * np.log10(np.sqrt(np.mean(mix ** 2)) + 1e-9)), 1))
if pk > 0.9: mix *= 0.9 / pk
w = wave.open(out, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes()); w.close(); print("wrote", out, len(mix) / SR)
