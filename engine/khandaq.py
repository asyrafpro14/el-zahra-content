import os, sys, math, json, random, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SS = 1080, 1920, 30, 1.5
RW, RH = int(W * SS), int(H * SS)
OUT = os.environ.get("OUT", "khandaq.mp4")
random.seed(3)
SCENES = [
    ["Sepuluh ribu tentera mara ke Madinah.", "Umat Islam hanya tiga ribu.", "Bagaimana mereka bertahan?"],
    ["Madinah dilindungi batu lava di timur dan barat,", "dan kebun kurma yang rapat di selatan.", "Hanya utara yang terbuka."],
    ["Seorang sahabat dari Parsi, Salman al-Farisi,", "memberi cadangan: gali parit.", "Rasulullah menerimanya,", "dan turun menggali bersama para sahabat."],
    ["Tentera Ahzab tiba, dan terhenti.", "Parit itu menghalang pasukan berkuda mereka.", "Hampir sebulan mereka mengepung."],
    ["Lalu Allah menghantar angin kencang dan kesejukan.", "Khemah mereka tumbang, dan mereka berundur."],
    ["Hari ini, jemaah menziarahi kawasan ini di Madinah,", "dikenali sebagai Masjid Tujuh.", "#Simpan video ini, dan kongsikan kepada yang bakal ke Madinah."],
]
SCRIPT, BLOCKS, SC_FIRST = [], [], []
for si, blocks in enumerate(SCENES):
    SC_FIRST.append(len(SCRIPT))
    for b in blocks:
        ws = b.lstrip("#").split(); BLOCKS.append([si, b[0] == "#", len(SCRIPT), len(SCRIPT) + len(ws) - 1]); SCRIPT.extend(ws)
NW = len(SCRIPT); NS = len(SCENES)
if os.environ.get("COUNT"): print(NW); sys.exit(0)
WT = json.load(open(os.environ.get("WORDS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "words", "words5.json")))); assert len(WT) == NW, (len(WT), NW)
def st(i): return WT[i][0]
def en(i): return WT[i][1]
def wi(word, start=0): return next(i for i in range(start, NW) if SCRIPT[i].rstrip(",.?:") == word)
DISP = list(SCRIPT); DISP[wi("Rasulullah")] = "Rasulullah SAW"
TS = [0.0] + [st(SC_FIRST[s]) - 0.2 for s in range(1, NS)]; END = en(NW - 1) + 2.0; TOTAL = int(END * FPS)
T1, T2, T3, T4, T5, T6 = TS
t_tiga = st(wi("tiga")); t_timur = st(wi("timur")); t_barat = st(wi("barat")); t_selatan = st(wi("selatan")); t_utara = st(wi("utara"))
t_gali = st(wi("gali")); t_turun = st(wi("turun")); t_tiba = st(wi("tiba")); t_henti = st(wi("terhenti")); t_hampir = st(wi("Hampir"))
t_angin = st(wi("angin")); t_khemah = st(wi("Khemah")); t_undur = st(wi("berundur")); t_masjid = st(wi("Masjid")); t_simpan = st(wi("Simpan")); t_kongsi = st(wi("kongsikan"))
TRENCH_T0, TRENCH_T1 = t_gali, t_turun + 0.2
EVENTS = {"total": END, "whoosh": [T2, T3, T4, T5, T6], "boom": [[0.05, 0.7], [t_gali, 0.8], [t_henti, 1.0], [t_khemah, 0.6]],
          "ticks": [t_timur, t_barat, t_selatan, t_utara], "riser_end": t_angin, "shimmer": T6 + 0.3, "pop": [t_simpan, t_kongsi], "wind": [t_angin - 0.3, T6 + 0.6]}
if os.environ.get("EVENTS"): json.dump(EVENTS, open(os.environ["EVENTS"], "w")); print("events", END, [round(x, 2) for x in TS]); sys.exit(0)

def clamp(x): return max(0.0, min(1.0, x))
def ease(t): t = clamp(t); return 1 - (1 - t) ** 3
def smooth(t): t = clamp(t); return t * t * (3 - 2 * t)
def back(t):
    t = clamp(t); c1 = 1.7; return 1 + (c1 + 1) * (t - 1) ** 3 + c1 * (t - 1) ** 2

class Scene:
    def __init__(s): s.P, s.C, s.L, s.D, s.E, s.T = [], [], [], [], [], []
    def quad(s, a, b, c, d, col, layer=2, ds=False, emit=False, t=-1e9):
        s.P.append([a, b, c, d]); s.C.append(col); s.L.append(layer); s.D.append(ds); s.E.append(emit); s.T.append(t)
    def tri(s, a, b, c, col, **k): s.quad(a, b, c, c, col, **k)
    def box(s, cx, cy, z0, sx, sy, h, col, rot=0.0, top=None, **k):
        ca, sa = math.cos(rot), math.sin(rot)
        def p(dx, dy, z): return (cx + dx * ca - dy * sa, cy + dx * sa + dy * ca, z)
        hx, hy = sx / 2, sy / 2; z1 = z0 + h
        b = [p(-hx, -hy, z0), p(hx, -hy, z0), p(hx, hy, z0), p(-hx, hy, z0)]; t_ = [p(-hx, -hy, z1), p(hx, -hy, z1), p(hx, hy, z1), p(-hx, hy, z1)]
        s.quad(t_[0], t_[1], t_[2], t_[3], top or col, **k)
        for i in range(4):
            j = (i + 1) % 4; s.quad(b[i], b[j], t_[j], t_[i], col, **k)
    def pyramid(s, cx, cy, z0, r, h, col, rot=0.0, n=4, lean=(0, 0), **k):
        pts = [(cx + r * math.cos(rot + 2 * math.pi * i / n), cy + r * math.sin(rot + 2 * math.pi * i / n), z0) for i in range(n)]
        for i in range(n): s.tri(pts[i], pts[(i + 1) % n], (cx + lean[0], cy + lean[1], z0 + h), col, **k)
    def arrays(s):
        P = np.array(s.P, dtype=np.float64).reshape(-1, 4, 3); C = np.array(s.C, dtype=np.float64).reshape(-1, 3)
        return P, C, np.array(s.L, dtype=np.int64), np.array(s.D, dtype=bool), np.array(s.E, dtype=bool), np.array(s.T, dtype=np.float64)

PAL = {"dusk": ((1.0, 0.84, 0.62), (0.40, 0.39, 0.52), (214, 160, 128), (40, 46, 96), (244, 170, 112)),
       "day": ((1.0, 0.96, 0.86), (0.50, 0.50, 0.56), (226, 200, 166), (96, 140, 200), (238, 216, 184)),
       "night": ((0.34, 0.40, 0.62), (0.19, 0.21, 0.36), (36, 44, 82), (8, 12, 38), (40, 52, 96)),
       "storm": ((0.50, 0.50, 0.58), (0.30, 0.32, 0.42), (96, 100, 118), (38, 42, 60), (124, 124, 136)),
       "dawn": ((1.0, 0.80, 0.70), (0.46, 0.42, 0.52), (240, 186, 156), (70, 92, 156), (255, 200, 156))}
PAL = {k: [np.array(x, float) for x in v] for k, v in PAL.items()}
def mixp(a, b, u): return [x * (1 - u) + y * u for x, y in zip(PAL[a] if isinstance(a, str) else a, PAL[b] if isinstance(b, str) else b)]
def env(t):
    if t < T2: return PAL["dusk"]
    if t < T3: return mixp("dusk", "day", smooth((t - T2) / 1.0))
    if t < T4: return mixp("day", "dusk", smooth((t - (T4 - 2.5)) / 2.0))
    if t < T5:
        if t < t_hampir: return PAL["dusk"]
        u = (t - t_hampir) / max(0.1, (T5 - t_hampir)); c = 0.5 - 0.5 * math.cos(2 * math.pi * 3 * u)
        return mixp(mixp("dusk", "day", 0.5), "night", c)
    if t < T6: return mixp("dusk", "storm", smooth((t - T5) / 0.8))
    return mixp("storm", "dawn", smooth((t - T6) / 1.2))
LIGHT = np.array([-0.62, -0.28, 0.55]); LIGHT /= np.linalg.norm(LIGHT); FOGD = 0.0085
KY = (np.minimum(1.0, np.arange(RH) / (RH * 0.56)) ** 1.6)[:, None, None]

def render(P, C, L, D, E, N, cen, pos, tgt, fov, ev):
    LCOL, AMB, FOG, STOP, SHOR = ev
    pos = np.array(pos, float); f = np.array(tgt, float) - pos; f /= np.linalg.norm(f)
    r = np.cross(f, [0, 0, 1.0]); r /= np.linalg.norm(r); u = np.cross(r, f)
    V = P - pos; x = V @ r; y = V @ u; z = V @ f; foc = (RH / 2) / math.tan(math.radians(fov) / 2)
    ok = (z.min(axis=1) > 0.25); front = np.einsum("ij,ij->i", N, pos[None] - cen) > 0; ok &= (front | D)
    zz = np.maximum(z, 0.25); sx = RW / 2 + x / zz * foc; sy = RH / 2 - y / zz * foc
    ok &= (sx.max(axis=1) > -50) & (sx.min(axis=1) < RW + 50) & (sy.max(axis=1) > -50) & (sy.min(axis=1) < RH + 50)
    idx = np.nonzero(ok)[0]; depth = z[idx].mean(axis=1); dist = np.linalg.norm(cen[idx] - pos, axis=1)
    nl = N[idx] @ LIGHT; nl = np.where(D[idx], np.abs(nl), np.maximum(nl, 0)); up = np.maximum(N[idx][:, 2], 0)
    sh = np.clip(C[idx] * (AMB[None] * (0.82 + 0.18 * up[:, None]) + LCOL[None] * nl[:, None] * 0.98), 0, 255)
    fg = np.clip(1 - np.exp(-(dist * FOGD) ** 1.5), 0, 0.93)[:, None]
    col = np.where(E[idx][:, None], C[idx], sh * (1 - fg) + FOG[None] * fg).astype(np.uint8)
    order = np.lexsort((-depth, L[idx]))
    img = np.broadcast_to((STOP[None, None] * (1 - KY) + SHOR[None, None] * KY).astype(np.uint8), (RH, RW, 3)).copy()
    pts = (np.stack([sx[idx], sy[idx]], axis=2) * 16).astype(np.int32)
    for i in order:
        c = col[i]; cv2.fillConvexPoly(img, pts[i], (int(c[0]), int(c[1]), int(c[2])), lineType=cv2.LINE_8, shift=4)
    def proj(p):
        v = np.array(p, float) - pos; z_ = v @ f
        if z_ < 0.3: return None
        return (W / 2 + (v @ r) / z_ * foc / SS, H / 2 - (v @ u) / z_ * foc / SS, z_)
    return cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA), proj

def hgt(x, y):
    h = 0.35 * math.sin(x * 0.21 + 1.3) * math.cos(y * 0.17) + 0.22 * math.sin(x * 0.53 + y * 0.41); d = math.hypot(x, y)
    h *= min(1.0, max(0.0, (d - 9) / 8.0)) * (0.25 if 9 < y < 34 and abs(x) < 20 else 1.0)
    ridge = math.exp(-((y - 54) / 7.0) ** 2) * (9 + 4 * math.sin(x * 0.23) + 3 * math.sin(x * 0.61 + 2))
    far = max(0.0, (d - 56) / 10.0) ** 1.6 * 7
    return h + ridge + far
def tpt(u):
    x = -12.5 + 25 * u; return x, 11.2 + 2.4 * math.sin(math.pi * u) + 0.5 * math.sin(u * 9)
def build():
    sc = Scene(); n, ext = 60, 78.0
    for i in range(n):
        for j in range(n):
            x0, x1 = -ext + 2 * ext * i / n, -ext + 2 * ext * (i + 1) / n; y0, y1 = -ext + 2 * ext * j / n, -ext + 2 * ext * (j + 1) / n
            a, b, c, d = (x0, y0, hgt(x0, y0)), (x1, y0, hgt(x1, y0)), (x1, y1, hgt(x1, y1)), (x0, y1, hgt(x0, y1))
            for tri in ((a, b, c), (a, c, d)):
                mx, my, mz = [sum(v[k] for v in tri) / 3 for k in range(3)]
                lava = max(0.0, min(1.0, (abs(mx) - 10.5) / 3.0)) * max(0.0, min(1.0, (16 - abs(my - 2)) / 5.0))
                grove = max(0.0, min(1.0, (-my - 8.5) / 3.0)) * max(0.0, min(1.0, (15 - abs(mx)) / 4.0))
                base = np.array([222, 184, 134.0]); base = base * (1 - lava) + np.array([66, 58, 62.0]) * lava; base = base * (1 - 0.5 * grove) + np.array([112, 136, 84.0]) * 0.5 * grove
                if mz > 3: base = base * 0.5 + np.array([150, 96, 78.0]) * 0.5
                sc.tri(*tri, tuple(base * random.uniform(0.94, 1.06)), layer=0, ds=True)
    def shadow(cx, cy, sx, sy, h, rot=0.0, t=-1e9):
        ca, sa = math.cos(rot), math.sin(rot); Ln = h * 1.15; dx, dy = 0.62 * Ln, 0.28 * Ln
        cs = [(cx + px * ca - py * sa, cy + px * sa + py * ca) for px, py in ((-sx / 2, -sy / 2), (sx / 2, -sy / 2), (sx / 2, sy / 2), (-sx / 2, sy / 2))]
        hull = cv2.convexHull(np.array(cs + [(x + dx, y + dy) for x, y in cs], dtype=np.float32)).reshape(-1, 2)
        for k in range(1, len(hull) - 1):
            sc.tri(*[(float(q[0]), float(q[1]), hgt(q[0], q[1]) + 0.03) for q in (hull[0], hull[k], hull[k + 1])], (124, 96, 96), layer=1, ds=True, t=t)
    placed = []
    for _ in range(900):
        ang = random.uniform(0, 2 * math.pi); rad = 8.6 * math.sqrt(random.random()); x, y = rad * math.cos(ang), rad * math.sin(ang) * 0.9
        sx, sy = random.uniform(0.7, 1.7), random.uniform(0.7, 1.7)
        if math.hypot(x, y) < 1.6 or any(abs(x - px) < (sx + ps) / 2 + 0.22 and abs(y - py) < (sy + pq) / 2 + 0.22 for px, py, ps, pq in placed): continue
        placed.append((x, y, sx, sy)); h = random.uniform(0.55, 1.5); tone = random.uniform(0.88, 1.08)
        col = (204 * tone, 166 * tone, 122 * tone); top = (236 * tone, 206 * tone, 160 * tone); sc.box(x, y, 0, sx, sy, h, col, top=top); shadow(x, y, sx, sy, h)
        if random.random() < 0.25: sc.box(x + sx * 0.2, y - sy * 0.15, h, sx * 0.4, sy * 0.4, 0.35, col, top=top)
        if len(placed) > 230: break
    sc.box(0, 0, 0, 2.6, 2.0, 1.1, (236, 214, 170), top=(250, 234, 196)); shadow(0, 0, 2.6, 2.0, 1.1)
    for _ in range(170):
        x, y = random.uniform(-14, 14), random.uniform(-21, -9.5); z = hgt(x, y); hh = random.uniform(1.3, 2.3)
        sc.box(x, y, z, 0.14, 0.14, hh, (104, 76, 54)); shadow(x, y, 0.5, 0.5, hh * 0.8)
        for k in range(7):
            a = 2 * math.pi * k / 7 + random.uniform(-0.2, 0.2); Ln = random.uniform(0.7, 1.0); w_ = 0.2
            sc.tri((x + w_ * math.cos(a + 1.57), y + w_ * math.sin(a + 1.57), z + hh), (x - w_ * math.cos(a + 1.57), y - w_ * math.sin(a + 1.57), z + hh), (x + Ln * math.cos(a), y + Ln * math.sin(a), z + hh - 0.28),
                   (52 * random.uniform(0.85, 1.1), 134 * random.uniform(0.9, 1.1), 78), ds=True)
    for side in (-1, 1):
        for _ in range(230):
            x = side * random.uniform(11.5, 26); y = random.uniform(-12, 17); z = hgt(x, y); s_ = random.uniform(0.4, 1.3); tone = random.uniform(0.8, 1.15)
            sc.box(x, y, z - 0.05, s_, s_ * random.uniform(0.7, 1.3), s_ * random.uniform(0.4, 0.9), (46 * tone, 40 * tone, 46 * tone), rot=random.uniform(0, 3.1), top=(64 * tone, 56 * tone, 60 * tone))
    NSEG = 60
    for k in range(NSEG):
        u0, u1 = k / NSEG, (k + 1) / NSEG; (x0, y0), (x1, y1) = tpt(u0), tpt(u1); tt = TRENCH_T0 + (TRENCH_T1 - TRENCH_T0) * (1 - u0)
        dx, dy = x1 - x0, y1 - y0; ln = math.hypot(dx, dy); nx, ny = -dy / ln, dx / ln; w_ = 0.5; z = 0.05
        sc.quad((x0 - nx * w_, y0 - ny * w_, z), (x1 - nx * w_, y1 - ny * w_, z), (x1 + nx * w_, y1 + ny * w_, z), (x0 + nx * w_, y0 + ny * w_, z), (52, 36, 32), layer=1, ds=True, t=tt)
        sc.pyramid((x0 + x1) / 2 - nx * 0.95, (y0 + y1) / 2 - ny * 0.95, 0, 0.5, random.uniform(0.25, 0.42), (178, 138, 96), rot=random.uniform(0, 1.5), n=5, t=tt + 0.05)
    for k in range(7):
        x, y = -10.6 + (k % 4) * 0.95 + random.uniform(-0.1, 0.1), 9.3 + (k // 4) * 1.0; sc.box(x, y, 0, 0.6, 0.6, 0.5, (240, 236, 226), top=(250, 248, 240), t=T6)
        sc.pyramid(x, y, 0.5, 0.36, 0.3, (250, 248, 240), rot=0.785, n=6, t=T6); shadow(x, y, 0.6, 0.6, 0.6, t=T6)
    return sc

UNITS = [(-14 + 2.0 * c + random.uniform(-0.3, 0.3), r_ * 1.35 + random.uniform(-0.2, 0.2), random.uniform(0, 6.3)) for r_ in range(10) for c in range(15)]
MUS = [(tpt(u)[0], tpt(u)[1] - 1.9 - 0.9 * (k % 2), random.uniform(0, 6.3)) for k, u in enumerate([0.03 + 0.94 * i / 44 for i in range(45)])]
TENTS = [(random.uniform(-16, 16), random.uniform(31, 41), random.uniform(0.7, 1.1), random.uniform(0.85, 1.25), random.uniform(0, 1.5), random.random(), random.random() < 0.35) for _ in range(60)]
def front_y(t):
    if t < T2: return 29 - 8 * smooth(t / T2)
    if t < T4: return None
    if t < T5 or t < t_undur - 0.8: return 34 - 17.5 * ease((t - T4) / max(0.6, (t_henti + 0.3 - T4)))
    if t < T6: return 16.5 + 30 * smooth((t - (t_undur - 0.8)) / 3.2)
    return None
def dynamic(t):
    d = Scene(); fy = front_y(t); fires = []
    if fy is not None:
        moving = t < T2 or (T4 <= t < t_henti + 0.3) or t >= t_undur - 0.8
        for ux, uy, ph in UNITS:
            x, y = ux, fy + uy; z = hgt(x, y) + (0.07 * abs(math.sin(t * 9 + ph)) if moving else 0)
            if y > 50: continue
            d.box(x, y, z, 0.42, 0.42, 0.3, (64, 44, 48)); d.box(x, y, z + 0.3, 0.06, 0.06, 1.05, (40, 30, 30))
            fl = 0.12 * math.sin(t * 7 + ph); d.tri((x, y, z + 1.35), (x, y, z + 0.95), (x + 0.55, y + fl, z + 1.15), (176, 52, 46), ds=True)
    if t_turun - 0.2 <= t < T6:
        for k, (x, y, ph) in enumerate(MUS):
            s_ = back((t - (t_turun - 0.2) - 0.03 * k) / 0.35)
            if s_ <= 0.02: continue
            d.box(x, y, 0, 0.42 * s_, 0.42 * s_, 0.3 * s_, (70, 96, 84)); d.box(x, y, 0.3 * s_, 0.06, 0.06, 1.05 * s_, (40, 44, 40))
            fl = 0.12 * math.sin(t * 7 + ph); d.tri((x, y, 1.35 * s_), (x, y, 0.95 * s_), (x + 0.55 * s_, y + fl, 1.15 * s_), (40, 150, 96), ds=True)
    if t_hampir - 0.3 <= t < T6 + 0.2:
        for x, y, r_, h_, rot, od, fire in TENTS:
            up = back((t - (t_hampir - 0.3) - od * 1.2) / 0.4); dn = smooth((t - t_khemah - od * 1.0) / 0.5) if t >= t_khemah else 0
            s_ = up * (1 - 0.86 * dn)
            if up <= 0.02: continue
            z = hgt(x, y); tone = 0.9 + 0.15 * od
            d.pyramid(x, y, z, r_ * (1 + 0.3 * dn), h_ * s_, (158 * tone, 128 * tone, 108 * tone), rot=rot, lean=(1.1 * dn, 0.3 * dn))
            if fire and t < t_angin + od * 0.8 and up > 0.9:
                d.pyramid(x + 1.0, y - 0.6, z, 0.16, 0.42 + 0.08 * math.sin(t * 11 + x), (255, 170, 70), emit=True); fires.append((x + 1.0, y - 0.6, z + 0.2))
    return d, fires

def cam(t):
    K = [(0.0, (0, 49, 9.5), (0, 16, 0)), (T2 - 0.5, (0, 47, 15), (0, 10, 0)), (T2 + 1.4, (0, -38, 74), (0, 3, 0)), (T3 - 0.2, (0, -36, 70), (0, 4, 0)),
         (T3 + 1.6, (13, -17, 24), (0, 9, 0)), (t_gali - 0.5, (11, -15, 25), (0, 10, 0)), (t_gali + 0.9, (0, -3, 31), (0, 12, 0)), (t_turun - 0.3, (0, -2, 29), (0, 12, 0)), (t_turun + 1.6, (-7, 7.5, 5.5), (5, 13.5, 0.2)), (T4 - 0.3, (-6, 7.2, 5.2), (5, 13.5, 0.2)),
         (T4 + 1.8, (-18, 23, 10), (0, 15, 0.5)), (t_hampir - 0.3, (-16, 21, 8.5), (0, 16, 0.5)), (t_hampir + 1.2, (-24, 33, 17), (0, 23, 0)), (T5 - 0.2, (-22, 32, 16), (0, 23, 0)),
         (T5 + 1.6, (9, 47, 11), (-2, 33, 1)), (T6 - 0.2, (7, 46, 10.5), (-2, 32, 1)), (T6 + 2.4, (-16, 3.5, 8.5), (-9.2, 10, 0.6)), (END, (0, -30, 42), (0, 4, 0))]
    ts = [k[0] for k in K]; t = max(0.0, min(END - 1e-6, t)); i = max(j for j in range(len(ts) - 1) if ts[j] <= t); u = smooth((t - ts[i]) / (ts[i + 1] - ts[i]))
    def lp(sel): return np.array(K[i][sel], float) * (1 - u) + np.array(K[i + 1][sel], float) * u
    p = lp(1)
    if K[i][1][1] * K[i + 1][1][1] < -200: p[2] += 26 * math.sin(math.pi * u)
    return p, lp(2)

def fpath(p):
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", {"Poppins:bold": "Poppins-Bold.ttf", "Poppins:medium": "Poppins-Medium.ttf", "Lora:bold": "Lora-Variable.ttf"}.get(p, ""))
    return f if os.path.isfile(f) else subprocess.check_output(["fc-match", "-f", "%{file}", p]).decode()
_f = {}
def font(kind, size):
    if (kind, size) not in _f:
        f = ImageFont.truetype(fpath({"bold": "Poppins:bold", "med": "Poppins:medium", "serif": "Lora:bold"}[kind]), size)
        if kind == "serif":
            try: f.set_variation_by_name("Bold")
            except Exception: pass
        _f[(kind, size)] = f
    return _f[(kind, size)]
_pc = {}
def pill(parts, size, pad=(34, 20), bg=(250, 247, 240), sub=None):
    key = (tuple(parts), size, pad, bg, sub)
    if key in _pc: return _pc[key]
    f = font("bold", size); asc, desc = f.getmetrics(); tw = sum(f.getlength(p[0]) for p in parts)
    fs = font("med", int(size * 0.62)) if sub else None; sw = fs.getlength(sub) if sub else 0; sh = int(size * 0.9) if sub else 0
    w = int(max(tw, sw) + pad[0] * 2); h = asc + desc + pad[1] * 2 + sh
    im = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0)); ImageDraw.Draw(im).rounded_rectangle([0, 0, w * 2 - 1, h * 2 - 1], min(h // 2, 30) * 2, fill=bg + (255,))
    im = im.resize((w, h), Image.LANCZOS); d = ImageDraw.Draw(im); x = (w - tw) / 2
    for txt, col in parts: d.text((x, pad[1]), txt, font=f, fill=col); x += f.getlength(txt)
    if sub: d.text(((w - sw) / 2, pad[1] + asc + desc - 2), sub, font=fs, fill=(110, 100, 90))
    big = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0)); shd = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    shd.paste(Image.new("RGBA", (w, h), (0, 0, 0, 120)), (30, 38), im.getchannel("A")); big.alpha_composite(shd.filter(ImageFilter.GaussianBlur(12))); big.alpha_composite(im, (30, 30))
    _pc[key] = big; return big
def paste(base, im, cx, cy, a=1.0, s=1.0):
    if a <= 0.01 or s <= 0.03: return
    if abs(s - 1) > 0.01: im = im.resize((max(2, int(im.width * s)), max(2, int(im.height * s))), Image.BILINEAR)
    x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    l, t, r, b = max(0, -x), max(0, -y), min(im.width, W - x), min(im.height, H - y)
    if r <= l or b <= t: return
    if (l, t, r, b) != (0, 0, im.width, im.height): im = im.crop((l, t, r, b)); x += l; y += t
    m = im.getchannel("A")
    if a < 0.995: m = m.point(lambda p: int(p * a))
    base.paste(im, (x, y), m)
def shadowed(im, blur, off, alpha=215):
    out = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(im.getchannel("A").filter(ImageFilter.GaussianBlur(blur)).point(lambda p: min(255, p * alpha // 150))); out.alpha_composite(sh, (0, off)); out.alpha_composite(im); return out
class TB:
    def __init__(s, words, idxs, size, max_w=960, gap=1.2):
        f = font("bold", size); sp = f.getlength(" "); ws = [f.getlength(w) for w in words]; lines, cur, cw = [], [], 0
        for j, w in enumerate(ws):
            if cur and cw + sp + w > max_w: lines.append(cur); cur, cw = [j], w
            else: cw = cw + (sp if cur else 0) + w; cur.append(j)
        lines.append(cur)
        def lw(a): return sum(ws[j] for j in a) + sp * (len(a) - 1)
        if len(lines) == 2 and len(words) > 2:
            best = None
            for k in range(1, len(words)):
                a, b = list(range(k)), list(range(k, len(words))); m = max(lw(a), lw(b))
                if m <= max_w and (best is None or m < best[0]): best = (m, [a, b])
            if best: lines = best[1]
        asc, desc = f.getmetrics(); lh = int((asc + desc) * gap); s.items = []; s.h = lh * len(lines); pad = 40
        for li, line in enumerate(lines):
            x = -lw(line) / 2
            for j in line:
                ims = []
                for c in ((252, 248, 238), (255, 208, 96)):
                    im = Image.new("RGBA", (int(ws[j]) + pad * 2, asc + desc + pad * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
                    d.text((pad, pad), words[j], font=f, fill=c, stroke_width=5, stroke_fill=(24, 18, 16)); ims.append(shadowed(im, 7, 4))
                s.items.append((x - pad, li * lh - pad, idxs[j], ims[0], ims[1])); x += ws[j] + sp
    def draw(s, base, cx, y, t, a=1.0):
        for x, yy, i, im, imh in s.items:
            p = ease((t - (st(i) - 0.07)) / 0.2)
            if p <= 0: continue
            nxt = st(i + 1) if i + 1 < NW and st(i + 1) - en(i) < 0.35 else en(i) + 0.12
            paste(base, imh if t < nxt - 0.05 else im, cx + x + im.width / 2, y + yy + im.height / 2 + (1 - p) * 22, p * a)
INK, GOLDT, REDT, GRN = (34, 30, 28), (176, 128, 36), (176, 58, 44), (30, 120, 80)
TBS = [None if cta else TB([DISP[i] for i in range(a, b + 1)], list(range(a, b + 1)), 60) for si, cta, a, b in BLOCKS]
def bl_end(k):
    si = BLOCKS[k][0]
    for j in range(k + 1, len(BLOCKS)):
        if BLOCKS[j][0] != si: break
        if not BLOCKS[j][1]: return st(BLOCKS[j][2]) - 0.08
    return TS[si + 1] if si < NS - 1 else t_simpan - 0.1
LABELS = [("Madinah", None, (0, 0, 1.6), T2 + 1.2, t_gali - 0.6, INK), ("Timur", "batu lava", (13.5, 2, 0.6), t_timur, T3 + 1.2, INK), ("Barat", "batu lava", (-13.5, 2, 0.6), t_barat, T3 + 1.2, INK),
          ("Selatan", "kebun kurma", (0, -11, 1.8), t_selatan, T3 + 1.0, INK), ("Utara", "terbuka", (0, 13, 0.3), t_utara, t_gali - 0.6, REDT),
          ("Khandaq", "parit", (3, 13.5, 0.4), t_gali + 1.5, T5 - 0.4, GOLDT), ("Muslimin", "sekitar 3,000", (-1, 10.6, 1.4), t_turun + 1.9, T5 - 0.4, GRN),
          ("Tentera Ahzab", "sekitar 10,000", (-2, 20, 1.4), t_henti + 0.3, T5 - 0.4, REDT), ("Masjid Tujuh", "Sab'ah Masajid", (-9.2, 9.8, 1.2), t_masjid - 0.3, 999, GOLDT),
          ("Madinah", None, (0, 0, 1.6), t_masjid + 0.6, 999, INK)]
CAPS = [(T2 + 0.3, T3 - 0.2, [("Di mana ", INK), ("titik lemah?", GOLDT)]), (T3 + 0.2, t_gali - 0.2, [("Idea ", INK), ("Salman al-Farisi", GOLDT)]), (t_gali - 0.1, T4 - 0.2, [("Gali ", INK), ("parit!", GOLDT)]),
        (t_henti - 0.1, t_hampir - 0.2, [("Tentera Ahzab ", INK), ("terhenti", REDT)]), (t_hampir - 0.1, T5 - 0.2, [("Hampir ", INK), ("sebulan", GOLDT)]),
        (t_angin - 0.2, T6 - 0.2, [("Angin ", INK), ("kencang", GOLDT)]), (T6 + 0.3, t_simpan - 0.2, [("Ziarah ", INK), ("Masjid Tujuh", GOLDT)])]
def mk_text(txt, kind, size, col, tr=0):
    f = font(kind, size); w = int(f.getlength(txt) + tr * len(txt)) + 30; im = Image.new("RGBA", (w, size + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 12
    for ch in txt: d.text((x + 2, 14), ch, font=f, fill=(0, 0, 0, 150)); d.text((x, 12), ch, font=f, fill=col); x += f.getlength(ch) + tr
    return im
MARK = mk_text("EL ZAHRA TRAVEL", "serif", 40, (246, 226, 170), 9); ILU = mk_text("Ilustrasi, bukan skala sebenar", "med", 24, (250, 246, 236))
SHARE = mk_text("Kongsi kepada yang bakal ke Madinah", "bold", 40, (252, 248, 238)); HANDLE = mk_text("@elzahratravel", "med", 38, (255, 214, 120))
gm = Image.new("L", (240, 240), 0); ImageDraw.Draw(gm).ellipse([70, 70, 170, 170], fill=255)
GLOW = Image.merge("RGBA", (*Image.new("RGB", (240, 240), (255, 190, 100)).split(), gm.filter(ImageFilter.GaussianBlur(34))))
vig = Image.new("L", (W, H), 0); vd = ImageDraw.Draw(vig); vd.rectangle([0, 0, W, 180], fill=120); vd.rectangle([0, H - 620, W, H], fill=185)
VIG = Image.merge("RGBA", (*Image.new("RGB", (W, H), (20, 14, 26)).split(), vig.filter(ImageFilter.GaussianBlur(150))))
WHITE = Image.new("RGB", (W, H), (255, 240, 214)); BLACK = Image.new("RGB", (W, H), (0, 0, 0))
STREAK = [(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0.6, 1.4), random.uniform(60, 220)) for _ in range(70)]

ST = None
def frame(gf):
    global ST
    if ST is None:
        sc = build(); P, C, L, D, E, T = sc.arrays(); n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]); N = n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9); ST = (P, C, L, D, E, T, N, P.mean(axis=1))
    P, C, L, D, E, T, N, cen = ST; t = gf / FPS; m = T <= t
    dyn, fires = dynamic(t)
    if dyn.P:
        dP, dC, dL, dD, dE, _ = dyn.arrays(); dn = np.cross(dP[:, 1] - dP[:, 0], dP[:, 2] - dP[:, 0]); dN = dn / np.maximum(np.linalg.norm(dn, axis=1, keepdims=True), 1e-9)
        A = [np.concatenate(z) for z in ((P[m], dP), (C[m], dC), (L[m], dL), (D[m], dD), (E[m], dE), (N[m], dN), (cen[m], dP.mean(axis=1)))]
    else: A = [P[m], C[m], L[m], D[m], E[m], N[m], cen[m]]
    pos, tgt = cam(t); storm = smooth((t - t_angin) / 0.6) * (1 - smooth((t - T6) / 0.6)) if t >= t_angin - 0.1 else 0
    hit = sum(a * math.exp(-(t - te) * 8.0) for te, a in EVENTS["boom"] if t >= te)
    sk = 0.10 * hit + 0.05 * storm; pos = pos + np.array([sk * math.sin(t * 61), sk * math.cos(t * 53), sk * math.sin(t * 47)])
    arr, proj = render(*A, pos, tgt, 42, env(t)); base = Image.fromarray(arr)
    for fx, fy, fz in fires:
        p = proj((fx, fy, fz))
        if p: paste(base, GLOW, p[0], p[1], 0.75 + 0.2 * math.sin(t * 9 + fx), clamp(22.0 / p[2]) * (1 + 0.08 * math.sin(t * 13 + fy)))
    base.paste(VIG, (0, 0), VIG); d = ImageDraw.Draw(base, "RGBA")
    if storm > 0.02:
        for sx_, sy_, spd, ln in STREAK:
            x = ((sx_ + t * spd * 1.5) % 1.2 - 0.1) * W; y = (sy_ * 0.9 + 0.04 * math.sin(t * 3 + sx_ * 9)) * H * 0.78 + 120
            d.line([x, y, x + ln, y + ln * 0.12], fill=(240, 240, 250, int(110 * storm)), width=3)
    for (a, b, anc, t0, t1, col) in LABELS:
        if t < t0 or t > t1 + 0.3: continue
        p = proj(anc)
        if not p: continue
        im = pill(((a, col),), 34, sub=b); al = clamp((t1 + 0.3 - t) / 0.3); pp = back((t - t0) / 0.35)
        lx = min(W - im.width / 2 + 10, max(im.width / 2 - 10, p[0])); ly = min(1180, max(470, p[1] - 150))
        d.line([p[0], p[1], lx, ly + im.height / 2 - 34], fill=(250, 247, 240, int(230 * al * clamp(pp))), width=3)
        d.ellipse([p[0] - 9, p[1] - 9, p[0] + 9, p[1] + 9], fill=(250, 247, 240, int(255 * al)), outline=(40, 34, 30, int(255 * al)), width=3)
        paste(base, im, lx, ly, al, max(0.05, pp))
    if t < T2 - 0.1:
        a_ = clamp((T2 - 0.1 - t) / 0.25); n1 = int(10000 * ease((t - st(0)) / 0.9)); n1 = n1 // 100 * 100 if n1 < 10000 else 10000
        if t >= st(0) - 0.05: paste(base, pill((("{:,}".format(n1), REDT), (" tentera Ahzab", INK)), 58, pad=(44, 24)), W / 2, 330, a_, max(0.05, back((t - st(0) + 0.05) / 0.4)))
        if t >= t_tiga - 0.5:
            n2 = int(3000 * ease((t - t_tiga + 0.5) / 0.8)); n2 = n2 // 100 * 100 if n2 < 3000 else 3000
            paste(base, pill((("{:,}".format(n2), GRN), (" Muslimin", INK)), 58, pad=(44, 24)), W / 2, 462, a_, max(0.05, back((t - t_tiga + 0.5) / 0.4)))
    for (t0, t1, parts) in CAPS:
        if t0 <= t <= t1 + 0.25: paste(base, pill(tuple(parts), 62, pad=(46, 26)), W / 2, 330, clamp((t1 + 0.25 - t) / 0.25), max(0.05, back((t - t0) / 0.4)))
    for k, (si, cta, a, b) in enumerate(BLOCKS):
        if cta or t < st(a) - 0.12: continue
        te = bl_end(k)
        if t >= te: continue
        TBS[k].draw(base, W / 2, 1360, t, clamp((te - t) / 0.12))
    if t >= t_simpan - 0.08:
        kk = (t - t_simpan + 0.08) * FPS; paste(base, pill((("Simpan video ini", INK),), 56, pad=(60, 30), bg=(255, 214, 120)), W / 2, 1300, 1, (0.4 + 0.6 * back(kk / 11.0)) * (1 + 0.035 * math.sin(kk / 3.0)))
        ps = ease((t - t_kongsi + 0.08) / 0.3); paste(base, SHARE, W / 2, 1400 + (1 - ps) * 22, ps); paste(base, HANDLE, W / 2, 1462, ease((t - t_kongsi - 0.6) / 0.3))
    paste(base, MARK, W / 2, 150); paste(base, ILU, W - 40 - ILU.width / 2, 262, 0.75)
    pw = 924 * gf / float(TOTAL); d.rounded_rectangle([78, 222, 1002, 228], 3, fill=(250, 246, 236, 70)); d.rounded_rectangle([78, 222, 78 + max(6, pw), 228], 3, fill=(255, 214, 120, 255))
    for ts_ in TS[1:]:
        if 0 <= t - ts_ < 0.27: base = Image.blend(base, WHITE, 0.45 * (1 - (t - ts_) / 0.27) ** 2)
    if hit > 0.05 and t > 0.4: base = Image.blend(base, WHITE, min(0.3, 0.22 * hit * math.exp(-0)))  if False else base
    if gf < 10: base = Image.blend(BLACK, base, gf / 10.0)
    if gf > TOTAL - 14: base = Image.blend(BLACK, base, clamp((TOTAL - gf) / 14.0))
    return base

if __name__ == "__main__":
    if os.environ.get("PREVIEW"):
        for tt in [float(x) for x in os.environ["PREVIEW"].split(",")]:
            frame(int(tt * FPS)).resize((540, 960), Image.LANCZOS).save("/tmp/kh_%05.2f.jpg" % tt, quality=90)
        sys.exit(0)
    lo, hi = int(os.environ.get("F0", "0")), int(os.environ.get("F1", str(TOTAL))); tmp = OUT.replace(".mp4", ".part.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "21", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
    for gf in range(lo, hi): p.stdin.write(frame(gf).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, OUT); print("OK", OUT, lo, hi)
