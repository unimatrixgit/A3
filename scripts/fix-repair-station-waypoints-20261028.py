"""Enable rally commands on existing repair-capable stations in armadaIII only."""
from pathlib import Path
import datetime,json,re,shutil,subprocess
root=Path('D:/armadaIII');repo=Path('D:/aramada')
# Do not mix station definitions into a running test.
probe=subprocess.run(['powershell','-NoProfile','-Command','@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'],capture_output=True,text=True)
assert probe.returncode==0 and probe.stdout.strip()=='0','Close Armada III before applying this patch.'
idx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')}
def properties(name,seen=()):
 name=Path(name.strip('"')).stem.lower()
 if name in seen or name not in idx:return{}
 t=idx[name].read_text(encoding='latin1');d={}
 for inc in re.findall(r'(?mi)^\s*#include\s+"([^"]+)"',t):d.update(properties(inc,seen+(name,)))
 for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t):d[k.lower()]=v.split('//')[0].strip().strip('"')
 return d
def set_value(t,key,val):
 pattern=r'(?mi)^[ \t]*'+key+r'[ \t]*=[^\r\n]*'
 return re.sub(pattern,lambda m:key+' = '+val,t)if re.search(pattern,t)else t.rstrip()+'\n'+key+' = '+val+'\n'
backup=Path('D:/Xaramada-Modwork/backups')/('repair-station-waypoints-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));rows=[]
for name,p in sorted(idx.items()):
 if p.parent.name.lower()!='stations':continue
 before=properties(name)
 if before.get('repairfacility')!='1':continue
 assert before.get('classlabel','').lower()in ['shipyard','starbase'],(name,'Unexpected repair class')
 original=p.read_text(encoding='latin1');t=original
 for key in ['builder_ship','alwaysRecomputeRallyPoint']:t=set_value(t,key,'0' if key=='alwaysRecomputeRallyPoint' else '1')
 changed=t!=original;rel=p.relative_to(root)
 if changed:
  b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b)
  data=t.replace('\r','').replace('\n','\r\n').encode('latin1');p.write_bytes(data)
  out=repo/'bajor/overlay'/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
 after=properties(name);diff={k for k in before.keys()|after.keys()if before.get(k)!=after.get(k)}
 assert diff<={'builder_ship','alwaysrecomputerallypoint'},(name,diff)
 assert after['builder_ship']=='1'and after['alwaysrecomputerallypoint']=='0'
 rows.append({'unit':name,'name':before.get('unitname'),'class':before.get('classlabel'),'changed':changed,'previousBuilderControl':before.get('builder_ship'),'previousRallyRefresh':before.get('alwaysrecomputerallypoint'),'repairRetained':after['repairfacility']=='1','productionAndDockAnchorsUnchanged':True})
report={'target':str(root),'backup':str(backup),'stationsChecked':len(rows),'stationsUpdated':sum(x['changed']for x in rows),'results':rows,'runtimeVerified':False,'limitation':'Native rally command and recomputation flags verified in files. Repaired-unit departure behavior requires in-game verification.'}
(repo/'reports/repair-station-waypoints-20261028.json').write_text(json.dumps(report,indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']=f"All {len(rows)} repair-capable station definitions checked: rally command enabled and automatic rally reset disabled; {report['stationsUpdated']} files updated. Existing production, repairs, decommission and docking anchors preserved. Applied to armadaIII only. File checks passed; repaired-unit rally departure pending gameplay verification.";p.write_text(json.dumps(s,indent=2))
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n'+datetime.datetime.now().isoformat()+' '+s['current']+'\n')
print(json.dumps({'checked':len(rows),'updated':report['stationsUpdated'],'previouslyDisabledControls':sum(x['previousBuilderControl']=='0'for x in rows),'runtimeVerified':False}))
