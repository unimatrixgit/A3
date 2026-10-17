from pathlib import Path
import re,json,hashlib
root=Path('D:/armadaIII');stage=Path('D:/Xaramada-Modwork/bajor-paired-yard-tech');files=[]
req={'bjyard':['bjbase'],'bjresear':['bjbase'],'bjyard2':['bjresear'],'bjresear2':['bjresear']}
for p in (root/'techtree').glob('*.tt'):
 t=p.read_text(encoding='latin1')
 if not re.search(r'(?mi)^fresear\.odf[ \t]+2[ \t]+fbase\.odf[ \t]+fyard\.odf',t):continue
 for n,deps in req.items():
  t,count=re.subn(r'(?mi)^'+n+r'\.odf[^\r\n]*',n+'.odf '+str(len(deps))+''.join(' '+d+'.odf'for d in deps),t);assert count==1
 rel='techtree/'+p.name;o=stage/rel;o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));files.append({'path':rel,'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sha256':hashlib.sha256(o.read_bytes()).hexdigest()})
p=root/'odf/ships/bjcolony.odf';t=p.read_text();assert 'weapon1 = "xbj_fcolonypod"'in t;t=t.replace('weapon1 = "xbj_fcolonypod"','weapon1 = "fcolonypod"');rel='odf/ships/bjcolony.odf';o=stage/rel;o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('ascii'));files.append({'path':rel,'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sha256':hashlib.sha256(o.read_bytes()).hexdigest()})
Path('D:/aramada/reports/bajoran-paired-yard-tech.json').write_text(json.dumps({'stage':str(stage),'files':files,'requirements':req,'applied':False,'runtimeVerified':False},indent=2))
s=Path('D:/aramada/scripts/audit-bajoran-progression.cjs').read_text().replace("root+'/techtree/tech1.tt'","'D:/Xaramada-Modwork/bajor-paired-yard-tech/techtree/tech1.tt'").replace('bajoran-progression-live.json','bajoran-progression-paired-tech.json');Path('D:/aramada/scripts/audit-bajoran-paired-tech.cjs').write_text(s)
print('Staged',len(files),'files')
