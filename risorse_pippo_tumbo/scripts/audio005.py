"""Test 005 - audio: voce + musichetta sintetica + effetti. Esce audio/t005.wav (46.0 s)"""
import numpy as np, subprocess, wave
SR=44100; DUR=46.0; N=int(DUR*SR); rng=np.random.default_rng(5)
t=np.arange(N)/SR
def env(a,b,fi=0.1,fo=0.3):
    e=np.zeros(N); i0,i1=int(a*SR),min(N,int(b*SR)); n=i1-i0
    x=np.ones(n); fi_n=min(n//2,int(fi*SR)); fo_n=min(n//2,int(fo*SR))
    x[:fi_n]=np.linspace(0,1,fi_n); x[n-fo_n:]=np.linspace(1,0,fo_n); e[i0:i1]=x; return e
def lp(x,k): return np.convolve(x,np.ones(k)/k,mode='same')
def put(buf,t0,s):
    i0=int(t0*SR); n=min(len(s),N-i0)
    if n>0: buf[i0:i0+n]+=s[:n]
def tone(f0,f1,dur,dec=6.0,harm=0.3):
    n=int(dur*SR); tt=np.arange(n)/SR; f=np.linspace(f0,f1,n); ph=2*np.pi*np.cumsum(f)/SR
    return (np.sin(ph)+harm*np.sin(2*ph))*np.exp(-tt*dec)
def burst(dur,k=8,dec=10.0):
    n=int(dur*SR); tt=np.arange(n)/SR; return lp(rng.normal(0,1,n),k)*np.exp(-tt*dec)
def hiss(dur,k=3,dec=10.0):
    n=int(dur*SR); tt=np.arange(n)/SR; x=rng.normal(0,1,n); return (x-lp(x,k))*np.exp(-tt*dec)
# voce
subprocess.run(['/usr/local/bin/ffmpeg','-y','-loglevel','error','-i','audio/voce_t005.mp3','-ar',str(SR),'-ac','1','audio/voce44_t005.wav'],check=True)
w=wave.open('audio/voce44_t005.wav'); v=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(float)/32768; v=np.pad(v,(0,max(0,N-len(v))))[:N]
# musica: pizzicato allegro, 112 bpm, F C G Am
bpm=112; beat=60/bpm; chords=[(174.61,220.0,261.63),(130.81,164.81,196.0),(196.0,246.94,293.66),(220.0,261.63,329.63)]
m=np.zeros(N)
def pluck(f,t0,dur=0.5,amp=0.5):
    n=int(dur*SR); tt=np.arange(n)/SR; put(m,t0,amp*(np.sin(2*np.pi*f*tt)+0.4*np.sin(4*np.pi*f*tt)+0.2*np.sin(6*np.pi*f*tt))*np.exp(-tt*7))
for bar in range(int(DUR/(beat*4))+1):
    ch=chords[bar%4]
    for b in range(8):
        t0=bar*beat*4+b*beat/2; f=ch[[0,2,1,2,0,2,1,2][b]]*2
        pluck(f,t0,0.4,0.30 if b%2==0 else 0.22)
    pluck(ch[0]/2,bar*beat*4,0.9,0.5); pluck(ch[0]/2,bar*beat*4+2*beat,0.9,0.4); pluck(ch[2]/2,bar*beat*4+3*beat,0.5,0.3)
mus=m/np.abs(m).max()*0.20
mus*=np.interp(t,[0,1,41.6,42.0,44.5,46.0],[0.6,1,1,0.25,0.25,0.0])
fx=np.zeros(N)
# aereo (passaggio iniziale e scena finale)
dr=(np.sign(np.sin(2*np.pi*92*t))*0.5+np.sin(2*np.pi*46*t)); dr=lp(dr,40)*(1+0.5*np.sin(2*np.pi*23*t))
fx+=dr*env(0.0,1.6,0.5,0.6)*0.10+dr*env(31.0,38.4,0.3,1.0)*0.22
# tovaglia: strappo e stoviglie
put(fx,2.80,hiss(0.3,6,9)*0.5)
for k,f in enumerate((2100,2600,3100,2350)): put(fx,2.93+0.05*k,tone(f,f,0.25,14,0.1)*0.18)
# salto, fischio di caduta, tonfo
put(fx,4.45,burst(0.3,40,8)*1.2)
n=int(0.85*SR); tt=np.arange(n)/SR; f=np.linspace(1500,350,n); put(fx,4.9,np.sin(2*np.pi*np.cumsum(f)/SR)*np.minimum(1,tt*8)*0.22)
put(fx,5.75,tone(90,45,0.5,7,0.5)*1.3); put(fx,5.75,burst(0.4,20,9)*1.0)
# matita di Tumbo
for k in range(9): put(fx,7.2+0.13*k,hiss(0.08,2,20)*0.10)
# pop dei pezzi
for tp in (9.8,10.5,11.1,33.9,36.9): put(fx,tp,tone(420,900,0.14,16,0.2)*0.55)
# dondolio
for k in range(5): put(fx,13.3+0.575*k,burst(0.5,60,5)*2.2*np.hanning(int(0.5*SR)))
# toppa che salta e aria che sfoga
put(fx,17.0,tone(300,1200,0.12,10,0.2)*0.5); fx+=(lambda x:(x-lp(x,6)))(rng.normal(0,1,N))*env(17.2,20.3,0.3,0.8)*0.05
# vento, schianto nell'albero
fx+=lp(rng.normal(0,1,N),50)*3*(1+0.5*np.sin(2*np.pi*0.9*t))*env(20.6,23.2,0.5,0.1)*0.20
put(fx,23.2,hiss(0.7,5,5)*0.55); put(fx,23.2,tone(120,70,0.3,10,0.4)*0.8)
# ala che si gonfia, aria nelle celle
for tp in (26.3,38.2): put(fx,tp,tone(140,70,0.45,7,0.4)*0.9); put(fx,tp,burst(0.5,30,6)*1.5)
fx+=lp(rng.normal(0,1,N),30)*3*env(26.8,27.95,0.3,0.3)*0.10
for tp in (28.15,28.8): put(fx,tp,burst(0.4,45,6)*1.6*np.hanning(int(0.4*SR)))
# atterraggi morbidi
for tp in (30.3,41.2): put(fx,tp,tone(110,80,0.2,14,0.3)*0.5)
# lancio: vento forte, poi virata
fx+=lp(rng.normal(0,1,N),18)*3*env(37.55,38.25,0.1,0.15)*0.30
fx+=lp(rng.normal(0,1,N),45)*3*env(39.15,40.4,0.3,0.4)*0.14
# "uà uà" sul giardino del vicino
def wah(f,dur):
    n=int(dur*SR); tt=np.arange(n)/SR; s=np.zeros(n)
    for h in range(1,7): s+=np.sin(2*np.pi*f*h*(1-0.03*tt/dur)*tt)/h
    return lp(s,14)*np.minimum(1,tt*30)*np.minimum(1,(dur-tt)*12)
put(fx,42.0,wah(233,0.38)*0.16); put(fx,42.45,wah(220,0.38)*0.16); put(fx,42.9,wah(196,0.75)*0.17)
# pallone palleggiato dal vicino
for tp in (43.98,44.61,45.24,45.87): put(fx,tp,tone(170,120,0.12,30,0.3)*0.5)
fx=np.tanh(fx*1.1)*0.45
mix=v*1.0+mus+fx
mix=np.clip(mix/max(1,np.abs(mix).max()/0.95),-1,1)
mix[-int(0.15*SR):]*=np.linspace(1,0,int(0.15*SR))
st=np.stack([mix,mix],1); pcm=(st*32767).astype(np.int16)
with wave.open('audio/t005.wav','wb') as o:
    o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes(pcm.tobytes())
print('audio ok', np.abs(v).max(), np.abs(mus).max(), np.abs(fx).max())
