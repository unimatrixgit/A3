from pathlib import Path
import json,re,datetime
repo=Path('D:/aramada');ref=json.loads((repo/'reports/equal-station-sizes.json').read_text());backup=Path('D:/Xaramada-Modwork/backups')/('starbases-80-percent-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));records=[]
for u in ref['units']:
 if u['category']!='starbase':continue
 root=Path(u['root']);f=root/'odf/stations'/u['unit']
 if not f.exists():f=root/'odf/ships'/u['unit']
 t=f.read_text(encoding='latin1');old=t
 m=re.search(r'(?mi)^[ \t]*ScaleSOD[ \t]*=[ \t]*([\d.eE+-]+)',t);assert m;scale=float(m[1]);new=scale*.8
 t=re.sub(r'(?mi)^[ \t]*ScaleSOD[ \t]*=[^\r\n]*','ScaleSOD = '+format(new,'.9g'),t)
 values={}
 for key in ['footprintBuffer','eastBuffer','westBuffer','northBuffer','southBuffer']:
  m=re.search(r'(?mi)^[ \t]*'+key+r'[ \t]*=[ \t]*([\d.eE+-]+)',t);assert m,(f,key)
  before=float(m[1]);after=before*.8;values[key]={'before':before,'after':after};t=re.sub(r'(?mi)^[ \t]*'+key+r'[ \t]*=[^\r\n]*',key+' = '+format(after,'.9g'),t)
 rel=f.relative_to(root);b=backup/root.name/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(f.read_bytes());f.chmod(0o666);data=t.replace('\r','').replace('\n','\r\n').encode('latin1');f.write_bytes(data);assert f.read_bytes()==data
 out=repo/('lab/overlay'if root.name=='ArmadaLab'else'bajor/overlay')/rel;out.write_bytes(data);records.append({'root':str(root),'unit':u['unit'],'oldScale':scale,'newScale':new,'footprintValues':values})
(repo/'reports/starbases-80-percent.json').write_text(json.dumps({'backup':str(backup),'factor':.8,'units':records,'runtimeVerified':False},indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='All 23 starbase variants reduced to 80 percent of current visual scale in armadaIII and ArmadaLab. Construction footprint clearance also reduced 20 percent (100 to80), with own-model square/rectangular shape retained and directional buffers kept zero. Heavy platforms unchanged. Backups saved; in-game placement/visual verification pending.';p.write_text(json.dumps(s,indent=2));
with(repo/'build.log').open('a')as log:log.write('\n'+s['current']+'\n')
print(json.dumps({'starbasesPerInstallation':len(records)//2,'files':len(records),'backup':str(backup),'factor':.8}))
