from pathlib import Path
import json,re,contextlib,io
exec(Path('D:/aramada/scripts/build-bajoran-redesign-v3.py').read_text().split('ROOT=')[0])
r=Path('D:/armadaIII');repo=Path('D:/aramada');o=Path('D:/Xaramada-Modwork/riker-galaxyx');o.mkdir(exist_ok=True)
def put(rel,t):
 p=o/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='latin1')
with contextlib.redirect_stdout(io.StringIO()):m=IO().read_file(str(r/'SOD/fgalaxyx.sod'))
a={n['id'].lower()for n in m.nodes};hps=['hp01','hp16','hp04','hp08','hp39','hp07'];assert set(hps)<=a,(set(hps)-a)
textures={p.stem.lower()for p in(r/'Textures').rglob('*.tga')};missing=[]
for n in m.nodes:
 if n['type']=='MESH':
  tx=n['data']['texture']
  if tx and tx.lower()not in textures:missing.append(tx)
assert not missing,missing
# Five offensive banks (Galaxy has two), plus native cloaking in slot six.
t='''#include "fgalaxyx.odf"
unitName = "Cpt William T Riker"
label = "Cpt William T Riker - USS Enterprise-D Galaxy-X"
tooltip = "Cpt William T Riker - Galaxy-X"
verboseTooltip = "Three-nacelle Enterprise-D refit. Five offensive banks: two phasers, two photon launchers and a heavy phaser cannon; cloaking device. Buildable hero."
baseName = "fgalaxyx"
race = "federation"
isHero = 1
possibleCraftNames = "USS Enterprise NCC-1701-D - Riker"
maxHealth = 15000
shieldRate = 150
maxSpecialEnergy = 15000
specialEnergyRate = 150
dilithiumCost = 4470
metalCost = 670
latinumCost = 0
biomatterCost = 0
crewCost = 856
officerCost = 10
buildTime = 120
hotkeyLabel = ""
'''
for i,(w,hp)in enumerate(zip(['fgalaxyxphas','fgalaxyxphot','fgalaxyxphas','fgalaxyxphot','fgalxcannon','gkcloak'],hps),1):t+=f'weapon{i} = "{w}"\nweaponHardpoints{i} = "{hp}"\n'
for action in ['Select','Acknowledge','Attack','Stop','Move','Repair','RedAlert','YellowAlert','GreenAlert','Transport','SelfDestruct','Decommission']:t+=f'event{action} = "XV_fentdx_{action}"\n'
put(Path('odf/ships/xhfriker.odf'),t)
p=r/'odf/stations/fyard3.odf';t=p.read_text(encoding='latin1');assert not re.search(r'buildItem12\s*=',t,re.I);put(p.relative_to(r),t+'\nbuildItem12 = "xhfriker"\n')
for p in(r/'techtree').glob('*.tt'):
 t=p.read_text(encoding='latin1');match=re.search(r'^xhfhero\.odf[ \t]+([^\r\n]*)',t,re.M|re.I)
 if match:put(p.relative_to(r),t+'\n// Riker Galaxy-X hero; same availability as Federation command hero.\nxhfriker.odf '+match.group(1)+'\n')
p=r/'Sprites/gui_global.spr';t=p.read_text(encoding='latin1');put(p.relative_to(r),t+'\n// Riker Galaxy-X hero build icon; model uses existing Galaxy-X wireframes.\n@reference=64\n@tmaterial=default\nb_xhfriker gbfgalaxyx 0 0 64 64\n')
report={'target':str(r),'unit':'xhfriker','displayName':'Cpt William T Riker','producer':'fyard3','model':'fgalaxyx','sourceListing':'https://armadafiles.com/files/armada-2/ships/federation/tng-ds9-voy-and-future/page-19','modelNote':'Existing installed Galaxy-X model reused; Armada Files indexed listing confirms Galaxy-X All Good Things variant. Direct site pages returned 502; no replacement archive downloaded.','galaxyOffensiveBanks':2,'heroOffensiveBanks':5,'cloak':'gkcloak','hardpointsValidated':hps,'startingHeroAdded':False,'voiceNote':'Existing Federation command event set reused; no actor voice generated.','gameplayVerified':False};(repo/'reports/riker-galaxyx.json').write_text(json.dumps(report,indent=2));print('Staged',len([p for p in o.rglob("*")if p.is_file()]),'files. Existing model textures and six weapon hardpoints valid.')

