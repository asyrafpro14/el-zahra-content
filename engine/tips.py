# Templat video TIPS / PANTANG LARANG / ADAB (bukan sirah). Salin fail ini, tukar TAJUK, SC, ROWS, PRESET dan label.
# Babak: [hook], satu babak setiap isi (ikut ROWS), [penutup dengan blok '#'].
# Semakan tanpa suara: FAKE=1 PREVIEW=1,6,12 python3 tips.py   |   Dengan suara: letak masa perkataan di words/<WORDS>.json
from ezlib import *
random.seed(7)
PRESET = os.environ.get("PRESET", "haram")          # "haram" (Makkah) atau "madinah"
TAJUK = "3 BARANG KECIL YANG SELALU TERLUPA"
SC = [["Tiga barang kecil", "yang ramai jemaah terlupa bawa."],
      ["Satu: beg kasut kecil.", "Kasut anda dibawa masuk,", "bukan ditinggal di pintu."],
      ["Dua: botol air boleh lipat,", "untuk diisi air zamzam."],
      ["Tiga: tali pengenalan,", "dengan nombor hotel dan mutawwif anda."],
      ["#Simpan video ini sebelum anda berkemas."]]
ROWS = ["Beg kasut kecil", "Botol air boleh lipat", "Tali pengenalan"]
HOOK = [("3 barang ", GOLDT), ("selalu terlupa", INK)]
LESSON = "Simpan sebelum anda berkemas"
S = Script(SC, os.environ.get("WORDS", "tips-contoh.json")); TS = S.TS; T2 = TS[1]; TL = TS[-1]; t_simpan = S.st(S.SC_FIRST[-1])
def hgt_h(x, y):
    r = math.hypot(x, y); a = math.atan2(y, x); n = 0.2 * math.sin(x * 0.21 + 1.3) * math.cos(y * 0.17)
    return n * (0.25 if r < 13 else 1.0) + math.exp(-((r - 22) / 6.0) ** 2) * (7 + 2.5 * math.sin(a * 5 + 1) + 1.5 * math.sin(a * 11)) + max(0.0, (r - 66) / 10.0) ** 1.6 * 6
def hgt_m(x, y):
    r = math.hypot(x, y); return 0.2 * math.sin(x * 0.21 + 1.3) * math.cos(y * 0.17) * (0.2 if r < 16 else 1.0) + 9 * math.exp(-(((x + 6) / 16.0) ** 2 + ((y - 40) / 7.0) ** 2)) + max(0.0, (r - 66) / 10.0) ** 1.6 * 6
hgt = hgt_h if PRESET == "haram" else hgt_m
def col(x, y, z):
    base = np.array([224, 190, 142.0]); k = min(1.0, max(0.0, (z - 1.0) / 5.0)); return base * (1 - k) + np.array([146, 106, 88.0]) * k
def build():
    sc = Scene(); terrain(sc, hgt, col, n=66, ext=84.0)
    if PRESET == "haram":
        city(sc, hgt, 0, 0, 10.5, 200, hole=3.6); sc.quad((-3.2, -3.2, 0.04), (3.2, -3.2, 0.04), (3.2, 3.2, 0.04), (-3.2, 3.2, 0.04), (236, 226, 204), layer=1, ds=True)
        sc.box(0, 0, 0, 1.5, 1.5, 1.8, (26, 24, 26), top=(40, 38, 40)); sc.box(0, 0, 1.25, 1.54, 1.54, 0.16, (212, 170, 70))
    else:
        city(sc, hgt, 0, 0, 12, 170, hole=4.6); sc.quad((-4.2, -3.6, 0.04), (4.2, -3.6, 0.04), (4.2, 3.6, 0.04), (-4.2, 3.6, 0.04), (236, 226, 204), layer=1, ds=True)
        sc.box(0, 0, 0, 5.0, 3.6, 1.3, (244, 240, 230), top=(250, 248, 242)); sc.pyramid(-1.2, 0.4, 1.3, 0.95, 0.9, (40, 128, 86), n=8)
        for mx, my_ in ((-2.7, -2.0), (2.7, -2.0), (-2.7, 2.0), (2.7, 2.0)): sc.box(mx, my_, 0, 0.4, 0.4, 3.4, (244, 240, 230)); sc.pyramid(mx, my_, 3.4, 0.34, 0.6, (212, 170, 70), n=6)
        for _ in range(70):
            a = random.uniform(0, 6.283); r = random.uniform(13, 22); palm(sc, hgt, r * math.cos(a), r * math.sin(a))
    return sc
TAWAF = [(random.uniform(2.0, 5.0), random.uniform(0, 6.283), random.uniform(0.8, 1.2)) for _ in range(140)]
def dynamic(t):
    d = Scene(); glows = []
    if PRESET == "haram":
        for r, ph, sp in TAWAF:
            ang = ph + t * 0.45 * sp; d.box(r * math.cos(ang), r * math.sin(ang), 0.05, 0.2, 0.2, 0.3, (248, 246, 240), rot=ang)
        glows.append((0, 0, 1.6, 2.4 + 0.3 * math.sin(t * 3)))
    return d, glows
def cam(t):
    k = sum(1 for x in TS if t >= x); u = smooth((t - TS[k - 1]) / 1.2) if k > 1 else 1.0
    R = [30, 13, 18, 11, 22, 26][(k - 1) % 6]; Hh = [14, 7, 13, 6, 18, 20][(k - 1) % 6]; Rp = [30, 13, 18, 11, 22, 26][(k - 2) % 6]; Hp = [14, 7, 13, 6, 18, 20][(k - 2) % 6]
    R = lerp(Rp, R, u) if k > 1 else R; Hh = lerp(Hp, Hh, u) if k > 1 else Hh; a = -1.4 + 0.10 * t + 0.5 * (k - 1 + u - 1)
    if PRESET != "haram": R, Hh = R * 1.5, Hh * 1.3
    return (R * math.cos(a), R * math.sin(a), Hh), (0, 0, 0.8)
def env(t): return pmix("dawn", "day", (t - T2) / 1.5) if t < TL else pmix("day", "dusk", (t - TL) / 1.5)
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
        dd.text((128, y + 37), txt, font=font("bold", 36), fill=(252, 248, 238, int(255 * p)), anchor="lm")
    paste(base, im, W / 2, 300 + hh / 2, a)
run(dict(S=S, tag="tp", out=os.environ.get("OUT", "tips.mp4"), build=build, dynamic=dynamic, cam=cam, env=env, overlay=overlay, fogd=0.006,
    hook=[(0.1, HOOK, 330)], labels=[("Kaabah" if PRESET == "haram" else "Masjid Nabawi", None, (0, 0, 2.4), 0.8, T2 - 0.2, GOLDT)], caps=[],
    cta=(t_simpan, t_simpan + 0.8, t_simpan + 1.6), lesson=LESSON,
    events={"whoosh": list(TS[1:]), "boom": [[0.05, 0.6]], "ticks": [x + 0.2 for x in TS[1:-1]], "riser_end": T2, "shimmer": TL, "pop": [t_simpan, t_simpan + 0.8]}))
