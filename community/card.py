# Usage: python3 card.py out.png "TAG" "Big title line\nsecond line" "small line 1\nsmall line 2" "🎓"
import sys, re
from PIL import Image, ImageDraw, ImageFilter, ImageFont
FD="/usr/share/fonts/opentype/inter/"
def F(n,s): return ImageFont.truetype(FD+n,s)
EM=ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",109)
out,tag,title,sub,emo=sys.argv[1:6]; title=title.replace("\\n","\n"); sub=sub.replace("\\n","\n")
S=1080; GOLD=(255,206,60); RED=(230,45,30)
im=Image.new("RGB",(S,S),(10,16,44))
for col,box,a in [((150,22,40),(500,-300,1500,600),200),((40,60,170),(-400,600,500,1500),170)]:
    g=Image.new("L",(S,S)); ImageDraw.Draw(g).ellipse(box,fill=a)
    im=Image.composite(Image.new("RGB",(S,S),col),im,g.filter(ImageFilter.GaussianBlur(200)))
im=im.convert("RGBA"); d=ImageDraw.Draw(im)
d.text((S//2,90),"SCHOLARSHIPS IN CHINA",font=F("Inter-Black.otf",40),fill=GOLD,anchor="mm")
tf=F("Inter-ExtraBold.otf",40); tw=d.textlength(tag,font=tf)
d.rounded_rectangle((S//2-tw//2-36,140,S//2+tw//2+36,210),radius=35,fill=RED); d.text((S//2,175),tag,font=tf,fill=(255,255,255),anchor="mm")
e=Image.new("RGBA",(200,150)); ImageDraw.Draw(e).text((10,5),emo,font=EM,embedded_color=True); e=e.crop(e.getbbox()); e=e.resize((220,int(220*e.height/e.width)))
im.alpha_composite(e,(S//2-e.width//2,250))
lines=title.split("\n"); s=110
while s>50 and max(d.textlength(l.replace("*",""),font=F("Inter-Black.otf",s)) for l in lines)>960: s-=4
fo=F("Inter-Black.otf",s); y=520
for l in lines:
    parts=[p for p in re.split(r"(\*[^*]+\*)",l) if p]; tw=sum(d.textlength(p.strip("*"),font=fo) for p in parts); x=(S-tw)/2
    for p in parts:
        h=p.startswith("*"); p=p.strip("*"); d.text((x,y),p,font=fo,fill=GOLD if h else (255,255,255),stroke_width=5,stroke_fill=(5,8,22)); x+=d.textlength(p,font=fo)
    y+=int(s*1.15)
y+=30; sf=F("Inter-SemiBold.otf",44)
for l in sub.split("\n"): d.text((S//2,y),l,font=sf,fill=(210,218,240),anchor="mt"); y+=60
d.text((S//2,1030),"@scholarshipsinchina-sic",font=F("Inter-Bold.otf",32),fill=(255,255,255),anchor="mm")
im.convert("RGB").save(out)
