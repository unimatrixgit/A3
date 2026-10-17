from pathlib import Path
import re,json,contextlib,io
exec(Path('D:/aramada/scripts/build-bajoran-redesign-v3.py').read_text().split('ROOT=')[0])
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
o=Path('D:/Xaramada-Modwork/enterprise-legacy-heroes');o.mkdir(exist_ok=True)
def put(rel,t):
 p=o/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='latin1')
heroes=[('xhfkirktos','fent','James T Kirk - Enterprise',2160,325),('xhfkirkrefit','fenta','James T Kirk - Enterprise A',2250,340),('xhfharriman','fentb','John Harriman - Enterprise B',3265,490),('xhfgarrett','fentc','Rachel Garrett - Enterprise C',3265,490),('xhfpicardd','fentd','Jean-Luc Picard - Enterprise D',3900,585)]
checks=[]
for unit,base,name,dil,metal in heroes:
 d=props(base)
 with contextlib.redirect_stdout(io.StringIO()):model=IO().read_file(str(root/'SOD'/(base+'.sod')))
 anchors={n['id'].lower()for n in model.nodes};assert'hp01'in anchors
 text=f'#include "battle.odf"\nunitName = "{name}"\nlabel = "{name}"\ntooltip = "{name}"\nverboseTooltip = "Enterprise command hero. Buildable at the Enterprise Legacy Yard."\nbaseName = "{base}"\nrace = "federation"\nisHero = 1\npossibleCraftNames = "'+name.split(' - ')[-1]+'"\nhotkeyLabel = ""\n'
 for key in ['maxHealth','shieldRate','maxSpecialEnergy','specialEnergyRate','crewCost','officerCost','buildTime','ScaleSOD']:
  if key.lower()in d:text+=key+' = '+d[key.lower()]+'\n'
 for key in ['physicsFile','trekPhysicsFile']:
  if key.lower()in d:text+=key+' = "'+d[key.lower()]+'"\n'
 text+=f'dilithiumCost = {dil}\nmetalCost = {metal}\nlatinumCost = 0\nbiomatterCost = 0\n'
 weapons=[]
 for key,w in sorted(d.items(),key=lambda x:int(x[0][6:])if re.fullmatch('weapon[0-9]+',x[0])else 999):
  if not re.fullmatch('weapon[0-9]+',key)or props(w).get('classlabel')=='fusingweapon':continue
  hp=d.get('weaponhardpoints'+key[6:],'hp01');names=re.findall(r'hp\d+',hp,re.I);names=[n for n in names if n.lower()in anchors]or['hp01'];weapons.append((w,names))
 if not any(w=='gselfdes'for w,h in weapons):weapons.append(('gselfdes',['hp01']))
 for i,(w,hps)in enumerate(weapons,1):text+=f'weapon{i} = "{w}"\nweaponHardpoints{i} = '+' '.join('"'+hp+'"'for hp in hps)+'\n'
 for action in ['Select','Acknowledge','Attack','Stop','Move','Repair','RedAlert','YellowAlert','GreenAlert','Transport','SelfDestruct','Decommission']:
  ev=d.get('event'+action.lower())or'XV_xhfhero_'+action;text+=f'event{action} = "{ev}"\n'
 put(Path('odf/ships')/(unit+'.odf'),text);checks.append({'unit':unit,'sourceModel':base,'name':name,'weaponCount':len(weapons),'fusionUpgradeRemoved':True})
t=(root/'odf/stations/fyard3.odf').read_text(encoding='latin1');t=re.sub(r'^\s*buildItem\d+\s*=.*$','',t,flags=re.M|re.I)
for key,val in [('unitName','Enterprise Legacy Yard'),('tooltip','Enterprise Legacy Yard'),('verboseTooltip','Historic Enterprise command ships; direct hero construction, repair and decommission.')]:t=re.sub(r'^\s*'+key+r'\s*=.*$','',t,flags=re.M|re.I)+f'\n{key} = "{val}"\n'
t+='\nbaseName = "fyard3"\n'
for i,n in enumerate(['fnxent']+[x[0]for x in heroes]):t+=f'buildItem{i} = "{n}"\n'
put(Path('odf/stations/xflegacyyard.odf'),t)
p=root/'odf/ships/fconst.odf';t=p.read_text(encoding='latin1');assert not re.search(r'^buildItem12\s*=',t,re.M|re.I);put(p.relative_to(root),t+'\nbuildItem12 = "xflegacyyard"\n')
p=root/'Sprites/gui_global.spr';t=p.read_text(encoding='latin1')+'\n// Enterprise Legacy Yard and direct hero build icons.\n@reference=64\n@tmaterial=default\nb_xflegacyyard gbfyard3 0 0 64 64\n'
for unit,base,*rest in heroes:t+=f'b_{unit} gb{base} 0 0 64 64\n'
put(p.relative_to(root),t)
for p in(root/'techtree').glob('*.tt'):
 t=p.read_text(encoding='latin1');m=re.search(r'^xhfhero\.odf[ \t]+([^\r\n]+)',t,re.M|re.I)
 if m:
  free=bool(re.match(r'^0(?:\s|$)',m[1]));t+='\nxflegacyyard.odf '+('0'if free else'1 fyard3.odf')+'\n'
  for unit,*rest in heroes:t+=unit+'.odf '+('0'if free else'1 xflegacyyard.odf')+'\n'
  put(p.relative_to(root),t)
report={'stage':str(o),'heroes':checks,'yard':'xflegacyyard','producer':'fconst','producerMenuItems':13,'existingArcherIncluded':True,'sources':['https://www.startrek.com/news/ships/enterprise-starfleets-finest-flagships','https://www.startrek.com/news/who-is-rachel-garrett'],'usesExistingModelsIconsVoices':True,'voiceNote':'Existing installed command audio reused; no claim of actor-specific Harriman/Garrett recordings.','files':[str(p.relative_to(o))for p in o.rglob('*')if p.is_file()],'installed':False,'gameplayVerified':False};(repo/'reports/enterprise-legacy-heroes.json').write_text(json.dumps(report,indent=2));print('Staged',len(report['files']),'files;',len(heroes),'new hero options plus existing Archer.')
