"""Test 006 - audio: voce + musichetta sintetica + effetti. Esce audio/t006.wav (66.5 s)"""
import numpy as np, subprocess, wave
SR=44100; DUR=66.5; N=int(DUR*SR); rng=np.random.default_rng(6)
t=np.arange(N)/SR
def env(a,b,fi=0.1,fo=0.3):
    e=np.zeros(N); i0,i1=int(a*SR),min(N,int(b*SR)); n=i1-i0
    x=np.ones(n); fi_n=min(n//2,int(fi*SR)); fo_n=min(n//2,int(fo*SR))
    x[:fi_n]=np.linspace(0,1,fi_n); x[n-fo_n:]=np.linspace(1,0,fo_n); e[i0:i1]=x; return e
def lp(x,k): return np.convolve(x,np.ones(k)/k,mode='same')
def put(buf,t0,s):
    i0=int(t0*SR); n=min(len(s),N-i0)
    if n>0 and i0>=0: buf[i0:i0+n]+=s[:n]
def tone(f0,f1,dur,dec=6.0,harm=0.3):
    n=int(dur*SR); tt=np.arange(n)/SR; f=np.linspace(f0,f1,n); ph=2*np.pi*np.cumsum(f)/SR
    return (np.sin(ph)+harm*np.sin(2*ph))*np.exp(-tt*dec)
def burst(dur,k=8,dec=10.0):
    n=int(dur*SR); tt=np.arange(n)/SR; return lp(rng.normal(0,1,n),k)*np.exp(-tt*dec)
def hiss(dur,k=3,dec=10.0):
    n=int(dur*SR); tt=np.arange(n)/SR; x=rng.normal(0,1,n); return (x-lp(x,k))*np.exp(-tt*dec)
subprocess.run(['/usr/local/bin/ffmpeg','-y','-loglevel','error','-i','audio/voce_t006.mp3','-ar',str(SR),'-ac','1','audio/voce44_t006.wav'],check=True)
w=wave.open('audio/voce44_t006.wav'); v=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(float)/32768; v=np.pad(v,(0,max(0,N-len(v))))[:N]
# musica: pizzicato allegro, 118 bpm, Am F C G
bpm=118; beat=60/bpm; chords=[(220.0,261.63,329.63),(174.61,220.0,261.63),(130.81,164.81,196.0),(196.0,246.94,293.66)]
m=np.zeros(N)
def pluck(f,t0,dur=0.5,amp=0.5):
    n=int(dur*SR); tt=np.arange(n)/SR; put(m,t0,amp*(np.sin(2*np.pi*f*tt)+0.4*np.sin(4*np.pi*f*tt)+0.2*np.sin(6*np.pi*f*tt))*np.exp(-tt*7))
for bar in range(int(DUR/(beat*4))+1):
    ch=chords[bar%4]
    for b in range(8):
        t0=bar*beat*4+b*beat/2; f=ch[[0,2,1,2,0,2,1,2][b]]*2
        pluck(f,t0,0.4,0.30 if b%2==0 else 0.22)
    pluck(ch[0]/2,bar*beat*4,0.9,0.5); pluck(ch[0]/2,bar*beat*4+2*beat,0.9,0.4); pluck(ch[2]/2,bar*beat*4+3*beat,0.5,0.3)
mus=m/np.abs(m).max()*0.19
mus*=np.interp(t,[0,1,64.8,65.0,66.0,66.5],[0.6,1,1,0.2,0.2,0.0])
fx=np.zeros(N)
# sferragliare del carrello (rumore metallico modulato)
ratt=(lambda x:(x-lp(x,5)))(rng.normal(0,1,N))*(0.6+0.4*np.sign(np.sin(2*np.pi*23*t)))
for (a,b,g) in ((4.8,5.7,0.10),(7.8,10.25,0.22),(24.1,27.0,0.20),(33.2,35.6,0.16),(35.6,42.6,0.04)): fx+=ratt*env(a,b,0.2,0.05)*g
# fischio in discesa e botta nel cassonetto
n=int(2.2*SR); tt=np.arange(n)/SR; f=np.linspace(500,1500,n); put(fx,8.0,np.sin(2*np.pi*np.cumsum(f)/SR)*np.minimum(1,tt*4)*0.12)
def clang(t0,g=1.0):
    put(fx,t0,tone(95,45,0.5,7,0.5)*1.2*g); put(fx,t0,burst(0.45,12,8)*1.2*g)
    for f in (620,930,1410): put(fx,t0,tone(f,f*0.98,0.6,6,0.1)*0.22*g)
clang(10.25)
for k in range(6): put(fx,11.2+0.25*k,tone(180,120,0.08,30,0.3)*0.35)
put(fx,12.85,tone(300,700,0.14,14,0.2)*0.5)
# Tumbo ride (guaiti a raffica)
for k in range(16):
    tk=15.6+0.24*k+0.03*np.sin(k*2.1); put(fx,tk,tone(820-20*(k%4),560,0.13,10,0.5)*0.22)
# pop dei pezzi
for tp in (22.8,23.5,30.6,31.3,32.0,44.45,45.3,45.9,46.5,52.6,53.3,53.9,55.3): put(fx,tp,tone(420,900,0.14,16,0.2)*0.55)
# frenata: stridio e scintille, poi siepe
sq=np.sin(2*np.pi*np.cumsum(2300+300*np.sin(2*np.pi*7*t))/SR)
fx+=sq*env(24.5,27.0,0.3,0.05)*0.07
put(fx,27.0,hiss(0.9,5,4)*0.6); put(fx,27.0,tone(120,70,0.3,10,0.4)*0.8)
put(fx,28.55,hiss(0.12,3,25)*0.5)
# stridio di gomme in curva
fx+=sq*env(34.35,34.95,0.1,0.15)*0.06+sq*env(59.0,59.5,0.05,0.2)*0.08+sq*env(60.3,61.0,0.1,0.2)*0.09
# a spinta: ruota che cigola, Tumbo ansima, deambulatore
for k in range(14): put(fx,36.1+0.45*k,tone(1700,2100,0.10,18,0.2)*0.10)
for k in range(12): put(fx,36.2+0.5*k,burst(0.22,30,10)*0.9)
for k in range(11): put(fx,38.0+0.22*k,tone(900,700,0.04,60,0.1)*0.22)
# motore del tosaerba
put(fx,44.3,tone(160,90,0.2,12,0.4)*0.8)
def motor(a,b,g,f0=62,rev=0.0):
    f=f0+rev*np.clip((t-a)/(b-a),0,1); ph=2*np.pi*np.cumsum(f)/SR
    s=(np.sign(np.sin(ph))*0.5+np.sin(ph*0.5))*(0.65+0.35*np.sign(np.sin(2*np.pi*13*t)))
    return lp(s,25)*env(a,b,0.15,0.2)*g
fx+=motor(47.4,51.4,0.30,62,25)+motor(58.6,64.85,0.34,58,50)+motor(51.6,58.6,0.05,45,0)
# denti che battono (Tumbo)
for k in range(48): put(fx,55.0+0.045*k,tone(1500,1300,0.02,90,0.1)*0.10)
# semaforo
put(fx,58.3,tone(520,520,0.22,5,0.2)*0.4); put(fx,58.65,tone(520,520,0.22,5,0.2)*0.4); put(fx,58.95,tone(1040,1040,0.5,4,0.2)*0.45)
# sorpasso, leva che si stacca
put(fx,61.75,burst(0.5,50,5)*2.0*np.hanning(int(0.5*SR))); put(fx,62.98,tone(1900,1700,0.25,12,0.1)*0.4); put(fx,62.98,burst(0.08,4,30)*0.6)
# schianto nel garage, pezzi che cadono, ruota
clang(64.85,1.3); put(fx,64.85,hiss(1.0,4,4)*0.6)
for k in range(7): put(fx,65.05+0.13*k+0.04*rng.random(),tone(500+rng.random()*900,400,0.12,20,0.2)*0.25)
# "uà uà uà" finale e pallone
def wah(f,dur):
    n=int(dur*SR); tt=np.arange(n)/SR; s=np.zeros(n)
    for h in range(1,7): s+=np.sin(2*np.pi*f*h*(1-0.03*tt/dur)*tt)/h
    return lp(s,14)*np.minimum(1,tt*30)*np.minimum(1,(dur-tt)*12)
put(fx,65.35,wah(233,0.26)*0.16); put(fx,65.63,wah(220,0.26)*0.16); put(fx,65.91,wah(196,0.5)*0.17)
fx=np.tanh(fx*1.1)*0.45
mix=v*1.0+mus+fx
mix=np.clip(mix/max(1,np.abs(mix).max()/0.95),-1,1)
mix[-int(0.15*SR):]*=np.linspace(1,0,int(0.15*SR))
st=np.stack([mix,mix],1); pcm=(st*32767).astype(np.int16)
with wave.open('audio/t006.wav','wb') as o:
    o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes(pcm.tobytes())
print('audio ok', np.abs(v).max(), np.abs(mus).max(), np.abs(fx).max())
