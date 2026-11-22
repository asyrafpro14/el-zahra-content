from ezlib import *
random.seed(43)
SC = [["Sepuluh ribu tentera mara ke sebuah kota.", "Tetapi hari itu berakhir dengan kemaafan.", "Inilah Fathu Makkah."],
      ["Tahun kelapan Hijrah.", "Malam sebelum memasuki Makkah,", "setiap tentera diperintah menyalakan api.", "Ribuan unggun api menerangi bukit."],
      ["Esoknya, tentera Islam masuk dari empat arah.", "Penduduk dijamin selamat jika berada di rumah,", "atau di Masjidil Haram."],
      ["Makkah dibuka hampir tanpa pertempuran.", "Berhala di sekeliling Kaabah dimusnahkan,", "dan penduduknya dimaafkan."],
      ["Hari ini, jutaan jemaah bertawaf", "di tempat yang sama.", "#Simpan video ini, dan ingat: kemenangan paling besar ialah memaafkan."]]
S = Script(SC, "we3.json"); T1, T2, T3, T4, T5 = S.TS
t_tetapi = S.t("Tetapi"); t_inilah = S.t("Inilah"); t_malam = S.t("Malam", 1); t_api = S.t("menyalakan", 1); t_ribuan = S.t("Ribuan", 1); t_masuk = S.t("masuk", 2); t_empat = S.t("empat", 2); t_penduduk = S.t("Penduduk", 2); t_haram = S.t("Masjidil", 2)
t_dibuka = S.t("dibuka", 3); t_berhala = S.t("Berhala", 3); t_musnah = S.t("dimusnahkan", 3); t_maaf = S.t("dimaafkan", 3); t_tawaf = S.t("bertawaf", 4); t_simpan = S.t("Simpan", 4); t_ingat = S.t("ingat", 4); t_menang = S.t("kemenangan", 4)
def hgt(x, y):
    r = math.hypot(x, y); a = math.atan2(y, x); n = 0.22 * math.sin(x * 0.21 + 1.3) * math.cos(y * 0.17) + 0.14 * math.sin(x * 0.53 + y * 0.41)
    gap = max(math.exp(-((math.sin(a)) / 0.22) ** 2), math.exp(-((math.cos(a)) / 0.22) ** 2))
    ring = math.exp(-((r - 21) / 6.0) ** 2) * (7.5 + 2.5 * math.sin(a * 5 + 1) + 1.5 * math.sin(a * 11)) * (1 - 0.86 * gap)
    return n * (0.25 if r < 13 else 1.0) + ring + max(0.0, (r - 66) / 10.0) ** 1.6 * 6
def col(x, y, z):
    base = np.array([224, 190, 142.0]); k = min(1.0, max(0.0, (z - 1.0) / 5.0)); return base * (1 - k) + np.array([146, 106, 88.0]) * k
IDOLS = [(2.3 * math.cos(2 * math.pi * k / 14), 2.3 * math.sin(2 * math.pi * k / 14), random.uniform(0.5, 0.9), random.random()) for k in range(14)]
def build():
    sc = Scene(); terrain(sc, hgt, col, n=70, ext=84.0); city(sc, hgt, 0, 0, 10.5, 210, hole=3.6)
    sc.quad((-3.2, -3.2, 0.04), (3.2, -3.2, 0.04), (3.2, 3.2, 0.04), (-3.2, 3.2, 0.04), (236, 226, 204), layer=1, ds=True)
    sc.box(0, 0, 0, 1.5, 1.5, 1.8, (26, 24, 26), top=(40, 38, 40)); sc.box(0, 0, 1.25, 1.54, 1.54, 0.16, (212, 170, 70))
    return sc
ARMY = []
for dirx, diry in ((0, 1), (0, -1), (1, 0), (-1, 0)):
    for k in range(36): ARMY.append((dirx, diry, (k % 4 - 1.5) * 0.95 + random.uniform(-0.15, 0.15), (k // 4) * 1.25 + random.uniform(-0.15, 0.15), random.uniform(0, 6.3)))
HOOKA = [(-14 + 2.0 * c + random.uniform(-0.3, 0.3), r * 1.4 + random.uniform(-0.2, 0.2), random.uniform(0, 6.3)) for r in range(8) for c in range(15)]
FIRES = []
while len(FIRES) < 150:
    a = random.uniform(0, 6.283); r = random.uniform(15.5, 26); FIRES.append((r * math.cos(a), r * math.sin(a), random.random(), a))
TAWAF = [(random.uniform(2.0, 5.2), random.uniform(0, 6.283), random.uniform(0.8, 1.2)) for _ in range(150)]
def adist(t):
    if t < t_masuk - 0.4: return 34.0
    return 34.0 - 21.5 * smooth((t - (t_masuk - 0.4)) / 3.6)
def dynamic(t):
    d = Scene(); glows = []
    if t < T2 + 0.4:
        fy = 40 - 8 * smooth(t / T2); s_ = 1 - smooth((t - T2 + 0.2) / 0.5)
        for x, y, ph in HOOKA: unit(d, hgt, x, fy + y, t, ph, MUSB, MUSF, s_, hop=True)
    if t_malam - 0.3 <= t < T3 + 1.2:
        out = 1 - smooth((t - (T3 + 0.2)) / 0.9)
        for k, (x, y, rr, a) in enumerate(FIRES):
            wave = ((a + 2.2) % 6.283) / 6.283; s_ = back((t - (t_malam + 0.6) - wave * (t_ribuan + 0.8 - t_malam - 0.6)) / 0.35) * out
            if s_ <= 0.03: continue
            z = hgt(x, y); d.pyramid(x, y, z, 0.3 * s_, (0.8 + 0.15 * math.sin(t * 11 + k)) * s_, (255, 176, 74), emit=True, n=4)
            if k % 2 == 0: glows.append((x, y, z + 0.4, 1.3 * s_ * (0.85 + 0.15 * math.sin(t * 9 + k))))
    if t >= t_masuk - 0.6 and t < T5 + 0.5:
        r0 = adist(t); gone = 1 - smooth((t - (T5 - 0.3)) / 0.7); mv = t < t_masuk + 3.2
        for dx, dy, lat, back_, ph in ARMY:
            r = r0 + back_; x, y = dx * r + (-dy) * lat, dy * r + dx * lat; unit(d, hgt, x, y, t, ph, MUSB, MUSF, gone * back((t - (t_masuk - 0.6)) / 0.4), hop=mv)
    for k, (x, y, h, rr) in enumerate(IDOLS):
        s_ = 1 - smooth((t - t_musnah + 0.5 - rr * 0.9) / 0.35) if t >= t_musnah - 0.5 else 1.0
        if s_ > 0.03: d.box(x, y, 0.04, 0.34 * s_, 0.34 * s_, h * s_, (120, 112, 108))
    if t >= T5 - 0.2:
        a_ = smooth((t - (T5 - 0.2)) / 1.0)
        for k, (r, ph, sp) in enumerate(TAWAF):
            if k / 150.0 > a_: continue
            ang = ph - t * 0.45 * sp; d.box(r * math.cos(ang), r * math.sin(ang), 0.05, 0.2, 0.2, 0.3, (248, 246, 240), rot=ang)
    if t_penduduk <= t < T4: glows.append((0, 0, 1.2, 3.0 * smooth((t - t_haram + 0.4) / 0.5)))
    if t >= t_maaf - 0.1: glows.append((0, 0, 1.6, 2.6 + 0.4 * math.sin(t * 3)))
    return d, glows
K = [(0.0, (0, 66, 13), (0, 18, 1)), (T2 - 0.3, (0, 62, 17), (0, 12, 0)), (T2 + 1.6, (30, -44, 22), (-6, 6, 0)), (t_api, (34, -38, 22), (-5, 8, 0)), (T3 - 0.3, (44, -22, 26), (-6, 6, 0)),
     (T3 + 1.7, (0, -42, 64), (0, 2, 0)), (t_penduduk - 0.2, (0, -40, 60), (0, 2, 0)), (t_penduduk + 1.6, (9, -15, 13), (0, 0, 0.5)), (T4 - 0.2, (8, -14, 12), (0, 0, 0.5)),
     (T4 + 1.5, (13, -24, 20), (0, 1, 0)), (t_berhala - 0.2, (12, -22, 19), (0, 1, 0)), (t_berhala + 1.2, (5.5, -8.5, 6.5), (0, 0, 0.9)), (T5 - 0.2, (4.5, -8, 6.2), (0, 0, 0.9)),
     (T5 + 2.2, (0, -9, 17), (0, 0.5, 0)), (S.END, (0, -13, 30), (0, 1, 0))]
def env(t):
    if t < T2: return PAL["dusk"]
    if t < T3: return pmix("dusk", "night", (t - T2) / 1.0)
    if t < T4: return pmix("night", "day", (t - T3) / 1.4)
    if t < T5: return pmix("day", "dawn", (t - (t_maaf - 0.4)) / 1.0)
    return PAL["dawn"]
def cnt(t):
    v = int(10000 * ease((t - 0.1) / 0.9)); v = v // 100 * 100 if v < 10000 else 10000; return (("{:,}".format(v), GRN), (" tentera", INK))
run(dict(S=S, tag="e3", out=os.environ.get("OUT", "e3.mp4"), build=build, dynamic=dynamic, cam=lambda t: camera(K, t), env=env, fogd=0.006,
    hook=[(0.1, cnt, 330), (t_tetapi - 0.1, [("Berakhir dengan ", INK), ("kemaafan", GOLDT)], 462)],
    labels=[("Makkah", None, (0, 0, 2.4), 1.2, T2 - 0.2, INK), ("Unggun api", "ribuan, di sekeliling bukit", (-14, 14, 6.0), t_ribuan, T3 - 0.3, GOLDT), ("Utara", None, (0, 15, 1.6), t_empat, t_penduduk - 0.3, GRN), ("Selatan", None, (0, -15, 1.6), t_empat + 0.15, t_penduduk - 0.3, GRN),
            ("Timur", None, (15, 0, 1.6), t_empat + 0.3, t_penduduk - 0.3, GRN), ("Barat", None, (-15, 0, 1.6), t_empat + 0.45, t_penduduk - 0.3, GRN), ("Masjidil Haram", "selamat", (0, 0, 2.2), t_haram, T4 - 0.3, GOLDT),
            ("Di rumah", "selamat", (6, -5, 1.4), t_penduduk + 1.7, T4 - 0.3, GRN), ("Kaabah", None, (0, 0, 2.2), t_berhala + 1.3, T5 - 0.3, GOLDT)],
    caps=[(T2 + 0.3, t_malam - 0.2, [("Tahun ", INK), ("8 Hijrah", GOLDT)]), (t_malam - 0.1, t_ribuan - 0.2, [("Malam sebelum ", INK), ("memasuki Makkah", GOLDT)]), (t_ribuan - 0.1, T3 - 0.2, [("Ribuan ", GOLDT), ("unggun api", INK)]),
          (T3 + 0.2, t_penduduk - 0.2, [("Masuk dari ", INK), ("empat arah", GRN)]), (t_penduduk - 0.1, T4 - 0.2, [("Penduduk ", INK), ("dijamin selamat", GRN)]), (T4 + 0.2, t_berhala - 0.2, [("Hampir tanpa ", INK), ("pertempuran", GRN)]),
          (t_berhala - 0.1, t_maaf - 0.3, [("Berhala ", INK), ("dimusnahkan", REDT)]), (t_maaf - 0.2, T5 - 0.2, [("Penduduk ", INK), ("dimaafkan", GOLDT)]), (T5 + 0.3, t_simpan - 0.2, [("Tawaf ", GOLDT), ("di tempat yang sama", INK)])],
    cta=(t_simpan, t_ingat, t_menang + 1.2), lesson="Kemenangan paling besar ialah memaafkan", white=[t_maaf],
    events={"whoosh": [T2, T3, T4, T5], "boom": [[0.05, 0.7], [t_masuk, 0.6], [t_musnah, 0.8]], "ticks": [t_empat, t_empat + 0.15, t_empat + 0.3, t_empat + 0.45], "riser_end": t_maaf, "shimmer": t_maaf, "pop": [t_simpan, t_ingat]}))
