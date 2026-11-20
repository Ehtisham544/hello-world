import json, math, sys, subprocess, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from beats import BEATS, HEADER

W, H, FPS = 1080, 1920, 30
GAP = 0.15
durs = json.load(open("durs.json"))
starts, t = [], 0.0
for d in durs:
    starts.append(t); t += d + GAP
TOTAL = t + 0.4
NF = int(TOTAL * FPS)

FD = "/usr/share/fonts/opentype/inter/"
def F(n, s): return ImageFont.truetype(FD + n, s)
EMO = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
NAVY = (10, 16, 40); RED = (230, 45, 30); GOLD = (255, 206, 60); WHITE = (255, 255, 255)

def ease_back(x):
    x = min(max(x, 0), 1); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def ease_out(x):
    x = min(max(x, 0), 1); return 1 - (1 - x) ** 3

# --- background: big gradient with glowing blobs, panned over time
def make_bg():
    bw, bh = 1500, 2500
    im = Image.new("RGB", (bw, bh), NAVY)
    g = Image.new("L", (bw, bh), 0); d = ImageDraw.Draw(g)
    d.ellipse((800, 0, 1700, 900), fill=200)
    d.ellipse((-300, 1500, 700, 2500), fill=170)
    d.ellipse((500, 900, 1200, 1500), fill=70)
    g = g.filter(ImageFilter.GaussianBlur(200))
    im = Image.composite(Image.new("RGB", (bw, bh), (150, 20, 40)), im, g)
    g2 = Image.new("L", (bw, bh), 0); d2 = ImageDraw.Draw(g2)
    d2.ellipse((0, 200, 600, 800), fill=120)
    g2 = g2.filter(ImageFilter.GaussianBlur(180))
    im = Image.composite(Image.new("RGB", (bw, bh), (40, 50, 140)), im, g2)
    return im
BG = make_bg()
rng = np.random.default_rng(3)
PARTS = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(2, 6), rng.uniform(20, 60)) for _ in range(40)]

def emoji_img(e, size):
    im = Image.new("RGBA", (160, 150)); ImageDraw.Draw(im).text((10, 5), e, font=EMO, embedded_color=True)
    im = im.crop(im.getbbox())
    r = size / max(im.size)
    return im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
EMOJI = [emoji_img(b["emo"], 300) for b in BEATS]

def caption_layer(text):
    lines = text.split("\n")
    plain = [l.replace("*", "") for l in lines]
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    s = 132
    while True:
        fo = F("Inter-Black.otf", s)
        if max(tmp.textlength(p, font=fo) for p in plain) <= 960 or s < 60: break
        s -= 4
    lh = int(s * 1.18)
    layer = Image.new("RGBA", (W, lh * len(lines) + 40))
    d = ImageDraw.Draw(layer)
    for k, l in enumerate(lines):
        parts = re.split(r"(\*[^*]+\*)", l)
        tw = sum(d.textlength(p.strip("*"), font=fo) for p in parts if p)
        x = (W - tw) / 2; y = 10 + k * lh
        for p in parts:
            if not p: continue
            hi = p.startswith("*"); p = p.strip("*")
            d.text((x, y), p, font=fo, fill=GOLD if hi else WHITE, stroke_width=7, stroke_fill=(5, 8, 22))
            x += d.textlength(p, font=fo)
    return layer
CAPS = {i: caption_layer(b["cap"]) for i, b in enumerate(BEATS) if "count" not in b}

HF = F("Inter-ExtraBold.otf", 34)
def header(im):
    d = ImageDraw.Draw(im)
    d.text((W / 2, 100), "SCHOLARSHIPS IN CHINA", font=F("Inter-Black.otf", 40), fill=GOLD, anchor="mm")
    t = HEADER
    tw = d.textlength(t, font=HF); x0 = (W - tw) / 2 - 34
    d.rounded_rectangle((x0, 150, x0 + tw + 68, 216), radius=33, fill=RED)
    d.text((W / 2, 183), t, font=HF, fill=WHITE, anchor="mm")

def frame(fi):
    t = fi / FPS
    bi = max(i for i, s in enumerate(starts) if s <= t + 1e-6)
    lt = t - starts[bi]; b = BEATS[bi]
    ox = int(100 + 100 * math.sin(t * 0.35)); oy = int(150 + 150 * math.cos(t * 0.27))
    im = BG.crop((ox, oy, ox + W, oy + H)).convert("RGBA")
    d = ImageDraw.Draw(im)
    for (x, y, r, sp) in PARTS:
        yy = (y - t * sp) % H
        d.ellipse((x - r, yy - r, x + r, yy + r), fill=(255, 255, 255, 40))
    # progress bar
    d.rectangle((0, 0, W, 16), fill=(255, 255, 255, 40))
    d.rectangle((0, 0, int(W * t / TOTAL), 16), fill=GOLD)
    header(im)
    # emoji pop + bob
    e = EMOJI[bi]; sc = 0.3 + 0.7 * ease_back(lt / 0.32)
    ew, eh = max(1, int(e.width * sc)), max(1, int(e.height * sc))
    es = e.resize((ew, eh), Image.BILINEAR)
    bob = int(12 * math.sin(lt * 4)); rot = 8 * math.sin(lt * 3) * (1 - ease_out(lt / 1.5))
    if abs(rot) > 0.5: es = es.rotate(rot, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(es, (int(W / 2 - es.width / 2), int(600 - es.height / 2 + bob)))
    # caption
    if "count" in b:
        n = int(b["count"] * ease_out((lt - 0.9) / 1.3))
        cap = caption_layer(b["cap"].replace("{n}", f"{n:,}"))
    else:
        cap = CAPS[bi]
    cs = 0.82 + 0.18 * ease_back(lt / 0.22)
    cw, ch = int(cap.width * cs), int(cap.height * cs)
    c2 = cap.resize((cw, ch), Image.BILINEAR)
    a = min(1, lt / 0.08)
    if a < 1:
        c2.putalpha(c2.getchannel("A").point(lambda v: int(v * a)))
    slide = int(40 * (1 - ease_out(lt / 0.25)))
    im.alpha_composite(c2, (int(W / 2 - cw / 2), int(880 + slide)))
    # hook flash
    if bi == 0 and lt < 0.25:
        fl = Image.new("RGBA", (W, H), (255, 255, 255, int(200 * (1 - lt / 0.25))))
        im.alpha_composite(fl)
    elif lt < 0.1:
        fl = Image.new("RGBA", (W, H), (255, 255, 255, int(50 * (1 - lt / 0.1))))
        im.alpha_composite(fl)
    return im.convert("RGB")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for s in sys.argv[1:]:
            frame(int(float(s) * FPS)).save(f"f_{s}.png")
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "v_tmp.mp4"], stdin=subprocess.PIPE)
    for fi in range(NF):
        p.stdin.write(frame(fi).tobytes())
    p.stdin.close(); p.wait(); print("frames", NF, "dur", TOTAL)
