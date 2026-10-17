from pathlib import Path
import re,json,hashlib,datetime
root=Path('D:/armadaIII');stage=Path('D:/Xaramada-Modwork/bajor-fed-building-tech');files=[];changes=[]
# Federation building tiers adapted to Bajor's two-yard roster; hero yard shares special-station requirements.
req={'bjbase':[],'bjmining':[],'bjorbital':[],'bjsensor':['bjbase'],'bjturret':['bjbase'],'bjturret2':['bjresear'],'bjyard':['bjbase'],'bjyard2':['bjresear'],'bjtrading':['bjbase'],'bjresear':['bjbase','bjyard'],'bjresear2':['bjyard2','bjresear'],'bjupgrade':['bjresear','bjresear2'],'bjyard3':['bjbase','bjresear2','bjyard2'],'bjsuperlab':['bjbase','bjresear2','bjyard2']}
for p in (root/'techtree').glob('*.tt'):
 t=p.read_text(encoding='latin1');original=t
 # Preserve free-tech and mission-specific prerequisite rules: change normal trees with matching existing Fed research gates only.
 if not re.search(r'(?mi)^fresear\.odf[ \t]+2[ \t]+fbase\.odf[ \t]+fyard\.odf',t):continue
 for name,deps in req.items():
  pattern=r'(?mi)^'+name+r'\.odf[^\r\n]*'
  row=name+'.odf '+str(len(deps))+''.join(' '+d+'.odf'for d in deps)
  if re.search(pattern,t):t=re.sub(pattern,row,t)
  else:t+='\n'+row+'\n'
 if t!=original:
  rel='techtree/'+p.name;out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));files.append({'path':rel,'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
assert any(f['path'].lower()=='techtree/tech1.tt'for f in files)
r={'stage':str(stage),'files':files,'buildingRequirements':req,'adaptations':['Bajor has no Federation yard0; basic yard requires starbase.','Advanced research uses advanced yard plus basic research to avoid the installed Federation cycle.','Hero yard and special station share late-tier prerequisites.'],'applied':False,'runtimeVerified':False}
Path('D:/aramada/reports/bajoran-fed-building-tech.json').write_text(json.dumps(r,indent=2));print('Staged',len(files),'normal tech trees')
