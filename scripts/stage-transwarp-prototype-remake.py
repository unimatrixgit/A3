from pathlib import Path
import re,json
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
stage=Path('D:/Xaramada-Modwork/transwarp-prototype-remake');files=[]
def put(rel,t):
 p=stage/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='latin1');files.append(str(rel))
# Ship-local aliases keep other Borg ability buttons unchanged.
for n,base,slot in [('xbtpblue','gborgbor',4),('xbtpgreen','xacgreen',3),('xbtpregen','gregen',6),('xbtpwarp','gtwarpd',5)]:
 put(Path('odf/special_weapons')/(n+'.odf'),f'#include "{base}.odf"\nbuttonSlot = {slot}\npopupSlot = {slot}\nhotkeyLabel = "HOTKEY_F{slot}"\n')
p=idx['brenborg.odf'];t=p.read_text(encoding='latin1');t=re.sub(r'^\s*weapon(?:Hardpoints)?\d+\s*=.*(?:\r?\n|$)','',t,flags=re.M|re.I)
for key,val in [('maxSpecialEnergy',3000),('specialEnergyRate',30),('maxExtraWeapons',2)]:
 t=re.sub(r'^\s*'+key+r'\s*=.*$',f'{key} = {val}',t,flags=re.M|re.I)if re.search(r'^\s*'+key+r'\s*=',t,re.M|re.I)else t+f'\n{key} = {val}\n'
weapons=[('bt4phas','hp10'),('bt4phas','hp11'),('bt4phas','hp12'),('bt4phas','hp13'),('bc2phot','hp08" "hp09'),('bc2phot','hp14" "hp15'),('xbtpgreen','hp16'),('xbtpblue','hp16'),('xbtpregen','hp16'),('xbtpwarp','hp16'),('gTechAssimBeam','hp16'),('gselfdes','hp16')]
t+='\n// Prototype remake:4 beam banks,2 torpedo launchers,blue and green beams,regeneration,transwarp,tech capture.\n'
for i,(w,hp)in enumerate(weapons,1):assert w.lower()+'.odf'in idx or w.startswith('xbtp');t+=f'weapon{i} = "{w}"\nweaponHardpoints{i} = "{hp}"\n'
put(p.relative_to(root),t)
p=idx['gtechassim.odf'];t=p.read_text(encoding='latin1')
if not any(v.lower()=='brenborg'for k,v in props('gTechAssim').items()if k.startswith('assignclass')):
 slot=max(int(x)for x in re.findall(r'^assignClass(\d+)\s*=',t,re.M|re.I))+1;t+=f'\nassignClass{slot} = "brenborg"\n'
put(p.relative_to(root),t)
# Match the model hardpoints already used by the live ship.
assert all(h in props('brenborg').get('weaponhardpoints2','')for h in ['hp10','hp11','hp12','hp13'])
report=dict(stage=str(stage),files=files,ship='brenborg',beamBanks=4,torpedoLaunchers=2,capturedWeaponSlots=2,energyCapacity=3000,energyRegeneration=30,formula='(4 + captured slots) *500 capacity;*5 regeneration',installed=False,gameplayVerified=False,notes=['Ship only; Technology Assimilator assignClass includes prototype.','Transwarp and self-destruct retained.','Blue beam added only to this prototype,not cubes.','Button slots:green3,blue4,transwarp5,regeneration6,tech7;selfdestruct10.','Continuous toggle drains can exceed regeneration; reserve is finite.'])
(repo/'reports/transwarp-prototype-remake.json').write_text(json.dumps(report,indent=2));sfile=repo/'status.json';s=json.loads(sfile.read_text(encoding='utf-8-sig'));s['current']='Transwarp Prototype SHIP remake staged:4beam/2torpedo,blue+green,regeneration,transwarp,2captured slots,3000energy/30regen. Waiting for game closure;not installed.';sfile.write_text(json.dumps(s,indent=2));print('Staged',len(files),'files;ship-only loadout ready.')

