from pathlib import Path
import re,json
r=Path('D:/armadaIII');o=Path('D:/Xaramada-Modwork/faction-tech-building-fix');files=[]
for p in(r/'techtree').glob('*.tt'):
 t=p.read_text(encoding='latin1');out=re.sub(r'^(fresear2\.odf[^\r\n]*?)\bfyard3\.odf\b',r'\1fyard2.odf',t,flags=re.M|re.I)
 if out!=t:d=o/p.relative_to(r);d.parent.mkdir(parents=True,exist_ok=True);d.write_text(out,encoding='latin1');files.append(str(p.relative_to(r)))
for name in ['xbuconst','uconst']:
 p=r/'odf/ships'/(name+'.odf');t=p.read_text(encoding='latin1');items=re.findall(r'^buildItem(\d+)\s*=',t,re.M|re.I);assert len(items)==12 and '12'not in items;t+='\n// Advanced transwarp facility; avoids an unavailable third builder.\nbuildItem12 = "hub"\n';d=o/p.relative_to(r);d.parent.mkdir(parents=True,exist_ok=True);d.write_text(t,encoding='latin1');files.append(str(p.relative_to(r)))
print('Staged',len(files),'files:',files)
