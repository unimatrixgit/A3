from pathlib import Path
import re,json
exec(Path('D:/aramada/scripts/prepare-bajoran-durability-research.py').read_text().split("for u in m['units']:")[0])
stage=Path('D:/Xaramada-Modwork/bajor-research-baseline');liveidx=dict(idx);keys=set('maxhealth maxshields maxhull maxcrew shieldgeneratorhitpoints engineshitpoints weaponshitpoints lifesupporthitpoints sensorshitpoints shieldrate hullrate repairrate maxspecialenergy specialenergyrate dilithiumcost metalcost latinumcost biomattercost crewcost officercost buildtime sanecrewlossmethod weaponred weaponyellow'.split());liveDiff=[]
for u in m['units']:
 a=props(u['odf']);b=props('fente'if u['odf']=='bjnerys'else u['parent'])
 for k in keys:
  if k in b and a.get(k)!=b[k]:liveDiff.append({'unit':u['odf'],'property':k,'bajor':a.get(k),'federation':b[k]})
for p in(stage/'odf').rglob('*.odf'):idx[p.name.lower()]=p
errors=[];checked=0;research=0
spr=(root/'Sprites/gui_global.spr').read_text();spriteNames=set(re.findall(r'(?m)^([^\s#@/]+)[ \t]+\S+[ \t]+\d+[ \t]+\d+[ \t]+\d+[ \t]+\d+',spr));tt={}
for l in(root/'techtree/tech1.tt').read_text(encoding='latin1').splitlines():
 a=l.split('//')[0].split()
 if len(a)>1 and a[0].endswith('.odf'):tt[a[0].lower()]=a[2:2+max(0,int(a[1]))]
for u in m['units']:
 n=u['odf'];a=props(n);b=props('fente'if n=='bjnerys'else u['parent'])
 for k in keys:
  if k in b:
   checked+=1
   if a.get(k)!=b[k]:errors.append({'unit':n,'mismatch':k,'bajor':a.get(k),'fed':b[k]})
 if n.startswith('bjpod'):
  for k in ['isshipupgrade','upgradelevel','upgrademultiplier','upgradesystem']:
   if k in b:
    research+=1
    if a.get(k)!=b[k]:errors.append({'unit':n,'researchMismatch':k})
  if a.get('race')!='"bajoran"':errors.append({'unit':n,'race':a.get('race')})
 base=a.get('basename','"'+n+'"').strip('"')
 if 'b_'+base not in spriteNames and 'b_'+n not in spriteNames:errors.append({'unit':n,'missingButton':base})
 slots=[]
 for k,v in a.items():
  if re.fullmatch(r'weapon\d+',k):
   if not v.strip('"'):errors.append({'unit':n,'emptyWeapon':k});continue
   if v.strip('"').lower()+'.odf'not in idx:errors.append({'unit':n,'missingWeapon':v})
   slots.append(int(k[6:]))
 if slots and sorted(slots)!=list(range(1,max(slots)+1)):errors.append({'unit':n,'weaponSlotGap':slots})
for n in ['bjyard','bjyard2','bjyard3']:
 if props(n).get('repairfacility')!='1':errors.append({'unit':n,'repairDisabled':True})
report={'liveComparisonDifferences':liveDiff,'stagedNumericPropertiesChecked':checked,'researchEffectPropertiesChecked':research,'errors':errors,'intentionalDifferences':['Bajor race, names, models, icons and voice events','Kira matches fente hero, not base destroyer','Bajor-specific special abilities retain Bj research IDs','Paired yards/research unlock together; no Federation legacy yard0','Bajor yards support repair, unlike current modded Federation yards','Freighter retains requested movement settings and mining-only layout'],'runtimeVerified':False}
(repo/'reports/federation-bajor-comparison.json').write_text(json.dumps(report,indent=2));print(json.dumps({'liveNumericDifferences':len(liveDiff),'stagedPropertiesChecked':checked,'researchSettingsChecked':research,'errors':errors}))

