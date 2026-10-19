from pathlib import Path
import sys,re,json,contextlib,io,hashlib,datetime
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils')
from sod_io import SodIO
class Reader(SodIO):
 def read_unknown_legacy_data(self,s):return []if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
root=Path('D:/ArmadaLab');repo=Path('D:/aramada');idx={f.name.lower():f for f in(root/'odf').rglob('*.odf')};stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup=Path('D:/Xaramada-Modwork/backups')/('yard-special-colony-lab-'+stamp)
def props(n,seen=None):
 seen=set()if seen is None else seen
 if n not in idx or n in seen:return{}
 seen.add(n);t=idx[n].read_text(encoding='latin1');v={}
 for inc in re.findall(r'(?mi)^[ \t]*#include[ \t]+"([^"\r\n]+)"',t):v.update(props(inc.lower(),seen))
 for k,x in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t):v[k.lower()]=x.split('//')[0].strip().strip('"')
 return v
def put(t,k,v):return re.sub(r'(?mi)^[ \t]*'+re.escape(k)+r'[ \t]*=[^\r\n]*','',t)+'\n'+k+' = '+str(v)+'\n'
def number(v,k):
 try:return float(v.get(k,'0').rstrip('fF'))
 except:return 0
choices=[('kbwing','gplasmac','kbattle','battleship ion cannon'),('rktinga','gplasmaw','rcruise4','cruiser offensive plasma'),('rscruise','gposijam','rcruise1','cruiser sensor disruption'),('bjartillery','xbj_gamine','bjinterceptor','destroyer-derived artillery defensive mines'),('fneworleans','gchainp','fcruise1','cruiser chain-reaction pulsar'),('xhfriker','gcorbom','fente','battleship defensive reflector'),('rtscout','gromspy','rdestroy','scout reconnaissance'),('rtspec','gromspy','rdestroy','destroyer reconnaissance')]
pending={};units=[]
for ship,weapon,donor,reason in choices:
 v=props(ship+'.odf');w=props(weapon+'.odf');d=props(donor+'.odf');o=props(w.get('ordname','').lower()+'.odf')
 if v.get('race')!=d.get('race'):raise ValueError('Cross-faction ability '+ship)
 if weapon.lower()not in[x.lower()for k,x in d.items()if re.fullmatch(r'weapon\d+',k)]:raise ValueError('Donor does not use ability '+donor)
 if number(w,'special')!=1 or'cloak'in w.get('classlabel','').lower():raise ValueError('Not a qualifying special '+weapon)
 banks=[(int(k[6:]),x)for k,x in v.items()if re.fullmatch(r'weapon\d+',k)]
 active=[x for _,x in banks if number(props(x.lower()+'.odf'),'special')==1 and'cloak'not in props(x.lower()+'.odf').get('classlabel','').lower()]
 if active:raise ValueError('Ship already has qualifying special '+ship)
 slot=max(i for i,x in banks)+1
 if slot>16:raise ValueError('No weapon slots '+ship)
 model=v.get('basename',ship)
 with contextlib.redirect_stdout(io.StringIO()):m=Reader().read_file(str(root/'SOD'/(model+'.sod')))
 nodes={n['id'].lower():n['id']for n in m.nodes};hp=next((n for n in ['hp01','hp02','hp03']if n in nodes),None)or next((n for n in nodes if re.fullmatch(r'hp\d+',n)),None)
 if not hp:raise ValueError('No valid ability hardpoint '+ship)
 for _,x in banks:
  other=props(x.lower()+'.odf')
  if number(other,'special')!=1:continue
  if w.get('buttonslot')is not None and other.get('buttonslot')==w.get('buttonslot'):raise ValueError('Button collision '+ship)
  if w.get('popupslot')is not None and other.get('popupslot')==w.get('popupslot'):raise ValueError('Popup collision '+ship)
 f=idx[ship+'.odf'];t=f.read_text(encoding='latin1');t=put(t,'weapon'+str(slot),'"'+weapon+'"');t=put(t,'weaponHardpoints'+str(slot),'"'+hp+'"');energy=max(number(w,'specialenergycost'),number(o,'specialenergycost'))
 if number(v,'maxspecialenergy')<energy:t=put(t,'maxSpecialEnergy',int(energy))
 if number(v,'specialenergyrate')<=0:t=put(t,'specialEnergyRate',5)
 pending[f.relative_to(root).as_posix()]=t;units.append({'unit':ship,'ability':weapon,'abilityName':w.get('wpnname'),'sourceShip':donor,'race':v.get('race'),'reason':reason,'newWeaponSlot':slot,'hardpoint':hp,'requiredEnergy':energy,'energyCapacity':max(number(v,'maxspecialenergy'),energy)})
trees=[]
for tree in ['tech1.tt','earlytech.tt','nosci.tt','nosuper.tt','nospweap.tt','fulltech.tt']:
 f=root/'techtree'/tree;t=f.read_text(encoding='latin1');t=re.sub(r'(?mi)^[ \t]*fcolony\.odf[ \t]+[^\r\n]*','',t);entry='fcolony.odf 0'if tree=='fulltech.tt'else'fcolony.odf 1 fyard.odf';t+='\n// Federation colony ships unlock with the standard shipyard.\n'+entry+'\n';pending[f.relative_to(root).as_posix()]=t;trees.append({'tree':tree,'entry':entry})
files=[]
for rel,t in pending.items():
 f=root/rel;b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(f.read_bytes());f.chmod(0o666);data=t.replace('\r','').replace('\n','\r\n').encode('latin1');f.write_bytes(data);out=repo/'lab/overlay'/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);files.append({'path':rel,'sha256':hashlib.sha256(data).hexdigest()})
(repo/'reports/yard-specials-colony-lab.json').write_text(json.dumps({'root':str(root),'backup':str(backup),'units':units,'techTrees':trees,'files':files,'runtimeVerified':False,'deployed':False},indent=2));print(json.dumps({'ships':units,'techTrees':len(trees),'files':len(files)}))
