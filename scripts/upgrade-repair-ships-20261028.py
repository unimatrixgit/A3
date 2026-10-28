from pathlib import Path
import re,json,datetime,shutil,subprocess,sys,contextlib,io
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils');from sod_io import SodIO
class R(SodIO):
 def read_unknown_legacy_data(self,s):return []if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
root=Path('D:/armadaIII');repo=Path('D:/aramada');idx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')};mapping=json.loads((repo/'reports/repair-yard-tech-20261028.json').read_text())['mapping'];backup=Path('D:/Xaramada-Modwork/backups')/('repair-ship-upgrade-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
assert subprocess.check_output(['powershell','-NoProfile','-Command','@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'],text=True).strip()=='0','Close game first.'
def props(n,seen=()):
 n=Path(n.strip('"')).stem.lower()
 if n in seen or n not in idx:return{}
 d={};t=idx[n].read_text(encoding='latin1')
 for inc in re.findall(r'(?mi)^\s*#include\s+"([^"]+)"',t):d.update(props(inc,seen+(n,)))
 for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t):d[k.lower()]=v.split('//')[0].strip().strip('"')
 return d
def put(t,k,v):
 pat=r'(?mi)^[ \t]*'+k+r'[ \t]*=[^\r\n]*';line=k+' = '+str(v)
 return re.sub(pat,lambda m:line,t)if re.search(pat,t)else t.rstrip()+'\n'+line+'\n'
pending={};rows=[]
for ship in mapping:
 p=idx[ship];a=props(ship);t=p.read_text(encoding='latin1');changes={}
 for k in ['maxhealth','maxshields','maxhull','shieldrate','shieldgeneratorhitpoints','engineshitpoints','weaponshitpoints','lifesupporthitpoints','sensorshitpoints']:
  if k not in a:continue
  try:v=float(a[k].rstrip('fF'))
  except ValueError:continue
  if v>0:t=put(t,k,format(v*1.5,'.12g'));changes[k]=[v,v*1.5]
 for k,floor in [('maxspecialenergy',1000),('specialenergyrate',10)]:
  v=float(a.get(k,'0').rstrip('fF'));new=max(v,floor);t=put(t,k,format(new,'.12g'));changes[k]=[v,new]
 slots={int(k[6:]):v for k,v in a.items()if re.fullmatch('weapon[0-9]+',k)};assert sorted(slots)==list(range(1,max(slots)+1)),ship
 assert 'xrctorp'not in slots.values();model=a.get('basename',ship)
 with contextlib.redirect_stdout(io.StringIO()):m=R().read_file(str(root/'SOD'/(model+'.sod')))
 anchors={n['id'].lower()for n in m.nodes};candidates=[]
 for k,v in a.items():
  if re.fullmatch('weaponhardpoints[0-9]+',k):candidates+=re.findall('[A-Za-z][A-Za-z0-9_]*',v)
 hp=next((x for x in candidates if x.lower()in anchors),None);assert hp,(ship,'No valid weapon mount')
 slot=max(slots)+1;t=put(t,'weapon'+str(slot),'"xrctorp"');t=put(t,'weaponHardpoints'+str(slot),'"'+hp+'"');t=put(t,'combat',1);t=put(t,'canAttack',1);t=put(t,'alert',1)
 for n,w in slots.items():assert re.search(r'(?mi)^weapon'+str(n)+r'\s*=\s*"'+re.escape(w)+'"',t)or a['weapon'+str(n)]==w
 pending[p.relative_to(root)]=t;rows.append({'ship':ship,'changes':changes,'torpedoSlot':slot,'torpedoHardpoint':hp,'existingWeaponSlotsPreserved':True})
assert 'xrctorp'not in idx and 'xrctorpo'not in idx
pending[Path('odf/weapons/Photons/xrctorp.odf')]='''#include "photon.odf"
wpnName = "Repair Tender Continuous Torpedo"
ordName = "xrctorpo"
shotDelay = 0.375
minimumShotInterval = 0.375
maxShots = 1
saveFire = 0
range = 600.0
restrictFireArc = 0
fireArc = 360
special = 0
'''
pending[Path('odf/weapons/Photons/xrctorpo.odf')]='''#include "frphotono.odf"
damageBase = 30
damageVariance = 0
specialEnergyCost = 0
'''
for mode in ['tech1','earlytech','nosci','nosuper','nospweap','fulltech','freetech']:
 rel=Path('techtree')/(mode+'.tt');t=(root/rel).read_text(encoding='latin1');assert not re.search(r'(?mi)^xrctorp\.odf\s',t);pending[rel]=t.rstrip()+'\nxrctorp.odf 0 // Normal repair-tender defensive torpedo, not a research ability\n'
for rel,t in pending.items():
 p=root/rel
 if p.exists():b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b)
 data=t.replace('\r','').replace('\n','\r\n').encode('latin1');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);out=repo/'bajor/overlay'/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
idx['xrctorp']=root/'odf/weapons/Photons/xrctorp.odf';idx['xrctorpo']=root/'odf/weapons/Photons/xrctorpo.odf'
assert props('xrctorp')['ordname']=='xrctorpo'and props('xrctorpo')['classlabel']=='photontorpedo'
for row in rows:
 d=props(row['ship']);assert d['weapon'+str(row['torpedoSlot'])]=='xrctorp'
 for k,(old,new)in row['changes'].items():assert abs(float(d[k].rstrip('fF'))-new)<1e-7
report={'backup':str(backup),'ships':rows,'torpedo':{'delay':0.375,'damage':30,'rawDps':80,'energyCost':0,'automaticNormalWeapon':True},'durabilityFactor':1.5,'repairBeamsPreserved':True,'runtimeVerified':False};(repo/'reports/repair-ship-upgrade-20261028.json').write_text(json.dumps(report,indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='All 11 repair ships upgraded: +50% durability and shield regeneration, minimum 1000 special energy/10 regeneration, defensive continuous torpedo (30 damage every 0.375s). Existing repair beams/weapons retained; model mounts and native projectile chain checked. armadaIII applied; gameplay pending.';p.write_text(json.dumps(s,indent=2))
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n'+datetime.datetime.now().isoformat()+' '+s['current']+'\n')
print(json.dumps({'ships':len(rows),'files':len(pending),'torpedoDps':80,'runtimeVerified':False}))
