"""Quiz video generator (Erics Quiz Kanal).
Usage: python3 quiz.py questions.json out.mp4
Question types: "flag" (stripes, dir v/h) and "text".
The last question is NOT revealed: viewers answer in the comments.
Sounds/music from ./sounds (ElevenLabs): tick, richtig, whoosh, finale, musik.
"""
import json, sys, subprocess, math, wave, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, SR = 1080, 1920, 30, 44100
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_fc = {}
def F(s):
    if s not in _fc: _fc[s] = ImageFont.truetype(FB, s)
    return _fc[s]

BG1, BG2 = (14, 18, 40), (44, 20, 70)
GOLD, WHITE, GREEN, RED, BOX = (255, 200, 60), (245, 245, 250), (40, 200, 110), (220, 60, 70), (36, 40, 70)
Q_IN, COUNT, REVEAL, FINAL_HOLD = 0.5, 3.0, 1.4, 3.5
QLEN = Q_IN + COUNT + REVEAL

cfg = json.load(open(sys.argv[1]))
qs = cfg["questions"]
NQ = len(qs)
PAUSE_AFTER, PAUSE = NQ // 2, 3.0          # follow reminder after half the levels
PA = QLEN * PAUSE_AFTER
PLUS = (990, 952)                          # TikTok follow "+" under the avatar (template: column x 900..1080 from y 840)
TOTAL = QLEN * (NQ - 1) + Q_IN + COUNT + FINAL_HOLD + PAUSE
NF = int(TOTAL * FPS)

bg = Image.new("RGB", (W, H)); bd = ImageDraw.Draw(bg)
for y in range(H):
    t = y / H
    bd.line([(0, y), (W, y)], fill=tuple(int(BG1[i] + (BG2[i] - BG1[i]) * t) for i in range(3)))

def ctext(d, y, s, font, fill=WHITE, stroke=0):
    w = d.textlength(s, font=font)
    d.text(((W - w) / 2, y), s, font=font, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))

def wrap(d, s, font, maxw):
    lines, cur = [], ""
    for w_ in s.split():
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w_
    lines.append(cur); return lines

def draw_flag(d, q, x0, y0, fw, fh):
    cols = [tuple(c) for c in q["stripes"]]; n = len(cols)
    for i, c in enumerate(cols):
        if q.get("dir", "v") == "v":
            d.rectangle([x0 + fw * i / n, y0, x0 + fw * (i + 1) / n, y0 + fh], fill=c)
        else:
            d.rectangle([x0, y0 + fh * i / n, x0 + fw, y0 + fh * (i + 1) / n], fill=c)
    d.rectangle([x0, y0, x0 + fw, y0 + fh], outline=(255, 255, 255), width=4)

def follow_frame(pt):
    im = bg.copy(); d = ImageDraw.Draw(im)
    ctext(d, 130, cfg["title"], F(78), GOLD, 4)
    ctext(d, 230, cfg["subtitle"], F(46), WHITE, 3)
    k = min(pt / 0.35, 1); s = 0.8 + 0.2 * (1 - (1 - k) ** 3)
    def ltext(y, txt, size, col):  # centered in the area left of TikTok's button column
        f = F(int(size * s)); w = d.textlength(txt, font=f)
        d.text((470 - w / 2, y), txt, font=f, fill=col, stroke_width=5, stroke_fill=(0, 0, 0))
    ltext(850, "Folge mir für mehr", 72, WHITE)
    ltext(940, "solcher Quiz", 72, GOLD)
    if k >= 1:
        # arrow from the text towards the follow plus, gently pulsing
        p = 0.5 + 0.5 * math.sin(pt * 7)
        x0, y0 = 820, 975
        x1, y1 = PLUS[0] - 58 - int(10 * p), PLUS[1]
        d.line([(x0, y0), (x1, y1)], fill=GOLD, width=16)
        d.polygon([(x1 + 40, y1), (x1 - 6, y1 - 30), (x1 - 6, y1 + 30)], fill=GOLD)
        r = 52 + int(8 * p)
        d.ellipse([PLUS[0] - r, PLUS[1] - r, PLUS[0] + r, PLUS[1] + r], outline=GOLD, width=7)
    return im

def frame(t):
    if PA <= t < PA + PAUSE:
        return follow_frame(t - PA)
    if t >= PA + PAUSE:
        t -= PAUSE
    im = bg.copy(); d = ImageDraw.Draw(im)
    ctext(d, 130, cfg["title"], F(78), GOLD, 4)
    ctext(d, 230, cfg["subtitle"], F(46), WHITE, 3)
    qi = min(int(t // QLEN), NQ - 1)
    q, lt = qs[qi], t - qi * QLEN
    last = qi == NQ - 1
    slide = min(lt / Q_IN, 1); off = int((1 - slide) ** 2 * 300)
    lvl = f"LEVEL {qi + 1}" + (" (FINALE)" if last else "")
    lf = F(56); lw = d.textlength(lvl, font=lf)
    d.rounded_rectangle([(W - lw) / 2 - 36, 330, (W + lw) / 2 + 36, 420], 40, fill=RED if last else GOLD)
    d.text(((W - lw) / 2, 344), lvl, font=lf, fill=WHITE if last else (20, 20, 30))
    qf = F(58); y = 470
    for ln in wrap(d, q["q"], qf, 920):
        ctext(d, y + off, ln, qf, WHITE, 3); y += 72
    if q["type"] == "flag":
        fw, fh = 660, 440
        draw_flag(d, q, (W - fw) / 2, 560 + off, fw, fh); oy = 1090
    else:
        oy = max(y + 80, 820)
    ended = lt >= Q_IN + COUNT
    reveal = ended and not last
    of = F(54)
    for i, opt in enumerate(q["options"]):
        yy = oy + i * 165 + off
        fill = (GREEN if i == q["answer"] else (70, 40, 50)) if reveal else BOX
        d.rounded_rectangle([110, yy, 970, yy + 135], 28, fill=fill, outline=(255, 255, 255), width=3)
        d.text((150, yy + 36), "ABC"[i], font=of, fill=WHITE if reveal else GOLD)
        sz = 54
        while d.textlength(opt, font=F(sz)) > 700 and sz > 30: sz -= 2
        d.text((230, yy + 36 + (54 - sz) // 2), opt, font=F(sz), fill=WHITE)
    by = oy + 3 * 165 + 30
    if not ended:
        rem = max(0, COUNT - max(0, lt - Q_IN)); frac = rem / COUNT
        d.rounded_rectangle([110, by, 970, by + 26], 13, fill=(60, 60, 90))
        col = GREEN if frac > 0.5 else (GOLD if frac > 0.25 else RED)
        d.rounded_rectangle([110, by, 110 + 860 * frac, by + 26], 13, fill=col)
        ctext(d, by + 40, str(max(1, math.ceil(rem))), F(64), col, 3)
    elif last:
        # dim everything, then pop the comment prompt in, centered
        k = min((lt - Q_IN - COUNT) / 0.4, 1)
        ov = Image.new("RGBA", (W, H), (8, 6, 20, int(228 * k)))
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        d = ImageDraw.Draw(im)
        s = 0.8 + 0.2 * (1 - (1 - k) ** 3)
        cy = H // 2 - 130
        ctext(d, cy, "Schreib die Antwort", F(int(84 * s)), WHITE, 6)
        ctext(d, cy + int(115 * s), "in die Kommentare", F(int(84 * s)), GOLD, 6)
        if k >= 1:
            # small animated arrow pointing down
            bounce = int(12 * math.sin((lt - Q_IN - COUNT) * 6))
            ax, ay = W // 2, cy + 270 + bounce
            d.polygon([(ax - 34, ay), (ax + 34, ay), (ax, ay + 40)], fill=GOLD)
    return im

# ---------- audio ----------
def load(name):
    path = os.path.join(HERE, "sounds", name)
    raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le",
                                   "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)

N = int(TOTAL * SR)
mix = np.zeros(N)
def add(at, snd, vol=1.0):
    i = int(at * SR)
    if i >= N: return
    seg = snd[:N - i]; mix[i:i + len(seg)] += seg * vol

tick, ok, whoosh, finale, music = (load(f) for f in ["stoppuhr.mp3", "richtig.mp3", "whoosh.mp3", "finale.mp3", cfg.get("music", "musik.mp3")])
def norm(x): return x / max(1e-9, np.abs(x).max())
tick, ok, whoosh, finale = map(norm, (tick, ok, whoosh, finale))
mus = np.tile(music, int(np.ceil(N / len(music))) + 1)[:N]
mus = norm(mus) * 0.22
fade = int(0.8 * SR); mus[-fade:] *= np.linspace(1, 0, fade)
mix += mus
glocke = norm(load("glocke.mp3")) if os.path.exists(os.path.join(HERE, "sounds", "glocke.mp3")) else whoosh
add(PA + 0.15, glocke, 0.18)  # follow reminder bell
for qi in range(NQ):
    s = qi * QLEN + (PAUSE if qi >= PAUSE_AFTER else 0)
    last = qi == NQ - 1
    add(s, whoosh, 0.25)
    if last: add(s, finale, 0.4)
    add(s + Q_IN, tick, 0.4)  # 3 s stopwatch, plays once over the countdown
    if not last:
        add(s + Q_IN + COUNT, ok, 0.22)
mix = np.clip(mix / max(1e-9, np.abs(mix).max()) * 0.9, -1, 1)
apath = os.path.join(os.path.dirname(os.path.abspath(sys.argv[2])), "audio_tmp.wav")
with wave.open(apath, "w") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((mix * 32767).astype(np.int16).tobytes())

# ---------- render ----------
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                      "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", apath,
                      "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                      "-af", "loudnorm=I=-15:TP=-2:LRA=11", "-ar", "44100", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", sys.argv[2]],
                     stdin=subprocess.PIPE)
for f in range(NF):
    p.stdin.write(frame(f / FPS).tobytes())
p.stdin.close(); p.wait()
print("done", round(TOTAL, 1), "s")
