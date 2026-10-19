from pathlib import Path
import re,json,math,datetime,sys,contextlib,io
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils')
from sod_io import SodIO
class Reader(SodIO):
 def read_unknown_legacy_data(self,s):return [] if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
repo=Path('D:/aramada');backup=Path('D:/Xaramada-Modwork/backups')/('yard2-special-rebalance-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));all_pending=[];report=[]
choices={'brbattle2':'brgshieldd','cbattle':'gplasmabank','cbattle2':'gplasmabank','chutet':'gaccelcannon','kbattle2':'gplasmac','kvodleh':'gplasmac','kvood':'gplasmac','kbatleth':'gplasmac','rbattle2':'gplasmaw','rdread':'gplasmaw'}
def num(v,key,default=0):
 try:return float(str(v.get(key,default)).rstrip('fF;'))
 except:return default
def put(t,k,v):return re.sub(r'(?mi)^[ \t]*'+re.escape(k)+r'[ \t]*=[^\r\n]*','',t)+'\n'+k+' = '+str(v)+'\n'
for root in [Path('D:/ArmadaLab'),Path('D:/armadaIII')]:
 idx={f.name.lower():f for f in(root/'odf').rglob('*.odf')};sods={f.stem.lower():f for f in(root/'SOD').iterdir()if f.suffix.lower()=='.sod'};pending={};alias_sources={};alias_serial=0
 def text(f):return pending.get(f.relative_to(root).as_posix(),f.read_text(encoding='latin1')if f.exists()else'')
 def props(n,seen=None):
  seen=set()if seen is None else seen
  if n in seen or n not in idx:return {}
  seen.add(n);t=text(idx[n]);v={}
  for inc in re.findall(r'(?mi)^\s*#include\s+"([^"]+)"',t):v.update(props(inc.lower(),seen))
  for k,x in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t):v[k.lower()]=x.split('//')[0].strip().strip('"')
  return v
 spritepath=root/'Sprites/gui_global.spr';sprite=text(spritepath);sprite_docs=[(f,f.read_text(encoding='latin1'))for f in(root/'Sprites').glob('*.spr')];gui_fixes=[]
 def sprite_definition(name):
  for f,t in [(spritepath,sprite)]+sprite_docs:
   m=re.search(r'(?mi)^'+re.escape(name)+r'[ \t]+[^\r\n]*',t)
   if m:
    refs=re.findall(r'(?mi)^@reference\s*=\s*(\d+)',t[:m.start()]);return m[0],refs[-1]if refs else'64'
  return None
 def gui_source(w,seen=None):
  seen=set()if seen is None else seen
  if w.lower()in seen:return None
  seen.add(w.lower());found=sprite_definition('b_'+w)
  if found:return found
  f=idx.get(w.lower()+'.odf')
  if f:
   for inc in re.findall(r'(?mi)^\s*#include\s+"([^"]+)"',text(f)):
    found=gui_source(Path(inc).stem,seen)
    if found:return found
  name=props(w.lower()+'.odf').get('wpnname')
  # Existing matching native ability icon, for a standalone cloned definition.
  for other in ['gchainp','gdetectf','gshldemt','gcorbom','gplasmac','gplasmaw','gplasmabank','gaccelcannon']:
   if props(other+'.odf').get('wpnname')==name:
    found=sprite_definition('b_'+other)
    if found:return found
  return None
 def ensure_gui(w,source=None):
  nonlocal_dummy=None
  global_unused=None
  if sprite_definition('b_'+w):return
  found=gui_source(source or w);assert found,('No source GUI',w,source)
  line,ref=found;new=re.sub(r'^\S+','b_'+w,line);gui_fixes.append({'weapon':w,'source':source or w,'reference':ref,'line':new})
  return '\n@reference='+ref+'\n@tmaterial=default\n'+new+'\n'
 yards=[];ships={}
 for f in(root/'odf/stations').glob('*.odf'):
  if not re.search('yard2$',f.stem,re.I):continue
  y=props(f.name.lower());yards.append(f.stem)
  for k,n in y.items():
   if re.fullmatch('builditem[0-9]+',k):ships.setdefault(n.lower(),[]).append(f.stem)
 for ship,yardnames in ships.items():
  f=idx[ship+'.odf'];v=props(ship+'.odf');t=text(f);banks=sorted((int(k[6:]),w)for k,w in v.items()if re.fullmatch('weapon[0-9]+',k));added=None
  def specials():return [(slot,w,props(w.lower()+'.odf'))for slot,w in banks if num(props(w.lower()+'.odf'),'special')==1]
  qualifying=[w for slot,w,a in specials()if not re.search('cloak|selfdestruct',a.get('classlabel',''),re.I)]
  if not qualifying:
   w=choices[ship];a=props(w.lower()+'.odf');assert num(a,'special')==1
   slot=max(n for n,w in banks)+1;assert slot<=16
   with contextlib.redirect_stdout(io.StringIO()):model=Reader().read_file(str(sods[v.get('basename',ship).lower()]))
   nodes={n['id'].lower()for n in model.nodes};hp=next((x for x in sorted(nodes)if re.fullmatch('hp[0-9]+',x)),None);assert hp
   t=put(t,'weapon'+str(slot),'"'+w+'"');t=put(t,'weaponHardpoints'+str(slot),'"'+hp+'"');banks.append((slot,w));added={'weapon':w,'name':a.get('wpnname'),'hardpoint':hp}
  seen_buttons=set();seen_popup=set();fixes=[];spec=specials();reserved_buttons={int(num(a,'buttonslot'))for _,_,a in spec};reserved_popup={int(num(a,'popupslot'))for _,_,a in spec if 'popupslot'in a}
  for slot,w,a in spec:
   button=int(num(a,'buttonslot'));popup=int(num(a,'popupslot',-1));passive=button==0
   bc=not passive and button in seen_buttons;pc=popup>=0 and popup in seen_popup
   if bc or pc:
    alias_serial+=1;alias='y2a'+str(alias_serial).zfill(3);source=idx[w.lower()+'.odf'];target=source.with_name(alias+'.odf');clone='#include "'+source.name+'"\n// Yard II per-ship GUI slot correction.\n'
    if bc:button=next(x for x in range(1,10)if x not in reserved_buttons);reserved_buttons.add(button);clone=put(clone,'buttonSlot',button);clone=put(clone,'hotkeyLabel','"HOTKEY_F'+str(button)+'"')
    if pc:popup=next(x for x in range(1,12)if x not in reserved_popup);reserved_popup.add(popup);clone=put(clone,'popupSlot',popup)
    pending[target.relative_to(root).as_posix()]=clone;idx[alias+'.odf']=target;alias_sources[alias]=w;t=put(t,'weapon'+str(slot),'"'+alias+'"');banks=[(s,alias if s==slot else z)for s,z in banks];fixes.append({'from':w,'to':alias,'button':button,'popup':popup});w=alias;a=props(w+'.odf')
   if not passive:seen_buttons.add(button)
   if popup>=0:seen_popup.add(popup)
   if not passive:
    extra=ensure_gui(w,alias_sources.get(w));sprite+=extra or''
  # Validate original as well as newly added special-weapon attachments.
  with contextlib.redirect_stdout(io.StringIO()):checkedModel=Reader().read_file(str(sods[v.get('basename',ship).lower()]))
  checkedNodes={n['id'].lower()for n in checkedModel.nodes}
  validHp=next((n for n in sorted(checkedNodes)if re.fullmatch('hp[0-9]+',n)),None);assert validHp
  for bankSlot,bankWeapon,bankProps in specials():
   match=re.search(r'(?mi)^[ \t]*weaponHardpoints'+str(bankSlot)+r'[ \t]*=[ \t]*([^\r\n]*)',t)
   attachments=re.findall(r'[A-Za-z_]+[0-9]+',match[1]if match else v.get('weaponhardpoints'+str(bankSlot),''))
   if not attachments or any(h.lower()not in checkedNodes for h in attachments):t=put(t,'weaponHardpoints'+str(bankSlot),'"'+validHp+'"')
  required=0
  for slot,w,a in specials():
   o=props(a.get('ordname','').lower()+'.odf');required=max(required,num(a,'specialenergycost'),num(o,'specialenergycost'))
  base={'scout':500,'destroyer':700,'frigate':900,'cruiser':1000,'battleship':1400,'special':1800}.get(v.get('shipclass',''),1000)
  cap=max(base,math.ceil(required*1.5/50)*50);regen=round(cap/100,2)
  t=put(t,'maxSpecialEnergy',cap);t=put(t,'specialEnergyRate',regen);pending[f.relative_to(root).as_posix()]=t
  assert any(not re.search('cloak|selfdestruct',a.get('classlabel',''),re.I)for _,_,a in specials()),ship
  report.append({'root':str(root),'ship':ship,'name':v.get('unitname'),'yards':yardnames,'race':v.get('race'),'added':added,'slotCorrections':fixes,'energyBefore':num(v,'maxspecialenergy'),'regenBefore':num(v,'specialenergyrate'),'energyAfter':cap,'regenAfter':regen,'maximumActivationCost':required,'abilities':[{'odf':w,'name':a.get('wpnname'),'class':a.get('classlabel'),'button':a.get('buttonslot'),'popup':a.get('popupslot')}for _,w,a in specials()]})
 pending['Sprites/gui_global.spr']=sprite
 # Cloned weapons retain their original research prerequisites in each skirmish tree.
 for tree in ['tech1','earlytech','fulltech','nosci','nosuper','nospweap']:
  rel='techtree/'+tree+'.tt';t=text(root/rel)
  for alias,source in alias_sources.items():
   m=re.search(r'(?mi)^'+re.escape(source)+r'\.odf\s+([^\r\n]+)',t)
   requirement=m[1]if m else'0'
   t+='\n'+alias+'.odf '+requirement+' // GUI alias of '+source+'\n'
  if alias_sources:pending[rel]=t
 # Construction speed only: default torpedo turret is 75 seconds. Preserve class and all other values.
 default=props('cturret2.odf');buildtime=num(default,'buildtime');assert buildtime==75
 for name in ['fhwp','khwp','rhwp','chwp','dturret3','bjhwp','bhwp']:
  f=idx[name+'.odf'];pending[f.relative_to(root).as_posix()]=put(text(f),'buildTime',75)
 # Validate every new wrapper include stays in its original native folder.
 for alias,source in alias_sources.items():assert idx[alias+'.odf'].parent==idx[source.lower()+'.odf'].parent
 for rel,t in pending.items():all_pending.append((root,Path(rel),t))
# Both installations fully planned and checked before writes.
for root,rel,t in all_pending:
 f=root/rel
 if f.exists():
  b=backup/root.name/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(f.read_bytes());f.chmod(0o666)
 data=t.replace('\r','').replace('\n','\r\n').encode('latin1');f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data);assert f.read_bytes()==data
 out=repo/('lab/overlay'if root.name=='ArmadaLab'else'bajor/overlay')/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
result={'backup':str(backup),'ships':report,'runtimeVerified':False,'heavyPlatformBuildTime':75,'changedFiles':[{'root':str(root),'path':str(rel)}for root,rel,t in all_pending]};(repo/'reports/yard2-special-rebalance.json').write_text(json.dumps(result,indent=2))
md='# Yard II ability patch\n\n| Faction | Ship | New ability | Energy / recharge per second |\n|---|---|---|---|\n'
for x in report:
 if x['root'].lower().endswith('armadaiii')and x['added']:md+='| '+x['race']+' | '+x['name']+' | '+x['added']['name']+' | '+str(x['energyAfter'])+' / '+str(x['regenAfter'])+' |\n'
md+='\nAll Yard II ships audited; cloak and self-destruct alone do not count. Existing meaningful abilities preserved. Duplicate GUI slots corrected through local weapon aliases, retaining original research where declared. Recharge targets about 100 seconds for a full energy pool. Heavy-platform build times matched to default torpedo turret:75 seconds. File validation completed; gameplay pending.\n';(repo/'reports/yard2-new-weapons.md').write_text(md)
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Yard II ability and energy patch applied to armadaIII and ArmadaLab: '+str(len(report)//2)+' ships audited, '+str(sum(bool(x['added'])for x in report)//2)+' missing meaningful abilities added, GUI button collisions corrected with per-ship aliases, original research retained for aliases, energy capacities/recharge balanced. All7 heavy platforms now build in75s like default torpedo turret; class types unchanged. Backed up; gameplay pending; preparing Git push.';p.write_text(json.dumps(s,indent=2));
with(repo/'build.log').open('a')as log:log.write('\n'+s['current']+'\n')
print(json.dumps({'shipsPerInstallation':len(report)//2,'addedPerInstallation':sum(bool(x['added'])for x in report)//2,'slotFixesPerInstallation':sum(len(x['slotCorrections'])for x in report)//2,'files':len(all_pending),'backup':str(backup)}))
