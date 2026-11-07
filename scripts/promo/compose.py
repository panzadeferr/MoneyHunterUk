import json,subprocess,sys
# compose.py framesdir out.mp4 overlays.json [end_time]
d,out,ovf=sys.argv[1],sys.argv[2],sys.argv[3]
end=float(sys.argv[4]) if len(sys.argv)>4 else None
ovs=json.load(open(ovf))
cmd=['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',d+'/list.txt']
for o in ovs: cmd+=['-loop','1','-i',o['png']]
cmd+=['-f','lavfi','-i','anullsrc=r=44100:cl=stereo']
import os
SAFE=os.environ.get('SAFE')
if SAFE:
    fc=f"color=c=0x161a33:s=1080x1920:r=30[bg];[0:v]fps=30,scale=675:1200:flags=lanczos,setsar=1[g];[bg][g]overlay=202:300:shortest=1[v0]"
else:
    fc='[0:v]fps=30,scale=1080:1920:flags=lanczos,setsar=1[v0]'
last='v0'
for i,o in enumerate(ovs):
    oy=0 if (not SAFE or 'end' in o['png']) else 90
    fade="format=rgba" if o["s"]==0 else f"format=rgba,fade=t=in:st={o['s']}:d=0.15:alpha=1"
    fc+=f";[{i+1}:v]{fade}[o{i}];[{last}][o{i}]overlay=0:{oy}:enable='between(t,{o['s']},{o['e']})':shortest=1[v{i+1}]"
    last=f'v{i+1}'
cmd+=['-filter_complex',fc,'-map',f'[{last}]','-map',f'{len(ovs)+1}:a']
if end: cmd+=['-t',str(end)]
cmd+=['-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','30','-c:a','aac','-b:a','96k','-shortest','-movflags','+faststart',out]
subprocess.run(cmd,check=True)
print(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',out],capture_output=True,text=True).stdout.strip())
