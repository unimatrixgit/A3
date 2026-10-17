from pathlib import Path
import re,json
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
rows=[];issues=[]
for n,cap in json.loads((repo/'reports/cube-tech-assimilation.json').read_text())['capturedSpecialCapacities'].items():
 d=props(n);ws=[(k,v)for k,v in d.items()if re.fullmatch('weapon[0-9]+',k)];slots={};collision=[]
 for k,v in ws:
  w=props(v)
  if w.get('special')=='1' and w.get('classlabel')!='detectcloak':
   slot=w.get('buttonslot');slots.setdefault(slot,[]).append(v)
 collision=[{'slot':k,'weapons':v}for k,v in slots.items()if len(v)>1]
 rows.append({'unit':n,'capacity':int(d['maxextraweapons']),'expectedCapacity':cap,'hasTechnologyBeam':any(v.lower()=='gtechassimbeam'for k,v in ws),'builtInButtonCollisionsBeforeFix':collision,'maximumActiveButtons':4+cap,'gameplayCaptureVerified':False})
 assert int(d['maxextraweapons'])==cap
 assert any(v.lower()=='gtechassimbeam'for k,v in ws)
rel=Path('odf/special_weapons/gTechAssimBeam.odf');t=(root/rel).read_text(encoding='latin1');t=re.sub(r'^buttonSlot\s*=.*$','buttonSlot = 7',t,flags=re.M|re.I);t+='\npopupSlot = 7\n';stage=Path('D:/Xaramada-Modwork/cube-tech-button-fix');p=stage/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='latin1')
out={'cubes':rows,'allCapacityFieldsValid':True,'allHaveNativeTechBeam':True,'stationAssignedCubeCount':16,'fixStaged':'Technology beam buttonSlot7/popupSlot7, resolves collision with adaptation slot6.','remainingLimitations':['Captured foreign weapons can share button slots with built-in abilities or other captured weapons.','Six captured plus four built-in active abilities may exceed HUD display capacity.','No claim of successful runtime capture without fresh-game testing.']};(repo/'reports/cube-captured-tech-audit.json').write_text(json.dumps(out,indent=2));f=repo/'status.json';s=json.loads(f.read_text(encoding='utf-8-sig'));s['current']='Cube captured-tech audit: all16 have native technology beam and requested capacities. Found shield adaptation/tech beam HUD slot6 collision; slot7 fix staged. Foreign captured-button collisions and Omega 10-active-button display remain unverified. Waiting for closure.';f.write_text(json.dumps(s,indent=2),encoding='utf-8');print('Audited 16 cubes; one native HUD collision fix staged; runtime UI limitations recorded.')
