from pathlib import Path
import re,json,datetime,shutil,subprocess
repo=Path('D:/aramada');root=Path('D:/armadaIII')
assert subprocess.check_output(['powershell','-NoProfile','-Command','@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'],text=True).strip()=='0','Close Armada III before installing.'
exec((repo/'scripts/audit-borg-sequence-20261028.py').read_text(encoding='utf-8-sig').split('reports=[]')[0])
backup=Path('D:/Xaramada-Modwork/backups')/('all-ai-economy-trade-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));pending={};reports=[];errors=[]
specs={'federation':('f','fed'),'klingon':('k','kling'),'romulan':('r','rom'),'cardassian':('c','card'),'dominion':('d','dominion'),'borg':('b','borg'),'breen':('br','breen'),'bajoran':('bj','bajoran')}
pat=r'^\s*"([^"]+)"\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,'
def parse(t):return [(m[1],*map(int,m.groups()[1:]))for m in re.finditer(pat,t,re.M)]
def fmt(rows):return '// Economy-first home-base build sequence; retain small escorts before later attack fleets.\n#include "aipdef.h"\nint checkTechnologyAvailable = 1;\nWay_Better_Build_List_Element the_build_list[MAX_ELEMENTS] =\n{\n'+'\n'.join('    "'+n+'", '+', '.join(map(str,(c,b,m,l)))+','for n,c,b,m,l in rows)+'\n};\n'
for faction,(prefix,race)in specs.items():
 base=prefix+'base';const=prefix+'const';mine=prefix+'mining';freight=prefix+'freight';orbital='bbase2'if faction=='borg'else prefix+'orbital';yard=prefix+'yard';colony=prefix+'colony';destroy='bjinterceptor'if faction=='bajoran'else prefix+'destroy'
 for p in sorted((root/'AI/AIPs').glob(faction+'_*list.aip')):
  old=parse(p.read_text(encoding='latin1'));remaining=list(old);first=[];available={Path(v).stem.lower()for k,v in cache[race].items()if re.fullmatch('standardunits[0-9]+',k)};visiting=set()
  def ensure(name,count=1):
   if name in visiting:raise AssertionError((p.name,'Cycle',name))
   if name not in available:
    visiting.add(name);gate,deps=tech.get(name,(0,[]));assert name in idx and gate>=0,(p.name,name,'Unavailable')
    for dep in deps:
     if dep not in available:ensure(dep)
    if not(producers.get(name,set())&available):
     candidates=[n for n,c,b,m,l in remaining if n in producers.get(name,set())and n not in visiting]
     assert candidates,(p.name,name,'No reachable producer',producers.get(name))
     candidates.sort(key=lambda n:(len(set(tech.get(n,(0,[]))[1])-available),len(tech.get(n,(0,[]))[1])))
     ensure(candidates[0])
    visiting.remove(name)
   match=next((i for i,x in enumerate(remaining)if x[0]==name and x[2]==0),None)
   if match is not None:remaining.pop(match)
   first.append((name,count,0,-1,0));available.add(name)
  # Economy and colony access before a two-ship home escort, followed by trade.
  for name,count in [(base,1),(const,2),(mine,1),(freight,2),(orbital,1),(yard,1),(colony,1),(freight,3),(destroy,2)]:ensure(name,count)
  trade=[]
  if faction not in ['borg','breen']:
   for name,count in [(prefix+'trading',1),(prefix+'cargo',2)]:ensure(name,count);trade.append(name)
  elif faction=='breen':
   # Breen's established Ferengi service branch provides cargo ships.
   for name,count in [('xfgmerc',1),('xfgconst',1),('xfgserv',1),('xfgtrade',2)]:ensure(name,count);trade.append(name)
  # Keep repair-yard prerequisite ahead of repair-craft requests after the latest unlock change.
  new=list(first);done={Path(v).stem.lower()for k,v in cache[race].items()if re.fullmatch('standardunits[0-9]+',k)}|{x[0]for x in first};moves=[]
  def append_existing(row,stack=()):
   name=row[0]
   if name not in done:
    gate,deps=tech.get(name,(0,[]));assert gate>=0,(p.name,name,'Disabled')
    for dep in deps:
     if dep not in done:
      i=next((i for i,x in enumerate(remaining)if x[0]==dep),None);assert i is not None,(p.name,name,dep)
      moved=remaining.pop(i);append_existing(moved,stack+(name,));moves.append(dep)
    assert producers.get(name,set())&done,(p.name,name,'Missing producer')
   n,c,b,m,l=row
   if n in [mine,orbital,prefix+'trading']:b=0
   new.append((n,c,b,m,l));done.add(n)
  while remaining:append_existing(remaining.pop(0))
  assert len(new)<=200
  # Validate every row again against the completed native sequence.
  avail={Path(v).stem.lower()for k,v in cache[race].items()if re.fullmatch('standardunits[0-9]+',k)}
  for i,row in enumerate(new):
   n=row[0]
   if n not in avail:
    gate,deps=tech.get(n,(0,[]));assert gate>=0 and set(deps)<=avail and producers.get(n,set())&avail,(p.name,i,n)
   avail.add(n)
  pending[p.relative_to(root)]=fmt(new);reports.append({'profile':p.name,'steps':len(new),'opening':first,'tradeUnits':trade,'prerequisitesMovedEarlier':moves,'homeResourcePlacementBase':0,'issues':[]})
# 8472 keeps its consumed-producer sequence, adding a third collector before combat.
for p in sorted((root/'AI/AIPs').glob('species8472_*list.aip')):
 rows=parse(p.read_text(encoding='latin1'));at=next(i for i,row in enumerate(rows)if row[0]=='714const')+1
 extra=[('8472_passive',2,0,-1,0),('8472_active',2,0,-1,0),('8472_collector',3,0,-1,0),('8472_active',2,0,-1,0)]
 rows[at:at]=extra;assert len(rows)<=200;pending[p.relative_to(root)]=fmt(rows);reports.append({'profile':p.name,'steps':len(rows),'openingExtra':extra,'preservesConsumedProducerReplacement':True,'trade':'No native 8472 cargo/trade system; not fabricated','issues':[]})
# Native site selection: higher distance weight explicitly means prefer nearby resource sites.
configs=['newdefault.aip','a2_aggressive.aip','a2_defensive.aip','a2_exploration.aip','a2_hard_aggressive.aip','a2_hard_defensive.aip','a2_hard_exploration.aip','a2_modified_aggressive.aip','a2_modified_defensive.aip','a2_modified_exploration.aip','a2_very_aggressive.aip'];cfgrows=[]
settings={'resource_dilithium_tendency':'2.0','resource_latinum_tendency':'1.0','resource_metal_tendency':'1.5','resource_distance_multiplier':'20000.0','resource_enemy_penalty':'300.0','MAX_EXEC_RESOURCE':'3','MAX_EVAL_RESOURCE':'20'}
for name in configs:
 rel=Path('AI/AIPs')/name;p=root/rel;t=p.read_text(encoding='latin1');changes={}
 for key,value in settings.items():
  pattern=r'(?mi)^(\s*(?:int|double)\s+'+re.escape(key)+r'\s*=\s*)([^;]+);';m=re.search(pattern,t)
  if m:changes[key]={'before':m[2].strip(),'after':value};t=re.sub(pattern,lambda m:m[1]+value+';',t)
 pending[rel]=t;cfgrows.append({'file':name,'changes':changes})
for rel,t in pending.items():
 p=root/rel;b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b);data=t.replace('\r','').replace('\n','\r\n').encode('latin1');p.chmod(0o666);p.write_bytes(data);out=repo/'bajor/overlay'/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
report={'backup':str(backup),'profiles':reports,'resourceProfiles':cfgrows,'runtimeVerified':False,'limitations':['Home-base bias is not a hard distance cutoff and cannot guarantee every moon is occupied before combat. No impossible fixed mining count is imposed on maps with few moons.','Native trade route selection rejects enemy stations; allied-route formation requires compatible stations in the match. AIP lists cannot condition cargo construction on ally presence.','Borg has no native trading station; its existing assimilated economy branch is retained. 8472 has no native colony/trade system.','Generic strategic AIPs are shared defaults; campaign-specific build lists are not edited.'],'tradeNativeEvidence':'CargoShipProcess::Update_Cargo_Goal calls TradingStation::GetNearestTradingStation; native station search checks GameObject::isEnemy.'};(repo/'reports/all-ai-economy-trade-20261028.json').write_text(json.dumps(report,indent=2))
p=repo/'status.json';j=json.loads(p.read_text(encoding='utf-8-sig'));j['current']='Economy-first AI patch installed: 45 skirmish build profiles and 11 native resource-priority configs. Local mining/metal and early colony+3 freighters before bulk fleets; small two-ship escorts retained; native trade/cargo promoted where supported. Missing repair-yard prerequisites moved before repair ships. Nearby resource-site bias strengthened, latinum enabled. No fixed all-moons guarantee; native allied route behavior needs gameplay check.';p.write_text(json.dumps(j,indent=2))
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n'+datetime.datetime.now().isoformat()+' '+j['current']+'\n')
print(json.dumps({'profiles':len(reports),'resourceConfigs':len(cfgrows),'files':len(pending),'issues':errors}))
