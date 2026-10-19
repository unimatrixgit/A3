from pathlib import Path
import re,json,datetime
repo=Path('D:/aramada');backup=Path('D:/Xaramada-Modwork/backups')/('small-ships-150-percent-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));pending=[];report=[]
for root in [Path('D:/ArmadaLab'),Path('D:/armadaIII')]:
 idx={f.name.lower():f for f in(root/'odf').rglob('*.odf')}
 def props(n,seen=None):
  seen=set()if seen is None else seen
  if n in seen or n not in idx:return {}
  seen.add(n);t=idx[n].read_text(encoding='latin1');v={}
  for inc in re.findall(r'(?mi)^\s*#include\s+"([^"]+)"',t):v.update(props(inc.lower(),seen))
  for k,x in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t):v[k.lower()]=x.split('//')[0].strip().strip('"')
  return v
 for f in(root/'odf/ships').glob('*.odf'):
  v=props(f.name.lower());cls=v.get('shipclass','').lower();name=v.get('unitname','')
  if not name or cls not in ['scout','destroyer','frigate','fighter']:continue
  scale=float(v.get('scalesod','1').rstrip('fF'));new=scale*1.5
  t=f.read_text(encoding='latin1');t=re.sub(r'(?mi)^[ \t]*ScaleSOD[ \t]*=[^\r\n]*','',t)+'\n// Visual size: 150 percent of pre-patch scale.\nScaleSOD = '+format(new,'.8g')+'\n'
  pending.append((root,f.relative_to(root),t));report.append({'root':str(root),'unit':f.name,'name':name,'class':cls,'previousScale':scale,'newScale':new})
for root,rel,t in pending:
 f=root/rel;b=backup/root.name/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(f.read_bytes());f.chmod(0o666);data=t.replace('\r','').replace('\n','\r\n').encode('latin1');f.write_bytes(data);assert f.read_bytes()==data
 out=repo/('lab/overlay'if root.name=='ArmadaLab'else'bajor/overlay')/rel;out.write_bytes(data)
(repo/'reports/small-ships-size-150.json').write_text(json.dumps({'backup':str(backup),'criteria':'Named shipclass scout/destroyer/frigate/fighter; no shared parent files changed','units':report,'runtimeVerified':False},indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Applied two updates to armadaIII and ArmadaLab: all 27 named constructor variants have at least one combat beam and torpedo, attack enabled, existing tools/specials/stronger loadouts retained. '+str(len(report)//2)+' small ship definitions (scout/destroyer/frigate/fighter classes) enlarged to 150 percent of prior visual scale. Gameplay stats untouched by size patch. Backups and reports saved; in-game verification pending.';p.write_text(json.dumps(s,indent=2));
with(repo/'build.log').open('a')as log:log.write('\n'+s['current']+'\n')
print(json.dumps({'shipsPerInstallation':len(report)//2,'classes':sorted(set(x['class']for x in report)),'backup':str(backup)}))
