import numpy as np,wave,sys
SR=44100
def note(f,d,duty=0.5,vol=0.3):
    t=np.arange(int(SR*d))/SR
    if f<=0: return np.zeros_like(t)
    w=np.where((t*f)%1<duty,1.0,-1.0)*vol
    env=np.minimum(1,np.minimum(t*200,(d-t)*60)).clip(0,1)
    return w*env
def tri(f,d,vol=0.35):
    t=np.arange(int(SR*d))/SR
    w=(2*np.abs(2*((t*f)%1)-1)-1)*vol
    env=np.minimum(1,(d-t)*40).clip(0,1);return w*env
def noise(d,vol=0.25,decay=30):
    t=np.arange(int(SR*d))/SR;return np.random.uniform(-1,1,len(t))*vol*np.exp(-t*decay)
def hz(n): return 0 if n is None else 440*2**((n-69)/12)
def track(seed,bpm,key,prog,out,length=20):
    rng=np.random.default_rng(seed);beat=60/bpm;s=beat/2
    scale=[0,2,4,7,9,12,14,16]
    bars=[]
    mel_motif=[rng.choice(scale) for _ in range(8)]
    for bi,ch in enumerate(prog*2):
        # melody: 8 eighths, vary motif
        m=[]
        for i in range(8):
            n=mel_motif[i] if (bi%2==0 or rng.random()<0.6) else rng.choice(scale)
            m.append(None if rng.random()<0.15 else key+12+ch+n)
        mel=np.concatenate([note(hz(n),s,0.25,0.18) for n in m])
        bass=np.concatenate([tri(hz(key-12+ch+(0 if i%2==0 else 7)),s,0.32) for i in range(8)])
        dr=np.concatenate([noise(s,0.22 if i%4==0 else 0.12,40 if i%2==0 else 80) for i in range(8)])
        L=min(len(mel),len(bass),len(dr));bars.append(mel[:L]+bass[:L]+dr[:L])
    loop=np.concatenate(bars);n=int(SR*length)
    a=np.tile(loop,int(np.ceil(n/len(loop))))[:n]
    fade=int(SR*1.5);a[-fade:]*=np.linspace(1,0,fade)
    a=a/np.max(np.abs(a))*0.7
    with wave.open(out,'w') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((a*32767).astype(np.int16).tobytes())
track(3,132,60,[0,5,7,5],'tune_bouncy.wav')
track(11,116,57,[0,3,5,7],'tune_sneaky.wav')
track(21,140,62,[0,7,9,5],'tune_upbeat.wav')
