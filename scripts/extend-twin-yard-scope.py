"""Add matching standalone research/HWP art and mining-station scale updates."""
from pathlib import Path
exec(Path('D:/aramada/scripts/nexus-common.py').read_text())
stage=repo/'patches/twin-yards-20261025';overlay=stage/'overlay';d=json.loads((stage/'design.json').read_text());pending={}
for p in(overlay/'odf').rglob('*.odf'):idx[p.stem.lower()]=root/p.relative_to(overlay);pending[p.relative_to(overlay).as_posix()]=p.read_text(encoding='latin1')
assets=d['assets'];new=d['newUnits'];research=[]
for code,units in RESEARCH.items():
 for n in units:
  if n=='brresear2'and not ordered(P[n]):continue
  assets[n]={'unit':n,'kind':'research','theme':code,'donor':n,'name':P[n].get('unitname',n)};research.append(n)
for n,code in [('xfomegalab','f'),('xbomegalab','b')]:assets[n]={'unit':n,'kind':'research','theme':code,'donor':n,'name':P[n].get('unitname',n)};research.append(n)
for code in ['fg','bg','br']:
 n={'fg':'tyfghwp','bg':'tybghwp','br':'tybrhwp'}[code];donor='chwp';t=clean(source(donor),r'buildItem\d+|secondaryBuildItem\d+')
 for i in range(1,7):
  # Keep the established HWP damage/cadence; faction effects are selected by ordnance.
  w='ty'+code+('beam'if i<=3 else'torp'if i<=5 else'rapid');original='xp4b'if i<=3 else'xp4t'if i<=5 else'xp4r'
  if w not in idx:
   ordnance=P[BEAMS[code]if i<=3 else TORPS[code]]['ordname'];emit(w,update(source(original),{'ordName':q(ordnance)}),'special_weapons');new.append(w)
  t=put(t,'weapon'+str(i),q(w))
 title='Thot Gor Heavy Weapons Platform'if code=='br'else'Liquidator Heavy Weapons Platform'
 vals={'race':q(RACE[code]),'unitName':q(title),'tooltip':q(title),'verboseTooltip':q(title+'\\nHeavy defensive fire support\\nFortified batteries protect the frontier.'),'dilithiumCost':0 if code=='fg'else 150,'metalCost':0 if code=='fg'else 300,'latinumCost':450 if code=='fg'else 0,'biomatterCost':0}
 t=update(t,vals);emit(n,t);assets[n]={'unit':n,'kind':'hwp','theme':code,'donor':donor,'name':title};new.append(n)
 candidates=d['constructorTypes'][code];owner=next((u for u in candidates if len(ordered(props(u)))<14),None);assert owner,('HWP menu full',code);emit(owner,menu(raw(owner),[v for i,v in ordered(props(owner))]+[n]),'ships')
for code,n in [('f','fhwp'),('b','bhwp'),('k','khwp'),('r','rhwp'),('c','chwp'),('d','dturret3'),('bj','bjhwp')]:assets[n]={'unit':n,'kind':'hwp','theme':code,'donor':n,'name':P[n].get('unitname',n)}
mining=[]
for n,p in P.items():
 if n in ['brecycle','btechass']:continue
 if p.get('classlabel')in ['mining','planetminingbase']or n in ['forbital','borbital','bbase2','korbital','rorbital','corbital','dorbital','bjorbital','brorbital']or n.startswith(('xfgmetal','xbgmetal')):
  if '/stations/'not in str(idx[n]).replace('\\','/'):continue
  t=update(raw(n),{'ScaleSOD':format(float(p.get('scalesod',1))*1.15,'.12g'),'footprintBuffer':format(float(p.get('footprintbuffer',0).rstrip('fF;'))*1.15,'.12g')});emit(n,t);mining.append(n)
for tree in(overlay/'techtree').glob('*.tt'):
 t=tree.read_text(encoding='latin1')
 for n in new:
  if re.search(r'(?mi)^'+n+r'\.odf[ \t]',t):continue
  code=assets[n]['theme']if n in assets else None;req=d['yards'][code][0]if code else None;t+='\n'+n+'.odf '+('0'if not req or tree.stem=='fulltech'else'1 '+req+'.odf')+'\n'
 tree.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'))
for rel,t in pending.items():p=overlay/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'))
d['assets']=assets;d['newUnits']=list(dict.fromkeys(new));d['researchStations']=research;d['miningSizeChanges']=mining;d['centralReference']='Each faction native starbase';d['yardReference']='Native original shipyard meshes, two production/repair wings';d['biodome']=False;(stage/'design.json').write_text(json.dumps(d,indent=2));print(json.dumps({'models':len(assets),'researchStations':len(research),'miningStations':len(mining)}))

