from ezlib import *
random.seed(41)
SC = [["Tiga ratus tiga belas orang,", "berdepan seribu tentera.", "Inilah Perang Badar."],
      ["Umat Islam tiba dahulu di lembah Badar.", "Seorang sahabat, Hubab bin Munzir,", "memberi cadangan:", "berkhemah di telaga yang paling hampir dengan musuh,", "dan kuasai sumber air."],
      ["Rasulullah menerima cadangan itu.", "Malam itu, hujan turun membasahi lembah."],
      ["Pagi tujuh belas Ramadan,", "tentera Quraisy yang jauh lebih ramai tiba,", "dan dikalahkan."],
      ["Hari ini, jemaah boleh menziarahi Badar,", "lebih seratus kilometer dari Madinah.", "#Simpan video ini, dan ingat pengajarannya: kemenangan bermula dengan musyawarah."]]
S = Script(SC, "we1.json"); S.DISP[S.wi("Rasulullah")] = "Rasulullah SAW"; T1, T2, T3, T4, T5 = S.TS
t_seribu = S.t("seribu"); t_tiba = S.t("tiba", 1); t_hubab = S.t("Hubab", 1); t_khemah = S.t("berkhemah", 1); t_telaga = S.t("telaga", 1); t_kuasai = S.t("kuasai", 1); t_malam = S.t("Malam", 2); t_hujan = S.t("hujan", 2)
t_pagi = S.t("Pagi", 3); t_qur = S.t("Quraisy", 3); t_tiba2 = S.t("tiba", 3); t_kalah = S.t("dikalahkan", 3); t_badar = S.t("Badar", 4); t_lebih = S.t("lebih", 4); t_simpan = S.t("Simpan", 4); t_ingat = S.t("ingat", 4); t_menang = S.t("kemenangan", 4)
WELLS = [(-4, 15), (3, 11), (-2, 6), (4, 1), (0, -6)]
def hgt(x, y):
    n = 0.25 * math.sin(x * 0.21 + 1.3) * math.cos(y * 0.17) + 0.15 * math.sin(x * 0.53 + y * 0.41); flat = 0.25 if abs(x) < 15 else 1.0
    side = 6.5 * (1 - math.exp(-(max(0.0, abs(x) - 17) / 7.0) ** 2)) * (0.8 + 0.2 * math.sin(y * 0.2 + x * 0.1))
    dune = 5.5 * math.exp(-((y + 24) / 5.5) ** 2) * (0.85 + 0.15 * math.sin(x * 0.3)); far = max(0.0, (math.hypot(x, y) - 66) / 10.0) ** 1.6 * 6
    return n * flat + side + dune + far
def col(x, y, z):
    base = np.array([228, 192, 142.0]); k = min(1.0, max(0.0, (z - 1.2) / 4.0)); return base * (1 - k) + np.array([196, 150, 104.0]) * k
def build():
    sc = Scene(); terrain(sc, hgt, col)
    for wx, wy in WELLS:
        sc.pyramid(wx, wy, 0.05, 1.0, 0.0, (70, 150, 204), n=8, emit=True, layer=1, ds=True)
        for k in range(8):
            a = 2 * math.pi * k / 8; sc.box(wx + 1.15 * math.cos(a), wy + 1.15 * math.sin(a), 0, 0.5, 0.36, 0.34, (170, 150, 128), rot=a + 1.57)
    for _ in range(26): palm(sc, hgt, random.uniform(-9, 9), random.uniform(-2, 18))
    for dx in (-1.2, 0, 1.2): sc.box(6 + dx, -3, 0, 0.7, 0.5, 1.5, (244, 240, 230), top=(252, 250, 244), t=T5)
    return sc
MUS = [(random.uniform(-5, 5), random.uniform(0, 5), random.uniform(0, 6.3), random.random()) for _ in range(32)]
QUR = [(-11.2 + 1.5 * c + random.uniform(-0.2, 0.2), -1.3 * r + random.uniform(-0.15, 0.15), random.uniform(0, 6.3), random.random()) for r in range(7) for c in range(16)]
TENT = [(random.uniform(-6, 6), random.uniform(-2.5, 3.5), random.uniform(0, 1.5), random.random()) for _ in range(9)]
def my(t):
    y = 34 - 20 * smooth(t / (t_tiba + 0.8))
    if t >= t_khemah: y -= 15.5 * smooth((t - t_khemah) / 2.6)
    if t >= t_tiba2: y -= 4 * smooth((t - t_tiba2) / 1.4)
    return y
def qy(t):
    y = -31.0
    if t >= t_qur - 0.6: y += 20 * smooth((t - (t_qur - 0.6)) / 2.6)
    if t >= t_kalah: y -= 30 * smooth((t - t_kalah - 0.2) / 2.4)
    return y
def dynamic(t):
    d = Scene(); gone = 1 - smooth((t - (T5 - 0.3)) / 0.6); glows = []
    if gone > 0.02:
        mv = t < t_tiba + 0.8 or t_khemah < t < t_khemah + 2.6 or t_tiba2 < t < t_tiba2 + 1.4; y0 = my(t)
        for x, y, ph, rr in MUS: unit(d, hgt, x, y0 + y, t, ph, MUSB, MUSF, gone, hop=mv)
        q0 = qy(t); qm = t_qur - 0.6 < t < t_qur + 2 or t > t_kalah
        for x, y, ph, rr in QUR:
            s_ = gone * (1 - 0.8 * smooth((t - t_kalah - rr * 1.2) / 0.8) if (t >= t_kalah and rr < 0.4) else 1)
            unit(d, hgt, x, q0 + y, t, ph, QURB, QURF, s_, hop=qm)
        if t >= t_malam - 0.4:
            for x, y, rot, rr in TENT:
                s_ = back((t - (t_malam - 0.4) - rr * 0.8) / 0.4) * gone
                if s_ > 0.03: d.pyramid(x + 8 * (1 if x > 0 else -1) * 0 + (7.5 if rr > 0.5 else -7.5), y, 0, 0.9 * s_, 1.1 * s_, (214, 204, 184), rot=rot)
    if t >= t_kuasai - 0.1 and t < T5:
        g = 0.6 + 0.4 * math.sin(t * 4); glows.append((0, -6, 0.3, 2.2 * g))
    return d, glows
K = [(0.0, (15, -56, 17), (0, -12, 0)), (T2 - 0.3, (12, -52, 20), (0, -8, 0)), (T2 + 1.6, (0, 38, 21), (0, 4, 0)), (t_khemah - 0.2, (1, 36, 20), (0, 3, 0)), (t_khemah + 2.2, (12, 12, 13), (0, -4, 0)), (t_kuasai + 0.8, (8, 3, 8), (0, -5.5, 0.3)),
     (T3 + 1.5, (-10, 8, 9), (0, -3, 0.5)), (T4 - 0.2, (-11, 9, 9.5), (0, -3, 0.5)), (T4 + 1.5, (-20, 8, 17), (0, -8, 0)), (t_kalah, (-21, 9, 18), (0, -9, 0)), (T5 - 0.2, (-22, 10, 19), (0, -10, 0)), (T5 + 2.2, (4, 22, 22), (1, -3, 0)), (S.END, (4, 30, 36), (1, -2, 0))]
def env(t):
    if t < T2: return PAL["dusk"]
    if t < t_malam - 0.5: return pmix("dusk", "day", (t - T2) / 1.0)
    if t < T4: return pmix("day", "night", (t - (t_malam - 0.5)) / 1.2)
    if t < T5: return pmix("night", "day", (t - T4) / 1.6)
    return pmix("day", "dawn", (t - T5) / 1.2)
RAIN = [(random.random(), random.random(), random.uniform(0.8, 1.5)) for _ in range(120)]
def overlay(base, d, t, proj):
    a = smooth((t - t_hujan + 0.3) / 0.6) * (1 - smooth((t - (T4 - 0.4)) / 0.6))
    if a > 0.02:
        for rx, ry, sp in RAIN:
            x = rx * W; y = ((ry + t * sp * 1.6) % 1.0) * H * 0.82 + 60; d.line([x, y, x - 10, y + 70], fill=(200, 216, 255, int(120 * a)), width=2)
def cnt(n, t0, dur, colr, txt):
    def f(t):
        v = int(n * ease((t - t0) / dur)); return (("{:,}".format(v), colr), (txt, INK))
    return f
run(dict(S=S, tag="e1", out=os.environ.get("OUT", "e1.mp4"), build=build, dynamic=dynamic, cam=lambda t: camera(K, t), env=env, overlay=overlay, fogd=0.0062,
    hook=[(0.1, cnt(313, 0.1, 0.9, GRN, " Muslimin"), 330), (t_seribu - 0.3, cnt(1000, t_seribu - 0.3, 0.8, REDT, " tentera Quraisy"), 462)],
    labels=[("Muslimin", "313 orang", lambda t: (0, my(t) + 2.5, 1.5), 0.6, T2 - 0.2, GRN), ("Quraisy", "sekitar 1,000", (0, -34, 1.5), t_seribu, T2 - 0.2, REDT), ("Telaga Badar", None, (0, -6, 0.4), t_telaga, T3 - 0.3, GOLDT),
            ("Sumber air", "dikuasai Muslimin", (0, -6, 0.4), T3 + 0.4, T4 - 0.3, GRN), ("Quraisy", "sekitar 1,000", lambda t: (0, qy(t) - 3, 1.5), t_qur + 1.2, t_kalah + 0.3, REDT), ("Medan Badar", None, (6, -3, 1.6), t_badar - 0.2, 999, GOLDT)],
    caps=[(T2 + 0.3, t_hubab - 0.3, [("Lembah ", INK), ("Badar", GOLDT)]), (t_hubab - 0.1, t_khemah - 0.3, [("Cadangan ", INK), ("Hubab bin Munzir", GOLDT)]), (t_khemah - 0.1, T3 - 0.2, [("Kuasai ", INK), ("sumber air", GOLDT)]),
          (T3 + 0.2, t_malam - 0.2, [("Cadangan ", INK), ("diterima", GRN)]), (t_malam - 0.1, T4 - 0.2, [("Malam itu, ", INK), ("hujan turun", GOLDT)]), (T4 + 0.2, t_kalah - 0.2, [("17 ", GOLDT), ("Ramadan", INK)]),
          (t_kalah - 0.1, T5 - 0.2, [("Quraisy ", INK), ("dikalahkan", REDT)]), (T5 + 0.3, t_simpan - 0.2, [("Ziarah ", INK), ("Badar", GOLDT)])],
    cta=(t_simpan, t_ingat, t_menang + 0.6), lesson="Kemenangan bermula dengan musyawarah", white=[t_kalah],
    events={"whoosh": [T2, T3, T4, T5], "boom": [[0.05, 0.7], [t_seribu, 0.8], [t_kuasai, 0.5], [t_kalah, 1.0]], "ticks": [t_hubab, t_telaga, t_pagi], "riser_end": t_kalah, "shimmer": T5 + 0.3, "pop": [t_simpan, t_ingat], "wind": [t_hujan - 0.3, T4]}))
