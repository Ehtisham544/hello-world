"""Real-footage backgrounds for SIC videos.
Library: media/index.json + media/clips/<id>_<p|l>.mp4 (p = portrait 720x1280, l = landscape 1280x720) + media/images/*.jpg.
Tags: students, study, campus, city, china, graduation, documents, money.
"""
import json, os, re, subprocess, hashlib
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
IDX = json.load(open(os.path.join(ROOT, "index.json")))
TAGS = sorted({c["tag"] for c in IDX["clips"]} | {i["tag"] for i in IDX["images"]})

RULES = [
    ("graduation", r"follow|subscribe|save this|send it|good luck|win|winner|won|congrat|graduat|accepted|success"),
    ("money", r"stipend|yuan|¥|cny|allowance|pay|paid|salary|money|cost|budget|\$|cash|bank"),
    ("exam", r"exam|test|ielts|toefl|hsk|gpa|csca|hard|difficult|mistake|reject|avoid|wrong"),
    ("documents", r"document|passport|transcript|certificate|form|letter|notar|checklist|scan|upload|recommendation|police|physical exam|study plan|proposal|\bcv\b|sign"),
    ("campus", r"universit|campus|college|dorm|tuition|degree|institute|insurance"),
    ("study", r"apply|application|portal|online|email|professor|research|phd|p h d|master|postdoc|fellow|step"),
    ("city", r"beijing|shanghai|city|cities|shenzhen|guangzhou|chengdu|wuhan|hangzhou|nanjing|province|provincial"),
    ("china", r"china|chinese|visa|arriv|life|culture|embassy|silk road|belt"),
    ("students", r"student|international|any country|world|who can|eligib|age|under"),
]

def auto_tag(text, fallback="students"):
    t = text.lower()
    for tag, rx in RULES:
        if tag in TAGS and re.search(rx, t):
            return tag
    return fallback

def _sources(tag):
    s = [("clip", c["id"]) for c in IDX["clips"] if c["tag"] == tag] + [("img", i["id"]) for i in IDX["images"] if i["tag"] == tag]
    return s or [("clip", c["id"]) for c in IDX["clips"]]

def pick(tag, key):
    """Deterministic pick of a source for a tag; key varies the choice (e.g. beat index + topic)."""
    s = _sources(tag)
    h = int(hashlib.md5(f"{tag}:{key}".encode()).hexdigest(), 16)
    return s[h % len(s)]

class ClipSrc:
    def __init__(self, cid, W, H, fps=30):
        o = "p" if H > W else "l"
        self.path = os.path.join(ROOT, "clips", f"{cid}_{o}.mp4"); self.W, self.H, self.fps = W, H, fps
        self.dur = next(c["dur"] for c in IDX["clips"] if c["id"] == cid)
        self.p = None; self.next = None
    def _open(self, k):
        if self.p: self.p.kill()
        ss = (k / self.fps) % max(self.dur - 0.1, 0.5)
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-stream_loop", "-1", "-ss", f"{ss:.3f}", "-i", self.path,
                                   "-vf", f"scale={self.W}:{self.H},fps={self.fps}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.next = k
    def frame(self, k):
        if self.p is None or k < self.next or k > self.next + 60: self._open(k)
        n = self.W * self.H * 3
        while self.next <= k:
            buf = self.p.stdout.read(n); self.next += 1
            if len(buf) < n: self._open(k); buf = self.p.stdout.read(n); self.next = k + 1
        return Image.frombuffer("RGB", (self.W, self.H), buf)
    def close(self):
        if self.p: self.p.kill(); self.p = None

class ImgSrc:
    def __init__(self, iid, W, H, fps=30):
        im = Image.open(os.path.join(ROOT, "images", iid)).convert("RGB")
        r = max(W / im.width, H / im.height) * 1.15
        self.im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.BILINEAR)
        self.W, self.H, self.fps = W, H, fps
    def frame(self, k):
        t = k / self.fps; z = 1.0 + 0.012 * t  # slow zoom-in (Ken Burns)
        cw, ch = int(self.im.width / 1.15 / z * 1.0), int(self.im.height / 1.15 / z)
        cw, ch = min(cw, self.im.width), min(ch, self.im.height)
        x = (self.im.width - cw) // 2 + int(10 * t) % max(1, (self.im.width - cw) // 2 + 1); y = (self.im.height - ch) // 2
        return self.im.crop((x, y, x + cw, y + ch)).resize((self.W, self.H), Image.BILINEAR)
    def close(self): pass

_open = {}
def frame_for(kind_id, local_k, W, H, slot):
    """Return the frame of a source; one open source per 'slot' (e.g. beat group / slide)."""
    key = (slot, kind_id)
    if key not in _open:
        for k2 in [k for k in _open if k[0] != slot]:
            _open.pop(k2).close()
        kind, sid = kind_id
        _open[key] = ClipSrc(sid, W, H) if kind == "clip" else ImgSrc(sid, W, H)
    return _open[key].frame(local_k)

_shade = {}
def shade(W, H, strength=120):
    """Dark overlay with a stronger bottom/top gradient so text stays readable."""
    k = (W, H, strength)
    if k not in _shade:
        a = np.full((H, W), strength, np.float32)
        y = np.linspace(0, 1, H)[:, None]
        a += 70 * np.clip((y - 0.55) / 0.45, 0, 1) + 50 * np.clip((0.18 - y) / 0.18, 0, 1)
        rgba = np.zeros((H, W, 4), np.uint8); rgba[..., :3] = (6, 10, 28); rgba[..., 3] = np.clip(a, 0, 230).astype(np.uint8)
        _shade[k] = Image.fromarray(rgba, "RGBA")
    return _shade[k]
