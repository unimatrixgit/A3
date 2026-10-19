from pathlib import Path
import re,json,datetime,sys,contextlib,io
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils')
from sod_io import SodIO
class R(SodIO):
 def read_unknown_legacy_data(self,s):return [] if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
repo=Path('D:/aramada');backup=Path('D:/Xaramada-Modwork/backups')/('all-constructor-arms-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));pending=[];records=[]
def put(t,k,v):return re.sub(r'(?mi)^[ \t]*'+k+r'[ \t]*=[^\r\n]*','',t)+'\n'+k+' = '+str(v)+'\n'
donors={'borg':('bc1phas','xp6t'),'federation':('fc08phas','xp8t'),'klingon':('kc03phas','xp9t'),'romulan':('rc01phas','xp10t'),'cardassian':('xp11b','xp11t'),'dominion':('dphaser','xp12t'),'breen':('xp13b','xp13t'),'bajoran':('xp14b','xp14t'),'species8472':('biolev2','xp12t')}
for root in [Path('D:/ArmadaLab'),Path('D:/armadaIII')]:
 idx={p.name.lower():p for p in(root/'odf').rglob('*.odf')};sods={p.name.lower():p for p in(root/'SOD').iterdir()if p.is_file()}
 def props(n,seen=None):
  seen=set()if seen is None else seen
  if n in seen or n not in idx:return {}
  seen.add(n);t=idx[n].read_text(encoding='latin1');v={}
  for inc in re.findall(r'(?mi)^\s*#include\s+"([^"]+)"',t):v.update(props(inc.lower(),seen))
  for k,x in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t):v[k.lower()]=x.split('//')[0].strip().strip('"')
  return v
 for f in(root/'odf/ships').glob('*.odf'):
  v=props(f.name.lower())
  if v.get('shipclass')!='construction' or not v.get('unitname'):continue
  race=v['race'];beam,torp=donors[race];found=set();slots=[]
  for k,w in v.items():
   if not re.fullmatch('weapon[0-9]+',k):continue
   slots.append(int(k[6:]));a=props(w.lower()+'.odf');o=props(a.get('ordname','').lower()+'.odf')
   if a.get('special','0').rstrip('f')in['1','1.0']:continue
   if o.get('classlabel')=='phaser':found.add('beam')
   if o.get('classlabel')=='photontorpedo':found.add('torpedo')
  model=v.get('basename',f.stem)
  assert model.lower()+'.sod'in sods,(f,model)
  with contextlib.redirect_stdout(io.StringIO()):m=R().read_file(str(sods[model.lower()+'.sod']))
  nodes={n['id'].lower()for n in m.nodes};hp=sorted(n for n in nodes if re.fullmatch(r'hp\d+',n))
  if not hp:hp=[n for n in ['root','target']if n in nodes]
  assert hp,(f,'no attachment')
  t=f.read_text(encoding='latin1');added=[];slot=max(slots,default=0)
  for kind,w in [('beam',beam),('torpedo',torp)]:
   if kind in found:continue
   a=props(w.lower()+'.odf');o=props(a.get('ordname','').lower()+'.odf');assert o.get('classlabel')==('phaser'if kind=='beam'else'photontorpedo'),(w,o.get('classlabel'))
   slot+=1;assert slot<=16;t=put(t,'weapon'+str(slot),'"'+w+'"');t=put(t,'weaponHardpoints'+str(slot),'"'+hp[(slot-1)%len(hp)]+'"');added.append({'kind':kind,'weapon':w,'slot':slot,'hardpoint':hp[(slot-1)%len(hp)]})
  for k in ['canAttack','combat','alert']:t=put(t,k,1)
  if float(v.get('weaponshitpoints','0').rstrip('f'))<=0:t=put(t,'weaponsHitPoints',100)
  assert 'beam'in found or any(x['kind']=='beam'for x in added)
  assert 'torpedo'in found or any(x['kind']=='torpedo'for x in added)
  pending.append((root,f.relative_to(root),t));records.append({'root':str(root),'unit':f.name,'name':v['unitname'],'race':race,'added':added,'previousWeaponSlots':len(slots),'model':model,'attackEnabled':True})
# No writes until all models, attachment nodes and weapons pass.
for root,rel,t in pending:
 f=root/rel;b=backup/root.name/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(f.read_bytes());f.chmod(0o666);data=t.replace('\r','').replace('\n','\r\n').encode('latin1');f.write_bytes(data);assert f.read_bytes()==data
 out=repo/('lab/overlay'if root.name=='ArmadaLab'else'bajor/overlay')/rel;out.write_bytes(data)
(repo/'reports/all-constructor-armament.json').write_text(json.dumps({'backup':str(backup),'constructors':records,'runtimeVerified':False},indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Minimum constructor armament applied in armadaIII and ArmadaLab: '+str(len(records)//2)+' named constructor variants each have at least one combat beam and one torpedo. Existing stronger weapons, tractor tools, cloak, transwarp and construction menus preserved. Explicit attack enabled; model hardpoints/weapon classes validated. Backed up; gameplay pending.';p.write_text(json.dumps(s,indent=2));
with(repo/'build.log').open('a')as log:log.write('\n'+s['current']+'\n')
print(json.dumps({'constructorsPerInstallation':len(records)//2,'files':len(pending),'backup':str(backup),'addedWeapons':sum(len(x['added'])for x in records)//2}))
