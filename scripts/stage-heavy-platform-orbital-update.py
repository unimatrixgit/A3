from pathlib import Path
import sys,re,json,hashlib,datetime,contextlib,io
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils')
from sod_io import SodIO
class Reader(SodIO):
 def read_unknown_legacy_data(self,s):return [] if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
root=Path('D:/ArmadaLab');repo=Path('D:/aramada');stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup=Path('D:/Xaramada-Modwork/backups')/('heavy-orbital-lab-'+stamp)
idx={f.name.lower():f for f in (root/'odf').rglob('*.odf')}
def props(n,seen=None):
 seen=set()if seen is None else seen
 if n in seen or n not in idx:raise ValueError('Missing/cyclic definition '+n)
 seen.add(n);t=idx[n].read_text(encoding='latin1');v={}
 for inc in re.findall(r'(?mi)^[ \t]*#include[ \t]+"([^"\r\n]+)"',t):v.update(props(inc.lower(),seen))
 for k,x in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t):v[k.lower()]=x.split('//')[0].strip().strip('"')
 return v
def put(t,k,v):return re.sub(r'(?mi)^[ \t]*'+re.escape(k)+r'[ \t]*=[^\r\n]*','',t)+'\n'+k+' = '+str(v)+'\n'
def serialize(v):
 def value(x):return x if re.fullmatch(r'[+\-\d.eEfF]+(?:[ \t]+[+\-\d.eEfF]+)*',x)else '"'+x+'"'
 return '// Explicit native weapon definition; no cross-directory includes.\n'+'\n'.join(k+' = '+value(str(x))for k,x in v.items())+'\n'
heavy=['fhwp','khwp','rhwp','cturret2','dturret3'];miners=['bbase2','borbital','forbital','korbital','rorbital','corbital','dorbital','brorbital','bjorbital']
parents={'borg':('bb3phas','bfphot'),'federation':('fsovereignphas','fsovereignphot'),'klingon':('kc10phas','kc03phot'),'romulan':('rc06phas','rc05phot'),'cardassian':('cc07phas','cc06plas'),'dominion':('zjmphas','jmphot'),'breen':('zjmphas','jmphot'),'bajoran':('fsovereignphas','fsovereignphot')}
overrides={'fhwp':('fhwpphas','fhwpphot'),'khwp':('kc10phas','kc05phot'),'rhwp':('rc06phas','rc07phot'),'cturret2':('cc07phas','cd03torp'),'dturret3':('nova','dgphoton')}
heavy_cost={'dilithiumCost':900,'metalCost':900,'latinumCost':0,'biomatterCost':0,'crewCost':200,'officerCost':8,'buildTime':90}
mining_cost={'dilithiumCost':400,'metalCost':0,'latinumCost':0,'biomatterCost':0,'crewCost':100,'officerCost':2,'buildTime':60,'maximumCrew':250}
pending={};units=[]
for number,name in enumerate(heavy+miners,1):
 f=idx[name+'.odf'];before=props(name+'.odf');t=f.read_text(encoding='latin1');model=before.get('basename',name)
 with contextlib.redirect_stdout(io.StringIO()):s=Reader().read_file(str(root/'SOD'/(model+'.sod')))
 nodes={n['id'].lower():n['id']for n in s.nodes};hps=sorted([n for n in nodes if re.fullmatch(r'(?:hp|pod)\d+',n)],key=lambda x:(x[:2],int(re.search(r'\d+',x)[0])))
 if not hps:raise ValueError('No usable model hardpoints '+name)
 old=[]
 for key,weapon in before.items():
  if not re.fullmatch(r'weapon\d+',key):continue
  w=props(weapon.lower()+'.odf');ord=props(w['ordname'].lower()+'.odf')if w.get('ordname')else {}
  slot=int(key[6:]);hp=re.findall(r'"([^"]+)"',before.get('weaponhardpoints'+str(slot),''))
  if not hp:hp=before.get('weaponhardpoints'+str(slot),'').split('" "')
  hp=[n.strip('"').lower()for n in hp if n.strip('"').lower()in nodes]
  old.append((slot,weapon,w,ord,hp))
 old.sort()
 preserved=[]
 if name in miners:
  preserved=[(w,hp)for _,w,v,o,hp in old if 'mining' in o.get('classlabel','').lower()or w.lower()=='gorbitalbeam']
  if not preserved:raise ValueError('Mining weapon absent '+name)
 else:
  preserved=[(w,hp)for _,w,v,o,hp in old if v.get('special','0').rstrip('f')in ['1','1.0']]
 beam,torp=overrides.get(name,parents[before['race']]);aliases={};bank_count=3 if name in heavy else 2
 for kind,parent in [('beam',beam),('torpedo',torp)]+([('rapid',torp)]if name in heavy else []):
  v=props(parent+'.odf');o=props(v['ordname'].lower()+'.odf')
  if v.get('classlabel')not in ['cannon','launcher']:raise ValueError('Weapon is not native cannon/launcher '+parent)
  v['classlabel']='cannon'
  if kind=='beam'and o.get('classlabel')!='phaser':raise ValueError('Not a beam '+parent)
  if kind!='beam'and o.get('classlabel')!='photontorpedo':raise ValueError('Not a torpedo '+parent)
  v.update({'restrictfirearc':'0','firearc':'360'})
  if kind=='rapid':v.update({'shotdelay':'0.375','maxshots':'1','minimumshotinterval':'0.375','savefire':'0','wpnname':'Continuous Torpedo Launcher'})
  alias='xp'+str(number)+{'beam':'b','torpedo':'t','rapid':'r'}[kind];folder='Phasers'if kind=='beam'else'Photons';pending['odf/weapons/'+folder+'/'+alias+'.odf']=serialize(v);aliases[kind]=alias
 t=re.sub(r'(?mi)^[ \t]*weapon(?:Hardpoints)?\d+[ \t]*=[^\r\n]*','',t)
 layout=[(aliases['beam'],[hps[i%len(hps)]])for i in range(bank_count)]+[(aliases['torpedo'],[hps[(bank_count+i)%len(hps)]])for i in range(2)]
 if name in heavy:layout.append((aliases['rapid'],[hps[5%len(hps)]]))
 layout+=preserved
 if len(layout)>16:raise ValueError('Weapon slot overflow '+name)
 for i,(w,hp)in enumerate(layout,1):
  hp=hp or[hps[(i-1)%len(hps)]]
  if not all(x.lower()in nodes for x in hp):raise ValueError('Invalid attachment '+name)
  t=put(t,'weapon'+str(i),'"'+w+'"');t=put(t,'weaponHardpoints'+str(i),' '.join('"'+x+'"'for x in hp))
 cost=heavy_cost if name in heavy else mining_cost
 for k,v in cost.items():t=put(t,k,v)
 if name in heavy and int(float(before.get('maximumcrew',before.get('crewcost','0'))))<200:t=put(t,'maximumCrew',200)
 pending[f.relative_to(root).as_posix()]=t
 units.append({'unit':name,'name':before.get('unitname'), 'category':'heavy platform'if name in heavy else'orbital miner','beamBanks':bank_count,'torpedoBanks':2,'rapidTorpedoBanks':1 if name in heavy else 0,'rapidInterval':0.375 if name in heavy else None,'preservedWeapons':[w for w,hp in preserved],'costs':cost,'model':model,'attachmentsVerified':True,'originalCosts':{k:before.get(k.lower())for k in cost}})
# All targets, weapon types and actual model nodes pass before any file is changed.
manifest=[]
for rel,t in pending.items():
 f=root/rel;b=backup/rel;existed=f.exists()
 if existed:b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(f.read_bytes());f.chmod(0o666)
 data=t.replace('\r','').replace('\n','\r\n').encode('latin1');f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
 overlay=repo/'lab/overlay'/rel;overlay.parent.mkdir(parents=True,exist_ok=True);overlay.write_bytes(data)
 manifest.append({'path':rel,'existed':existed,'sha256':hashlib.sha256(data).hexdigest()})
out={'root':str(root),'backup':str(backup),'units':units,'files':manifest,'heavyCost':heavy_cost,'orbitalCost':mining_cost,'runtimeVerified':False,'deployed':False}
(repo/'reports/heavy-platform-orbital-lab.json').write_text(json.dumps(out,indent=2));print(json.dumps({'structures':len(units),'files':len(manifest),'backup':str(backup),'heavyCost':heavy_cost,'orbitalCost':mining_cost}))

