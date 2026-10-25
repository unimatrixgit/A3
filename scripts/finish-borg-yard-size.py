from pathlib import Path
import json,re
p=Path('D:/aramada/patches/twin-yards-20261025');d=json.loads((p/'design.json').read_text());b=d['baseline']['bhwp'];f=p/'overlay'/b['file'];t=f.read_text(encoding='latin1');v=b['properties']
for k in ['ScaleSOD','footprintBuffer','northBuffer','southBuffer','eastBuffer','westBuffer']:
 if k.lower()not in v and k!='ScaleSOD':continue
 value=float(v.get(k.lower(),'1').rstrip('fF;'))*.875;t=re.sub(r'(?mi)^[ \t]*'+k+r'[ \t]*=[^\r\n]*','',t).rstrip()+'\n'+k+' = '+format(value,'.12g')+'\n'
f.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));a=json.loads((p/'artwork.json').read_text())
for row in a:
 if row['unit']=='bhwp':row['size']*=.875;row['scale']*=.875
(p/'artwork.json').write_text(json.dumps(a,indent=2));d['borgModelCorrection']={'nexus':'xvstock_bbase','yardWings':'xvstock_byard','source':'Preserved Armada II original models','hwpReduction':.125};d['yardSizeIncrease']=.25;(p/'design.json').write_text(json.dumps(d,indent=2));print('Borg HWP size/footprint reduced 12.5%; Armada II source correction recorded.')
