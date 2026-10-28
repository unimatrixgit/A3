from pathlib import Path
import re,json,datetime,shutil,subprocess
root=Path('D:/armadaIII');repo=Path('D:/aramada');backup=Path('D:/Xaramada-Modwork/backups')/('repair-yard-production-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));idx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')}
assert subprocess.check_output(['powershell','-NoProfile','-Command','@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'],text=True).strip()=='0','Close game before installation.'
def props(n,seen=()):
 n=Path(n.strip('"')).stem.lower()
 if n in seen or n not in idx:return{}
 t=idx[n].read_text(encoding='latin1');d={}
 for inc in re.findall(r'(?mi)^\s*#include\s+"([^"]+)"',t):d.update(props(inc,seen+(n,)))
 for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t):d[k.lower()]=v.split('//')[0].strip().strip('"')
 return d
def put(t,k,v):
 pat=r'(?mi)^[ \t]*'+k+r'[ \t]*=[^\r\n]*';line=k+' = '+str(v)
 return re.sub(pat,lambda m:line,t)if re.search(pat,t)else t.rstrip()+'\n'+line+'\n'
def save(rel,data):
 p=root/rel
 if p.exists():b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);out=repo/'bajor/overlay'/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
def textsave(rel,t):save(rel,t.replace('\r','').replace('\n','\r\n').encode('latin1'))
# Faction-native repair craft for the two factions without an existing repair unit.
new=[]
for name,donor,race,title,bio in [('brrepair','brfreight','breen','Breen Restoration Tender',False),('xsrepair','8472_scout','species8472','Species 8472 Regeneration Tender',True)]:
 assert name not in idx,name
 d=props(donor);model=d.get('basename',donor);sod=root/'SOD'/(model+'.sod');assert sod.exists(),sod
 t=idx['fsrepair'].read_text(encoding='latin1');t=re.sub(r'(?mi)^[ \t]*weapon(?:Hardpoints)?\d+[ \t]*=[^\r\n]*','',t)
 values={'race':'"'+race+'"','unitName':'"'+title+'"','tooltip':'"'+title+'"','verboseTooltip':'"Mobile vessel repair support."','baseName':'"'+name+'"','ScaleSOD':d.get('scalesod','1'),'weapon1':'"gRepairBeam"','weaponHardpoints1':'"hp01"'}
 if bio:values.update(crewCost=0,maximumCrew=0,has_crew=0,dilithiumCost=0,metalCost=0,latinumCost=0,biomatterCost=400)
 for k,v in values.items():t=put(t,k,v)
 textsave(Path('odf/ships')/(name+'.odf'),t);save(Path('SOD')/(name+'.sod'),sod.read_bytes());idx[name]=root/'odf/ships'/(name+'.odf');new.append(name)
# Reuse the existing repair-craft GUI image with the atlas's own coordinate system.
rel=Path('Sprites/gui_global.spr');sprite=(root/rel).read_text(encoding='latin1');ref='64';material='default';sample=None
for line in sprite.splitlines():
 if line.lower().startswith('@reference='):ref=line.split('=',1)[1]
 if line.lower().startswith('@tmaterial='):material=line.split('=',1)[1]
 if re.match(r'^b_fsrepair\s',line,re.I):sample=(ref,material,line.split(None,1)[1])
assert sample
for name in new:
 sprite+='\n@reference='+sample[0]+'\n@tmaterial='+sample[1]+'\nb_'+name+' '+sample[2]+'\n'
 for i in range(1,6):sprite+=name+'w'+str(i)+' '+sample[2]+'\n'
textsave(rel,sprite)
# Existing repair units retain their research. New utility units unlock with their service yards.
for mode in ['tech1','earlytech','nosci','nosuper','nospweap','fulltech','freetech']:
 rel=Path('techtree')/(mode+'.tt');p=root/rel
 if not p.exists():continue
 t=p.read_text(encoding='latin1')
 for name,station in [('brrepair','xyr_br'),('xsrepair','mysyard')]:
  assert not re.search(r'(?mi)^'+name+r'\.odf\s',t)
  t+='\n'+name+'.odf '+('0'if mode in ['fulltech','freetech']else'1 '+station+'.odf')+'\n'
 textsave(rel,t)
crafts={'fremmeler':'fsrepair','mysyard':'xsrepair','xyr_f':'fsrepair','xyr_b':'xbrepair','xyr_k':'ksrepair','xyr_r':'rsrepair','xyr_c':'csrepair','xyr_d':'dsrepair','xyr_bj':'bjrepair','xyr_br':'brrepair','xyr_fg':'xfgrepair','xyr_bg':'xbgrepair'};rows=[]
for name,craft in crafts.items():
 p=idx[name];before=props(name);t=p.read_text(encoding='latin1');slots={int(k[9:]):v for k,v in before.items()if re.fullmatch('builditem[0-9]+',k)}
 if craft not in slots.values():t=put(t,'buildItem'+str(max(slots,default=-1)+1),'"'+craft+'"')
 for k,v in [('classLabel','"shipyard"'),('builder_ship',1),('alwaysRecomputeRallyPoint',1),('repairFacility',1)]:t=put(t,k,v)
 if not before.get('buildhardpoint'):t=put(t,'buildHardpoint','"'+before.get('repairhardpoint','hp01')+'"')
 textsave(p.relative_to(root),t);after=props(name)
 assert craft in [v for k,v in after.items()if re.fullmatch('builditem[0-9]+',k)]
 assert after.get('scalesod')==before.get('scalesod')and after.get('buildtime')==before.get('buildtime')and after.get('decommissionfacility')==before.get('decommissionfacility')
 assert re.search(r'(?mi)^b_'+craft+r'\s',sprite),craft
 rows.append({'station':name,'repairCraft':craft,'classLabel':'shipyard','sizeAndBuildTimePreserved':True,'existingProductionPreserved':True})
report={'backup':str(backup),'stations':rows,'newFactionUtilityShips':new,'existingCraftTechUnchanged':True,'runtimeVerified':False,'limitation':'Rally behavior must be checked in-game; these changes provide actual production and shipyard command support.'};(repo/'reports/repair-yard-production-20261028.json').write_text(json.dumps(report,indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='All 12 repair-capable stations now function as shipyards and produce a repair craft, with GUI and technology paths. Added faction-model Breen and 8472 repair tenders. Current reduced sizes/times and other production preserved. File checks passed; repaired-unit rally departure requires gameplay test.';p.write_text(json.dumps(s,indent=2))
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n'+datetime.datetime.now().isoformat()+' '+s['current']+'\n')
print(json.dumps({'stations':len(rows),'newRepairCraft':new,'runtimeVerified':False}))
