from pathlib import Path
import re,json,datetime,sys,contextlib,io,hashlib
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils')
from sod_io import SodIO
class Reader(SodIO):
 def read_unknown_legacy_data(self,s): return [] if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
repo=Path('D:/aramada'); stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S'); backup=Path('D:/Xaramada-Modwork/backups')/('original-borg-orbital-strength-'+stamp)
source=Path('D:/Startrek Armada II install/Activision/Star Trek Armada II/odf/stations/bbase2.odf')
def direct(t): return {k.lower():v.split('//')[0].strip() for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t)}
base=direct(source.read_text(encoding='latin1'))
keys=['maxHealth','shieldRate','shieldProtection','shieldGeneratorHitPoints','enginesHitPoints','weaponsHitPoints','lifeSupportHitPoints','sensorsHitPoints','crewCost','maximumCrew']
values={k:base[k.lower()] for k in keys}
assert values['crewCost']=='100' and values['maximumCrew']=='500'
combat=[base['weapon'+str(i)].strip('"') for i in range(2,8)]
assert combat==['bb3phas','bfphot','bfphot','bb3phas','bc2phas','bc2phas']
names=['bbase2','borbital','forbital','korbital','rorbital','corbital','dorbital','brorbital','bjorbital']; pending=[];report=[]
for root in [Path('D:/ArmadaLab'),Path('D:/armadaIII')]:
 idx={p.name.lower():p for p in (root/'odf').rglob('*.odf')}
 for name in names:
  f=idx[name+'.odf']; t=f.read_text(encoding='latin1'); v=direct(t)
  mining=[]
  for key,w in v.items():
   if re.fullmatch('weapon[0-9]+',key) and w.strip('"').lower()=='gorbitalbeam': mining.append((int(key[6:]),w,v['weaponhardpoints'+key[6:]]))
  mining.sort();assert mining
  model=v.get('basename','"'+name+'"').strip('"')
  with contextlib.redirect_stdout(io.StringIO()): sod=Reader().read_file(str(root/'SOD'/(model+'.sod')))
  nodes={n['id'].lower() for n in sod.nodes}
  hps=sorted(n for n in nodes if re.fullmatch(r'hp\d+',n));assert hps
  for _,w,hp in mining: assert all(x.lower() in nodes for x in re.findall('"([^"]+)"',hp))
  for w in combat: assert w+'.odf' in idx
  t=re.sub(r'(?mi)^[ \t]*weapon(?:Hardpoints)?\d+[ \t]*=[^\r\n]*','',t)
  for k,val in values.items():
   t=re.sub(r'(?mi)^[ \t]*'+k+r'[ \t]*=[^\r\n]*','',t)
   t+='\n'+k+' = '+val+'\n'
  layout=[(w,hp) for _,w,hp in mining]+[('"'+w+'"','"'+hps[i%len(hps)]+'"') for i,w in enumerate(combat)]
  for i,(w,hp) in enumerate(layout,1): t+='\nweapon'+str(i)+' = '+w+'\nweaponHardpoints'+str(i)+' = '+hp+'\n'
  after=direct(t)
  assert after['weapon1'].strip('"')=='gOrbitalBeam'
  assert [(after['weapon'+str(i+1)],after['weaponhardpoints'+str(i+1)])for i in range(len(mining))]==[(w,hp)for _,w,hp in mining]
  for k in v:
   if re.search(r'mining|resourcescanhandle|orbit|classlabel',k): assert after[k]==v[k]
  pending.append((root,f,t.replace('\r','').replace('\n','\r\n').encode('latin1')))
  report.append({'root':str(root),'unit':name,'values':values,'combatWeapons':combat,'miningAttachmentsPreserved':True,'modelHardpointsVerified':True})
for root,f,data in pending:
 rel=f.relative_to(root); bak=backup/root.name/rel;bak.parent.mkdir(parents=True,exist_ok=True);bak.write_bytes(f.read_bytes());f.chmod(0o666);f.write_bytes(data)
 overlay=repo/('lab/overlay' if root.name=='ArmadaLab' else 'bajor/overlay')/rel;overlay.parent.mkdir(parents=True,exist_ok=True);overlay.write_bytes(data)
 assert f.read_bytes()==data
(repo/'reports/original-borg-orbital-strength.json').write_text(json.dumps({'source':str(source),'backup':str(backup),'units':report,'runtimeVerified':False},indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='All 9 orbitals matched to original supplied Borg bbase2 combat strength in ArmadaLab and armadaIII: 10000 health, shieldRate 15.5, original 6 combat banks, 100 crew / 500 max crew. Mining beams and their attachments preserved first. Backed up and file-validated; gameplay pending. Autonomy settings deferred.';p.write_text(json.dumps(s,indent=2));
with (repo/'build.log').open('a') as log:log.write('\n['+datetime.datetime.now(datetime.timezone.utc).isoformat()+'] '+s['current']+'\n')
print(json.dumps({'updated':len(pending),'backup':str(backup),'values':values,'combat':combat,'miningPreserved':True}))
