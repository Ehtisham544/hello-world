import json, numpy as np, soundfile as sf
from scipy.signal import resample_poly, butter, lfilter
SR=48000; GAP=0.15
d=json.load(open("durs.json")); st=[]; t=0
for x in d: st.append(t); t+=x+GAP
T=t+0.4; N=int(T*SR); mix=np.zeros(N); voice=np.zeros(N); rng=np.random.default_rng(1)
def add(buf,sig,at,g=1.0):
    i=int(at*SR); j=min(N,i+len(sig))
    if j<=i: return
    buf[i:j]+=g*sig[:j-i]
for i,s in enumerate(st):
    a,_=sf.read(f"b{i}.wav"); a=resample_poly(a,2,1); add(voice,a,s)
# whoosh
def whoosh(dur=0.35):
    n=int(dur*SR); x=rng.standard_normal(n); out=np.zeros(n); seg=n//20
    for k in range(20):
        f=300+k*400; b,a=butter(2,[f/(SR/2),min(0.99,(f+800)/(SR/2))],'band'); out[k*seg:(k+1)*seg]=lfilter(b,a,x[k*seg:(k+1)*seg])
    env=np.sin(np.linspace(0,np.pi,n))**2; return out*env/np.abs(out).max()
def pop():
    n=int(0.12*SR); tt=np.arange(n)/SR; f=900*np.exp(-tt*25)+300
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*35)
def ching():
    n=int(0.9*SR); tt=np.arange(n)/SR; s=np.zeros(n)
    for f,dl in [(2093,0),(2637,0.08),(3136,0.16)]:
        m=tt>=dl; s[m]+=np.sin(2*np.pi*f*(tt[m]-dl))*np.exp(-(tt[m]-dl)*6)
    return s/np.abs(s).max()
W,P,C=whoosh(),pop(),ching()
for i,s in enumerate(st):
    add(mix,W,max(0,s-0.12),0.18); add(mix,P,s+0.05,0.25)
from beats import BEATS
for i,b in enumerate(BEATS):
    if "count" in b: add(mix,C,st[i]+2.2,0.3)
add(mix,whoosh(0.6),0,0.35)
# music bed: 100 bpm, Am F C G
bpm=100; beat=60/bpm; tt=np.arange(N)/SR
chords=[[220,261.6,329.6],[174.6,220,261.6],[261.6,329.6,392],[196,246.9,293.7]]
music=np.zeros(N)
bar=4*beat
for k in range(int(T/bar)+1):
    ch=chords[k%4]; i0=int(k*bar*SR); n=min(N-i0,int(bar*SR))
    if n<=0: break
    x=np.arange(n)/SR; env=np.minimum(1,x/0.3)*np.minimum(1,(bar-x)/0.3)
    pad=sum(np.sin(2*np.pi*f*x)+0.3*np.sin(2*np.pi*2*f*x+0.5) for f in ch)*env*0.12
    bass=np.sin(2*np.pi*ch[0]/2*x)*0.35*env
    music[i0:i0+n]+=pad+bass
for k in range(int(T/beat)+1):
    i0=int(k*beat*SR); n=int(0.25*SR); x=np.arange(n)/SR
    kick=np.sin(2*np.pi*(50+90*np.exp(-x*30))*x)*np.exp(-x*12)
    add(music,kick,k*beat,0.9)
    h=rng.standard_normal(int(0.05*SR))*np.exp(-np.arange(int(0.05*SR))/SR*80)
    b,a=butter(2,7000/(SR/2),'high'); h=lfilter(b,a,h)
    add(music,h,k*beat+beat/2,0.25)
music/=np.abs(music).max()
# duck music under voice
venv=np.convolve(np.abs(voice),np.ones(2400)/2400,'same'); duck=1-0.55*np.clip(venv/0.05,0,1)
out=voice*1.0+mix+music*0.16*duck
fade=int(0.6*SR); out[-fade:]*=np.linspace(1,0,fade)
out/=max(1,np.abs(out).max()/0.95)
sf.write("mix.wav",np.stack([out,out],1),SR); print(T)
