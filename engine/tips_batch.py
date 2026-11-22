# Enjin batch untuk video TIPS / PANTANG LARANG / ZIARAH / ADAB. Spesifikasi dalam batch/specs.py (satu entri setiap video).
# Guna: SLUG=<slug> FAKE=1 PREVIEW=1,6,12 python3 tips_batch.py   |   SLUG=<slug> WORDS=words/<slug>.json OUT=x.mp4 python3 tips_batch.py
# PRESET: haram (Kaabah), madinah (Masjid Nabawi), quba, qiblatain (masjid putih), hira (Jabal Nur).
from ezlib import *
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "batch")); from specs import V
SP = V[os.environ["SLUG"]]; PRESET = SP["preset"]; TAJUK, SC, ROWS, LESSON = SP["kad"], SP["sc"], SP["rows"], SP["lesson"]
HOOK = [(SP["hook"][0], GOLDT), (SP["hook"][1], INK)]
SEED = sum(ord(c) for c in SP["slug"]); random.seed(SEED); VAR = SEED % 4
S = Script(SC, os.environ.get("WORDS", "words/%s.json" % SP["slug"])); TS = S.TS; T2 = TS[1]; TL = TS[-1]; t_simpan = S.st(S.SC_FIRST[-1])
MOSQ = PRESET in ("madinah", "quba", "qiblatain")
def hgt_h(x, y):
    r = math.hypot(x, y); a = math.atan2(y, x); n = 0.2 * math.sin(x * 0.21 + 1.3) * math.cos(y * 0.17)
    return n * (0.25 if r < 13 else 1.0) + math.exp(-((r - 22) / 6.0) ** 2) * (7 + 2.5 * math.sin(a * 5 + 1 + VAR) + 1.5 * math.sin(a * 11)) + max(0.0, (r - 66) / 10.0) ** 1.6 * 6
def hgt_m(x, y):
    r = math.hypot(x, y); return 0.2 * math.sin(x * 0.21 + 1.3) * math.cos(y * 0.17) * (0.2 if r < 16 else 1.0) + 9 * math.exp(-(((x + 6) / 16.0) ** 2 + ((y - 40) / 7.0) ** 2)) + max(0.0, (r - 66) / 10.0) ** 1.6 * 6
def hgt_g(x, y):
    r = math.hypot(x, y); a = math.atan2(y, x)
    return 0.25 * math.sin(x * 0.21 + 1.3) * math.cos(y * 0.17) + 15 * math.exp(-(r / 9.5) ** 2) * (1 + 0.10 * math.sin(a * 5) + 0.06 * math.sin(a * 9 + 1)) + 4 * math.exp(-(((x - 26) / 9.0) ** 2 + ((y + 18) / 12.0) ** 2)) + max(0.0, (r - 66) / 10.0) ** 1.6 * 6
hgt = hgt_h if PRESET == "haram" else hgt_g if PRESET == "hira" else hgt_m
GUA = (2.2, -2.6, hgt_g(2.2, -2.6) + 0.5)
def col(x, y, z):
    base = np.array([224, 190, 142.0]); k = min(1.0, max(0.0, (z - 1.0) / (9.0 if PRESET == "hira" else 5.0))); return base * (1 - k) + np.array([146, 106, 88.0]) * k
def mosque(sc, wx, wy, nmin, dome):
    sc.quad((-wx - 1.6, -wy - 1.8, 0.04), (wx + 1.6, -wy - 1.8, 0.04), (wx + 1.6, wy + 1.8, 0.04), (-wx - 1.6, wy + 1.8, 0.04), (236, 226, 204), layer=1, ds=True)
    sc.box(0, 0, 0, 2 * wx, 2 * wy, 1.3, (244, 240, 230), top=(250, 248, 242))
    for dx, dy, rr, hh in dome: sc.pyramid(dx, dy, 1.3, rr, hh, (40, 128, 86) if PRESET == "madinah" else (236, 232, 222), n=8)
    P = [(-wx - 0.2, -wy - 0.2), (wx + 0.2, -wy - 0.2), (-wx - 0.2, wy + 0.2), (wx + 0.2, wy + 0.2)][:nmin]
    for mx, my_ in P: sc.box(mx, my_, 0, 0.4, 0.4, 3.4, (244, 240, 230)); sc.pyramid(mx, my_, 3.4, 0.34, 0.6, (212, 170, 70), n=6)
def build():
    sc = Scene(); terrain(sc, hgt, col, n=66, ext=84.0)
    if PRESET == "haram":
        city(sc, hgt, 0, 0, 10.5, 200, hole=3.6); sc.quad((-3.2, -3.2, 0.04), (3.2, -3.2, 0.04), (3.2, 3.2, 0.04), (-3.2, 3.2, 0.04), (236, 226, 204), layer=1, ds=True)
        sc.box(0, 0, 0, 1.5, 1.5, 1.8, (26, 24, 26), top=(40, 38, 40)); sc.box(0, 0, 1.25, 1.54, 1.54, 0.16, (212, 170, 70))
    elif PRESET == "hira":
        gx, gy, gz = GUA; sc.box(gx, gy, gz - 0.9, 1.1, 0.9, 0.9, (58, 42, 40), top=(96, 72, 62))
    else:
        if PRESET == "madinah": city(sc, hgt, 0, 0, 12, 170, hole=4.6); mosque(sc, 2.5, 1.8, 4, [(-1.2, 0.4, 0.95, 0.9)])
        elif PRESET == "quba": city(sc, hgt, 0, 0, 11, 90, hole=5.4); mosque(sc, 2.6, 1.9, 4, [(-1.2, -0.7, 0.7, 0.6), (0, -0.7, 0.7, 0.6), (1.2, -0.7, 0.7, 0.6), (-1.2, 0.7, 0.7, 0.6), (0, 0.7, 0.7, 0.6), (1.2, 0.7, 0.7, 0.6)])
        else: city(sc, hgt, 0, 0, 11, 110, hole=5.0); mosque(sc, 2.2, 1.7, 2, [(-0.9, 0, 0.85, 0.75), (0.9, 0, 0.85, 0.75)])
        for _ in range(70 if PRESET == "madinah" else 110):
            a = random.uniform(0, 6.283); r = random.uniform(13 if PRESET == "madinah" else 6.5, 22); palm(sc, hgt, r * math.cos(a), r * math.sin(a))
    return sc
TAWAF = [(random.uniform(2.0, 5.0), random.uniform(0, 6.283), random.uniform(0.8, 1.2)) for _ in range(140)]
def dynamic(t):
    d = Scene(); glows = []
    if PRESET == "haram":
        for r, ph, sp in TAWAF:
            ang = ph - t * 0.45 * sp; d.box(r * math.cos(ang), r * math.sin(ang), 0.05, 0.2, 0.2, 0.3, (248, 246, 240), rot=ang)
        glows.append((0, 0, 1.6, 2.4 + 0.3 * math.sin(t * 3)))
    elif PRESET == "hira": glows.append((GUA[0], GUA[1], GUA[2], 3.0 + 0.5 * math.sin(t * 2.4)))
    return d, glows
RR = [[30, 13, 18, 11, 22, 26], [26, 15, 11, 19, 13, 24], [32, 12, 20, 14, 24, 16], [24, 16, 12, 21, 11, 27]][VAR]; HH = [[14, 7, 13, 6, 18, 20], [16, 6, 9, 14, 7, 19], [12, 8, 15, 6, 20, 9], [18, 9, 6, 15, 7, 21]][VAR]
def cam(t):
    k = sum(1 for x in TS if t >= x); u = smooth((t - TS[k - 1]) / 1.2) if k > 1 else 1.0
    R, Hh, Rp, Hp = RR[(k - 1) % 6], HH[(k - 1) % 6], RR[(k - 2) % 6], HH[(k - 2) % 6]
    R = lerp(Rp, R, u) if k > 1 else R; Hh = lerp(Hp, Hh, u) if k > 1 else Hh; a = -1.4 + 1.57 * VAR + (0.10 if VAR % 2 == 0 else -0.10) * t + 0.5 * (k - 1 + u - 1)
    if MOSQ: R, Hh = R * 1.5, Hh * 1.3
    if PRESET == "hira": return ((R * 1.9 + 14) * math.cos(a), (R * 1.9 + 14) * math.sin(a), Hh * 1.2 + 12), (0, 0, 9.0)
    return (R * math.cos(a), R * math.sin(a), Hh), (0, 0, 0.8)
PA, PB, PC = [("dawn", "day", "dusk"), ("day", "dusk", "night"), ("dusk", "day", "dawn"), ("night", "dawn", "day")][VAR]
def env(t): return pmix(PA, PB, (t - T2) / 1.5) if t < TL else pmix(PB, PC, (t - TL) / 1.5)
NAVYG, CR = (15, 61, 46), (247, 243, 232)
def overlay(base, d, t, proj):
    if t < T2 + 0.1 or t > t_simpan - 0.2: return
    a = clamp((t - T2 - 0.1) / 0.25) * clamp((t_simpan - 0.2 - t) / 0.3); hh = 104 + 82 * len(ROWS) + 22
    im = Image.new("RGBA", (960, hh), (0, 0, 0, 0)); dd = ImageDraw.Draw(im); dd.rounded_rectangle([0, 0, 959, hh - 1], 34, fill=NAVYG + (236,), outline=(201, 162, 75, 255), width=3)
    f = font("serif", 40); tw = f.getlength(TAJUK); dd.text((40, 26), TAJUK, font=font("serif", int(40 * min(1.0, 880.0 / tw))), fill=(246, 226, 170))
    for k, txt in enumerate(ROWS):
        y = 104 + 82 * k; t0 = TS[k + 1] + 0.2; t1 = TS[k + 2] - 0.1 if k + 2 < len(TS) else 1e9; p = ease((t - t0) / 0.3)
        if p <= 0: dd.rounded_rectangle([40, y + 8, 920, y + 66], 14, fill=(22, 74, 56, 240)); continue
        on = t >= t1; dd.rounded_rectangle([40, y + 4, 920, y + 70], 16, fill=(34, 96, 72, 244)); dd.ellipse([54, y + 10, 108, y + 64], fill=((70, 200, 140) if on else (201, 162, 75)) + (255,))
        if on: dd.line([68, y + 38, 78, y + 50, 96, y + 26], fill=NAVYG + (255,), width=6, joint="curve")
        else: dd.text((81, y + 37), str(k + 1), font=font("bold", 32), fill=NAVYG, anchor="mm")
        fs = 36
        while font("bold", fs).getlength(txt) > 780 and fs > 24: fs -= 2
        dd.text((128, y + 37), txt, font=font("bold", fs), fill=(252, 248, 238, int(255 * p)), anchor="lm")
    paste(base, im, W / 2, 300 + hh / 2, a)
LBL = {"haram": ("Kaabah", (0, 0, 2.4)), "madinah": ("Masjid Nabawi", (0, 0, 2.4)), "quba": ("Masjid Quba", (0, 0, 2.4)), "qiblatain": ("Masjid Qiblatain", (0, 0, 2.4)), "hira": ("Gua Hira", (GUA[0], GUA[1], GUA[2] + 0.8))}[PRESET]
run(dict(S=S, tag="tb", out=os.environ.get("OUT", "tips.mp4"), build=build, dynamic=dynamic, cam=cam, env=env, overlay=overlay, fogd=0.006,
    hook=[(0.1, HOOK, 330)], labels=[(LBL[0], None, LBL[1], 0.8, T2 - 0.2, GOLDT)], caps=[],
    cta=(t_simpan, t_simpan + 0.8, t_simpan + 1.6), lesson=LESSON,
    events={"whoosh": list(TS[1:]), "boom": [[0.05, 0.6]], "ticks": [x + 0.2 for x in TS[1:-1]], "riser_end": T2, "shimmer": TL, "pop": [t_simpan, t_simpan + 0.8]}))
