# Spesifikasi video lukisan sinematik: Tahun Gajah. Guna: python3 tahun_gajah.py <dir input> <dir fon> > spec.json
import json, sys
WORDS = json.load(open(__file__.replace("tahun_gajah.py", "../words/sirah-tahun-gajah.json")))
PHRASES = ["Seorang penguasa Yaman", "bernama Abrahah", "mara ke Makkah", "dengan tentera bergajah.", "Tujuannya satu:", "meruntuhkan Kaabah.",
    "Tenteranya merampas unta", "milik Abdul Muttalib,", "datuk Nabi.", "Abdul Muttalib meminta", "untanya dipulangkan.", "Katanya:", "aku pemilik unta ini.",
    "Kaabah ada Pemiliknya,", "yang akan menjaganya.", "Penduduk Makkah", "berundur ke bukit.", "Lalu Allah menghantar", "burung berbondong-bondong,",
    "melontar tentera itu", "dengan batu daripada", "tanah yang dibakar.", "Kisah ini dirakam", "dalam Surah Al-Fil.", "Pada tahun itu juga,", "yang dikenali sebagai",
    "Tahun Gajah,", "Nabi Muhammad dilahirkan.", "Hari ini,", "Kaabah itulah", "yang anda tawaf.", "Pengajarannya:", "buat bahagian kita,", "selebihnya serahkan", "kepada Allah."]
C = [0.5, 0.5]
SHOTS = [  # t0 = masa potongan; src .png = imej (zoom, pan), .mp4 = klip video AI
    dict(t0=0.0, src="v01.mp4"),
    dict(t0=5.80, src="s02.png", zoom=[1.02, 1.16], pan=[[0.5, 0.42], [0.5, 0.48]]),
    dict(t0=9.40, src="s03.png", zoom=[1.14, 1.03], pan=[[0.42, 0.5], [0.56, 0.48]]),
    dict(t0=13.85, src="s04.png", zoom=[1.03, 1.17], pan=[[0.5, 0.56], [0.58, 0.40]]),
    dict(t0=17.95, src="s05.png", zoom=[1.10, 1.18], pan=[[0.5, 0.45], [0.5, 0.42]]),
    dict(t0=19.88, src="s06.png", zoom=[1.18, 1.03], pan=[[0.5, 0.60], [0.5, 0.42]]),
    dict(t0=23.72, src="s07.png", zoom=[1.04, 1.14], pan=[[0.5, 0.55], [0.5, 0.44]]),
    dict(t0=26.42, src="v08.mp4"),
    dict(t0=31.05, src="s09.png", zoom=[1.16, 1.05], pan=[[0.5, 0.40], [0.5, 0.50]]),
    dict(t0=33.66, src="s10.png", zoom=[1.03, 1.12], pan=[[0.46, 0.5], [0.54, 0.5]]),
    dict(t0=36.85, src="s11.png", zoom=[1.02, 1.18], pan=[[0.5, 0.58], [0.5, 0.40]]),
    dict(t0=43.18, src="s12.png", zoom=[1.16, 1.03], pan=[C, C], dust=0),
    dict(t0=46.80, src="s13.png", zoom=[1.03, 1.14], pan=[[0.5, 0.52], [0.5, 0.46]]),
]
CTA = WORDS[91][0] - 0.12
cuts = [s["t0"] for s in SHOTS[1:]]
print(json.dumps(dict(slug="el-zahra-sirah-tahun-gajah", **{"in": sys.argv[1]}, fonts=sys.argv[2], words=WORDS, phrases=PHRASES, shots=SHOTS, cta=CTA, cta_line="untuk kisah seterusnya",
    hook=["Tentera bergajah ", "menuju Kaabah"], hook_t=[0.15, 5.6],
    labels=[dict(text="Surah Al-Fil (surah ke-105)", t0=34.2, t1=36.7), dict(text="Tahun Gajah", t0=39.5, t1=43.0), dict(text="Masjidil Haram, hari ini", t0=43.4, t1=46.6)],
    ev=dict(whoosh=cuts, boom=[[0.05, 0.55], [26.45, 0.85], [31.1, 0.7]], ticks=[], riser_end=26.42, shimmer=36.85, water=False, pop=[CTA + 0.25, CTA + 0.7]))))
