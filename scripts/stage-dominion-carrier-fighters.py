"""Adapt the native mobile-starbase launch approach without importing mod assets."""
from pathlib import Path
exec(Path('D:/aramada/scripts/build-native-faction-stations.py').read_text().split('for index,(n,a)in enumerate')[0])
stage=repo/'patches/dominion-carrier-launch-20261025';dest=stage/'overlay';sourceHashes={}
def emit(rel,t):
 path=dest/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'))
 if(root/rel).is_file():sourceHashes[rel]=hashlib.sha256((root/rel).read_bytes()).hexdigest()
carrier=(root/'odf/ships/xdcarrier.odf').read_text(encoding='latin1');p=yard_unit_properties('xdcarrier',globals());original=dict(p)
carrier=re.sub(r'(?mi)^\s*aiName\s*=[^\r\n]*','',carrier)
for k,v in {'classLabel':'"starbase"','physicsFile':'"'+p.get('trekphysicsfile','trek_sbattphys.odf')+'"','ship':1,'facility':0,'is_starbase':0,'builder_ship':1,'alwaysRecomputeRallyPoint':1,'buildItem0':'"xdcfighter"','buildHardpoint':'"hp18"','repairFacility':0,'decommissionFacility':0,'recrewRate':0,'maxCrewGain':0,'officerGain':0,'maximumUpgrades':0,'verboseTooltip':'"Dominion Carrier\\nLaunch Jem\'Hadar carrier fighters\\nThe Founders project power across the quadrant."'}.items():carrier=put(carrier,k,v)
emit('odf/ships/xdcarrier.odf',carrier)
fighter=(root/'odf/ships/xdofighter.odf').read_text(encoding='latin1');fp=yard_unit_properties('xdofighter',globals())
for k,v in {'unitName':'"Jem\'Hadar Carrier Fighter"','tooltip':'"Launch Jem\'Hadar Fighter"','verboseTooltip':'"Jem\'Hadar Carrier Fighter\\nCarrier-deployed attack craft\\nVictory is life."','race':'"dominion"','baseName':'"'+fp.get('basename','xdofighter')+'"','dilithiumCost':25,'metalCost':10,'latinumCost':0,'biomatterCost':0,'crewCost':5,'maximumCrew':5,'officerCost':1,'buildTime':6,'hotkeyLabel':'"HOTKEY_F1"'}.items():fighter=put(fighter,k,v)
emit('odf/ships/xdcfighter.odf',fighter)
model=native(p.get('basename','xdcarrier'));nodes={n['id'].lower()for n in model.nodes};assert'hp18'in nodes and'hp19'in nodes
assert(p.get('trekphysicsfile','trek_sbattphys.odf').removesuffix('.odf'))in{q.stem.lower()for q in(root/'odf').rglob('*.odf')}
sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1');m=re.search(r'(?mi)^b_xdofighter[ \t]+([^\r\n]+)',sprite);assert m
sprite+='\n@reference=64\n@tmaterial=default\nb_xdcfighter '+m[1]+'\n'
for i in range(1,6):
 m=re.search(r'(?mi)^xdofighterw'+str(i)+r'[ \t]+([^\r\n]+)',sprite)
 if m:sprite+='xdcfighterw'+str(i)+' '+m[1]+'\n'
emit('Sprites/gui_global.spr',sprite)
for tree in ['tech1','earlytech','fulltech','nosci','nosuper','nospweap']:
 rel='techtree/'+tree+'.tt';t=(root/rel).read_text(encoding='latin1');m=re.search(r'(?mi)^xdcarrier\.odf\s+(-?\d+)',t);assert m
 t+='\nxdcfighter.odf '+('-1'if int(m[1])<0 else'0'if tree=='fulltech'else'1 xdcarrier.odf')+' // Dominion carrier launch craft\n';emit(rel,t)
ai=[]
for f in(root/'AI/AIPs').glob('dominion_*list.aip'):
 t=f.read_text(encoding='latin1')
 if re.search(r'(?m)^\s*"xdcarrier"\s*,',t):
  t=t.replace('};','    "xdcfighter", 6, 0, -1, 0,\n};');emit(f.relative_to(root).as_posix(),t);ai.append(f.name)
report={'status':'PASS','description':'Dominion carrier equipped with native onboard fighter production: player-owned Jem\'Hadar fighters, 6-second launch queue. Carrier movement and combat require in-game verification.','files':{f.relative_to(dest).as_posix():hashlib.sha256(f.read_bytes()).hexdigest()for f in dest.rglob('*')if f.is_file()},'sourceHashes':sourceHashes,'baselineUpdates':['xdcarrier','xdcfighter'],'attackAssignments':{'xdcfighter':'xdcarrier'},'originalCarrierProperties':original,'launchHardpoint':'hp18','fighter':{'unit':'xdcfighter','buildTime':6,'crew':5,'dilithium':25,'metal':10},'aiProfiles':ai,'reference':'http://armadafiles.com/files/armada-2/ships/federation/tng-ds9-voy-and-future/typhon-and-valkyrie/details','externalAssetsImported':False,'runtimeVerified':False};(stage/'patch.json').write_text(json.dumps(report,indent=2));print(json.dumps({'status':'PASS','files':len(report['files']),'aiProfiles':len(ai),'launch':'Jem\'Hadar carrier fighter'}))
report['extraAiTargets']={'dominion':['xdcarrier','xdcfighter']};(stage/'patch.json').write_text(json.dumps(report,indent=2))
