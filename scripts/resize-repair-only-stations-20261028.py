from pathlib import Path
import re,json,datetime,shutil,subprocess
root=Path('D:/armadaIII');repo=Path('D:/aramada');idx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')}
probe=subprocess.run(['powershell','-NoProfile','-Command','@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'],capture_output=True,text=True);assert probe.stdout.strip()=='0','Close Armada III before installing.'
def props(n,seen=()):
 n=Path(n.strip('"')).stem.lower()
 if n not in idx or n in seen:return{}
 t=idx[n].read_text(encoding='latin1');d={}
 for inc in re.findall(r'(?mi)^\s*#include\s+"([^"]+)"',t):d.update(props(inc,seen+(n,)))
 for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t):d[k.lower()]=v.split('//')[0].strip().strip('"')
 return d
def put(t,k,v):
 pat=r'(?mi)^[ \t]*'+k+r'[ \t]*=[^\r\n]*';line=k+' = '+format(v,'.12g')
 return re.sub(pat,lambda m:line,t)if re.search(pat,t)else t.rstrip()+'\n'+line+'\n'
backup=Path('D:/Xaramada-Modwork/backups')/('repair-only-size-time-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));rows=[];excluded=[]
for name,p in sorted(idx.items()):
 if p.parent.name.lower()!='stations':continue
 a=props(name)
 if a.get('repairfacility')!='1':continue
 items=[v for k,v in a.items()if re.fullmatch('builditem[0-9]+',k)and v and v.lower()not in ['0','none','null']]
 if items:excluded.append({'unit':name,'production':items});continue
 scale=float(a.get('scalesod','1').rstrip('fF'));time=float(a['buildtime'].rstrip('fF'));t=p.read_text(encoding='latin1');t=put(t,'ScaleSOD',scale*.5);t=put(t,'buildTime',time*.25)
 rel=p.relative_to(root);b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b);data=t.replace('\r','').replace('\n','\r\n').encode('latin1');p.write_bytes(data);(repo/'bajor/overlay'/rel).write_bytes(data)
 after=props(name);changed={k for k in a.keys()|after.keys()if a.get(k)!=after.get(k)};assert changed<={'scalesod','buildtime'}
 assert abs(float(after['scalesod'])-scale*.5)<1e-8 and abs(float(after['buildtime'])-time*.25)<1e-8
 rows.append({'unit':name,'name':a.get('unitname'),'oldScale':scale,'newScale':scale*.5,'oldBuildTime':time,'newBuildTime':time*.25})
(repo/'reports/repair-only-size-time-20261028.json').write_text(json.dumps({'backup':str(backup),'updated':rows,'excludedProductionStations':excluded,'runtimeVerified':False},indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']=f'{len(rows)} repair-only stations reduced to 50% current model size and 25% current build time. {len(excluded)} repair stations with production menus excluded. Repair, decommission, rally controls and other stats retained. Applied to armadaIII; file validation passed, gameplay pending.';p.write_text(json.dumps(s,indent=2))
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n'+datetime.datetime.now().isoformat()+' '+s['current']+'\n')
print(json.dumps({'updated':rows,'excluded':excluded}))
