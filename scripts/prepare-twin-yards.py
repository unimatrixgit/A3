"""Consolidate standalone native shipyards; never attach a yard as a research pod."""
from pathlib import Path
exec(Path('D:/aramada/scripts/nexus-common.py').read_text())
stage=repo/'patches/twin-yards-20261025';overlay=stage/'overlay';old=json.loads((repo/'reports/twin-yard-production-input.json').read_text());pending={}
names={'f':['Antares Fleet Yard','Copernicus Fleet Yard','McKinley Command Yard','Archer Legacy Yard','Sloan Special Projects Yard','Mars Utopia Planetia Yard I','Mars Utopia Planetia Yard II'],'b':['Assembly Matrix','Tactical Assembly Matrix','Omega Assimilation Yard'],'k':["B’rel Patrol Forge","Vor’cha Assault Forge",'Kahless Command Forge'],'r':['Valdore Patrol Yard',"D’deridex Fleet Yard",'Tal Shiar Command Yard'],'c':['Hideki Patrol Foundry','Galor Fleet Foundry','Obsidian Command Foundry'],'d':["Jem’Hadar Attack Yard",'Founder Heavy Yard','Great Link Command Yard'],'bj':['Dahkur Militia Yard','Shakaar Command Yard'],'br':['Thot Gor Fleet Yard'],'fg':["D’Kora Contract Yard",'Nog Industrial Exchange'],'bg':["D’Kora Contract Yard",'Nog Industrial Exchange']}
names={k:[x.replace('’',"'")for x in v]for k,v in names.items()}
repairs={'f':'Starbase 74 Service Dock','b':'Collective Regeneration Dock','k':"Qo\'noS Refit Dock",'r':"Ch\'Rihan Restoration Dock",'c':'Lakarian Service Dock','d':'Great Link Restoration Dock','bj':'Kendra Service Dock','br':'Confederacy Restoration Dock','fg':"Nog\'s Service Exchange",'bg':"Nog\'s Service Exchange"}
targets={k:list(v)for k,v in YARDS.items()};targets['f']+=['xflegacyyard','s31yard','mryfeda','mryfedb'];targets['d']=['dyard','dyard2','dyard3']
rosters={};support={};assigned={};assets={};retired={};weapons={};new=[];changes=[];baseline={n:{'file':idx[n].relative_to(root).as_posix(),'hash':hashlib.sha256(idx[n].read_bytes()).hexdigest(),'properties':d}for n,d in P.items()}
exempt={'fhwp','bhwp','khwp','rhwp','chwp','bjhwp','dturret3','unicomplex','brecycle','btechass'}
for code,ys in targets.items():
 for i,n in enumerate(ys):
  src='nxdheavy'if n=='dyard2'else n;m=next(m for m in old['modules']if m['unit']==src and m['role']=='yard');rosters[n]=m['ships'];support[n]=m['support']
  for ship in rosters[n]:assigned[ship]=n
  # Original production yards retain their economy, health, crew and build time.
  t=raw(n);t=clean(t,r'buildItem\d+|weapon\d+|weaponHardpoints\d+')
  t=menu(t,rosters[n]+support[n]);t=update(t,{'classLabel':q('shipyard'),'builder_ship':1,'research':0,'repairFacility':0,'decommissionFacility':0,'recrewRate':0,'unitName':q(names[code][i]),'tooltip':q(names[code][i]),'verboseTooltip':q(names[code][i]+'\\nFleet construction; research unlocks ships\\nTwin bays forge the next generation.')})
  for j,w in enumerate([BEAMS[code],BEAMS[code],TORPS[code]],1):t=put(t,'weapon'+str(j),q(w));t=put(t,'weaponHardpoints'+str(j),q('tygun'+str(j)))
  t=update(t,{'canAttack':1,'COMBAT':1,'ALERT':1,'weaponsHitPoints':max(500,float(P[n].get('weaponshitpoints',0)))})
  emit(n,t);assets[n]={'unit':n,'kind':'yard','theme':code,'donor':n,'name':names[code][i]}
 # Independent repair/recrew/decommission dock; no production menu.
 n='xyr_'+code;donor=ys[0];t=clean(raw(donor),r'buildItem\d+|secondaryBuildItem\d+');t=update(t,{'unitName':q(repairs[code]),'tooltip':q(repairs[code]),'verboseTooltip':q(repairs[code]+'\\nRepair, recrew and decommission\\nDamaged vessels return to service here.'),'builder_ship':0,'repairFacility':1,'decommissionFacility':1,'recrewRate':20,'crewCost':100,'maximumCrew':200,'buildTime':60})
 for key in ['dilithiumCost','metalCost','latinumCost','biomatterCost']:t=put(t,key,round(float(P[donor].get(key.lower(),0))*.8))
 emit(n,t);assets[n]={'unit':n,'kind':'service','theme':code,'donor':donor,'name':repairs[code]};new.append(n)
# Remove duplicated attack craft everywhere except explicit historical exemptions.
for n,d in P.items():
 if n in exempt or n in assets or d.get('race')=='species8472':continue
 entries=[v for i,v in ordered(d)];values=[v for v in entries if v not in assigned]
 if entries!=values:
  emit(n,menu(raw(n),values),'ships'if '/ships/'in str(idx[n]).replace('\\','/')else'stations');changes.append({'producer':n,'removed':[v for v in entries if v not in values]})
  if not values and d.get('classlabel')in ['shipyard','starbase']and not any(re.fullmatch('weapon[0-9]+',k)for k in d):retired[n]=assigned[next(v for v in entries if v in assigned)]
# Existing service-only Remmla is replaced by the new matching service dock.
retired['fremmeler']='xyr_f'
# Production-only docking removal. The Recycler and non-producing special stations are preserved.
for n,d in P.items():
 if n in exempt or n in assets or d.get('race')=='species8472':continue
 if d.get('classlabel')=='shipyard'and ordered(d):emit(n,update(raw(n),{'repairFacility':0,'decommissionFacility':0,'recrewRate':0}))
constructors={};second={'f':'fconst2','b':'bconst2','k':'kconst2','r':'rconst2','c':'xcconst2','d':'xdconst2','bj':'xbjconst2','br':None,'fg':'xfgconst2','bg':'xbgconst2'};third={'f':'xfuconst','b':'xbuconst','k':'xkuconst','r':'xruconst','c':'xcuconst','d':'xduconst','bj':'xbjuconst'}
for n,d in P.items():
 if d.get('classlabel')!='constructionrig'or d.get('race')=='species8472':continue
 values=list(dict.fromkeys(retired.get(v,v)for i,v in ordered(d)));emit(n,menu(raw(n),values),'ships')
for code,ys in targets.items():
 candidates=[x for x in [BUILD[code],second.get(code),third.get(code)]if x in idx];constructors[code]=candidates
 for target in ys+['xyr_'+code]:
  if any(target in dict(ordered(props(n))).values()for n in candidates):continue
  owner=next((n for n in candidates if len(ordered(props(n)))<14),None);assert owner,('No constructor button',code,target)
  emit(owner,menu(raw(owner),[v for i,v in ordered(props(owner))]+[target]),'ships')
# Rewrite producer gates, preserving actual research requirements and mode locks.
producer_refs={}
for n,d in P.items():
 matches=[v for i,v in ordered(d)if v in assigned]
 if matches and n not in exempt and n not in assigned.values()and(d.get('classlabel')=='shipyard'or n in retired or n in ['bbattle5','bbattle6','fbyard']):producer_refs[n]=assigned[matches[0]]
for file in [root/'techtree'/(s+'.tt')for s in ['tech1','earlytech','fulltech','nosci','nosuper','nospweap']]:
 out=[];seen=set()
 for line in file.read_text(encoding='latin1').splitlines():
  a=line.split('//')[0].split()
  if len(a)<2 or not a[0].lower().endswith('.odf'):out.append(line);continue
  n=Path(a[0]).stem.lower()
  if n in seen:continue
  seen.add(n);count=int(a[1]);deps=[Path(x).stem.lower()for x in a[2:2+max(0,count)]]
  if n in retired:out.append(n+'.odf -1 // Consolidated production');continue
  if n=='dyard2':count=2;deps=['dyard','dresear']
  if count<0:out.append(line);continue
  deps=[retired.get(x,producer_refs.get(x,x))for x in deps]
  if n in assigned:
   deps=[x for x in deps if x not in set(target for ys in targets.values()for target in ys)];deps.insert(0,assigned[n])
  deps=list(dict.fromkeys(x for x in deps if x!=n));out.append(n+'.odf '+('0'if file.stem=='fulltech'else str(len(deps))+(' '+' '.join(x+'.odf'for x in deps)if deps else'')))
 for n in new:
  code=assets[n]['theme'];deps=[targets[code][0]];out.append(n+'.odf '+('0'if file.stem=='fulltech'else'1 '+deps[0]+'.odf'))
 pending[file.relative_to(root).as_posix()]='\n'.join(out)+'\n'
for rel,t in pending.items():p=overlay/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'))
report={'status':'STAGED','yards':targets,'assets':assets,'rosters':rosters,'support':support,'attackAssignments':assigned,'retired':retired,'constructorTypes':constructors,'baseline':baseline,'duplicateCleanup':changes,'exemptStructures':sorted(exempt),'newUnits':new,'runtimeVerified':False,'researchConsolidation':False,'queue':'One production or repair queue per station; twin bays are one complete model.','references':['https://www.ditl.org/station-pictures.php?ClassID=drydock&ImageNo=1&ListID=Stations','https://www.ex-astris-scientia.org/schematics/starfleet_stations.htm']}
(stage/'design.json').write_text(json.dumps(report,indent=2));print(json.dumps({'yards':sum(map(len,targets.values())),'serviceDocks':len(new),'uniqueAttackShips':len(assigned),'retired':retired,'files':len(pending)}))
