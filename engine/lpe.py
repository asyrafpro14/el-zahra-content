import os, sys, math, json, random, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SS = 1080, 1920, 30, 1.5
RW, RH = int(W * SS), int(H * SS)
def clamp(x): return max(0.0, min(1.0, x))
def ease(t): t = clamp(t); return 1 - (1 - t) ** 3
def smooth(t): t = clamp(t); return t * t * (3 - 2 * t)
def back(t):
    t = clamp(t); c1 = 1.7; return 1 + (c1 + 1) * (t - 1) ** 3 + c1 * (t - 1) ** 2
def lerp(a, b, u): return a + (b - a) * u

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
        n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]); N = n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
        return [P, C, np.array(s.L, dtype=np.int64), np.array(s.D, dtype=bool), np.array(s.E, dtype=bool), N, P.mean(axis=1)], np.array(s.T, dtype=np.float64)
def merge(static, T, t, dyn):
    m = T <= t; A = [a[m] for a in static]
    if dyn.P:
        B, _ = dyn.arrays(); A = [np.concatenate((a, b)) for a, b in zip(A, B)]
    return A

LIGHT = np.array([-0.62, -0.28, 0.55]); LIGHT /= np.linalg.norm(LIGHT)
KY = (np.minimum(1.0, np.arange(RH) / (RH * 0.56)) ** 1.6)[:, None, None]
def render(A, pos, tgt, fov, ev, fogd=0.0085, light=LIGHT):
    P, C, L, D, E, N, cen = A; LCOL, AMB, FOG, STOP, SHOR = [np.array(x, float) for x in ev]
    pos = np.array(pos, float); f = np.array(tgt, float) - pos; f /= np.linalg.norm(f)
    r = np.cross(f, [0, 0, 1.0]); r /= np.linalg.norm(r); u = np.cross(r, f)
    V = P - pos; x = V @ r; y = V @ u; z = V @ f; foc = (RH / 2) / math.tan(math.radians(fov) / 2)
    ok = (z.min(axis=1) > 0.25); front = np.einsum("ij,ij->i", N, pos[None] - cen) > 0; ok &= (front | D)
    zz = np.maximum(z, 0.25); sx = RW / 2 + x / zz * foc; sy = RH / 2 - y / zz * foc
    ok &= (sx.max(axis=1) > -50) & (sx.min(axis=1) < RW + 50) & (sy.max(axis=1) > -50) & (sy.min(axis=1) < RH + 50)
    idx = np.nonzero(ok)[0]; depth = z[idx].mean(axis=1); dist = np.linalg.norm(cen[idx] - pos, axis=1)
    nl = N[idx] @ light; nl = np.where(D[idx], np.abs(nl), np.maximum(nl, 0)); up = np.maximum(N[idx][:, 2], 0)
    sh = np.clip(C[idx] * (AMB[None] * (0.82 + 0.18 * up[:, None]) + LCOL[None] * nl[:, None] * 0.98), 0, 255)
    fg = np.clip(1 - np.exp(-(dist * fogd) ** 1.5), 0, 0.93)[:, None]
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
def mixp(a, b, u): return [np.array(x, float) * (1 - u) + np.array(y, float) * u for x, y in zip(a, b)]
def camera(K, t, lift=26):
    ts = [k[0] for k in K]; t = max(ts[0], min(ts[-1] - 1e-6, t)); i = max(j for j in range(len(ts) - 1) if ts[j] <= t); u = smooth((t - ts[i]) / (ts[i + 1] - ts[i]))
    p = np.array(K[i][1], float) * (1 - u) + np.array(K[i + 1][1], float) * u; g = np.array(K[i][2], float) * (1 - u) + np.array(K[i + 1][2], float) * u
    d = np.linalg.norm(np.array(K[i][1], float)[:2] - np.array(K[i + 1][1], float)[:2])
    if d > 34 and lift: p[2] += lift * math.sin(math.pi * u) * min(1, d / 60)
    return p, g

class Script:
    def __init__(s, scenes, words):
        s.SCRIPT, s.BLOCKS, s.SC_FIRST = [], [], []
        for si, blocks in enumerate(scenes):
            s.SC_FIRST.append(len(s.SCRIPT))
            for b in blocks:
                ws = b.lstrip("#").split(); s.BLOCKS.append([si, b[0] == "#", len(s.SCRIPT), len(s.SCRIPT) + len(ws) - 1]); s.SCRIPT.extend(ws)
        s.NW = len(s.SCRIPT); s.NS = len(scenes)
        if os.environ.get("COUNT"): print(s.NW); sys.exit(0)
        if not os.path.exists(words): words = os.path.join(os.path.dirname(os.path.abspath(__file__)), "words", os.path.basename(words))
        if os.environ.get("FAKE"): s.WT = [[0.3 + 0.42 * i, 0.3 + 0.42 * i + 0.36] for i in range(s.NW)]
        else: s.WT = json.load(open(words))
        assert len(s.WT) == s.NW, (len(s.WT), s.NW)
        s.DISP = list(s.SCRIPT); s.TS = [0.0] + [s.st(s.SC_FIRST[k]) - 0.2 for k in range(1, s.NS)]; s.END = s.en(s.NW - 1) + 2.0; s.TOTAL = int(s.END * FPS)
    def st(s, i): return s.WT[i][0]
    def en(s, i): return s.WT[i][1]
    def wi(s, word, scene=0, nth=0):
        hits = [i for i in range(s.SC_FIRST[scene], s.NW) if s.SCRIPT[i].rstrip(",.?:").lower() == word.lower()]; return hits[nth]
    def t(s, word, scene=0, nth=0): return s.st(s.wi(word, scene, nth))
    def bl_end(s, k, last):
        si = s.BLOCKS[k][0]
        for j in range(k + 1, len(s.BLOCKS)):
            if s.BLOCKS[j][0] != si: break
            if not s.BLOCKS[j][1]: return s.st(s.BLOCKS[j][2]) - 0.08
        return s.TS[si + 1] if si < s.NS - 1 else last

FONTS = {"bold": "Poppins:bold", "med": "Poppins:medium", "serif": "Lora:bold", "anton": "Anton"}
HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL = {"Poppins:bold": "Poppins-Bold.ttf", "Poppins:medium": "Poppins-Medium.ttf", "Lora:bold": "Lora-Variable.ttf", "Anton": "Anton-Regular.ttf"}
def fpath(p):
    f = os.path.join(HERE, "fonts", LOCAL.get(p, ""))
    return f if os.path.isfile(f) else subprocess.check_output(["fc-match", "-f", "%{file}", p]).decode()
_f = {}
def font(kind, size):
    if (kind, size) not in _f:
        f = ImageFont.truetype(fpath(FONTS[kind]), size)
        if kind == "serif":
            try: f.set_variation_by_name("Bold")
            except Exception: pass
        _f[(kind, size)] = f
    return _f[(kind, size)]
_pc = {}
def pill(parts, size, pad=(34, 20), bg=(250, 247, 240), sub=None, subcol=(110, 100, 90), kind="bold", rad=30):
    key = (tuple(parts), size, pad, bg, sub, subcol, kind, rad)
    if key in _pc: return _pc[key]
    f = font(kind, size); asc, desc = f.getmetrics(); tw = sum(f.getlength(p[0]) for p in parts)
    fs = font("med", int(size * 0.62)) if sub else None; sw = fs.getlength(sub) if sub else 0; sh = int(size * 0.9) if sub else 0
    w = int(max(tw, sw) + pad[0] * 2); h = asc + desc + pad[1] * 2 + sh
    im = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0)); ImageDraw.Draw(im).rounded_rectangle([0, 0, w * 2 - 1, h * 2 - 1], min(h // 2, rad) * 2, fill=tuple(bg) + (255,))
    im = im.resize((w, h), Image.LANCZOS); d = ImageDraw.Draw(im); x = (w - tw) / 2
    for txt, col in parts: d.text((x, pad[1]), txt, font=f, fill=col); x += f.getlength(txt)
    if sub: d.text(((w - sw) / 2, pad[1] + asc + desc - 2), sub, font=fs, fill=subcol)
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
def mk_text(txt, kind, size, col, tr=0, stroke=0, sfill=(0, 0, 0)):
    f = font(kind, size); asc, desc = f.getmetrics(); w = int(f.getlength(txt) + tr * len(txt)) + 40 + stroke * 2; im = Image.new("RGBA", (w, asc + desc + 40 + stroke * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 20 + stroke
    for ch in txt:
        if not stroke: d.text((x + 2, 22), ch, font=f, fill=(0, 0, 0, 150))
        d.text((x, 20 + stroke), ch, font=f, fill=col, stroke_width=stroke, stroke_fill=sfill); x += f.getlength(ch) + tr
    return shadowed(im, 8, 5) if stroke else im
class TB:
    def __init__(s, S, words, idxs, size, max_w=960, gap=1.2, hi=(255, 208, 96), kind="bold"):
        s.S = S; f = font(kind, size); sp = f.getlength(" "); ws = [f.getlength(w) for w in words]; lines, cur, cw = [], [], 0
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
                for c in ((252, 248, 238), hi):
                    im = Image.new("RGBA", (int(ws[j]) + pad * 2, asc + desc + pad * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
                    d.text((pad, pad), words[j], font=f, fill=c, stroke_width=5, stroke_fill=(24, 18, 16)); ims.append(shadowed(im, 7, 4))
                s.items.append((x - pad, li * lh - pad, idxs[j], ims[0], ims[1])); x += ws[j] + sp
    def draw(s, base, cx, y, t, a=1.0):
        S = s.S
        for x, yy, i, im, imh in s.items:
            p = ease((t - (S.st(i) - 0.07)) / 0.2)
            if p <= 0: continue
            nxt = S.st(i + 1) if i + 1 < S.NW and S.st(i + 1) - S.en(i) < 0.35 else S.en(i) + 0.12
            paste(base, imh if t < nxt - 0.05 else im, cx + x + im.width / 2, y + yy + im.height / 2 + (1 - p) * 22, p * a)
class Captions:
    def __init__(s, S, last, size=60, hi=(255, 208, 96), y=1360):
        s.S = S; s.last = last; s.y = y
        s.TBS = [None if cta else TB(S, [S.DISP[i] for i in range(a, b + 1)], list(range(a, b + 1)), size, hi=hi) for si, cta, a, b in S.BLOCKS]
    def draw(s, base, t):
        S = s.S
        for k, (si, cta, a, b) in enumerate(S.BLOCKS):
            if cta or t < S.st(a) - 0.12: continue
            te = S.bl_end(k, s.last)
            if t >= te: continue
            s.TBS[k].draw(base, W / 2, s.y, t, clamp((te - t) / 0.12))
def label(base, d, proj, text, sub, anc, t, t0, t1, col, size=34, ymin=470, ymax=1180, dy=150, bg=(250, 247, 240), subcol=(110, 100, 90)):
    if t < t0 or t > t1 + 0.3: return
    p = proj(anc)
    if not p: return
    im = pill(((text, col),), size, sub=sub, bg=bg, subcol=subcol); al = clamp((t1 + 0.3 - t) / 0.3); pp = back((t - t0) / 0.35)
    lx = min(W - im.width / 2 + 10, max(im.width / 2 - 10, p[0])); ly = min(ymax, max(ymin, p[1] - dy))
    d.line([p[0], p[1], lx, ly + im.height / 2 - 34], fill=(250, 247, 240, int(230 * al * clamp(pp))), width=3)
    d.ellipse([p[0] - 9, p[1] - 9, p[0] + 9, p[1] + 9], fill=(250, 247, 240, int(255 * al)), outline=(40, 34, 30, int(255 * al)), width=3)
    paste(base, im, lx, ly, al, max(0.05, pp))
def vignette(col=(20, 14, 26), top=120, bot=185):
    vig = Image.new("L", (W, H), 0); vd = ImageDraw.Draw(vig); vd.rectangle([0, 0, W, 180], fill=top); vd.rectangle([0, H - 620, W, H], fill=bot)
    return Image.merge("RGBA", (*Image.new("RGB", (W, H), col).split(), vig.filter(ImageFilter.GaussianBlur(150))))
def glow(col=(255, 190, 100)):
    gm = Image.new("L", (240, 240), 0); ImageDraw.Draw(gm).ellipse([70, 70, 170, 170], fill=255)
    return Image.merge("RGBA", (*Image.new("RGB", (240, 240), col).split(), gm.filter(ImageFilter.GaussianBlur(34))))
BLACK = Image.new("RGB", (W, H), (0, 0, 0))
def fades(base, gf, total):
    if gf < 10: base = Image.blend(BLACK, base, gf / 10.0)
    if gf > total - 14: base = Image.blend(BLACK, base, clamp((total - gf) / 14.0))
    return base
def main(frame, total, out, tag):
    if os.environ.get("PREVIEW"):
        for tt in [float(x) for x in os.environ["PREVIEW"].split(",")]:
            frame(int(tt * FPS)).resize((540, 960), Image.LANCZOS).save("/tmp/%s_%05.2f.jpg" % (tag, tt), quality=90)
        return
    tmp = out.replace(".mp4", ".part.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "22", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
    for gf in range(total): p.stdin.write(frame(gf).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, out); print("OK", out, total)
