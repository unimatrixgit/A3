from pathlib import Path
import json,re,math,shutil,hashlib
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
root=Path('D:/ArmadaLab');idx={p.name.lower():p for p in(root/'odf').rglob('*.odf')};cache={}
mode=repo/'modes/last-man-standing';stage=root/'Development/stage';snap=stage.parent/'source-snapshot';profiles={
'federation':('xhfhero','fconst',['fdestroy','fcruise1','fbattle'],['fbase','fmining','forbital','fyard0','fyard','fresear','ffreight','ffreight','fconst']),
'borg':('blocutus','bconst',['bdestroy','bcruise1','bbattle1'],['bbase','bmining','bbase2','byard','bresear','bfreight','bfreight','bconst']),
'klingon':('xhkhero','kconst',['kdestroy','kcruise1','kbattle'],['kbase','kmining','korbital','kyard','kresear','kfreight','kfreight','kconst']),
'romulan':('xhrhero','rconst',['rdestroy','rcruise1','rbattle'],['rbase','rmining','rorbital','ryard','rresear','rfreight','rfreight','rconst']),
'cardassian':('xhchero','cconst',['cdestroy','ccruise1','cbattle'],['cbase','cmining','corbital','cyard','cresear','cfreight','cfreight','cconst']),
'dominion':('xhdhero','dconst',['ddestroy','dcruise1','dbattle'],['dbase','dmining','dorbital','dyard','dresear','dfreight','dfreight','dconst']),
'breen':('xhbrhero','brconst',['brdestroy','brcruise1','brbattle'],['brbase','brmining','brorbital','bryard','brresear','brfreight','brfreight','brconst']),
'bajoran':('bjnerys','bjconst',['bjinterceptor','bjcruiser','bjbattle'],['bjbase','bjmining','bjorbital','bjyard','bjresear','bjfreight','bjfreight','bjconst']),
'species8472':('xhshero','714const',['8472_destroy','8472_cruise1','8472_battle'],['8472_mothership','8472_transmuter','8472_collector','8472_collector','8472_basicresearch','714const'])}
config=dict(minimumRelocationDistance=2000,minimumEnemyDistance=1200,factions={});manifest=[]
for race,(hero,builder,escorts,rebuild)in profiles.items():
 ids=[hero,builder]+escorts+rebuild
 for n in ids:
  assert n.lower()+'.odf'in idx,n
  p=idx[n.lower()+'.odf'];rel=p.relative_to(root);dst=snap/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst);manifest.append(dict(file=str(rel),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 totals={}
 for name,field in [('dilithium','dilithiumcost'),('metal','metalcost'),('latinum','latinumcost'),('biomatter','biomattercost'),('crew','crewcost'),('officers','officercost')]:
  amount=sum(float(props(n).get(field,'0').rstrip('f'))for n in rebuild);totals[name]=int(math.ceil(amount*1.25/100)*100)if amount else 0
 config['factions'][race]=dict(hero=hero+'.odf',constructor=builder+'.odf',escorts=[n+'.odf'for n in escorts for _ in range(3)],rebuildResources=totals,rebuildPlan=rebuild)
(mode/'rescue-config.json').write_text(json.dumps(config,indent=2));
def lua(v):
 if isinstance(v,dict):return '{'+','.join('['+json.dumps(str(k))+']='+lua(x)for k,x in v.items())+'}'
 if isinstance(v,list):return '{'+','.join(lua(x)for x in v)+'}'
 if isinstance(v,str):return json.dumps(v)
 if isinstance(v,bool):return 'true'if v else'false'
 return str(v)
(mode/'RescueConfig.lua').write_text('LMSRescueConfig='+lua(config)+'\nreturn LMSRescueConfig\n');dest=stage/'missions/Last Man Standing';dest.mkdir(parents=True,exist_ok=True)
stationClasses={'shipyard','sensor','research','starbase','p_mining','mining','trading_station','minearray','upgrade','planet_shield'}
definitions=dict(builders={n:True for n in idx if props(n).get('classlabel')=='constructionrig'},
    structures={n:True for n,p in idx.items() if 'stations' in p.parts and props(n).get('classlabel') in stationClasses})
(mode/'NativeDefinitions.lua').write_text('LMSNativeDefinitions='+lua(definitions)+'\nreturn LMSNativeDefinitions\n')
for p in mode.glob('*.lua'):shutil.copy2(p,dest/p.name)
base=Path('D:/Xaramada-Modwork/last-man-standing/research/mmm-extracted/mmm')
for rel in ['missions/mmm_loader.dll','odf/system/mmm_holder.odf','odf/system/mmm_mapper.odf']:
 dst=stage/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(base/rel,dst)
for rel in ['RTS_CFG.h','mshell.set','label.map']:
 p=root/rel
 if p.exists():dst=snap/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
(repo/'reports/last-man-standing-stage.json').write_text(json.dumps(dict(stage=str(stage),sourceSnapshot=str(snap),factions=9,references=manifest,installed=False,gameplayVerified=False,missing=['Adapter engine API test','Validated mission map and safe relocation sites','Gameplay rescue/save-load test']),indent=2));print('Staged loader prerequisites,rule controller and9 validated faction rescue rosters. Live game unchanged.')
