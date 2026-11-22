import numpy as np, subprocess, wave
SR=44100; N=int(45.0*SR); rng=np.random.default_rng(3)
t=np.arange(N)/SR
def env(a,b,fi=0.1,fo=0.3):
    e=np.zeros(N); i0,i1=int(a*SR),int(b*SR); n=i1-i0
    x=np.ones(n); fi_n=int(fi*SR); fo_n=int(fo*SR)
    x[:fi_n]=np.linspace(0,1,fi_n); x[-fo_n:]=np.linspace(1,0,fo_n); e[i0:i1]=x; return e
def lp(x,k):
    return np.convolve(x,np.ones(k)/k,mode='same')
# voce
subprocess.run(['/usr/local/bin/ffmpeg','-y','-loglevel','error','-i','audio/voce_t003.mp3','-ar',str(SR),'-ac','1','audio/voce44.wav'],check=True)
w=wave.open('audio/voce44.wav'); v=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(float)/32768; v=np.pad(v,(0,max(0,N-len(v))))[:N]
# musica: pluck ukulele-ish, 104 bpm, C Am F G
bpm=104; beat=60/bpm; chords=[(261.63,329.63,392.0),(220.0,261.63,329.63),(174.61,261.63,349.23),(196.0,246.94,293.66)]
m=np.zeros(N)
def pluck(f,t0,dur=0.5,amp=0.5):
    i0=int(t0*SR); n=int(dur*SR)
    if i0>=N: return
    n=min(n,N-i0); tt=np.arange(n)/SR; s=(np.sin(2*np.pi*f*tt)+0.4*np.sin(4*np.pi*f*tt)+0.2*np.sin(6*np.pi*f*tt))*np.exp(-tt*7)
    m[i0:i0+n]+=amp*s
for bar in range(int(45/(beat*4))+1):
    ch=chords[bar%4]
    for b in range(8):
        t0=bar*beat*4+b*beat/2
        f=ch[[0,1,2,1,0,1,2,1][b]]; pluck(f*(1 if b%2==0 else 2)*0.5 if b%2==0 else f,t0,0.45,0.35 if b%2==0 else 0.25)
    pluck(ch[0]/2,bar*beat*4,0.9,0.5); pluck(ch[0]/2,bar*beat*4+2*beat,0.9,0.4)
mus=m/np.abs(m).max()*0.22
mus*=np.interp(t,[0,1,38,42,45],[0.6,1,1,0.4,0.0]); mus[int(43.2*SR):]*=0.3
# fx
fx=np.zeros(N)
rum=lp(rng.normal(0,1,N),60)*3*(1+0.4*np.sin(2*np.pi*14*t))
fx+=rum*env(8.95,11.6,0.4,0.6)*0.20+lp(rng.normal(0,1,N),120)*3*(1+0.3*np.sin(2*np.pi*9*t))*env(10.6,12.4,0.3,0.5)*0.16
fx+=lp(rng.normal(0,1,N),90)*3*(1+0.3*np.sin(2*np.pi*11*t))*env(33.0,36.4,0.3,0.4)*0.0
rain=(rng.normal(0,1,N)-lp(rng.normal(0,1,N),12)); fx+=rain*env(13.9,24.9,1.0,1.2)*0.09
for tp in (16.0,19.4,21.8): # tonfi/ spruzzi
    i0=int(tp*SR); n=int(0.3*SR); fx[i0:i0+n]+=lp(rng.normal(0,1,n),30)*np.exp(-np.arange(n)/SR*12)*0.4
# colpi di pallone sul terreno sconnesso
for tp in (6.5,7.2,7.9,8.5):
    i0=int(tp*SR); n=int(0.12*SR); tt=np.arange(n)/SR; fx[i0:i0+n]+=np.sin(2*np.pi*150*tt)*np.exp(-tt*35)*0.5
# calcio finale + gol + folla
i0=int(43.25*SR); n=int(0.2*SR); tt=np.arange(n)/SR; fx[i0:i0+n]+=np.sin(2*np.pi*110*tt)*np.exp(-tt*25)*0.9
cr=lp(rng.normal(0,1,N),6)*env(43.9,45.0,0.1,0.5)*0.30*(1+0.4*np.sin(2*np.pi*4*t)); fx+=cr
# whoosh per zolle/scorrimento sintetico
for a,b in ((25.2,27.3),(37.7,39.3)):
    fx+=lp(rng.normal(0,1,N),25)*env(a,b,0.4,0.4)*0.10
mix=v*1.0+mus+fx*0.85
mix=np.clip(mix/ max(1,np.abs(mix).max()/0.95),-1,1)
st=np.stack([mix,mix],1); pcm=(st*32767).astype(np.int16)
with wave.open('audio/t003.wav','wb') as o:
    o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes(pcm.tobytes())
print('audio ok')
