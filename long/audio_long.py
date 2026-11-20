import json, numpy as np, soundfile as sf
from scipy.signal import resample_poly, butter, lfilter
import render_long as R
SR=48000; N=int(R.TOTAL*SR); voice=np.zeros(N); fx=np.zeros(N); rng=np.random.default_rng(2)
def add(buf,sig,at,g=1.0):
    i=int(at*SR); j=min(N,i+len(sig)); buf[i:j]+=g*sig[:j-i]
for si,ii,st,d in R.TL:
    a,_=sf.read(f"a_{si}_{ii}.wav"); add(voice,resample_poly(a,2,1),st+0.1)
def whoosh(dur=0.45):
    n=int(dur*SR); x=rng.standard_normal(n); out=np.zeros(n); seg=n//20
    for k in range(20):
        f=300+k*350; b,a=butter(2,[f/(SR/2),min(0.99,(f+800)/(SR/2))],'band'); out[k*seg:(k+1)*seg]=lfilter(b,a,x[k*seg:(k+1)*seg])
    return out*np.sin(np.linspace(0,np.pi,n))**2/np.abs(out).max()
def pop():
    n=int(0.1*SR); tt=np.arange(n)/SR; f=800*np.exp(-tt*25)+300
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*40)
Wh,P=whoosh(),pop()
for si,st in R.SLIDE_START.items(): add(fx,Wh,max(0,st-0.15),0.12)
for si,ii,st,d in R.TL:
    if R.SLIDES[si]["kind"]=="list": add(fx,P,st,0.10)
# calm music bed 84 bpm
bpm=84; beat=60/bpm; T=R.TOTAL; music=np.zeros(N); bar=4*beat
chords=[[220,261.6,329.6],[174.6,220,261.6],[261.6,329.6,392],[196,246.9,293.7]]
for k in range(int(T/bar)+1):
    ch=chords[k%4]; i0=int(k*bar*SR); n=min(N-i0,int(bar*SR))
    if n<=0: break
    x=np.arange(n)/SR; env=np.minimum(1,x/0.5)*np.minimum(1,(bar-x)/0.5)
    music[i0:i0+n]+=sum(np.sin(2*np.pi*f*x)+0.25*np.sin(2*np.pi*2*f*x) for f in ch)*env*0.12+np.sin(2*np.pi*ch[0]/2*x)*0.3*env
    for b4 in range(4):
        j=int((k*bar+b4*beat)*SR); m=int(0.2*SR); xx=np.arange(m)/SR
        if j+m<N: music[j:j+m]+=np.sin(2*np.pi*(50+80*np.exp(-xx*30))*xx)*np.exp(-xx*14)*(0.7 if b4%2==0 else 0.35)
music/=np.abs(music).max()
venv=np.convolve(np.abs(voice),np.ones(4800)/4800,'same'); duck=1-0.6*np.clip(venv/0.04,0,1)
out=voice+fx+music*0.09*duck
f=int(1.0*SR); out[-f:]*=np.linspace(1,0,f); out[:int(0.5*SR)]*=np.linspace(0,1,int(0.5*SR))
out/=max(1,np.abs(out).max()/0.95)
sf.write("mix_long.wav",np.stack([out,out],1),SR); print("audio",R.TOTAL)
