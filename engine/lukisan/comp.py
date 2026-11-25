# Penyusun video gaya LUKISAN SINEMATIK (PIL + numpy + ffmpeg sahaja, supaya boleh jalan dalam sandbox ElevenLabs).
# Guna: python3 comp.py <spec.json> all      |  python3 comp.py <spec.json> shot <k>  |  PREVIEW=1 python3 comp.py <spec.json> all (satu frame setiap shot)
# spec: {"slug", "in", "fonts", "voice", "words": [[mula, tamat]...], "phrases": ["ayat kapsyen"...], "shots": [...], "hook": [a, b], "labels": [...], "cta": t, "ev": {...}}
import os, sys, json, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
SP = json.load(open(sys.argv[1])); IN = SP["in"]; FD = SP["fonts"]; TMP = os.environ.get("TMP", "tmp"); os.makedirs(TMP, exist_ok=True)
WT = SP["words"]; END = WT[-1][1] + 1.8; TOTAL = int(END * FPS); SHOTS = SP["shots"]; CTA = SP["cta"]
GOLD, CREAM, INK, GREEN = (255, 208, 96), (247, 243, 232), (38, 34, 30), (15, 61, 46)
def font(k, s): return ImageFont.truetype(os.path.join(FD, {"bold": "pb.ttf", "med": "pm.ttf", "serif": "lo.ttf"}[k]), s)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)

# ---------- kapsyen ikut frasa, perkataan semasa diserlahkan ----------
PH = []; k = 0
for p in SP["phrases"]:
    ws = p.split(); PH.append((ws, k, k + len(ws) - 1)); k += len(ws)
assert k <= len(WT), (k, len(WT))
def text_img(parts, size, kind="bold", stroke=7, track=0):
    f = font(kind, size); sp = f.getlength(" "); x = stroke + 4; pos = []
    for txt, col in parts: pos.append((x, txt, col)); x += f.getlength(txt) + track * len(txt) + sp
    im = Image.new("RGBA", (int(x - sp + stroke + 6), int(size * 1.5 + 2 * stroke)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for px, txt, col in pos:
        if track:
            cx = px
            for ch in txt: d.text((cx, stroke), ch, font=f, fill=col); cx += f.getlength(ch) + track
        else: d.text((px, stroke), txt, font=f, fill=col, stroke_width=stroke, stroke_fill=(12, 10, 8, 235))
    return im
def shadowed(im, blur=10, off=5, a=150):
    sh = Image.new("RGBA", (im.width + 40, im.height + 40), (0, 0, 0, 0)); al = im.split()[3].point(lambda v: v * a // 255)
    sh.paste((0, 0, 0, 255), (20, 20 + off), al); sh = sh.filter(ImageFilter.GaussianBlur(blur)); sh.alpha_composite(im, (20, 20)); return sh
CAPC = {}
def caption(pi, wi):
    key = (pi, wi)
    if key not in CAPC:
        ws, a, b = PH[pi]; size = 66
        while font("bold", size).getlength(" ".join(ws)) > 930 and size > 44: size -= 2
        CAPC.clear() if len(CAPC) > 40 else None
        CAPC[key] = shadowed(text_img([(w, GOLD + (255,) if a + j == wi else (255, 252, 244, 255)) for j, w in enumerate(ws)], size))
    return CAPC[key]
def pill(parts, size, bg=CREAM, pad=(34, 18), rad=30):
    t = text_img(parts, size, stroke=0); im = Image.new("RGBA", (t.width + 2 * pad[0], int(size * 1.25) + 2 * pad[1]), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, im.height - 1], rad, fill=bg + (242,)); im.alpha_composite(t, (pad[0], pad[1] - 2)); return shadowed(im, 14, 8, 110)
def paste(base, im, cx, cy, a=1.0, sc=1.0):
    if a <= 0.01: return
    if sc != 1.0: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
    if a < 1: im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * a)))
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

# ---------- lapisan tetap ----------
def grad():
    y = np.linspace(0, 1, H)[:, None]; x = np.linspace(-1, 1, W)[None, :]
    a = np.clip((y - 0.60) / 0.40, 0, 1) ** 1.5 * 150 + np.clip((0.16 - y) / 0.16, 0, 1) ** 1.3 * 120 + np.clip((x ** 2 + (2 * y - 1) ** 2 * 0.7 - 0.9) / 0.9, 0, 1) * 90
    im = np.zeros((H, W, 4), np.uint8); im[..., 3] = np.clip(a, 0, 215); return Image.fromarray(im, "RGBA")
def dust(seed, n, r0, r1, al):
    rnd = random.Random(seed); im = Image.new("RGBA", (W, H * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for _ in range(n):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(r0, r1); c = (255, 236, 200, int(rnd.uniform(0.4, 1) * al))
        for yy in (y, y + H): d.ellipse([x - r, yy - r, x + r, yy + r], fill=c)
    return im.filter(ImageFilter.GaussianBlur(1.6))
GRAD = None; DUST = None; MARK = None; ILU = None; HOOK = None; LBL = None; ENDC = None
def init():
    global GRAD, DUST, MARK, ILU, HOOK, LBL, ENDC
    GRAD = grad(); DUST = [dust(3, 70, 1.5, 3.5, 120), dust(8, 26, 3, 7, 80)]
    MARK = text_img([("EL ZAHRA TRAVEL", (246, 226, 170, 255))], 40, "serif", 0, 9); ILU = text_img([("Ilustrasi, bukan gambaran sebenar", (250, 246, 236, 215))], 24, "med", 0)
    HOOK = pill([(SP["hook"][0], (176, 128, 30, 255)), (SP["hook"][1], INK + (255,))], 50)
    LBL = [(pill([(l["text"], (150, 108, 24, 255))], 36, pad=(26, 12), rad=24), l["t0"], l["t1"]) for l in SP.get("labels", [])]
    ENDC = (pill([("Follow @elzahratravel", GREEN + (255,))], 54, bg=(255, 214, 120), pad=(44, 22), rad=40), shadowed(text_img([(SP["cta_line"], (252, 248, 238, 255))], 40, "med", 0)), shadowed(text_img([("EL ZAHRA TRAVEL", (246, 226, 170, 255))], 64, "serif", 0, 12)))

# ---------- sumber gambar setiap shot ----------
class Still:
    def __init__(s, sh):
        im = Image.open(os.path.join(IN, sh["src"])).convert("RGB"); s.sw, s.sh = im.size; s.im = im
        s.k = max(W / s.sw, H / s.sh); s.sh_ = sh
    def frame(s, u, t):
        z0, z1 = s.sh_.get("zoom", [1.04, 1.14]); (ax, ay), (bx, by) = s.sh_.get("pan", [[0.5, 0.5], [0.5, 0.5]]); e = smooth(u) * 0.6 + u * 0.4
        z = z0 + (z1 - z0) * e; cx = (ax + (bx - ax) * e) * s.sw; cy = (ay + (by - ay) * e) * s.sh; inv = 1.0 / (s.k * z)
        hw, hh = W * inv / 2, H * inv / 2; cx = clamp(cx, hw, s.sw - hw); cy = clamp(cy, hh, s.sh - hh)
        return s.im.transform((W, H), Image.AFFINE, (inv, 0, cx - hw, 0, inv, cy - hh), resample=Image.BICUBIC)
class Clip:
    def __init__(s, sh, nfr):
        src = os.path.join(IN, sh["src"]); d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src]))
        a = sh.get("clip", [0, d]); want = nfr / FPS; r = want / (a[1] - a[0])     # r > 1: perlahankan sedikit supaya cukup panjang
        vf = "trim=%.3f:%.3f,setpts=(PTS-STARTPTS)*%.5f,fps=%d,scale=%d:%d:force_original_aspect_ratio=increase:flags=lanczos,crop=%d:%d" % (a[0], a[1], r, FPS, W, H, W, H)
        s.p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", src, "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE); s.last = None
    def frame(s, u, t):
        b = s.p.stdout.read(W * H * 3)
        if len(b) == W * H * 3: s.last = Image.frombytes("RGB", (W, H), b)
        return s.last.copy()

def shot_at(t): return max(i for i, sh in enumerate(SHOTS) if t >= sh["t0"] or i == 0)
def compose(bg, t, gf):
    base = bg.convert("RGBA"); k = shot_at(t); sh = SHOTS[k]
    for j, dl in enumerate(DUST):                                   # debu melayang, dua lapis
        oy = int((t * (26 + 22 * j)) % H); ox = int(30 * math.sin(t * 0.3 + j * 2)); layer = dl.crop((0, H - oy, W, 2 * H - oy))
        if sh.get("dust", 1) > 0: base.alpha_composite(layer.transform((W, H), Image.AFFINE, (1, 0, -ox, 0, 1, 0)) if ox else layer)
    base.alpha_composite(GRAD)
    fl = clamp(1 - (t - sh["t0"]) / 0.14) if k > 0 else 0                # kilat pendek pada setiap potongan
    if fl > 0: base = Image.blend(base, Image.new("RGBA", (W, H), (255, 240, 214, 255)), 0.30 * fl)
    endp = ease((t - CTA) / 0.5)
    if endp > 0: base = Image.blend(base, Image.new("RGBA", (W, H), (8, 28, 22, 255)), 0.55 * endp)
    paste(base, MARK, W / 2, 150); paste(base, ILU, W - 30 - ILU.width / 2, 250)
    d = ImageDraw.Draw(base); pw = 924 * gf / float(TOTAL); d.rounded_rectangle([78, 208, 1002, 214], 3, fill=(250, 246, 236, 70)); d.rounded_rectangle([78, 208, 78 + max(6, pw), 214], 3, fill=(255, 214, 120, 255))
    h0, h1 = SP["hook_t"]; ha = ease((t - h0) / 0.3) * clamp((h1 - t) / 0.3); paste(base, HOOK, W / 2, 350 - (1 - ease((t - h0) / 0.35)) * 30, ha)
    for im, a, b in LBL: paste(base, im, W / 2, 350, ease((t - a) / 0.3) * clamp((b - t) / 0.3))
    if t < CTA - 0.05:
        for pi, (ws, a, b) in enumerate(PH):
            ta = WT[a][0] - 0.10; tb = WT[PH[pi + 1][1]][0] - 0.10 if pi + 1 < len(PH) else WT[b][1] + 0.35; tb = min(tb, WT[b][1] + 0.6, CTA - 0.05)
            if ta <= t < tb:
                wi = max([j for j in range(a, b + 1) if t >= WT[j][0] - 0.04] or [a]); pop = 0.94 + 0.06 * ease((t - ta) / 0.12)
                paste(base, caption(pi, wi), W / 2, 1345, ease((t - ta) / 0.10) * clamp((tb - t) / 0.08 + 0.2), pop)
    if endp > 0:
        paste(base, ENDC[2], W / 2, 800, endp); paste(base, ENDC[0], W / 2, 960 + (1 - ease((t - CTA - 0.25) / 0.4)) * 30, ease((t - CTA - 0.25) / 0.4)); paste(base, ENDC[1], W / 2, 1080, ease((t - CTA - 0.7) / 0.4))
    gfade = min(1.0, gf / 8.0, (TOTAL - gf) / 12.0)
    out = base.convert("RGB")
    return out if gfade >= 1 else Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), out, max(0.0, gfade))

def frames_of(k):
    a = int(round(SHOTS[k]["t0"] * FPS)) if k else 0; b = int(round(SHOTS[k + 1]["t0"] * FPS)) if k + 1 < len(SHOTS) else TOTAL; return a, b
def render_shot(k):
    init(); a, b = frames_of(k); sh = SHOTS[k]; src = Clip(sh, b - a) if sh["src"].endswith(".mp4") else Still(sh)
    if os.environ.get("PREVIEW"):
        gf = a + int((b - a) * float(os.environ["PREVIEW"]));
        for _ in range(gf - a + 1 if isinstance(src, Clip) else 1): bg = src.frame((gf - a) / max(1, b - a - 1), gf / FPS)
        compose(bg, gf / FPS, gf).resize((540, 960), Image.LANCZOS).save("%s/prev_%02d.jpg" % (TMP, k), quality=88); return
    out = "%s/seg_%02d.mp4" % (TMP, k)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", os.environ.get("CRF", "19"), "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS), out], stdin=subprocess.PIPE)
    for gf in range(a, b): p.stdin.write(compose(src.frame((gf - a) / max(1, b - a - 1), gf / FPS), gf / FPS, gf).tobytes())
    p.stdin.close(); assert p.wait() == 0; print("shot", k, b - a, flush=True)

if sys.argv[2] == "shot": render_shot(int(sys.argv[3]))
elif sys.argv[2] == "events":
    ev = dict(SP["ev"]); ev["total"] = END; json.dump(ev, open(sys.argv[3], "w")); print("total", END)
else:
    J = int(os.environ.get("JOBS", "8")); ks = list(range(len(SHOTS))); run = []
    while ks or run:
        while ks and len(run) < J: k = ks.pop(0); run.append((k, subprocess.Popen([sys.executable, sys.argv[0], sys.argv[1], "shot", str(k)])))
        k, p = run.pop(0)
        if p.wait() != 0: sys.exit("shot %d gagal" % k)
    if not os.environ.get("PREVIEW"):
        open(TMP + "/list.txt", "w").write("".join("file 'seg_%02d.mp4'\n" % k for k in range(len(SHOTS))))
        subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", TMP + "/list.txt", "-c", "copy", TMP + "/silent.mp4"]); print("OK silent", TOTAL)
