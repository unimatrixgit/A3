from pathlib import Path
import re,json
root=Path('D:/armadaIII');stage=Path('D:/Xaramada-Modwork/bajor-icon-model-alias-fix');stage.mkdir(exist_ok=True)
s=(root/'Sprites/gui_global.spr').read_text();rows=[]
for line in s.splitlines():
 a=line.split()
 if len(a)==6 and a[1].startswith('bjic'):
  name=a[0];alias='b_br3_'+name[2:] if name.startswith('b_') else 'br3_'+name
  rows.append('@reference=64\n@tmaterial=default\n'+' '.join([alias]+a[1:]))
assert len(rows)==318
s+='\n# Redesigned model-name button and wireframe aliases\n'+'\n'.join(rows)+'\n'
p=stage/'Sprites/gui_global.spr';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.replace('\r','').replace('\n','\r\n').encode('ascii'))
p=stage/'odf/ships/bjnerys.odf';p.parent.mkdir(parents=True,exist_ok=True);t=(root/'odf/ships/bjnerys.odf').read_text();t,n=re.subn(r'(?mi)^ScaleSOD[ \t]*=[ \t]*[^\r\n]+','ScaleSOD = 0.75',t);assert n==1;p.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('ascii'))
report={'stage':str(stage),'files':['Sprites/gui_global.spr','odf/ships/bjnerys.odf'],'modelAliasesAdded':318,'kiraScaleBefore':0.3,'kiraScaleAfter':0.75,'applied':False,'runtimeVerified':False}
Path('D:/aramada/reports/bajoran-icon-model-alias-fix.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
