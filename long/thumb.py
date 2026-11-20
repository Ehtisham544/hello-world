import sys
from PIL import Image, ImageDraw, ImageFilter
import render_long as R
from script import THUMB
W,H=1280,720
bg=R.BGS[0].crop((200,150,200+1920,150+1080)).resize((W,H)).convert("RGBA")
bg.alpha_composite(Image.new("RGBA",(W,H),(0,0,0,60))); d=ImageDraw.Draw(bg); F=R.F
tag=THUMB.get("tag","FULLY FUNDED"); tf=F("Inter-Black.otf",44); tw=d.textlength(tag,font=tf)
d.rounded_rectangle((50,50,50+tw+80,125),radius=38,fill=R.RED); d.text((90,88),tag,font=tf,fill=(255,255,255),anchor="lm")
big=THUMB.get("big",""); bf=R.fit_font(d,big,"Inter-Black.otf",170,830)
d.text((50,160),big,font=bf,fill=R.GOLD,stroke_width=8,stroke_fill=(5,8,22))
for k,key in enumerate(("line1","line2")):
    txt=THUMB.get(key,"");
    if txt: d.text((50,360+k*130),txt,font=R.fit_font(d,txt,"Inter-Black.otf",104,830),fill=(255,255,255),stroke_width=7,stroke_fill=(5,8,22))
g=Image.new("RGBA",(W,H)); ImageDraw.Draw(g).ellipse((880,150,1260,530),fill=(255,206,60,120)); bg.alpha_composite(g.filter(ImageFilter.GaussianBlur(50)))
e=R.emoji(THUMB.get("emo","🎓"),300); bg.alpha_composite(e,(1070-e.width//2,330-e.height//2))
f=R.emoji("🇨🇳",130); bg.alpha_composite(f,(1150,520))
lg=Image.open("../brand/SIC_profile_800.png").resize((120,120)); m=Image.new("L",(120,120)); ImageDraw.Draw(m).ellipse((0,0,120,120),fill=255); bg.paste(lg,(1110,40),m)
bg.convert("RGB").save(sys.argv[1],quality=90)
