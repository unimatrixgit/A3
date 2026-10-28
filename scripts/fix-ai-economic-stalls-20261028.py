from pathlib import Path
import re,json,datetime,subprocess
repo=Path('D:/aramada');root=Path('D:/armadaIII')
assert subprocess.check_output(['powershell','-NoProfile','-Command','@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'],text=True).strip()=='0'
exec((repo/'scripts/audit-borg-sequence-20261028.py').read_text(encoding='utf-8-sig').split('reports=[]')[0])
backup=Path('D:/Xaramada-Modwork/backups')/('ai-economic-stalls-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));pending={};changes=[];audit=[]
for n in ['dbase','brbase']:
 p=idx[n];raw=p.read_bytes();t=raw.decode('latin1');assert cache[n]['officergain']=='0'
 t,c=re.subn(r'(?mi)^(officerGain\s*=\s*)0\b',r'\g<1>100',t);assert c==1;pending[p.relative_to(root)]=t.encode('latin1');changes.append({'unit':n,'officerGain':[0,100]})
spec={'federation':('f','fed'),'klingon':('k','kling'),'romulan':('r','rom'),'cardassian':('c','card'),'dominion':('d','dominion'),'borg':('b','borg'),'breen':('br','breen'),'bajoran':('bj','bajoran'),'species8472':('','species8472')}
pat=r'(?m)^\s*"([^"]+)"\s*,\s*(\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,'
for faction,(prefix,race)in spec.items():
 for p in sorted((root/'AI/AIPs').glob(faction+'_*list.aip')):
  t=p.read_text(encoding='latin1');lines=t.splitlines(keepends=True);pos=[i for i,l in enumerate(lines)if re.match(r'\s*"\w+",',l)]
  if faction not in ['romulan','species8472']:
   def unit(line):
    m=re.match(r'\s*"([^"]+)"',line);return m[1] if m else ''
   orbital='bbase2'if faction=='borg'else prefix+'orbital'
   oi=next(i for i,l in enumerate(lines)if unit(l)==orbital)
   ci=next(i for i,l in enumerate(lines)if unit(l)==prefix+'colony')
   if oi<ci:
    line=lines.pop(oi);ci=next(i for i,l in enumerate(lines)if unit(l)==prefix+'colony');lines.insert(ci+1,line)
   if faction not in ['borg','breen']:
    destroy='bjinterceptor'if faction=='bajoran'else prefix+'destroy'
    di=next(i for i,l in enumerate(lines)if unit(l)==destroy);ti=next(i for i,l in enumerate(lines)if unit(l)==prefix+'cargo')
    if di<ti:
     line=lines.pop(di);ti=next(i for i,l in enumerate(lines)if unit(l)==prefix+'cargo');lines.insert(ti+1,line)
   t=''.join(lines);pending[p.relative_to(root)]=t.encode('latin1')
  rows=[(m[1],*map(int,m.groups()[1:]))for m in re.finditer(pat,t)]
  avail={Path(v).stem.lower()for k,v in cache[race].items()if re.fullmatch('standardunits[0-9]+',k)};issues=[]
  for i,row in enumerate(rows):
   n=row[0];g,deps=tech.get(n,(0,[]))
   if n not in avail and(n not in idx or g<0 or not set(deps)<=avail or not(producers.get(n,set())&avail)):issues.append({'step':i+1,'unit':n,'missingTech':sorted(set(deps)-avail),'producer':sorted(producers.get(n,set())&avail)})
   avail.add(n)
  assert not issues,(p.name,issues)
  audit.append({'profile':p.name,'steps':len(rows),'issues':issues,'opening':[r[0]for r in rows[:13]],'consumedProducerSimulation':False if faction=='species8472'else 'not applicable'})
for rel,data in pending.items():
 p=root/rel;b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(p.read_bytes());p.write_bytes(data)
 m=repo/'bajor/overlay'/rel;m.parent.mkdir(parents=True,exist_ok=True);m.write_bytes(data);assert p.read_bytes()==m.read_bytes()
report={'backup':str(backup),'installedFiles':[str(r).replace('\\','/')for r in pending],'officerCorrections':changes,'profiles':audit,'runtimeVerified':False,'limitations':['Producer and prerequisite audit does not simulate map resource sites, live officer upgrades, trading partners or consumed Species 8472 producers.','No minimum moon or planet count is imposed, to avoid blocking maps without those sites.','Zero-officer Dominion/Breen bases corrected to existing Federation/Bajor allowance; other racial allowances preserved.']}
(repo/'reports/all-ai-economic-stalls-20261028.json').write_text(json.dumps(report,indent=2)+'\n')
p=repo/'status.json';d=json.loads(p.read_text());d['current']=f'AI economy patch installed: Dominion/Breen starbase officerGain corrected 0 to100;35 profiles reordered for early colony access, native trade before escorts where supported. All45 profiles ({sum(x["steps"]for x in audit)} steps) pass static producer/tech checks. Gameplay verification pending.';p.write_text(json.dumps(d,indent=2)+'\n')
with(repo/'build.log').open('a')as f:f.write('\n'+datetime.datetime.now().isoformat()+' '+d['current']+'\n')
print(d['current']);print('Installed',len(pending),'files; backup',backup)
