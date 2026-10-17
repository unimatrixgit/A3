from pathlib import Path
import re,json,hashlib
exec(Path('D:/aramada/scripts/prepare-bajoran-durability-research.py').read_text().split("for u in m['units']:")[0])
# Override previous staging variables; never rerun the earlier durability multiplier.
stage=Path('D:/Xaramada-Modwork/bajor-shield-capacity');files=[];changes=[]
for u in m['units']:
 n=u['odf']
 if n.startswith('bjpod'):continue
 source='fente'if n=='bjnerys'else u['parent'];d=props(source);p=idx[n+'.odf'];t=p.read_text(encoding='latin1');row={'unit':n,'equivalent':source}
 for k in ['maxhealth','shieldrate']:
  if k not in d:continue
  try:v=float(d[k].rstrip('fF'))
  except ValueError:continue
  if v<=0:continue
  t=put(t,k,format(v*2,'.8g'));row[k]=v*2
 if len(row)==2:continue
 rel=p.relative_to(root).as_posix();o=stage/rel;o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));files.append({'path':rel,'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sha256':hashlib.sha256(o.read_bytes()).hexdigest()});changes.append(row)
(repo/'reports/bajoran-shield-capacity.json').write_text(json.dumps({'stage':str(stage),'files':files,'changes':changes,'applied':False,'runtimeVerified':False,'basis':'Twice current Federation counterpart shield capacity and recharge. maxHealth is explicitly labelled shield strength in native definitions.'},indent=2));print('Prepared',len(files),'shield adjustments')
