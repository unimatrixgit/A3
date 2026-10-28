from pathlib import Path
import re,json,datetime,shutil,subprocess
repo=Path('D:/aramada');root=Path('D:/armadaIII');assert subprocess.check_output(['powershell','-NoProfile','-Command','@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'],text=True).strip()=='0','Close game first.'
# Reuse read-only native property, producer and technology resolution.
source=(repo/'scripts/audit-borg-sequence-20261028.py').read_text(encoding='utf-8-sig');exec(source.split('reports=[]')[0])
backup=Path('D:/Xaramada-Modwork/backups')/('ai-colony-after-yard-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));rows=[]
pairs={'federation':('fyard','fcolony'),'borg':('byard','bcolony'),'breen':('bryard','brcolony'),'cardassian':('cyard','ccolony'),'dominion':('dyard','dcolony'),'klingon':('kyard','kcolony'),'romulan':('ryard','rcolony'),'bajoran':('bjyard','bjcolony')}
pattern=r'^\s*"([^"]+)"\s*,\s*(\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,?'
for faction,(yard,colony)in pairs.items():
 profiles=sorted((root/'AI/AIPs').glob(faction+'_*list.aip'));assert len(profiles)==5,(faction,len(profiles))
 for p in profiles:
  lines=p.read_text(encoding='latin1').splitlines();old=list(lines);matches=[(i,l)for i,l in enumerate(lines)if re.match(r'\s*"'+colony+r'"\s*,\s*1\s*,',l)];assert len(matches)<=1,(p.name,colony)
  previous,line=matches[0]if matches else(-1,'    '+chr(34)+colony+chr(34)+', 1, 0, -1, 0,')
  if matches:lines.pop(previous)
  else:old.append(line)
  yardline=next(i for i,l in enumerate(lines)if re.match(r'\s*"'+yard+r'"\s*,',l));lines.insert(yardline+1,line)
  assert sorted(lines)==sorted(old)
  parsed=[re.match(pattern,l).groups()for l in lines if re.match(pattern,l)];position=next(i for i,r in enumerate(parsed)if r[0]==colony and r[1]=='1');assert parsed[position-1][0]==yard
  avail={Path(v).stem.lower()for k,v in cache[{'federation':'fed','cardassian':'card','klingon':'kling','romulan':'rom'}.get(faction,faction)].items()if re.fullmatch('standardunits[0-9]+',k)}
  avail.update(r[0].lower()for r in parsed[:position]);gate,deps=tech[colony];assert gate>=0 and set(deps)<=avail,(p.name,deps)
  availableProducers=sorted(producers.get(colony,set())&avail);assert availableProducers,(p.name,colony)
  rel=p.relative_to(root);b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b);data=('\r\n'.join(lines)+'\r\n').encode('latin1');p.write_bytes(data);out=repo/'bajor/overlay'/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
  rows.append({'profile':p.name,'yard':yard,'colonyShip':colony,'colonyStep':position+1,'availableProducers':availableProducers,'existingRequestsAndCountsPreserved':True,'newColonyRequestAdded':not bool(matches)})
report={'backup':str(backup),'profiles':rows,'updatedProfiles':len(rows),'factions':len(pairs),'exception':'Species 8472 has no colonization ship defined; biological profiles unchanged. No standalone Ferengi AI profile exists in current installation.','campaignAiUnchanged':True,'runtimeVerified':False};(repo/'reports/ai-colony-after-yard-20261028.json').write_text(json.dumps(report,indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='All eight colonizing AI factions now request one colony ship immediately after the first yard: 40 skirmish profiles patched. Producers and colony tech prerequisites verified at that step. All other requests/counts retained; 8472 (no colony vessel) and campaign AI unchanged. armadaIII applied; gameplay pending.';p.write_text(json.dumps(s,indent=2))
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n'+datetime.datetime.now().isoformat()+' '+s['current']+'\n')
print(json.dumps({'factions':len(pairs),'profiles':len(rows),'colonyStepRange':[min(r['colonyStep']for r in rows),max(r['colonyStep']for r in rows)]}))
