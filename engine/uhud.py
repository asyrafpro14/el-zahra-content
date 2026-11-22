import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lpe import *
random.seed(11)
OUT = os.environ.get("OUT", "uhud.mp4")
SCENES = [
    ["Lima puluh pemanah.", "Satu arahan.", "Dan satu bukit kecil yang mengubah Perang Uhud."],
    ["Tentera Quraisy seramai tiga ribu mara ke Madinah.", "Umat Islam sekitar tujuh ratus,", "berkubu membelakangi Gunung Uhud."],
    ["Rasulullah menempatkan lima puluh pemanah", "di atas sebuah bukit kecil, dengan pesanan:", "jangan tinggalkan tempat ini,", "walau apa pun yang berlaku."],
    ["Pada awalnya, umat Islam mendahului.", "Melihat harta rampasan,", "sebahagian besar pemanah turun dari bukit."],
    ["Pasukan berkuda Quraisy mengelilingi bukit itu,", "dan menyerang dari belakang.", "Tujuh puluh sahabat gugur syahid."],
    ["Hari ini, jemaah menziarahi Jabal Rumah", "dan makam syuhada Uhud.", "#Simpan video ini, dan ingat pengajarannya: taat pada arahan."],
]
S = Script(SCENES, os.environ.get("WORDS", "words7.json")); S.DISP[S.wi("Rasulullah")] = "Rasulullah SAW"
T1, T2, T3, T4, T5, T6 = S.TS; END, TOTAL = S.END, S.TOTAL
t_satu = S.t("Satu"); t_tiga = S.t("tiga", 1); t_umat = S.t("Umat", 1); t_uhud2 = S.t("Gunung", 1); t_lima = S.t("lima", 2); t_jangan = S.t("jangan", 2)
t_dahulu = S.t("mendahului", 3); t_harta = S.t("harta", 3); t_turun = S.t("turun", 3); t_keliling = S.t("mengelilingi", 4); t_serang = S.t("menyerang", 4); t_tujuh = S.t("Tujuh", 4)
t_jabal = S.t("Jabal", 5); t_makam = S.t("makam", 5); t_simpan = S.t("Simpan", 5); t_ingat = S.t("ingat", 5); t_taat = S.t("taat", 5)
EVENTS = {"total": END, "whoosh": [T2, T3, T4, T5, T6], "boom": [[0.05, 0.7], [t_jangan, 0.7], [t_serang, 1.0], [t_tujuh, 0.6]], "ticks": [t_tiga, t_umat, t_uhud2, t_lima],
          "riser_end": t_serang, "shimmer": T6 + 0.3, "pop": [t_simpan, t_ingat], "water": False}
if os.environ.get("EVENTS"): json.dump(EVENTS, open(os.environ["EVENTS"], "w")); print("events", END, [round(x, 2) for x in S.TS]); sys.exit(0)

PAL = {"dusk": ((1.0, 0.84, 0.62), (0.40, 0.39, 0.52), (214, 160, 128), (40, 46, 96), (244, 170, 112)),
       "day": ((1.0, 0.96, 0.86), (0.50, 0.50, 0.56), (226, 200, 166), (96, 140, 200), (238, 216, 184)),
       "war": ((0.92, 0.62, 0.50), (0.34, 0.30, 0.40), (150, 96, 92), (46, 30, 54), (190, 104, 84)),
       "dawn": ((1.0, 0.80, 0.70), (0.46, 0.42, 0.52), (240, 186, 156), (70, 92, 156), (255, 200, 156))}
def env(t):
    if t < T2: return PAL["dusk"]
    if t < T5: return mixp(PAL["dusk"], PAL["day"], smooth((t - T2) / 1.0))
    if t < T6: return mixp(PAL["day"], PAL["war"], smooth((t - (t_serang - 0.8)) / 1.2))
    return mixp(PAL["war"], PAL["dawn"], smooth((t - T6) / 1.2))

HX, HY = 12.0, 9.0
def hill(x, y): return 2.7 * math.exp(-(((x - HX) / 3.4) ** 2 + ((y - HY) / 2.6) ** 2))
def uh(x, y): return math.exp(-((y - 44) / 9.0) ** 2) * (15 + 5 * math.sin(x * 0.16 + 1) + 3 * math.sin(x * 0.47)) / (1 + (abs(x) / 48.0) ** 4)
def hgt(x, y):
    n = 0.3 * math.sin(x * 0.21 + 1.3) * math.cos(y * 0.17) + 0.18 * math.sin(x * 0.53 + y * 0.41)
    flat = 0.25 if (-18 < x < 28 and -10 < y < 28) else 1.0; d = math.hypot(x, y - 5)
    return n * flat + uh(x, y) + hill(x, y) + max(0.0, (d - 64) / 10.0) ** 1.6 * 6
def build():
    sc = Scene(); n, ext = 64, 82.0
    for i in range(n):
        for j in range(n):
            x0, x1 = -ext + 2 * ext * i / n, -ext + 2 * ext * (i + 1) / n; y0, y1 = -ext + 5 + 2 * ext * j / n, -ext + 5 + 2 * ext * (j + 1) / n
            a, b, c, d = (x0, y0, hgt(x0, y0)), (x1, y0, hgt(x1, y0)), (x1, y1, hgt(x1, y1)), (x0, y1, hgt(x0, y1))
            for tri in ((a, b, c), (a, c, d)):
                mx, my, mz = [sum(v[k] for v in tri) / 3 for k in range(3)]; base = np.array([226, 190, 140.0])
                m = min(1.0, uh(mx, my) / 5.0); base = base * (1 - m) + np.array([156, 92, 74.0]) * m * (0.85 + 0.15 * math.sin(mx * 0.7 + my))+ np.array([156, 92, 74.0]) * m * 0
                base = np.clip(base, 0, 255)
                sc.tri(*tri, tuple(base * random.uniform(0.94, 1.06)), layer=0, ds=True)
    # finer hill mesh
    m_ = 22
    for i in range(m_):
        for j in range(m_):
            x0, x1 = HX - 7 + 14 * i / m_, HX - 7 + 14 * (i + 1) / m_; y0, y1 = HY - 6 + 12 * j / m_, HY - 6 + 12 * (j + 1) / m_
            if max(hill(x0, y0), hill(x1, y1), hill(x0, y1), hill(x1, y0)) < 0.12: continue
            a, b, c, d = (x0, y0, hgt(x0, y0) + 0.02), (x1, y0, hgt(x1, y0) + 0.02), (x1, y1, hgt(x1, y1) + 0.02), (x0, y1, hgt(x0, y1) + 0.02)
            for tri in ((a, b, c), (a, c, d)):
                mx, my = sum(v[0] for v in tri) / 3, sum(v[1] for v in tri) / 3; k = min(1.0, hill(mx, my) / 1.6)
                base = np.array([222, 186, 138.0]) * (1 - k) + np.array([166, 124, 92.0]) * k
                sc.tri(*tri, tuple(base * random.uniform(0.92, 1.08)), layer=1, ds=True)
    placed = []
    for _ in range(600):
        ang = random.uniform(0, 2 * math.pi); rad = 6.5 * math.sqrt(random.random()); x, y = 5 + rad * math.cos(ang), -25 + rad * math.sin(ang) * 0.9
        sx, sy = random.uniform(0.7, 1.6), random.uniform(0.7, 1.6)
        if any(abs(x - px) < (sx + ps) / 2 + 0.2 and abs(y - py) < (sy + pq) / 2 + 0.2 for px, py, ps, pq in placed): continue
        placed.append((x, y, sx, sy)); h = random.uniform(0.55, 1.4); tone = random.uniform(0.88, 1.08)
        sc.box(x, y, hgt(x, y) - 0.1, sx, sy, h, (204 * tone, 166 * tone, 122 * tone), top=(236 * tone, 206 * tone, 160 * tone))
        if len(placed) > 130: break
    for _ in range(90):
        ang = random.uniform(0, 6.3); rad = random.uniform(7, 12); x, y = 5 + rad * math.cos(ang), -25 + rad * math.sin(ang); z = hgt(x, y); hh = random.uniform(1.3, 2.2)
        sc.box(x, y, z, 0.14, 0.14, hh, (104, 76, 54))
        for k in range(7):
            a = 2 * math.pi * k / 7; Ln = random.uniform(0.7, 1.0); w_ = 0.2
            sc.tri((x + w_ * math.cos(a + 1.57), y + w_ * math.sin(a + 1.57), z + hh), (x - w_ * math.cos(a + 1.57), y - w_ * math.sin(a + 1.57), z + hh), (x + Ln * math.cos(a), y + Ln * math.sin(a), z + hh - 0.28), (52, 134 * random.uniform(0.9, 1.1), 78), ds=True)
    for _ in range(45):
        x, y = random.uniform(-40, 44), random.uniform(-24, 30)
        if (-13 < x < 13 and -22 < y < 27) or hill(x, y) > 0.1: continue
        z = hgt(x, y); s_ = random.uniform(0.3, 0.9); tone = random.uniform(0.8, 1.1)
        sc.box(x, y, z - 0.05, s_, s_, s_ * 0.6, (150 * tone, 118 * tone, 92 * tone), rot=random.uniform(0, 3))
    for dx, dy, sx, sy in ((0, -1.1, 3.4, 0.16), (0, 1.1, 3.4, 0.16), (-1.7, 0, 0.16, 2.36), (1.7, 0, 0.16, 2.36)):
        sc.box(1.5 + dx, 14.5 + dy, 0, sx, sy, 0.45, (240, 236, 226), top=(250, 248, 240), t=T6)
    sc.quad((-0.1, 13.5, 0.04), (3.1, 13.5, 0.04), (3.1, 15.5, 0.04), (-0.1, 15.5, 0.04), (206, 196, 170), layer=1, ds=True, t=T6)
    return sc

MUS = [(-8.25 + 1.5 * c + random.uniform(-0.15, 0.15), 19 + 1.1 * r + random.uniform(-0.1, 0.1), random.uniform(0, 6.3), random.random()) for r in range(6) for c in range(12)]
QUR = [(-13.5 + 1.5 * c + random.uniform(-0.2, 0.2), -1.25 * r + random.uniform(-0.15, 0.15), random.uniform(0, 6.3)) for r in range(10) for c in range(15)]
ARC = []
for k in range(25):
    r_ = 1.75 * math.sqrt((k + 0.5) / 25.0); a_ = k * 2.39996; ARC.append((HX + r_ * 1.25 * math.cos(a_), HY + r_ * 0.9 * math.sin(a_), random.uniform(0, 6.3), random.uniform(1.5, 8.5), random.uniform(2.5, 7.5), random.random()))
SPOIL = [(random.uniform(-11, 7), random.uniform(1.5, 8), random.uniform(0.18, 0.34), random.random(), random.uniform(0, 3)) for _ in range(30)]
CAV = [(0.012 * k, random.uniform(-1.3, 1.3), random.uniform(0, 6.3)) for k in range(30)]
PATH = [(25, -9), (28.5, 3), (25.5, 14), (17, 22.5), (6, 24.2)]
def path(u):
    u = clamp(u) * (len(PATH) - 1); i = min(len(PATH) - 2, int(u)); f = u - i
    p0, p1, p2, p3 = PATH[max(0, i - 1)], PATH[i], PATH[i + 1], PATH[min(len(PATH) - 1, i + 2)]
    return tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * f + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * f * f + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * f ** 3) for k in (0, 1))
def cav_u(t): return 0.93 * smooth((t - (T5 + 0.1)) / (t_serang + 0.5 - T5))
def unit(d, x, y, t, ph, body, flag, s=1.0, hop=False, big=1.0):
    if s <= 0.03: return
    z = hgt(x, y) + (0.07 * abs(math.sin(t * 9 + ph)) if hop else 0); b = 0.42 * big
    d.box(x, y, z, b * s, b * s, 0.3 * s * big, body); d.box(x, y, z + 0.3 * s * big, 0.06, 0.06, 1.05 * s * big, (40, 30, 30))
    fl = 0.12 * math.sin(t * 7 + ph); d.tri((x, y, z + 1.35 * s * big), (x, y, z + 0.95 * s * big), (x + 0.55 * s * big, y + fl, z + 1.15 * s * big), flag, ds=True)
def qfront(t):
    y = 6.0
    if t >= T4: y -= 9 * smooth((t - (T4 + 0.5)) / 2.6)
    if t >= t_serang: y += 7 * smooth((t - t_serang) / 2.0)
    return y
def dynamic(t):
    d = Scene(); gone = 1 - smooth((t - (T6 - 0.35)) / 0.6)
    if gone <= 0.02: return d
    if t >= T2:
        fy = qfront(t); mv = (t < t_umat + 0.6) or (T4 + 0.5 < t < T4 + 3.1) or (t_serang < t < t_serang + 2)
        qs = 1 - smooth((t - (T2 + 0.2)) / (t_umat - T2 + 0.4)); mv = mv or qs > 0.01
        for x, r, ph in QUR: unit(d, x - 34 * qs, fy + r - 9 * qs, t, ph, (64, 44, 48), (176, 52, 46), gone, hop=mv)
    if t >= t_umat - 0.3:
        adv = -5 * smooth((t - (T4 + 0.3)) / 2.2) + (2.0 * smooth((t - t_serang) / 1.5) if t >= t_serang else 0)
        for k, (x, y, ph, rr) in enumerate(MUS):
            s_ = back((t - (t_umat - 0.3) - 0.012 * k) / 0.35) * gone; jx = 0.18 * math.sin(t * 23 + ph) * (clamp((t - t_serang) / 0.3) if t >= t_serang else 0)
            if t >= t_tujuh and rr < 0.3: s_ *= 1 - 0.75 * smooth((t - t_tujuh - rr * 3) / 0.8)
            unit(d, x + jx, y + adv, t, ph, (70, 96, 84), (40, 150, 96), s_, hop=(T4 + 0.3 < t < T4 + 2.5))
    for k, (x, y, ph, tx, ty, rr) in enumerate(ARC):
        s_ = back((t - 0.02 * k) / 0.4) * gone
        if k >= 5 and t >= t_turun - 1.2:
            u = smooth((t - (t_turun - 1.2) - rr * 1.3) / 1.7); x, y = lerp(x, tx, u), lerp(y, ty, u)
        unit(d, x, y, t, ph, (88, 84, 60), (236, 190, 70), s_, hop=(k >= 5 and t_turun - 1.2 < t < t_turun + 2))
    if t >= T4 + 1.0:
        for x, y, s_, rr, rot in SPOIL:
            p = back((t - (T4 + 1.0) - rr * 1.6) / 0.35) * gone
            if p > 0.03: d.box(x, y, 0.02, s_ * p, s_ * p, s_ * 0.8 * p, (224, 176, 66), rot=rot, top=(250, 214, 110))
    if t >= T5 - 0.5:
        u = cav_u(t)
        for lag, off, ph in CAV:
            uu = max(0.0, u - lag * 0.55); x, y = path(uu); x2, y2 = path(min(1, uu + 0.01)); dx, dy = x2 - x, y2 - y; ln = math.hypot(dx, dy) + 1e-6
            unit(d, x - dy / ln * off, y + dx / ln * off, t, ph, (44, 30, 36), (150, 30, 40), back((t - (T5 - 0.5)) / 0.4) * gone, hop=(0 < u < 0.93), big=1.35)
    return d

def cam(t):
    K = [(0.0, (21, 0, 5.5), (HX, HY, 2.0)), (T2 - 0.4, (22, 15, 7.5), (HX, HY, 2.0)), (T2 + 1.5, (-2, -32, 50), (-1, 14, 0)), (T3 - 0.2, (-2, -29, 46), (-1, 15, 0)),
         (T3 + 1.7, (21, -2, 8.5), (HX, HY, 1.6)), (t_jangan - 0.2, (20, 0.5, 6.5), (HX, HY, 1.8)), (T4 - 0.2, (19, 2, 5.6), (HX, HY, 2.0)),
         (T4 + 1.6, (-19, -2, 17), (2, 10, 0)), (t_harta + 0.6, (-10, -4, 14), (6, 7, 0)), (T5 - 0.2, (-4, -3, 11), (8, 7.5, 0.5)),
         (T5 + 1.3, (42, -16, 21), (27, 0, 0)), (t_keliling + 0.9, (42, 0, 21), (25, 13, 0)), (t_serang - 0.2, (33, 9, 21), (15, 21, 0)), (t_serang + 1.3, (23, 38, 19), (4, 20, 0)), (T6 - 0.2, (20, 38, 19), (3, 19, 0)),
         (T6 + 2.2, (23, -4, 9), (7, 11.5, 1)), (END, (27, -13, 21), (6, 11, 0))]
    return camera(K, t)
INK, GOLDT, REDT, GRN = (34, 30, 28), (176, 128, 36), (176, 58, 44), (30, 120, 80)
def cap(parts):
    for size in (62, 56, 50, 44):
        im = pill(tuple(parts), size, pad=(46, 26))
        if im.width <= 1060: return im
    return im
def cav_anchor(t):
    x, y = path(cav_u(t)); return (x, y, hgt(x, y) + 1.9)
LABELS = [("Gunung Uhud", None, (0, 42, 17), t_uhud2, T3 - 0.3, INK), ("Quraisy", "sekitar 3,000", (-3, 1, 1.4), t_tiga + 0.4, T3 - 0.3, REDT), ("Muslimin", "sekitar 700", (0, 21.5, 1.4), t_umat + 0.5, T3 - 0.3, GRN),
 ("Bukit pemanah", "50 pemanah", (HX, HY, 4.0), t_lima, t_jangan - 0.3, GOLDT),
          ("Harta rampasan", None, (2, 4.5, 0.4), t_harta, T5 - 0.4, GOLDT), ("Bukit pemanah", "tinggal sedikit", (HX, HY, 4.0), t_turun + 0.9, T5 - 0.4, REDT),
          ("Pasukan berkuda", "Quraisy", cav_anchor, T5 + 0.9, t_serang + 0.2, REDT), ("Jabal Rumah", "bukit pemanah", (HX, HY, 3.0), t_jabal - 0.2, 999, GOLDT),
          ("Makam Syuhada Uhud", None, (1.5, 14.5, 0.6), t_makam - 0.1, 999, INK)]
CAPS = [(T2 + 0.3, T3 - 0.2, [("Perang ", INK), ("Uhud", GOLDT)]), (T3 + 0.2, t_jangan - 0.3, [("50 pemanah ", INK), ("di atas bukit", GOLDT)]), (t_jangan - 0.1, T4 - 0.2, [("“Jangan tinggalkan ", INK), ("tempat ini”", GOLDT)]),
        (T4 + 0.2, t_harta - 0.2, [("Muslimin ", INK), ("mendahului", GRN)]), (t_harta - 0.1, T5 - 0.2, [("Pemanah ", INK), ("turun dari bukit", REDT)]), (T5 + 0.2, t_serang - 0.2, [("Berkuda ", INK), ("mengelilingi bukit", REDT)]),
        (t_serang - 0.1, t_tujuh - 0.2, [("Diserang ", INK), ("dari belakang", REDT)]), (t_tujuh - 0.1, T6 - 0.2, [("70 sahabat ", INK), ("gugur syahid", GOLDT)]), (T6 + 0.3, t_simpan - 0.2, [("Ziarah ", INK), ("Uhud", GOLDT)])]
MARK = mk_text("EL ZAHRA TRAVEL", "serif", 40, (246, 226, 170), 9); ILU = mk_text("Ilustrasi, bukan skala sebenar", "med", 24, (250, 246, 236))
LESSON = mk_text("Pengajaran: taat pada arahan", "bold", 44, (252, 248, 238)); HANDLE = mk_text("@elzahratravel", "med", 38, (255, 214, 120))
VIG = vignette(); WHITE = Image.new("RGB", (W, H), (255, 240, 214)); RED = Image.new("RGB", (W, H), (150, 30, 30)); CAPT = Captions(S, t_simpan - 0.1)
ST = None
def frame(gf):
    global ST
    if ST is None: ST = build().arrays()
    t = gf / FPS; A = merge(ST[0], ST[1], t, dynamic(t)); pos, tgt = cam(t)
    hit = sum(a * math.exp(-(t - te) * 8.0) for te, a in EVENTS["boom"] if t >= te); sk = 0.10 * hit
    pos = pos + np.array([sk * math.sin(t * 61), sk * math.cos(t * 53), sk * math.sin(t * 47)])
    arr, proj = render(A, pos, tgt, 42, env(t)); base = Image.fromarray(arr); base.paste(VIG, (0, 0), VIG); d = ImageDraw.Draw(base, "RGBA")
    for (a, b, anc, t0, t1, col) in LABELS: label(base, d, proj, a, b, anc(t) if callable(anc) else anc, t, t0, t1, col)
    if t < T2 - 0.1:
        a_ = clamp((T2 - 0.1 - t) / 0.25); n1 = min(50, int(50 * ease((t - 0.1) / 0.8)))
        paste(base, pill((("%d" % n1, GOLDT), (" pemanah", INK)), 58, pad=(44, 24)), W / 2, 330, a_, max(0.05, back((t - 0.05) / 0.4)))
        if t >= t_satu - 0.1: paste(base, pill((("1", REDT), (" arahan", INK)), 58, pad=(44, 24)), W / 2, 462, a_, max(0.05, back((t - t_satu + 0.1) / 0.4)))
    for (t0, t1, parts) in CAPS:
        if t0 <= t <= t1 + 0.25: paste(base, cap(parts), W / 2, 330, clamp((t1 + 0.25 - t) / 0.25), max(0.05, back((t - t0) / 0.4)))
    CAPT.draw(base, t)
    if t >= t_simpan - 0.08:
        kk = (t - t_simpan + 0.08) * FPS; paste(base, pill((("Simpan video ini", INK),), 56, pad=(60, 30), bg=(255, 214, 120)), W / 2, 1300, 1, (0.4 + 0.6 * back(kk / 11.0)) * (1 + 0.035 * math.sin(kk / 3.0)))
        ps = ease((t - t_ingat + 0.08) / 0.3); paste(base, LESSON, W / 2, 1404 + (1 - ps) * 22, ps); paste(base, HANDLE, W / 2, 1474, ease((t - t_taat - 0.3) / 0.3))
    paste(base, MARK, W / 2, 150); paste(base, ILU, W - 40 - ILU.width / 2, 262, 0.75)
    pw = 924 * gf / float(TOTAL); d.rounded_rectangle([78, 222, 1002, 228], 3, fill=(250, 246, 236, 70)); d.rounded_rectangle([78, 222, 78 + max(6, pw), 228], 3, fill=(255, 214, 120, 255))
    for ts_ in S.TS[1:]:
        if 0 <= t - ts_ < 0.27: base = Image.blend(base, WHITE, 0.45 * (1 - (t - ts_) / 0.27) ** 2)
    if 0 <= t - t_serang < 0.5: base = Image.blend(base, RED, 0.35 * (1 - (t - t_serang) / 0.5) ** 2)
    return fades(base, gf, TOTAL)
if __name__ == "__main__": main(frame, TOTAL, OUT, "uh")
