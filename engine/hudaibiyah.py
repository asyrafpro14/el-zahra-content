# Sirah: Perjanjian Hudaibiyah (tahun 6 Hijrah). Tanpa manusia: rombongan dan Quraisy hanya blok dengan bendera; wahyu hanya cahaya.
from ezlib import *
random.seed(48)
SC = [["Tahun keenam Hijrah.", "Sekitar seribu empat ratus orang Islam", "keluar dari Madinah.", "Bukan untuk berperang,", "tetapi untuk umrah."],
      ["Quraisy menghalang mereka", "daripada memasuki Makkah.", "Rombongan pun berhenti di Hudaibiyah."],
      ["Di situ, satu perjanjian dimeterai.", "Gencatan senjata selama sepuluh tahun.", "Tetapi umat Islam mesti pulang pada tahun itu,", "dan hanya boleh berumrah", "pada tahun berikutnya."],
      ["Nampak seperti rugi.", "Namun selepas itu, turun Surah Al-Fath,", "tentang kemenangan yang nyata."],
      ["Hari ini, Hudaibiyah dikenali", "sebagai Asy-Syumaisi,", "tidak jauh dari Makkah,", "di laluan ke Jeddah."],
      ["Pengajarannya: sabar dan berdamai", "kadangkala membuka jalan yang lebih besar.", "#Follow El Zahra Travel untuk kisah seterusnya."]]
S = Script(SC, "hudaibiyah.json"); T1, T2, T3, T4, T5, T6 = S.TS
t_sekitar = S.t("Sekitar"); t_keluar = S.t("keluar"); t_bukan = S.t("Bukan"); t_makkah = S.t("Makkah", 1); t_romb = S.t("Rombongan", 1); t_berhenti = S.t("berhenti", 1); t_hud = S.t("Hudaibiyah", 1)
t_janji = S.t("perjanjian", 2); t_gencat = S.t("Gencatan", 2); t_tetapi = S.t("Tetapi", 2); t_pulang = S.t("pulang", 2); t_namun = S.t("Namun", 3); t_turun = S.t("turun", 3); t_surah = S.t("Surah", 3)
t_syu = S.t("Asy-Syumaisi", 4); t_tidak = S.t("tidak", 4); t_jeddah = S.t("Jeddah", 4); t_follow = S.t("Follow", 5); t_untuk = S.t("untuk", 5)
MD, MK, HD, JD = (5.0, 40.0), (9.0, -30.0), (-3.0, -29.0), (-17.5, -27.0); CAMP = (-3.0, -25.0)
PEAKS = [(random.uniform(17, 36), random.uniform(-50, 46), random.uniform(2.5, 6), random.uniform(2.5, 4.5)) for _ in range(20)] + [(random.uniform(-17, -9), random.uniform(-12, 34), random.uniform(2, 4.5), random.uniform(2.5, 4)) for _ in range(8)]
def coast(y): return -21 + 2.0 * math.sin(y * 0.14) + 1.1 * math.sin(y * 0.37 + 1)
def hgt(x, y):
    if x < coast(y): return -0.25
    n = 0.25 * math.sin(x * 0.21 + 1.3) * math.cos(y * 0.17) + 0.15 * math.sin(x * 0.53 + y * 0.41) + 0.3; z = 0.0
    for px, py, ph, pr in PEAKS: z += ph * math.exp(-(((x - px) / pr) ** 2 + ((y - py) / pr) ** 2))
    return n * min(1.0, (x - coast(y)) / 3.0) + z * min(1.0, (x - coast(y)) / 6.0)
def col(x, y, z):
    if x < coast(y): return (58, 132, 176)
    base = np.array([226, 192, 144.0]); k = min(1.0, max(0.0, (z - 1.0) / 4.5)); return base * (1 - k) + np.array([150, 108, 86.0]) * k
ROUTE = [(MD[0] - 1, MD[1] - 5), (3, 24), (0, 8), (-2, -8), (-3, -18), CAMP]; U_STOP = 1.0
def prog(t):
    if t < t_pulang: return U_STOP * smooth((t - t_keluar + 0.4) / (t_berhenti + 0.3 - t_keluar + 0.4))
    return U_STOP - 0.42 * smooth((t - t_pulang) / (T5 - t_pulang))
def mpos(t):
    x, y = polyline(ROUTE, prog(t)); return x, y, hgt(x, y)
ROAD = [MK, (3.5, -29.2), HD, (-10, -27.5), JD]
def build():
    sc = Scene(); terrain(sc, hgt, col, n=72, ext=86.0)
    city(sc, hgt, MD[0], MD[1], 5.5, 80)
    for _ in range(60): palm(sc, hgt, MD[0] + random.uniform(-10, 10), MD[1] + random.uniform(-9, 9))
    city(sc, hgt, MK[0], MK[1], 5.0, 80, hole=1.6); sc.box(MK[0], MK[1], hgt(*MK), 1.1, 1.1, 1.3, (26, 24, 26), top=(40, 38, 40)); sc.box(MK[0], MK[1], hgt(*MK) + 0.9, 1.14, 1.14, 0.12, (212, 170, 70))
    city(sc, hgt, JD[0] + 1.5, JD[1], 3.6, 46, t=T5 + 0.2)
    zq = hgt(*HD)       # Masjid Asy-Syumaisi hari ini
    sc.box(HD[0], HD[1], zq, 2.4, 1.9, 1.1, (244, 240, 230), top=(252, 250, 244), t=t_syu - 0.2); sc.pyramid(HD[0], HD[1], zq + 1.1, 0.85, 0.75, (250, 248, 240), n=8, t=t_syu)
    sc.box(HD[0] + 1.5, HD[1] - 1.1, zq, 0.4, 0.4, 3.0, (244, 240, 230), t=t_syu + 0.1); sc.pyramid(HD[0] + 1.5, HD[1] - 1.1, zq + 3.0, 0.34, 0.6, (212, 170, 70), n=6, t=t_syu + 0.2)
    for k in range(44):
        if k % 2: continue
        a, b = polyline(ROAD, k / 44.0), polyline(ROAD, (k + 1) / 44.0); dx, dy = b[0] - a[0], b[1] - a[1]; ln = math.hypot(dx, dy) + 1e-6; nx, ny = -dy / ln * 0.2, dx / ln * 0.2; za, zb = hgt(*a) + 0.08, hgt(*b) + 0.08
        sc.quad((a[0] - nx, a[1] - ny, za), (b[0] - nx, b[1] - ny, zb), (b[0] + nx, b[1] + ny, zb), (a[0] + nx, a[1] + ny, za), (240, 236, 226), ds=True, t=T5 + 0.3 + 1.2 * k / 44.0)
    return sc
MUS = [(random.uniform(-1.6, 1.6), random.uniform(-2.6, 2.6), random.uniform(0, 6.3)) for _ in range(40)]
QUR = [(MK[0] + random.uniform(-3, 3), MK[1] + random.uniform(-3, 3), 3.4 + random.uniform(-0.5, 0.5), -33 + 10.0 * k / 25.0, random.uniform(0, 6.3)) for k in range(26)]
TENT = [(CAMP[0] + ox, CAMP[1] + oy) for ox, oy in [(-3.4, 1.2), (-3.0, -1.6), (3.0, 1.8), (-4.6, -0.2), (3.4, -0.6), (-2.2, 3.4), (2.0, 3.6)]]
def dynamic(t):
    d = Scene(); glows = []; x, y, z = mpos(t); sm = smooth((t - t_sekitar + 0.3) / 0.6) * (1 - smooth((t - (T5 - 0.9)) / 0.8)); moving = (t_keluar < t < t_berhenti + 0.3) or t > t_pulang
    for ox, oy, ph in MUS: unit(d, hgt, x + ox, y + oy, t, ph, MUSB, MUSF, sm, hop=moving)
    sq = smooth((t - T2 + 0.1) / 0.6) * (1 - smooth((t - (T5 - 0.9)) / 0.8)); uq = smooth((t - T2) / (t_makkah + 0.6 - T2))
    for x0, y0, x1, y1, ph in QUR: unit(d, hgt, lerp(x0, x1, uq), lerp(y0, y1, uq), t, ph, QURB, QURF, sq, hop=uq < 0.98)
    st = ease((t - t_berhenti - 0.2) / 0.5) * (1 - smooth((t - (T4 - 0.6)) / 0.8))
    if st > 0.03:
        for tx, ty in TENT: d.pyramid(tx, ty, hgt(tx, ty), 0.75 * st, 0.95 * st, (240, 230, 206), n=4)
    ss = ease((t - t_janji) / 0.4) * (1 - smooth((t - (T4 - 0.8)) / 0.6))   # helaian perjanjian (skrol), di antara dua pihak
    if ss > 0.03:
        zs = hgt(0.2, -27.0); d.box(0.2, -27.0, zs + 0.35, 0.10, 1.7 * ss, 1.25 * ss, (246, 238, 214)); d.box(0.2, -27.0, zs + 0.22, 0.20, 1.9 * ss, 0.16, (212, 170, 70)); d.box(0.2, -27.0, zs + 0.35 + 1.25 * ss, 0.20, 1.9 * ss, 0.16, (212, 170, 70))
    if t_turun - 0.2 <= t < T5:   # wahyu digambarkan sebagai cahaya sahaja
        zz = lerp(13.0, 2.6, smooth((t - t_turun + 0.2) / 1.4)); glows.append((x, y, z + zz, 2.6 + 0.4 * math.sin(t * 4))); d.pyramid(x, y, z + zz, 0.4, 0.7, (255, 224, 150), n=4, emit=True); d.pyramid(x, y, z + zz, 0.4, -0.5, (240, 196, 100), n=4, emit=True, ds=True)
    if t >= t_syu: glows.append((HD[0], HD[1], hgt(*HD) + 1.6, 1.6 + 0.2 * math.sin(t * 3)))
    return d, glows
def trk(tt, off, dz=0.6): x, y, z = mpos(tt); return (tt, (x + off[0], y + off[1], off[2]), (x, y, z + dz))
K = [(0.0, (MD[0] + 17, MD[1] - 12, 13), (MD[0], MD[1] - 2, 0.8)), (t_sekitar, (MD[0] + 15, MD[1] - 14, 11), (MD[0] - 1, MD[1] - 5, 0.8)), trk(t_keluar + 1.2, (13, -9, 9)), trk(t_bukan + 1.0, (14, -11, 10)), trk(T2 - 0.3, (15, -12, 12)),
     (T2 + 1.6, (24, -46, 19), (3, -29, 0)), (t_romb, (20, -48, 17), (1, -27, 0)), (T3 - 0.3, (12, -44, 13), (-1, -26, 0.5)),
     (T3 + 1.5, (7.5, -36.5, 5.5), (-0.6, -26.6, 1.0)), (t_tetapi - 0.2, (8.5, -35.5, 6.5), (-0.6, -26.4, 1.0)), trk(t_pulang + 1.8, (15, -18, 14)), trk(T4 - 0.2, (16, -18, 15)),
     trk(t_namun, (15, -16, 13), 1.5), trk(t_surah, (13, -14, 11), 2.5), trk(T5 - 0.3, (12, -13, 10), 2.5),
     (T5 + 1.8, (-2, -60, 36), (-4, -27, 0)), (t_jeddah + 1.0, (-5, -58, 34), (-5, -27, 0)), (T6 + 1.5, (4, -40, 9), (HD[0], HD[1], 1.2)), (t_follow, (5, -38.5, 8), (HD[0], HD[1], 1.4)), (S.END, (7, -41, 12), (HD[0], HD[1] + 1, 1.0))]
def cam(t): return camera(K, t)
def env(t):
    if t < T2: return pmix("dawn", "day", (t - 0.5) / 2.0)
    if t < T3: return pmix("day", "war", (t - T2) / 1.2)
    if t < T4: return pmix("war", "day", (t - T3) / 1.2)
    if t < T5: return pmix("day", "dusk", (t - T4) / 1.2) if t < t_turun else pmix("dusk", "dawn", (t - t_turun) / 1.5)
    return pmix("dawn", "day", (t - T5) / 1.5)
def lpos(t): x, y, z = mpos(t); return (x, y, z + 1.6)
QL = (3.4, -28.0, hgt(3.4, -28.0) + 1.6)
run(dict(S=S, tag="hd", out=os.environ.get("OUT", "hudaibiyah.mp4"), build=build, dynamic=dynamic, cam=cam, env=env, fogd=0.0058,
    hook=[(0.1, [("Tahun 6 ", GOLDT), ("Hijrah", INK)], 330), (t_bukan - 0.2, [("Bukan ", REDT), ("untuk berperang", INK)], 462)],
    labels=[("Madinah", None, (MD[0], MD[1], 2.4), 0.7, t_bukan - 0.4, INK), ("Rombongan umrah", "sekitar 1,400 orang", lpos, t_sekitar + 0.4, T2 - 0.3, GOLDT),
            ("Makkah", None, (MK[0], MK[1], 2.2), T2 + 1.0, T3 - 0.3, INK), ("Quraisy", "menghalang laluan", QL, t_makkah - 0.6, T3 - 0.3, REDT), ("Hudaibiyah", None, (CAMP[0], CAMP[1], 2.4), t_hud, T3 - 0.3, GOLDT),
            ("Perjanjian Hudaibiyah", None, (0.2, -27.0, hgt(0.2, -27.0) + 2.2), t_janji + 0.3, t_pulang, GOLDT), ("Surah Al-Fath", "ayat 1", lambda t: (mpos(t)[0], mpos(t)[1], mpos(t)[2] + 4.2), t_surah, T5 - 0.3, GOLDT),
            ("Makkah", None, (MK[0], MK[1], 2.2), T5 + 1.0, T6 + 0.4, INK), ("Asy-Syumaisi", "Hudaibiyah", (HD[0], HD[1], 3.4), t_syu + 0.2, 999, GOLDT), ("Jeddah", None, (JD[0] + 1.5, JD[1], 1.8), t_jeddah, T6 + 0.4, INK)],
    caps=[(T2 + 0.3, t_romb - 0.2, [("Dihalang ", REDT), ("masuk Makkah", INK)]), (t_romb - 0.1, T3 - 0.2, [("Berhenti di ", INK), ("Hudaibiyah", GOLDT)]),
          (t_gencat - 0.1, t_tetapi - 0.2, [("Gencatan senjata ", INK), ("10 tahun", GOLDT)]), (t_tetapi - 0.1, T4 - 0.2, [("Umrah ", INK), ("tahun berikutnya", GOLDT)]),
          (T4 + 0.2, t_namun - 0.2, [("Nampak seperti ", INK), ("rugi", REDT)]), (t_turun - 0.1, T5 - 0.2, [("Kemenangan ", INK), ("yang nyata", GOLDT)]),
          (t_tidak - 0.1, T6 - 0.2, [("Laluan ", INK), ("Makkah ke Jeddah", GOLDT)]), (T6 + 0.3, t_follow - 0.2, [("Sabar dan ", INK), ("berdamai", GRN)])],
    cta=(t_follow, t_untuk, t_untuk + 0.8), lesson="Sabar membuka jalan yang lebih besar", white=[t_turun + 1.0],
    events={"whoosh": [T2, T3, T4, T5, T6], "boom": [[0.05, 0.6], [t_makkah - 0.3, 0.7], [t_janji, 0.5]], "ticks": [t_sekitar, t_gencat, t_tetapi, t_tidak], "riser_end": t_turun + 1.0, "shimmer": t_turun + 0.6, "pop": [t_follow, t_untuk]}))
