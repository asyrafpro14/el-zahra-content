import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lpe import *
INK, GOLDT, REDT, GRN = (34, 30, 28), (176, 128, 36), (176, 58, 44), (30, 120, 80)
PAL = {"dusk": ((1.0, 0.84, 0.62), (0.40, 0.39, 0.52), (214, 160, 128), (40, 46, 96), (244, 170, 112)),
       "day": ((1.0, 0.96, 0.86), (0.50, 0.50, 0.56), (226, 200, 166), (96, 140, 200), (238, 216, 184)),
       "night": ((0.36, 0.42, 0.64), (0.20, 0.22, 0.38), (30, 38, 74), (6, 10, 32), (36, 48, 92)),
       "war": ((0.92, 0.62, 0.50), (0.34, 0.30, 0.40), (150, 96, 92), (46, 30, 54), (190, 104, 84)),
       "dawn": ((1.0, 0.80, 0.70), (0.46, 0.42, 0.52), (240, 186, 156), (70, 92, 156), (255, 200, 156))}
def pmix(a, b, u): return mixp(PAL[a] if isinstance(a, str) else a, PAL[b] if isinstance(b, str) else b, smooth(u))
def terrain(sc, hgt, colfn, n=64, ext=82.0, cx=0.0, cy=0.0):
    for i in range(n):
        for j in range(n):
            x0, x1 = cx - ext + 2 * ext * i / n, cx - ext + 2 * ext * (i + 1) / n; y0, y1 = cy - ext + 2 * ext * j / n, cy - ext + 2 * ext * (j + 1) / n
            a, b, c, d = (x0, y0, hgt(x0, y0)), (x1, y0, hgt(x1, y0)), (x1, y1, hgt(x1, y1)), (x0, y1, hgt(x0, y1))
            for tri in ((a, b, c), (a, c, d)):
                mx, my, mz = [sum(v[k] for v in tri) / 3 for k in range(3)]; sc.tri(*tri, tuple(np.clip(np.array(colfn(mx, my, mz), float) * random.uniform(0.94, 1.06), 0, 255)), layer=0, ds=True)
def patch(sc, hgt, colfn, x0, x1, y0, y1, m=22, lift=0.02):
    for i in range(m):
        for j in range(m):
            xa, xb = x0 + (x1 - x0) * i / m, x0 + (x1 - x0) * (i + 1) / m; ya, yb = y0 + (y1 - y0) * j / m, y0 + (y1 - y0) * (j + 1) / m
            a, b, c, d = (xa, ya, hgt(xa, ya) + lift), (xb, ya, hgt(xb, ya) + lift), (xb, yb, hgt(xb, yb) + lift), (xa, yb, hgt(xa, yb) + lift)
            for tri in ((a, b, c), (a, c, d)):
                mx, my, mz = [sum(v[k] for v in tri) / 3 for k in range(3)]; col = colfn(mx, my, mz)
                if col is not None: sc.tri(*tri, tuple(np.clip(np.array(col, float) * random.uniform(0.92, 1.08), 0, 255)), layer=1, ds=True)
def city(sc, hgt, cx, cy, rad, n, hole=0.0, t=-1e9):
    placed = []
    for _ in range(n * 6):
        ang = random.uniform(0, 2 * math.pi); r = rad * math.sqrt(random.random()); x, y = cx + r * math.cos(ang), cy + r * math.sin(ang) * 0.9; sx, sy = random.uniform(0.7, 1.6), random.uniform(0.7, 1.6)
        if r < hole or any(abs(x - px) < (sx + ps) / 2 + 0.2 and abs(y - py) < (sy + pq) / 2 + 0.2 for px, py, ps, pq in placed): continue
        placed.append((x, y, sx, sy)); h = random.uniform(0.55, 1.4); tone = random.uniform(0.88, 1.08)
        sc.box(x, y, hgt(x, y) - 0.1, sx, sy, h, (204 * tone, 166 * tone, 122 * tone), top=(236 * tone, 206 * tone, 160 * tone), t=t)
        if len(placed) >= n: break
def palm(sc, hgt, x, y, t=-1e9):
    z = hgt(x, y); hh = random.uniform(1.3, 2.2); sc.box(x, y, z, 0.14, 0.14, hh, (104, 76, 54), t=t)
    for k in range(7):
        a = 2 * math.pi * k / 7; Ln = random.uniform(0.7, 1.0); w_ = 0.2
        sc.tri((x + w_ * math.cos(a + 1.57), y + w_ * math.sin(a + 1.57), z + hh), (x - w_ * math.cos(a + 1.57), y - w_ * math.sin(a + 1.57), z + hh), (x + Ln * math.cos(a), y + Ln * math.sin(a), z + hh - 0.28), (52, 134 * random.uniform(0.9, 1.1), 78), ds=True, t=t)
def unit(d, hgt, x, y, t, ph, body, flag, s=1.0, hop=False, big=1.0):
    if s <= 0.03: return
    z = hgt(x, y) + (0.07 * abs(math.sin(t * 9 + ph)) if hop else 0); b = 0.42 * big
    d.box(x, y, z, b * s, b * s, 0.3 * s * big, body); d.box(x, y, z + 0.3 * s * big, 0.06, 0.06, 1.05 * s * big, (40, 30, 30))
    fl = 0.12 * math.sin(t * 7 + ph); d.tri((x, y, z + 1.35 * s * big), (x, y, z + 0.95 * s * big), (x + 0.55 * s * big, y + fl, z + 1.15 * s * big), flag, ds=True)
MUSB, MUSF, QURB, QURF = (70, 96, 84), (40, 150, 96), (64, 44, 48), (176, 52, 46)
def polyline(P, u):
    u = clamp(u) * (len(P) - 1); i = min(len(P) - 2, int(u)); f = u - i
    p0, p1, p2, p3 = P[max(0, i - 1)], P[i], P[i + 1], P[min(len(P) - 1, i + 2)]
    return tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * f + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * f * f + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * f ** 3) for k in (0, 1))
def run(cfg):
    S = cfg["S"]; T2 = S.TS[1]; END, TOTAL = S.END, S.TOTAL; EV = cfg["events"]; EV["total"] = END; EV.setdefault("water", False)
    if os.environ.get("EVENTS"): json.dump(EV, open(os.environ["EVENTS"], "w")); print("events", END, [round(x, 2) for x in S.TS]); sys.exit(0)
    t_simpan, t_lesson, t_handle = cfg["cta"]; ST = cfg["build"]().arrays()
    MARK = mk_text("EL ZAHRA TRAVEL", "serif", 40, (246, 226, 170), 9); ILU = mk_text("Ilustrasi, bukan skala sebenar", "med", 24, (250, 246, 236)); HANDLE = mk_text("Follow @elzahratravel", "bold", 40, (255, 214, 120))
    LESSON = mk_text(cfg["lesson"], "bold", 42, (252, 248, 238))
    if LESSON.width > 1040: LESSON = LESSON.resize((1040, int(LESSON.height * 1040 / LESSON.width)), Image.LANCZOS)
    VIG = vignette(); WHITE = Image.new("RGB", (W, H), (255, 240, 214)); RED = Image.new("RGB", (W, H), (150, 30, 30)); CAPT = Captions(S, t_simpan - 0.1); GLOW = glow()
    def cap(parts):
        for size in (62, 56, 50, 44):
            im = pill(tuple(parts), size, pad=(46, 26))
            if im.width <= 1060: return im
        return im
    def frame(gf):
        t = gf / FPS; dyn, glows = cfg["dynamic"](t); A = merge(ST[0], ST[1], t, dyn); pos, tgt = cfg["cam"](t)
        hit = sum(a * math.exp(-(t - te) * 8.0) for te, a in EV["boom"] if t >= te); sk = 0.10 * hit; pos = np.array(pos, float) + np.array([sk * math.sin(t * 61), sk * math.cos(t * 53), sk * math.sin(t * 47)])
        arr, proj = render(A, pos, tgt, 42, cfg["env"](t), fogd=cfg.get("fogd", 0.0085)); base = Image.fromarray(arr)
        for g in glows:
            p = proj(g[:3])
            if p and 0 < p[0] < W and 0 < p[1] < H: paste(base, GLOW, p[0], p[1], 0.8, clamp(22.0 * (g[3] if len(g) > 3 else 1.0) / p[2]))
        base.paste(VIG, (0, 0), VIG); d = ImageDraw.Draw(base, "RGBA")
        if cfg.get("overlay"): cfg["overlay"](base, d, t, proj)
        for (a, b, anc, t0, t1, col) in cfg["labels"]: label(base, d, proj, a, b, anc(t) if callable(anc) else anc, t, t0, t1, col)
        if t < T2 - 0.1:
            a_ = clamp((T2 - 0.1 - t) / 0.25)
            for (t0, parts, y) in cfg["hook"]:
                if t >= t0 - 0.05: paste(base, pill(tuple(parts(t) if callable(parts) else parts), 58, pad=(44, 24)), W / 2, y, a_, max(0.05, back((t - t0 + 0.05) / 0.4)))
        for (t0, t1, parts) in cfg["caps"]:
            if t0 <= t <= t1 + 0.25: paste(base, cap(parts), W / 2, 330, clamp((t1 + 0.25 - t) / 0.25), max(0.05, back((t - t0) / 0.4)))
        CAPT.draw(base, t)
        if t >= t_simpan - 0.08:
            kk = (t - t_simpan + 0.08) * FPS; paste(base, pill((("Simpan video ini", INK),), 56, pad=(60, 30), bg=(255, 214, 120)), W / 2, 1300, 1, (0.4 + 0.6 * back(kk / 11.0)) * (1 + 0.035 * math.sin(kk / 3.0)))
            ps = ease((t - t_lesson + 0.08) / 0.3); paste(base, LESSON, W / 2, 1404 + (1 - ps) * 22, ps); paste(base, HANDLE, W / 2, 1474, ease((t - t_handle) / 0.3))
        paste(base, MARK, W / 2, 150); paste(base, ILU, W - 40 - ILU.width / 2, 262, 0.75)
        pw = 924 * gf / float(TOTAL); d.rounded_rectangle([78, 222, 1002, 228], 3, fill=(250, 246, 236, 70)); d.rounded_rectangle([78, 222, 78 + max(6, pw), 228], 3, fill=(255, 214, 120, 255))
        for ts_ in S.TS[1:]:
            if 0 <= t - ts_ < 0.27: base = Image.blend(base, WHITE, 0.45 * (1 - (t - ts_) / 0.27) ** 2)
        for te in cfg.get("red", []):
            if 0 <= t - te < 0.5: base = Image.blend(base, RED, 0.35 * (1 - (t - te) / 0.5) ** 2)
        for te in cfg.get("white", []):
            if 0 <= t - te < 0.6: base = Image.blend(base, WHITE, 0.5 * (1 - (t - te) / 0.6) ** 2)
        return fades(base, gf, TOTAL)
    main(frame, TOTAL, cfg["out"], cfg["tag"])
