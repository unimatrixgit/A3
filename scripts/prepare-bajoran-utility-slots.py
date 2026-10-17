from pathlib import Path
import json,re,hashlib,datetime,shutil
root=Path('D:/armadaIII');report=Path('D:/aramada/reports/bajoran-federation-balance-repair.json');r=json.loads(report.read_text(encoding='utf-8-sig'));prior=Path(r['backup']);stage=Path('D:/Xaramada-Modwork/bajor-utility-slots');files=[]
for name in ['bjfreight','bjcargo','bjrepair']:
 rel='odf/ships/'+name+'.odf';p=root/rel;t=p.read_text();old=(prior/rel).read_text();oldprops=re.findall(r'(?mi)^[ \t]*(weapon\d+|weaponhardpoints\d+)[ \t]*=[ \t]*([^\r\n]*)',old)
 t=re.sub(r'(?mi)^[ \t]*(?:weapon\d+|weaponhardpoints\d+)[ \t]*=[^\r\n]*(?:\r?\n)?','',t)
 t+='\n// Preserve utility ability slots independently of combat balance.\n'+'\n'.join(k+' = '+v for k,v in oldprops)+'\n'
 if name=='bjfreight':
  t=re.sub(r'(?mi)^weapon[3-9]\d*[ \t]*=[^\r\n]*','',t)
  # Absent slots must be omitted; empty weapon names crash the engine.
  assert 'weapon1 = "gmineDilithium"'in t and 'weapon2 = "gmineLatinum"'in t
 o=stage/rel;o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));files.append({'path':rel,'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sha256':hashlib.sha256(o.read_bytes()).hexdigest()})
Path('D:/aramada/reports/bajoran-utility-slots.json').write_text(json.dumps({'stage':str(stage),'files':files,'applied':False,'runtimeVerified':False},indent=2))
# Prevent the generic balance generator from touching utility ability ordering again.
p=Path('D:/aramada/scripts/prepare-bajoran-federation-balance-repair.py');s=p.read_text();s=s.replace('if fw and cw:',"if fw and cw and name not in ['bjfreight','bjcargo','bjrepair','bjcolony','bjconst']:");p.write_text(s)
print('Staged three utility slot restorations; freighter mining-only')
