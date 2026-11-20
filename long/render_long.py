import json, math, re, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from script import SLIDES

W, H, FPS = 1920, 1080, 30
GAP, CH_EXTRA, TAIL = 0.45, 0.6, 1.0
FD = "/usr/share/fonts/opentype/inter/"
def F(n, s): return ImageFont.truetype(FD + n, s)
EMOF = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
GOLD = (255, 206, 60); RED = (230, 45, 30); WHITE = (255, 255, 255); SOFT = (205, 214, 235)

durs = json.load(open("durs.json"))
# timeline: list of (slide, item, start, dur)
TL = []; t = 0.0; k = 0
for si, s in enumerate(SLIDES):
    for ii, it in enumerate(s["items"]):
        d = durs[k][2] + GAP + (CH_EXTRA if s["kind"] == "chapter" else 0); k += 1
        TL.append((si, ii, t, d)); t += d
TOTAL = t + TAIL
NF = int(TOTAL * FPS)
SLIDE_START = {}
for si, ii, st, d in TL: SLIDE_START.setdefault(si, st)
CHAPTER_STARTS = [SLIDE_START[si] for si, s in enumerate(SLIDES) if s["kind"] == "chapter"]

def ease_out(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_back(x):
    x = min(max(x, 0), 1); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

# ---------- backgrounds (themes cycle by chapter)
THEMES = [((10, 16, 44), (150, 22, 40), (40, 60, 170)), ((14, 10, 50), (90, 30, 140), (200, 40, 60)),
          ((6, 26, 52), (0, 110, 140), (190, 40, 50)), ((20, 12, 36), (160, 60, 20), (60, 40, 160))]
def make_bg(theme):
    base, c1, c2 = theme; bw, bh = W + 300, H + 240
    im = Image.new("RGB", (bw, bh), base)
    for col, box, a in [(c1, (bw - 900, -300, bw + 200, 700), 190), (c2, (-300, bh - 700, 800, bh + 300), 160), (c1, (700, 500, 1400, 1000), 60)]:
        g = Image.new("L", (bw, bh), 0); ImageDraw.Draw(g).ellipse(box, fill=a)
        im = Image.composite(Image.new("RGB", (bw, bh), col), im, g.filter(ImageFilter.GaussianBlur(220)))
    d = ImageDraw.Draw(im, "RGBA")
    for y in range(0, bh, 40):
        for x in range(0, bw, 40): d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 255, 255, 18))
    return im
BGS = [make_bg(th) for th in THEMES]
rng = np.random.default_rng(4)
PARTS = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(2, 5), rng.uniform(15, 45)) for _ in range(45)]
def theme_idx(si):
    return sum(1 for j in range(si + 1) if SLIDES[j]["kind"] == "chapter") % len(BGS)
def bg_frame(t, si):
    b = BGS[theme_idx(si)]
    ox = int(150 + 150 * math.sin(t * 0.12)); oy = int(120 + 120 * math.cos(t * 0.09))
    im = b.crop((ox, oy, ox + W, oy + H)).convert("RGBA")
    d = ImageDraw.Draw(im)
    for (x, y, r, sp) in PARTS:
        yy = (y - t * sp) % H; d.ellipse((x - r, yy - r, x + r, yy + r), fill=(255, 255, 255, 35))
    return im

# ---------- helpers
_emo_cache = {}
def emoji(e, size):
    key = (e, size)
    if key not in _emo_cache:
        im = Image.new("RGBA", (200, 150)); ImageDraw.Draw(im).text((10, 5), e, font=EMOF, embedded_color=True)
        bb = im.getbbox(); im = im.crop(bb) if bb else im
        r = size / max(im.size); _emo_cache[key] = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
    return _emo_cache[key]
def rich(d, xy, text, font, base, hi=GOLD, anchor_center=False, stroke=0):
    text = text.replace("❌ ", "").replace("❌", "")
    parts = [p for p in re.split(r"(\*[^*]+\*)", text) if p]
    tw = sum(d.textlength(p.strip("*"), font=font) for p in parts)
    x, y = xy
    if anchor_center: x -= tw / 2
    for p in parts:
        h = p.startswith("*"); p = p.strip("*")
        d.text((x, y), p, font=font, fill=hi if h else base, stroke_width=stroke, stroke_fill=(5, 8, 22))
        x += d.textlength(p, font=font)
    return tw
def fit_font(d, text, name, start, maxw):
    s = start; plain = text.replace("*", "")
    while s > 24:
        f = F(name, s)
        if d.textlength(plain, font=f) <= maxw: return f
        s -= 2
    return F(name, s)

BRAND = F("Inter-Black.otf", 30); PILL = F("Inter-ExtraBold.otf", 28)
def chrome(im, si, t):
    d = ImageDraw.Draw(im)
    d.text((70, 58), "SCHOLARSHIPS IN CHINA", font=BRAND, fill=GOLD)
    s = SLIDES[si]; label = s.get("chapter") or ("CHAPTER " + s["num"] if s["kind"] == "chapter" else "CSC 2027 GUIDE")
    tw = d.textlength(label, font=PILL)
    d.rounded_rectangle((W - 70 - tw - 56, 46, W - 70, 100), radius=27, fill=RED)
    d.text((W - 70 - tw - 28, 73), label, font=PILL, fill=WHITE, anchor="lm")
    # progress
    d.rectangle((0, H - 10, W, H), fill=(255, 255, 255, 40))
    d.rectangle((0, H - 10, int(W * t / TOTAL), H), fill=GOLD)
    for c in CHAPTER_STARTS:
        x = int(W * c / TOTAL); d.rectangle((x - 2, H - 16, x + 2, H), fill=WHITE)

# ---------- slide layers (cached per slide, per active item)
_layer_cache = {}
def list_layer(si, active):
    key = (si, active)
    if key in _layer_cache: return _layer_cache[key]
    s = SLIDES[si]; L = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(L)
    # glass panel
    d.rounded_rectangle((60, 140, 1240, 1020), radius=36, fill=(5, 10, 30, 150))
    tf = fit_font(d, s["title"], "Inter-Black.otf", 64, 1080)
    d.text((110, 180), s["title"], font=tf, fill=WHITE)
    d.rectangle((110, 270, 250, 278), fill=GOLD)
    n = len(s["items"]); rowh = min(128, int(690 / max(n, 1)))
    for j, it in enumerate(s["items"]):
        if j > active: break
        y = 310 + j * rowh
        cur = (j == active)
        if cur: d.rounded_rectangle((90, y - 8, 1210, y + rowh - 20), radius=20, fill=(255, 255, 255, 28))
        if cur: d.rectangle((90, y - 8, 98, y + rowh - 20), fill=GOLD)
        e = emoji(it["emo"], 56)
        L.alpha_composite(e, (120, int(y + (rowh - 28) / 2 - e.height / 2)))
        bf = fit_font(d, it["b"], "Inter-Bold.otf", 44, 1000)
        rich(d, (200, y + (rowh - 28) / 2 - 26), it["b"], bf, WHITE if cur else SOFT)
    _layer_cache[key] = L
    return L

def frame(fi):
    t = fi / FPS
    idx = max(i for i, x in enumerate(TL) if x[2] <= t + 1e-6)
    si, ii, st, dur = TL[idx]; lt = t - st; s = SLIDES[si]; slt = t - SLIDE_START[si]
    im = bg_frame(t, si)
    if s["kind"] == "list":
        L = list_layer(si, ii)
        if ii > 0 and lt < 0.3:
            prev = list_layer(si, ii - 1); a = ease_out(lt / 0.3)
            im.alpha_composite(Image.blend(prev, L, a))
        else:
            off = int(60 * (1 - ease_out(slt / 0.45)))
            if off:
                tmp = Image.new("RGBA", (W, H)); tmp.alpha_composite(L, (0, off))
                tmp.putalpha(tmp.getchannel("A").point(lambda v: int(v * ease_out(slt / 0.45))))
                im.alpha_composite(tmp)
            else: im.alpha_composite(L)
        # big emoji on the right
        it = s["items"][ii]; sc = 0.4 + 0.6 * ease_back(lt / 0.35)
        size = int(300 * sc); e = emoji(it["emo"], 300).resize((size, size), Image.BILINEAR) if size > 0 else None
        g = Image.new("RGBA", (W, H)); ImageDraw.Draw(g).ellipse((1380, 330, 1780, 730), fill=(255, 206, 60, 70))
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(60)) if False else g)
        bob = int(10 * math.sin(lt * 3))
        if e: im.alpha_composite(e, (1580 - e.width // 2, 530 - e.height // 2 + bob))
    elif s["kind"] == "chapter":
        d = ImageDraw.Draw(im); a = ease_out(slt / 0.5); off = int(80 * (1 - a))
        tmp = Image.new("RGBA", (W, H)); td = ImageDraw.Draw(tmp)
        td.text((W // 2, 400 + off), s["num"], font=F("Inter-Black.otf", 240), fill=GOLD, anchor="mm")
        tf = fit_font(td, s["title"], "Inter-Black.otf", 96, 1700)
        td.text((W // 2, 610 + off), s["title"], font=tf, fill=WHITE, anchor="mm", stroke_width=4, stroke_fill=(5, 8, 22))
        td.rectangle((W // 2 - int(150 * a), 700 + off, W // 2 + int(150 * a), 710 + off), fill=RED)
        tmp.putalpha(tmp.getchannel("A").point(lambda v: int(v * a)))
        im.alpha_composite(tmp)
    else:  # intro / outro
        a = ease_out(slt / 0.6); tmp = Image.new("RGBA", (W, H)); td = ImageDraw.Draw(tmp)
        e = emoji("🎓", 220); tmp.alpha_composite(e, (W // 2 - e.width // 2, 200 + int(8 * math.sin(t * 2))))
        tf = fit_font(td, s["title"], "Inter-Black.otf", 150, 1700)
        td.text((W // 2, 560), s["title"], font=tf, fill=WHITE, anchor="mm", stroke_width=5, stroke_fill=(5, 8, 22))
        td.text((W // 2, 690), s["sub"], font=fit_font(td, s["sub"], "Inter-SemiBold.otf", 52, 1600), fill=GOLD, anchor="mm")
        if s["kind"] == "intro":
            for k2, (lab, col) in enumerate([("FULLY FUNDED", RED), ("STEP BY STEP", (40, 120, 220)), ("ALL COUNTRIES", (30, 150, 90))]):
                x = W // 2 + (k2 - 1) * 400; td.rounded_rectangle((x - 180, 780, x + 180, 850), radius=35, fill=col)
                td.text((x, 815), lab, font=F("Inter-ExtraBold.otf", 32), fill=WHITE, anchor="mm")
        tmp.putalpha(tmp.getchannel("A").point(lambda v: int(v * a)))
        im.alpha_composite(tmp)
    chrome(im, si, t)
    if slt < 0.12 and si > 0:
        im.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(60 * (1 - slt / 0.12)))))
    return im.convert("RGB")

if __name__ == "__main__":
    if sys.argv[1] == "frames":
        for s in sys.argv[2:]: frame(int(float(s) * FPS)).save(f"lf_{s}.png")
        sys.exit()
    part, nparts = int(sys.argv[1]), int(sys.argv[2])
    a, b = NF * part // nparts, NF * (part + 1) // nparts
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", f"part{part}_tmp.mp4"], stdin=subprocess.PIPE)
    for fi in range(a, b): p.stdin.write(frame(fi).tobytes())
    p.stdin.close(); p.wait()
    import os; os.replace(f"part{part}_tmp.mp4", f"part{part}.mp4"); print("part", part, "done", b - a)
