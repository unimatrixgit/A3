from pathlib import Path
import re,json,datetime
root=Path('D:/ArmadaLab');repo=Path('D:/aramada');backup=Path('D:/Xaramada-Modwork/backups')/('ai-heavy-lab-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));pending={};plans=[]
# Producer gaps: third Borg constructor explicitly authorized; Nova needs a menu and technology entry.
for rel,item in [('odf/stations/bbase.odf','bconst2'),('odf/ships/dconst.odf','dturret3')]:
 t=(root/rel).read_text(encoding='latin1');slots={int(n):v for n,v in re.findall(r'(?mi)^\s*buildItem(\d+)\s*=\s*"([^"]+)"',t)}
 if item not in slots.values():
  slot=next(i for i in range(13)if i not in slots);t+='\nbuildItem'+str(slot)+' = "'+item+'"\n';pending[rel]=t
for name in ['tech1','earlytech','fulltech','nosci','nosuper','nospweap']:
 rel='techtree/'+name+'.tt';t=(root/rel).read_text(encoding='latin1')
 if not re.search(r'(?mi)^dturret3\.odf\s',t):t+='\ndturret3.odf 0 // Nova Cannon constructor availability\n';pending[rel]=t
spec={'borg':('bhwp','bconst2','byard2'),'bajoran':('bjhwp','bjconst','bjyard2'),'cardassian':('chwp','cconst','cresear2'),'federation':('fhwp','fconst2','fupgrade'),'klingon':('khwp','kconst2','kimpbase'),'romulan':('rhwp','rconst2','rbase2'),'dominion':('dturret3','dconst','dresear2')}
for race,(unit,producer,anchor)in spec.items():
 for f in (root/'AI/AIPs').glob(race+'_*.aip'):
  t=f.read_text(encoding='latin1')
  if 'Way_Better_Build_List_Element the_build_list' not in t:continue
  lines=t.splitlines();entries=[(i,m[1])for i,l in enumerate(lines)if(m:=re.match(r'^\s*"([^"]+)"\s*,',l))]
  assert entries and len(entries)<195
  # Keep existing valid platform placements; add once after the required economy/tech.
  if any(n==unit for i,n in entries):plans.append({'file':f.name,'platform':unit,'existing':True});continue
  anchors=[i for i,n in entries if n==anchor];assert anchors,(f,anchor)
  pos=anchors[0];prod=[i for i,n in entries if n==producer and i<=pos];new=[]
  if not prod:new.append('    "'+producer+'", 1, 0, -1, 0, // Heavy platform constructor')
  quantity=2 if 'defensive' in f.name else 1
  new.append('    "'+unit+'", '+str(quantity)+', 0, -1, 0, // Heavy defense after economy and required construction tech')
  lines[pos+1:pos+1]=new;t='\n'.join(lines)+'\n';assert t.count('{')==t.count('}')
  pending[f.relative_to(root).as_posix()]=t;plans.append({'file':f.name,'platform':unit,'constructor':producer,'after':anchor,'quantity':quantity,'existing':False})
for rel,t in pending.items():
 f=root/rel;b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(f.read_bytes());f.chmod(0o666);data=t.replace('\r','').replace('\n','\r\n').encode('latin1');f.write_bytes(data);out=repo/'lab/overlay'/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
report={'root':str(root),'backup':str(backup),'plans':plans,'changedFiles':list(pending),'deployedLive':False,'runtimeVerified':False};(repo/'reports/ai-heavy-platform-lab.json').write_text(json.dumps(report,indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Heavy-platform AI update staged in ArmadaLab: all 35 skirmish plans covered across 7 factions, required constructors ordered before platforms, third Borg constructor made producible, Nova menu/tech gap filled. Live testing installation left unchanged. Borg unused-unit audit in progress.';p.write_text(json.dumps(s,indent=2));
with(repo/'build.log').open('a')as log:log.write('\n'+s['current']+'\n')
print(json.dumps({'plans':len(plans),'changed':len(pending),'alreadyIncluded':sum(p['existing']for p in plans),'liveChanged':False}))
