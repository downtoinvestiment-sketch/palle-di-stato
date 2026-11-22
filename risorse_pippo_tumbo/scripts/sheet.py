import sys, subprocess
times=[float(x) for x in sys.argv[3].split(',')]; d=sys.argv[2]; blend=sys.argv[1]; cols=int(sys.argv[4]) if len(sys.argv)>4 else 10
fr=[int(round(t*24))+1 for t in times]
subprocess.run(['/home/claude/venv/bin/python','render_t004.py',blend,d,'360','640','4',','.join(map(str,fr))],capture_output=True)
import os
lst=d+'/list.txt'; open(lst,'w').write(''.join("file 'f%04d.png'\n"%f for f in fr))
rows=(len(fr)+cols-1)//cols
subprocess.run(['/usr/local/bin/ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-r','1','-i',lst,'-vf','eq=saturation=1.25:contrast=1.05,scale=216:384,tile=%dx%d'%(cols,rows),'-frames:v','1',d+'/sheet.png'])
print('ok',len(fr))
