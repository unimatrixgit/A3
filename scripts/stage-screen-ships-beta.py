from pathlib import Path
import json,re,copy,contextlib,io
from PIL import Image
exec(Path('D:/aramada/scripts/build-bajoran-redesign-v3.py').read_text().split('ROOT=')[0])
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
S=Path('D:/Xaramada-Modwork/content-expansion');O=Path('D:/Xaramada-Modwork/screen-ships-beta');O.mkdir(exist_ok=True)
tos=S/'tos-adversaries/extracted';d7=next(tos.rglob('KD7TOS.sod'));bird=next(tos.rglob('rwarbirdTOS.sod'))
units=[{'id':'xhftitan','name':'William T Riker - USS Titan','race':'federation','model':S/'luna/payload/SOD/fluna.sod','assets':S/'luna/payload','scale':.6,'hull':8000,'crew':338,'dil':3000,'metal':1000,'officers':12,'yard':'xflegacyyard','voice':'XV_fentdx_','weapons':['fc1phas','fc1phot','gselfdes','gtracbm'],'physics':'fcruiserphys.odf'},
{'id':'xhfdaedalus','name':'Daedalus Command Prototype','race':'federation','model':S/'daedalus/extracted/SOD/fdaedalus.SOD','assets':S/'daedalus/extracted','scale':1,'hull':2200,'crew':101,'dil':1000,'metal':350,'officers':5,'yard':'xflegacyyard','voice':'XV_fent_','weapons':['fentphas','frphot','gselfdes'],'physics':'ffrigatephys.odf'},
{'id':'xhkraptor','name':'Raptor Command Ship','race':'klingon','model':S/'kling-raptor/extracted/kraptor.sod','assets':S/'kling-raptor/extracted','scale':1.3,'hull':2500,'crew':45,'dil':1100,'metal':400,'officers':5,'yard':'kyard3','voice':'XV_xhkhero_','weapons':['kd1phas','kd1phot','gkcloak','gselfdes'],'physics':'kdestroyphys.odf'},
{'id':'xhkold7','name':'Koloth - D7 Command Cruiser','race':'klingon','model':d7,'assets':d7.parent.parent,'scale':.67,'hull':4800,'crew':160,'dil':2500,'metal':700,'officers':7,'yard':'kyard3','voice':'XV_xhkhero_','weapons':['kd1phas','kd1phot','gkcloak','gselfdes'],'physics':'kcruiserphys.odf'},
{'id':'xhrtOSbird','name':'Romulan Commander - TOS Warbird','race':'romulan','model':bird,'assets':bird.parent.parent,'scale':.35,'hull':3000,'crew':80,'dil':1200,'metal':500,'officers':7,'yard':'ryard3','voice':'XV_xhrhero_','weapons':['rc1phas','rc1phot','grcloak','gselfdes'],'physics':'rcruiserphys.odf'},
{'id':'xhrearlybird','name':'Minefield Command Warbird','race':'romulan','model':S/'rom-prebird/extracted/earlyRbop.SOD','assets':S/'rom-prebird/extracted','scale':1,'hull':2000,'crew':80,'dil':1000,'metal':350,'officers':5,'yard':'ryard3','voice':'XV_xhrhero_','weapons':['rc1phas','rc1phot','grcloak','gselfdes'],'physics':'rcruiserphys.odf'}]
# Resolve weapon/physics identifiers against this exact installation.
for u in units:
 for i,w in enumerate(u['weapons']):
  if w.lower()+'.odf'not in idx:
   ref='kcruise1'if u['race']=='klingon'else'rcruise1';u['weapons'][i]=props(ref).get('weapon1'if i==0 else'weapon2',w)
 assert all(w.lower()+'.odf'in idx for w in u['weapons']),u
 if u['physics'].lower()not in idx:u['physics']=props('kcruise1'if u['race']=='klingon'else'rcruise1').get('physicsfile')
def put(rel,t):
 p=O/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='latin1')
def saveTexture(path,name):
 dst=O/'Textures/RGB'/(name+'.tga');dst.parent.mkdir(parents=True,exist_ok=True)
 with Image.open(path)as im:im.convert('RGBA'if'A'in im.getbands()else'RGB').save(dst)
for u in units:
 n=u['id'].lower();u['id']=n
 with contextlib.redirect_stdout(io.StringIO()):m=IO().read_file(str(u['model']))
 nodes=copy.deepcopy(m.nodes);texidx={p.stem.lower():p for p in u['assets'].rglob('*')if p.suffix.lower()in['.tga','.bmp']};mapping={}
 for node in nodes:
  if node['type']=='MESH':
   d=node['data'];old=d['texture'];key=old.lower()
   if old and key not in mapping:
    assert key in texidx,(n,key);new=n+'t'+str(len(mapping));mapping[key]=new;saveTexture(texidx[key],new)
   if old:d['texture']=mapping[key]
   borg=d.get('borgification')
   if borg:
    bt=borg['texture'].lower()
    if bt in texidx:
     new=n+'b'+str(len(mapping));saveTexture(texidx[bt],new);borg['texture']=new
    else:borg['texture']=d['texture']

  elif isinstance(node.get('data'),str)and node.get('data')=='gplasml':node['data']='plasmasml'
 m.set_nodes(nodes);p=O/'SOD'/(n+'.sod');p.parent.mkdir(parents=True,exist_ok=True);w=IO();w.curr_sod_version=m.version
 with contextlib.redirect_stdout(io.StringIO()):w.write_file(m,str(p));check=IO().read_file(str(p))
 assert len(check.nodes)==len(nodes);hps=sorted(x['id']for x in nodes if re.fullmatch('hp[0-9]+',x['id'],re.I));assert hps
 t=f'#include "battle.odf"\nunitName = "{u["name"]}"\nlabel = "{u["name"]}"\ntooltip = "{u["name"]}"\nverboseTooltip = "Screen-era command variant. Native weapons and faction command voice fallback."\nrace = "{u["race"]}"\nbaseName = "{n}"\nisHero = 1\npossibleCraftNames = "{u["name"]}"\nmaxHealth = {u["hull"]}\nshieldRate = {u["hull"]/100}\nmaxSpecialEnergy = 2500\nspecialEnergyRate = 25\ndilithiumCost = {u["dil"]}\nmetalCost = {u["metal"]}\nlatinumCost = 0\nbiomatterCost = 0\ncrewCost = {u["crew"]}\nmaximumCrew = {u["crew"]}\nofficerCost = {u["officers"]}\nbuildTime = {max(60,int((u["dil"]+u["metal"])/35))}\nScaleSOD = {u["scale"]}\nphysicsFile = "{u["physics"]}"\ntrekPhysicsFile = "{u["physics"]}"\nhotkeyLabel = ""\n'
 for i,weap in enumerate(u['weapons'],1):t+=f'weapon{i} = "{weap}"\nweaponHardpoints{i} = "{hps[(i-1)%len(hps)]}"\n'
 for a in ['Select','Acknowledge','Attack','Stop','Move','Repair','RedAlert','YellowAlert','GreenAlert','Transport','SelfDestruct','Decommission']:t+=f'event{a} = "{u["voice"]+a}"\n'
 put(Path('odf/ships')/(n+'.odf'),t)
for yard in set(u['yard']for u in units):
 p=root/'odf/stations'/(yard+'.odf');t=p.read_text(encoding='latin1');slots=[int(i)for i in re.findall(r'^buildItem(\d+)\s*=',t,re.M|re.I)];nextslot=max(slots)+1
 for u in units:
  if u['yard']==yard:t+=f'\nbuildItem{nextslot} = "{u["id"]}"\n';nextslot+=1
 assert nextslot<=13,(yard,nextslot);put(p.relative_to(root),t)
for p in(root/'techtree').glob('*.tt'):
 t=p.read_text(encoding='latin1');added=[]
 for u in units:
  marker='xhfhero'if u['race']=='federation'else'xhkhero'if u['race']=='klingon'else'xhrhero';m=re.search(r'^'+marker+r'\.odf[ \t]+([^\r\n]*)',t,re.M|re.I)
  if m:added.append(u['id']+'.odf '+('0'if re.match(r'^0(?:\s|$)',m[1])else'1 '+u['yard']+'.odf'))
 if added:put(p.relative_to(root),t+'\n// Screen-era command additions.\n'+'\n'.join(added)+'\n')
# Icon renderer appends GUI mappings after model previews are produced.
serial=[{k:str(v)if isinstance(v,Path)else v for k,v in u.items()}for u in units];(repo/'reports/screen-ships-beta.json').write_text(json.dumps({'stage':str(O),'units':serial,'installed':False,'gameplayVerified':False,'notes':['Command names for unnamed designs are extrapolations, not canon claims.','Native role weapons and faction command voice fallbacks used; no actor imitation.','Namespace copies preserve source geometry; missing Borg textures fall back to normal skin.','Custom Daedalus damage emitter mapped to installed plasma emitter.'],'files':[str(p.relative_to(O))for p in O.rglob('*')if p.is_file()]},indent=2));print('Staged6 ship models, namespace textures, hero definitions, menu/tech links.')


