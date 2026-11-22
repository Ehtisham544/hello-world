import math, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFilter
import render2 as R
W,H,FPS=R.W,R.H,R.FPS
rng=np.random.default_rng(11)
def grad(top,bot,w=W,h=H):
    a=np.linspace(0,1,h)[:,None,None]; g=(np.array(top)*(1-a)+np.array(bot)*a).astype(np.uint8)
    return Image.fromarray(np.repeat(g,w,1),"RGB")
def glow(im,box,col,blur):
    l=Image.new("RGBA",im.size); ImageDraw.Draw(l).ellipse(box,fill=col)
    return Image.alpha_composite(im,l.filter(ImageFilter.GaussianBlur(blur)))
# ---------- MAP (static base + animated arcs)
MAPW=W+120
def map_base():
    im=grad((4,22,52),(8,52,84),MAPW,H).convert("RGBA")
    im=glow(im,(500,500,1200,1100),(0,160,255,60),160)
    m=Image.new("L",(MAPW,H)); md=ImageDraw.Draw(m)
    for b in [(120,620,430,930),(250,930,430,1300),(500,560,700,760),(500,760,730,1150),(700,540,1080,860),(880,1150,1050,1290)]: md.ellipse(b,fill=255)
    m=np.array(m); d=ImageDraw.Draw(im)
    for y in range(480,1400,22):
        for x in range(40,MAPW-40,22):
            if m[y,x]>0: d.ellipse((x-5,y-5,x+5,y+5),fill=(90,220,255,210))
            else: d.ellipse((x-3,y-3,x+3,y+3),fill=(255,255,255,25))
    return im
MAP=map_base(); CHINA=(930,700)
SRCS=[(230,760),(330,1130),(590,640),(620,980),(960,1220),(150,880)]
def map_frame(t):
    ox=int(60+60*math.sin(t*0.3)); im=MAP.crop((ox,0,ox+W,H)).copy(); d=ImageDraw.Draw(im)
    cx,cy=CHINA[0]-ox,CHINA[1]
    for k,(x,y) in enumerate(SRCS):
        x-=ox; ph=((t*0.6+k*0.37)%1.4)/1.0; p=min(ph,1)
        pts=[(x+(cx-x)*s, y+(cy-y)*s-180*math.sin(math.pi*s)) for s in np.linspace(0,p,30)]
        if len(pts)>1: d.line(pts,fill=(255,206,60,210),width=5)
        d.ellipse((x-10,y-10,x+10,y+10),fill=(255,206,60))
        if p<1: px,py=pts[-1]; d.ellipse((px-12,py-12,px+12,py+12),fill=(255,255,255))
    r=18+6*math.sin(t*6)
    im=glow(im,(cx-70,cy-70,cx+70,cy+70),(230,45,30,140),30); d=ImageDraw.Draw(im)
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(230,45,30))
    return im
# ---------- CHINA NIGHT CITY
def city_base():
    im=grad((14,10,44),(140,30,40)).convert("RGBA")
    im=glow(im,(700,230,1000,530),(255,220,170,160),60)
    d=ImageDraw.Draw(im); d.ellipse((760,290,940,470),fill=(255,236,200))
    stars=[(rng.integers(0,W),rng.integers(0,900),rng.random()) for _ in range(70)]
    x=0; wins=[]
    while x<W:
        w=int(rng.integers(70,150)); h=int(rng.integers(300,760))
        d.rectangle((x,H-h,x+w,H),fill=(10,8,26,255))
        for yy in range(H-h+24,H-20,42):
            for xx in range(x+12,x+w-14,28):
                if rng.random()<0.4: wins.append((xx,yy,rng.random()))
        x+=w+int(rng.integers(0,16))
    cx,base=270,H-700
    for k in range(5):
        ww=250-k*40; y=base-k*90
        d.polygon([(cx-ww,y),(cx+ww,y),(cx+ww-45,y-55),(cx-ww+45,y-55)],fill=(10,8,26,255))
        d.rectangle((cx-ww+60,y,cx+ww-60,y+40),fill=(10,8,26,255))
    d.polygon([(cx-20,base-450),(cx+20,base-450),(cx,base-540)],fill=(10,8,26,255))
    return im,stars,wins
CITY,STARS,WINS=city_base()
LANTERNS=[(130,1180,0),(890,1060,1.3),(990,1420,2.1),(70,1560,0.7),(560,1300,2.8)]
def lantern_layer(t):
    l=Image.new("RGBA",(W,H)); d=ImageDraw.Draw(l)
    for (x,y,p) in LANTERNS:
        y2=y+12*math.sin(t*1.5+p); ang=0.12*math.sin(t*2+p); lx=x+math.sin(ang)*60
        d.ellipse((lx-110,y2-110,lx+110,y2+110),fill=(255,90,40,90))
    l=l.filter(ImageFilter.GaussianBlur(45)); d=ImageDraw.Draw(l)
    for (x,y,p) in LANTERNS:
        y2=y+12*math.sin(t*1.5+p); ang=0.12*math.sin(t*2+p); lx=x+math.sin(ang)*60
        d.line((x,y-200,lx,y2-60),fill=(60,40,40,255),width=3)
        d.rectangle((lx-28,y2-72,lx+28,y2-58),fill=(255,200,60))
        d.ellipse((lx-50,y2-62,lx+50,y2+62),fill=(225,40,30))
        d.ellipse((lx-24,y2-40,lx+24,y2+40),fill=(255,110,60,160))
        d.rectangle((lx-28,y2+58,lx+28,y2+70),fill=(255,200,60))
        for k in range(-2,3): d.line((lx+k*8,y2+70,lx+k*8,y2+110),fill=(255,200,60),width=3)
    return l
def city_frame(t):
    im=CITY.copy(); d=ImageDraw.Draw(im)
    for (x,y,p) in STARS:
        a=int(120+120*math.sin(t*3+p*10)); d.ellipse((x-2,y-2,x+2,y+2),fill=(255,255,255,max(0,a)))
    for (x,y,p) in WINS:
        on=math.sin(t*0.8+p*40)>-0.6
        d.rectangle((x,y,x+13,y+19),fill=(255,205,95,200) if on else (60,50,40,200))
    im.alpha_composite(lantern_layer(t))
    sc=1.04+0.02*math.sin(t*0.4); w,h=int(W*sc),int(H*sc)
    return im.resize((w,h),Image.BILINEAR).crop(((w-W)//2,(h-H)//2,(w-W)//2+W,(h-H)//2+H))
# ---------- CAMPUS with falling caps
def campus_base():
    im=grad((24,12,70),(70,20,90)).convert("RGBA")
    im=glow(im,(200,400,900,1000),(160,80,255,90),200)
    d=ImageDraw.Draw(im); C=(12,6,30,255); by=H-260
    d.rectangle((0,by,W,H),fill=C)
    # paifang gate
    for x in (180,420,660,900): d.rectangle((x-22,by-560,x+22,by),fill=C)
    d.polygon([(90,by-560),(990,by-560),(1040,by-640),(40,by-640)],fill=C)
    d.rectangle((150,by-600,930,by-560),fill=C)
    d.polygon([(260,by-700),(820,by-700),(870,by-760),(210,by-760)],fill=C)
    d.rectangle((300,by-700,780,by-640),fill=C)
    d.rectangle((330,by-470,750,by-400),fill=(200,40,40,255))
    return im
CAMPUS=campus_base()
CAPS=[(rng.uniform(0,W),rng.uniform(0,H),rng.uniform(60,140),rng.uniform(0,6.28),rng.uniform(35,70)) for _ in range(14)]
CONF=[(rng.uniform(0,W),rng.uniform(0,H),rng.uniform(80,200),rng.integers(0,4)) for _ in range(60)]
CC=[(255,206,60),(230,45,30),(90,220,255),(255,255,255)]
def campus_frame(t):
    im=CAMPUS.copy(); d=ImageDraw.Draw(im)
    for (x,y,sp,c) in CONF:
        yy=(y+t*sp)%H; xx=x+20*math.sin(t*2+y)
        d.rectangle((xx,yy,xx+10,yy+16),fill=CC[c]+(170,))
    for (x,y,sp,ph,s) in CAPS:
        yy=(y+t*sp)%(H+200)-100; xx=x+40*math.sin(t+ph); a=math.sin(t*1.5+ph)*0.35
        top=[(-1,0),(0,-0.45),(1,0),(0,0.45)]
        pts=[(xx+s*(px*math.cos(a)-py*math.sin(a)), yy+s*(px*math.sin(a)+py*math.cos(a))) for px,py in top]
        d.polygon([(xx-s*0.5,yy),(xx+s*0.5,yy),(xx+s*0.45,yy+s*0.45),(xx-s*0.45,yy+s*0.45)],fill=(15,15,25,230))
        d.polygon(pts,fill=(25,25,40,240),outline=(255,206,60,200))
        d.line((xx,yy,xx+s*0.7,yy+s*0.6),fill=(255,206,60,230),width=3)
    return im
# ---------- section schedule
SEC={0:map_frame,1:city_frame,2:campus_frame,3:map_frame}
_n=len(R.BEATS); B1=max(1,round(_n*0.22)); B2=max(B1+1,round(_n*0.5)); B3=max(B2+1,_n-2)
def sec_of(bi): return 0 if bi<B1 else 1 if bi<B2 else 2 if bi<B3 else 3
CUTS=[R.starts[B1],R.starts[B2],R.starts[B3]]
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "media"))
import media as M
# background tag per beat: explicit "bg" in spec, else auto from text
_TAGS = [b.get("bg") or M.auto_tag(b["say"] + " " + b["cap"], fallback=("china" if i % 2 else "students")) for i, b in enumerate(R.BEATS)]
_GROUP = []; g = 0
run = 0
for i in range(len(_TAGS)):
    if i > 0 and (_TAGS[i] != _TAGS[i - 1] or run >= 3): g += 1; run = 0
    _GROUP.append(g); run += 1
_GSTART = {}
for i, gg in enumerate(_GROUP): _GSTART.setdefault(gg, R.starts[i])
_TOPIC = R.HEADER
def bg(t):
    bi = max(i for i, s in enumerate(R.starts) if s <= t + 1e-6)
    gg = _GROUP[bi]; src = M.pick(_TAGS[bi], f"{_TOPIC}:{gg}")
    k = int(round((t - _GSTART[gg]) * FPS))
    im = M.frame_for(src, k, W, H, gg).convert("RGBA")
    im.alpha_composite(M.shade(W, H, R.STYLE['shade']))
    return im
def frame(fi):
    t=fi/FPS; bi=max(i for i,s in enumerate(R.starts) if s<=t+1e-6); lt=t-R.starts[bi]; b=R.BEATS[bi]
    im=bg(t); d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,16),fill=(255,255,255,40)); d.rectangle((0,0,int(W*t/R.TOTAL),16),fill=R.GOLD)
    R.header(im)
    e=R.EMOJI[bi]; sc=0.3+0.7*R.ease_back(lt/0.32)
    es=e.resize((max(1,int(e.width*sc)),max(1,int(e.height*sc))),Image.BILINEAR)
    rot=8*math.sin(lt*3)*(1-R.ease_out(lt/1.5))
    if abs(rot)>0.5: es=es.rotate(rot,resample=Image.BICUBIC,expand=True)
    im.alpha_composite(es,(int(W/2-es.width/2),int(R.STYLE['emo_y']-es.height/2+12*math.sin(lt*4))))
    if "count" in b:
        cap=R.caption_layer(b["cap"].replace("{n}",f"{int(b['count']*R.ease_out((lt-0.9)/1.3)):,}"))
    else: cap=R.CAPS[bi]
    cs=0.82+0.18*R.ease_back(lt/0.22); c2=cap.resize((int(cap.width*cs),int(cap.height*cs)),Image.BILINEAR)
    a=min(1,lt/0.08)
    if a<1: c2.putalpha(c2.getchannel("A").point(lambda v:int(v*a)))
    im.alpha_composite(c2,(int(W/2-c2.width/2),int(R.STYLE['cap_y']+40*(1-R.ease_out(lt/0.25)))))
    if bi==0 and lt<0.25: im.alpha_composite(Image.new("RGBA",(W,H),(255,255,255,int(200*(1-lt/0.25)))))
    elif lt<0.1: im.alpha_composite(Image.new("RGBA",(W,H),(255,255,255,int(50*(1-lt/0.1)))))
    return im.convert("RGB")
if __name__=="__main__":
    import sys
    if len(sys.argv)>1:
        for s in sys.argv[1:]: frame(int(float(s)*FPS)).save(f"g_{s}.png")
        sys.exit()
    p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-crf","18","-preset","veryfast","-pix_fmt","yuv420p","video_only.mp4"],stdin=subprocess.PIPE)
    for fi in range(R.NF): p.stdin.write(frame(fi).tobytes())
    p.stdin.close(); p.wait(); print("ok")
