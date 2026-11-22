"""Test 007 - audio: voce + musichetta sintetica + effetti. Esce audio/t007.wav (68.5 s)"""
import numpy as np, subprocess, wave
SR=44100; DUR=68.5; N=int(DUR*SR); rng=np.random.default_rng(7)
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
subprocess.run(['/usr/local/bin/ffmpeg','-y','-loglevel','error','-i','audio/voce_t007.mp3','-ar',str(SR),'-ac','1','audio/voce44_t007.wav'],check=True)
w=wave.open('audio/voce44_t007.wav'); v=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(float)/32768; v=np.pad(v,(0,max(0,N-len(v))))[:N]
bpm=108; beat=60/bpm; chords=[(130.81,164.81,196.0),(220.0,261.63,329.63),(174.61,220.0,261.63),(196.0,246.94,293.66)]
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
mus*=np.interp(t,[0,1,67.2,67.5,68.5],[0.6,1,1,0.35,0.0])
fx=np.zeros(N)
def pop(tp,g=0.55): put(fx,tp,tone(420,900,0.14,16,0.2)*g)
def hammer(tp,n=3,g=1.0):
    for k in range(n): put(fx,tp+0.11*k,tone(260,180,0.07,35,0.5)*0.7*g); put(fx,tp+0.11*k,burst(0.05,3,40)*0.8*g)
def thud(tp,g=1.0): put(fx,tp,tone(95,45,0.45,7,0.5)*1.2*g); put(fx,tp,burst(0.4,15,9)*1.0*g)
def boing(tp,f=180,g=0.5):
    n=int(0.45*SR); tt=np.arange(n)/SR; fr_=f*(1+0.6*np.exp(-tt*7)*np.sin(2*np.pi*9*tt)); put(fx,tp,np.sin(2*np.pi*np.cumsum(fr_)/SR)*np.exp(-tt*5)*g)
def whoosh(tp,dur=0.5,g=1.8,k=50): put(fx,tp,burst(dur,k,5)*g*np.hanning(int(dur*SR)))
# innamorato: campanellini a cuoricino
for k,tp in enumerate((0.4,1.3,2.2,3.1,4.3,5.4,6.2)): put(fx,tp,tone(1320+220*(k%3),1320+220*(k%3),0.5,7,0.2)*0.10)
for k in range(6): put(fx,5.3+0.25*k,tone(2000+300*(k%4),2000+300*(k%4),0.3,9,0.1)*0.07)       # il nano brilla
pop(8.5,0.4); pop(11.3)                                                                         # sogno, cartello
put(fx,12.8,tone(140,90,0.25,12,0.4)*0.8)                                                        # porta sbattuta
for k in range(5): put(fx,15.3+0.2*k,hiss(0.06,2,40)*0.35)                                       # citofono che frigge
hammer(16.5,3); pop(17.9); 
for k in range(4): put(fx,18.25+0.17*k,tone(300,260,0.05,40,0.3)*0.3)                            # pioli
hammer(20.05,3); pop(22.15)
for k in range(6): put(fx,22.45+0.15*k,tone(300+10*k,260,0.05,40,0.3)*0.3)
hammer(24.75,5,1.1)
n=int(0.6*SR); tt=np.arange(n)/SR; f=np.linspace(1300,400,n); put(fx,25.2,np.sin(2*np.pi*np.cumsum(f)/SR)*np.minimum(1,tt*8)*0.18)   # scala che cade
thud(25.85); put(fx,28.3,tone(196,196,0.9,3,0.5)*0.25); put(fx,28.3,tone(294,294,0.9,3,0.5)*0.2); thud(28.3,0.6)                     # gong della muraglia
for k in range(5): put(fx,29.4+0.25*k,tone(2000+300*(k%4),2000+300*(k%4),0.3,9,0.1)*0.07)
pop(31.3); boing(32.1,160); boing(32.6,200,0.6)
put(fx,33.2,hiss(0.35,4,9)*0.8); thud(33.3)                                                      # strappo e paletto
for k in range(16):                                                                              # Tumbo ride
    tk=38.0+0.24*k+0.03*np.sin(k*2.1); put(fx,tk,tone(820-20*(k%4),560,0.13,10,0.5)*0.2)
pop(42.3); put(fx,43.6,tone(200,90,0.2,10,0.5)*1.0); whoosh(43.62,0.8,2.2)                       # catapulta
n=int(0.75*SR); tt=np.arange(n)/SR; f=np.linspace(700,1500,n//2).tolist()+np.linspace(1500,500,n-n//2).tolist(); put(fx,43.68,np.sin(2*np.pi*np.cumsum(f)/SR)*np.minimum(1,tt*8)*0.14)
thud(44.45,0.9)
for k in range(8): put(fx,44.75+0.22*k,tone(240,150,0.08,25,0.4)*0.5)                            # borsettate
pop(46.75); 
n=int(1.2*SR); tt=np.arange(n)/SR; f=np.linspace(300,700,n); put(fx,47.0,np.sin(2*np.pi*np.cumsum(f)/SR)*np.minimum(1,tt*4)*np.minimum(1,(1.2-tt)*4)*0.10)
for tp in (47.9,48.25): put(fx,tp,burst(0.12,2,30)*1.6)                                          # scoppi
boing(48.6,140,0.7); boing(49.3,150,0.4)
for k in range(5): put(fx,51.6+0.11*k,hiss(0.09,6,20)*0.5)                                       # pala
whoosh(52.2,0.3,1.5,30)
put(fx,52.9,burst(0.5,60,6)*3.0); put(fx,52.95,tone(160,220,0.25,8,0.6)*0.5)                     # splash
fx+=np.sin(2*np.pi*np.cumsum(210+40*np.sin(2*np.pi*31*t))/SR)*env(53.5,61.7,0.3,0.4)*0.022       # mosche
for k in range(3): put(fx,57.6+0.3*k,tone(210,170,0.07,30,0.5)*0.75)                             # toc toc toc
put(fx,59.55,tone(500,300,0.35,5,0.2)*0.12); put(fx,59.6,burst(0.3,40,8)*0.6)                    # porta che cigola
for k in range(5): put(fx,61.05+0.12*k,tone(1320+220*(k%3),1320+220*(k%3),0.5,7,0.2)*0.11)
for k,f in enumerate((262,330,392,523)): put(fx,61.95+0.13*k,tone(f,f,0.7,3.5,0.5)*0.16)         # rivelazione: 200 nani
for k in range(6): put(fx,64.4+0.3*k,tone(1320+220*(k%3),1320+220*(k%3),0.5,7,0.2)*0.10)
hammer(67.3,3,1.1); pop(67.85)
fx=np.tanh(fx*1.1)*0.45
mix=v*1.0+mus+fx
mix=np.clip(mix/max(1,np.abs(mix).max()/0.95),-1,1)
mix[-int(0.15*SR):]*=np.linspace(1,0,int(0.15*SR))
st=np.stack([mix,mix],1); pcm=(st*32767).astype(np.int16)
with wave.open('audio/t007.wav','wb') as o:
    o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes(pcm.tobytes())
print('audio ok', np.abs(v).max(), np.abs(mus).max(), np.abs(fx).max())
