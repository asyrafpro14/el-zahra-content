from ezlib import *
random.seed(42)
SC = [["Tiga hari bersembunyi di dalam gua,", "sementara musuh mencari di merata tempat.", "Inilah permulaan Hijrah."],
      ["Dari Makkah, Rasulullah dan Abu Bakar", "tidak terus ke utara.", "Mereka ke selatan dahulu,", "menuju Gua Thur."],
      ["Pencari Quraisy sampai ke mulut gua,", "tetapi berpatah balik.", "Tiga hari kemudian, pencarian reda."],
      ["Mereka menyusur laluan pantai", "yang jarang dilalui,", "lebih empat ratus kilometer menuju Madinah."],
      ["Di Quba, masjid pertama dalam Islam dibina.", "Hari ini, jemaah menziarahi Masjid Quba.", "#Simpan video ini, dan kongsikan kepada yang bakal ke sana."]]
S = Script(SC, "we2.json"); S.DISP[S.wi("Rasulullah")] = "Rasulullah SAW"; T1, T2, T3, T4, T5 = S.TS
t_musuh = S.t("musuh"); t_inilah = S.t("Inilah"); t_utara = S.t("utara", 1); t_selatan = S.t("selatan", 1); t_thur = S.t("Gua", 1); t_mulut = S.t("mulut", 2); t_patah = S.t("berpatah", 2); t_reda = S.t("pencarian", 2)
t_susur = S.t("menyusur", 3); t_400 = S.t("lebih", 3); t_mad = S.t("Madinah", 3); t_quba = S.t("Quba", 4); t_hari = S.t("Hari", 4); t_simpan = S.t("Simpan", 4); t_kongsi = S.t("kongsikan", 4)
MK, TH, QB, MD = (6.0, -30.0), (9.0, -42.0), (2.0, 30.0), (3.0, 39.0)
PEAKS = [(random.uniform(4, 30), random.uniform(-22, 26), random.uniform(2.5, 6), random.uniform(2.5, 4.5)) for _ in range(22)] + [(random.uniform(18, 34), random.uniform(-48, -24), random.uniform(3, 6), random.uniform(3, 5)) for _ in range(6)]
def coast(y): return -15 + 2.2 * math.sin(y * 0.14) + 1.2 * math.sin(y * 0.37 + 1)
def hgt(x, y):
    if x < coast(y): return -0.25
    n = 0.25 * math.sin(x * 0.21 + 1.3) * math.cos(y * 0.17) + 0.15 * math.sin(x * 0.53 + y * 0.41) + 0.3
    z = 7.5 * math.exp(-(((x - TH[0]) / 3.6) ** 2 + ((y - TH[1]) / 3.6) ** 2))
    for px, py, ph, pr in PEAKS: z += ph * math.exp(-(((x - px) / pr) ** 2 + ((y - py) / pr) ** 2))
    return n * min(1.0, (x - coast(y)) / 3.0) + z * min(1.0, (x - coast(y)) / 6.0)
def col(x, y, z):
    if x < coast(y): return (58, 132, 176)
    base = np.array([226, 192, 144.0]); k = min(1.0, max(0.0, (z - 1.0) / 4.5)); return base * (1 - k) + np.array([150, 108, 86.0]) * k
ROUTE = [MK, (7.5, -36), TH, (2, -43), (-8, -38), (-11.5, -24), (-10.5, -6), (-11.5, 10), (-7, 22), QB]
U_TH = 2.0 / 9.0
def prog(t):
    if t < T4: return U_TH * smooth((t - (t_selatan - 0.3)) / (T3 - 0.4 - (t_selatan - 0.3)))
    return U_TH + (1 - U_TH) * smooth((t - (T4 + 0.1)) / (T5 + 0.2 - (T4 + 0.1)))
def mpos(t):
    x, y = polyline(ROUTE, prog(t)); return x, y, hgt(x, y)
def build():
    sc = Scene(); terrain(sc, hgt, col, n=72, ext=86.0)
    patch(sc, hgt, lambda x, y, z: (150 - 5 * z, 108 - 3 * z, 86) if z > 0.8 else None, TH[0] - 8, TH[0] + 8, TH[1] - 8, TH[1] + 8, m=24)
    city(sc, hgt, MK[0], MK[1], 5.5, 90, hole=1.6); sc.box(MK[0], MK[1], hgt(*MK), 1.1, 1.1, 1.3, (26, 24, 26), top=(40, 38, 40)); sc.box(MK[0], MK[1], hgt(*MK) + 0.9, 1.14, 1.14, 0.12, (212, 170, 70))
    sc.box(TH[0] - 0.6, TH[1] + 2.2, hgt(TH[0] - 0.6, TH[1] + 2.2) - 0.1, 1.5, 0.9, 1.3, (30, 24, 26))
    city(sc, hgt, MD[0], MD[1], 5.0, 70)
    for _ in range(50): palm(sc, hgt, MD[0] + random.uniform(-9, 9), MD[1] + random.uniform(-12, 5))
    zq = hgt(*QB); sc.box(QB[0], QB[1], zq, 2.6, 2.0, 1.2, (244, 240, 230), top=(252, 250, 244), t=t_quba + 0.3); sc.pyramid(QB[0], QB[1], zq + 1.2, 0.9, 0.8, (250, 248, 240), n=8, t=t_quba + 0.5)
    sc.box(QB[0] + 1.6, QB[1] - 1.2, zq, 0.4, 0.4, 3.0, (244, 240, 230), t=t_quba + 0.6); sc.pyramid(QB[0] + 1.6, QB[1] - 1.2, zq + 3.0, 0.34, 0.6, (212, 170, 70), n=6, t=t_quba + 0.7)
    for k in range(40):
        u = k / 40.0; x, y = MK[0] + (MD[0] - MK[0]) * u, MK[1] + (MD[1] - MK[1]) * u
        if k % 2 == 0: sc.box(x + 6 * math.sin(u * math.pi), y, hgt(x + 6 * math.sin(u * math.pi), y) + 0.05, 0.35, 0.9, 0.06, (240, 236, 226), t=t_utara - 0.4 + u * 0.8)
    return sc
SEARCH = [(random.uniform(0, 6.3), random.uniform(5, 15), random.uniform(0.6, 1.4), random.uniform(0, 6.3)) for _ in range(34)]
CLIMB = [(random.uniform(-1.2, 1.2), random.uniform(0, 1.8), random.uniform(0, 6.3)) for _ in range(8)]
def dynamic(t):
    d = Scene(); glows = []; u = prog(t); n = int(u * 180)
    for k in range(n):
        a, b = polyline(ROUTE, k / 180.0), polyline(ROUTE, (k + 0.7) / 180.0); dx, dy = b[0] - a[0], b[1] - a[1]; ln = math.hypot(dx, dy) + 1e-6; nx, ny = -dy / ln * 0.22, dx / ln * 0.22
        za, zb = hgt(*a) + 0.12, hgt(*b) + 0.12; d.quad((a[0] - nx, a[1] - ny, za), (b[0] - nx, b[1] - ny, zb), (b[0] + nx, b[1] + ny, zb), (a[0] + nx, a[1] + ny, za), (255, 206, 96), emit=True, ds=True)
    incave = (t < t_selatan - 0.3 and t < T2) or (T3 - 0.4 <= t < T4 + 0.1)
    if t < T2: glows.append((TH[0] - 0.6, TH[1] + 2.6, hgt(TH[0] - 0.6, TH[1] + 2.6) + 0.5, 1.6 + 0.3 * math.sin(t * 5)))
    elif incave: glows.append((TH[0] - 0.6, TH[1] + 2.6, hgt(TH[0] - 0.6, TH[1] + 2.6) + 0.5, 1.6 + 0.3 * math.sin(t * 5)))
    elif t >= t_selatan - 0.3 and t < t_quba + 1.5:
        x, y, z = mpos(t); d.pyramid(x, y, z + 0.5, 0.42, 0.7, (255, 214, 120), n=4, emit=True); d.pyramid(x, y, z + 0.5, 0.42, -0.5, (236, 186, 90), n=4, emit=True, ds=True); glows.append((x, y, z + 0.6, 1.8))
    sa = (1 - smooth((t - (T2 - 0.2)) / 0.5)) if t < T3 - 1 else smooth((t - (T3 - 0.3)) / 0.5) * (1 - smooth((t - (t_reda - 0.2)) / 1.2))
    if sa > 0.03:
        for ang, r, sp, ph in SEARCH:
            a = ang + 0.25 * math.sin(t * sp + ph); rr = r + 2.5 * math.sin(t * 0.7 * sp + ph); x, y = MK[0] + rr * math.cos(a), MK[1] - 4 + rr * math.sin(a) * 0.9
            if x > coast(y) + 1: unit(d, hgt, x, y, t, ph, QURB, QURF, sa, hop=True)
    if T3 - 0.2 <= t < t_reda + 1.0:
        up = smooth((t - (T3 - 0.2)) / (t_mulut + 0.5 - T3 + 0.2)) - smooth((t - t_patah) / 1.8); s_ = 1 - smooth((t - t_reda) / 1.0)
        for ox, oy, ph in CLIMB:
            x, y = lerp(TH[0] + 1 + ox * 2, TH[0] - 0.6 + ox, up), lerp(TH[1] + 11 + oy * 2, TH[1] + 3.6 + oy, up); unit(d, hgt, x, y, t, ph, QURB, QURF, s_, hop=True)
    return d, glows
K0 = [(0.0, (1, -27, 5.5), (TH[0] - 0.6, TH[1] + 2, 4.2)), (T2 - 0.3, (3, -29, 7), (TH[0] - 0.6, TH[1] + 2, 4.2)), (T2 + 1.6, (4, -70, 44), (6, -32, 0)), (T3 - 0.3, (5, -72, 42), (7, -36, 0)),
      (T3 + 1.4, (2, -30, 6.5), (TH[0] - 0.6, TH[1] + 2.5, 4.0)), (T4 - 0.2, (3, -31, 7.5), (TH[0] - 0.6, TH[1] + 2.5, 4.0))]
K1 = [(T5 + 0.3, (9, 17, 9), (QB[0], QB[1], 1.2)), (T5 + 2.5, (9.5, 20, 6.5), (QB[0], QB[1], 1.4)), (t_simpan, (10, 19, 8), (QB[0], QB[1] + 1, 1.4)), (S.END, (12, 12, 15), (QB[0], QB[1] + 3, 1.0))]
def cam(t):
    if t <= T4 - 0.2: return camera(K0, t)
    if t >= T5 + 0.3: return camera(K1, t)
    x, y, z = mpos(t); fp = np.array([x + 10, y - 24, 22.0]); ft = np.array([x, y + 5, 0.0]); a = smooth((t - (T4 - 0.2)) / 1.4); b = smooth((t - (T5 - 0.9)) / 1.2)
    p0, g0 = camera(K0, T4 - 0.2); p1, g1 = np.array(K1[0][1], float), np.array(K1[0][2], float)
    p = p0 * (1 - a) + fp * a; g = g0 * (1 - a) + ft * a; return p * (1 - b) + p1 * b, g * (1 - b) + g1 * b
def env(t):
    if t < T2: return PAL["night"]
    if t < T3: return pmix("night", "day", (t - T2) / 1.0)
    if t < T4: return pmix("day", "night", (t - T3) / 1.0)
    if t < T5: return pmix("night", "day", (t - T4) / 1.2)
    return pmix("day", "dawn", (t - T5) / 1.5)
run(dict(S=S, tag="e2", out=os.environ.get("OUT", "e2.mp4"), build=build, dynamic=dynamic, cam=cam, env=env, fogd=0.0058,
    hook=[(0.1, [("3 hari ", GOLDT), ("di dalam gua", INK)], 330), (t_musuh - 0.2, [("Musuh ", REDT), ("mencari", INK)], 462)],
    labels=[("Gua Thur", None, (TH[0] - 0.6, TH[1] + 2.2, hgt(TH[0] - 0.6, TH[1] + 2.2) + 1.3), 0.8, T2 - 0.2, GOLDT), ("Makkah", None, (MK[0], MK[1], 2.0), T2 + 1.2, T3 - 0.3, INK), ("Laluan biasa", "ke utara, ke Madinah", (10.5, -14, 0.5), t_utara, T3 - 0.3, INK),
            ("Gua Thur", "di selatan Makkah", (TH[0], TH[1], 7.6), t_thur, T3 - 0.3, GOLDT), ("Pencari Quraisy", None, (TH[0] - 0.4, TH[1] + 4.6, hgt(TH[0] - 0.4, TH[1] + 4.6) + 1.4), t_mulut - 0.3, t_reda, REDT),
            ("Laut Merah", None, (-22, -10, 0), t_susur + 0.6, T5 - 0.6, INK), ("Laluan Hijrah", "lebih 400 km", lambda t: mpos(t)[:2] + (mpos(t)[2] + 1.4,), t_400 - 0.2, T5 - 0.6, GOLDT),
            ("Masjid Quba", "masjid pertama dalam Islam", (QB[0], QB[1], 2.4), t_quba + 0.9, 999, GOLDT)],
    caps=[(T2 + 0.3, t_selatan - 0.3, [("Bukan terus ", INK), ("ke utara", REDT)]), (t_selatan - 0.1, T3 - 0.2, [("Ke selatan ", INK), ("dahulu", GOLDT)]), (T3 + 0.2, t_patah - 0.2, [("Sampai ke ", INK), ("mulut gua", REDT)]), (t_patah - 0.1, T4 - 0.2, [("Pencari ", INK), ("berpatah balik", GRN)]),
          (T4 + 0.2, t_400 - 0.2, [("Laluan ", INK), ("pantai", GOLDT)]), (t_400 - 0.1, T5 - 0.2, [("Lebih ", INK), ("400 km", GOLDT)]), (T5 + 0.3, t_simpan - 0.2, [("Masjid ", INK), ("Quba", GOLDT)])],
    cta=(t_simpan, t_kongsi, t_kongsi + 1.0), lesson="Kongsikan kepada yang bakal ke sana", white=[t_quba + 0.3],
    events={"whoosh": [T2, T3, T4, T5], "boom": [[0.05, 0.7], [t_mulut, 0.8], [t_quba + 0.3, 0.6]], "ticks": [t_utara, t_selatan, t_thur, t_400], "riser_end": t_mulut, "shimmer": T5 + 0.3, "pop": [t_simpan, t_kongsi]}))
