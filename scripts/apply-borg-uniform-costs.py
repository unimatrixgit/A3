from pathlib import Path
import re,json,math,datetime,shutil,stat,subprocess
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
def num(v,default=0):
 try:return float(str(v).strip().rstrip('f'))
 except:return default
def score(n):
 a=props(n);dps=0;abilities=[]
 for k,v in a.items():
  if not re.fullmatch('weapon[0-9]+',k):continue
  w=props(v);special=w.get('special')=='1'
  if special:
   if v.lower()!='gselfdes':abilities.append(v)
   continue
  if w.get('classlabel','').lower() not in ['cannon','launcher','phaser','pulse']:continue
  ordinance=props(w.get('ordname',''));damage=num(w.get('damagebase',ordinance.get('damagebase',0)));delay=num(w.get('shotdelay',1),1)
  if damage>0 and delay>0:dps+=damage/delay
 hull=num(a.get('maxhealth',0));crew=num(a.get('crewcost',0));slots=num(a.get('maxextraweapons',0));value=50+.12*hull+.08*crew+2*dps+40*len(abilities)+80*slots
 return value,dict(health=hull,crew=crew,nominalDPS=round(dps,2),builtInSpecials=len(abilities),capturedSlots=slots)
ref=score('bbattle1')[0];stage=Path('D:/Xaramada-Modwork/borg-uniform-costs');changes=[]
for p in(root/'odf/ships').glob('*.odf'):
 a=props(p.stem)
 if a.get('race','').lower()!='borg':continue
 value,factors=score(p.stem);each=max(100,int(math.floor((value/ref*700/2)/25+.5))*25);officers=max(1,int(math.floor((each*2)/200+.5)));t=p.read_text(encoding='latin1');old={k:a.get(k)for k in ['dilithiumcost','metalcost','officercost']}
 for k,v in [('dilithiumCost',each),('metalCost',each),('officerCost',officers)]:
  t=re.sub(r'^\s*'+k+r'\s*=.*$',f'{k} = {v}',t,flags=re.M|re.I)if re.search(r'^\s*'+k+r'\s*=',t,re.M|re.I)else t+f'\n{k} = {v}\n'
 rel=p.relative_to(root);dst=stage/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(t,encoding='latin1');changes.append(dict(ship=p.stem,name=a.get('unitname'),file=str(rel),previous=old,dilithium=each,metal=each,officers=officers,factors=factors))
running=subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode!=0;backup=Path('D:/Xaramada-Modwork/backups')/('borg-uniform-costs-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
if not running:
 for x in changes:
  p=root/x['file'];b=backup/x['file'];b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b);p.chmod(p.stat().st_mode|stat.S_IWRITE);shutil.copy2(stage/x['file'],p);o=repo/'overlay'/x['file'];o.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,o)
report=dict(installed=not running,stage=str(stage),backup=str(backup)if not running else None,formula='score=50+0.12*health+0.08*crew+2*nominalDPS+40*builtInSpecials+80*capturedSlots; totalResourceCost=700*score/referenceCubeScore; each resource=half total rounded to25,minimum100;officers=totalResources/200 rounded,minimum1',referenceCube='bbattle1',referenceScore=ref,changes=changes,gameplayVerified=False,notes=['Crew,start/max crew,health,weapon damage,build time,tech and models unchanged.','DPS assumes one shot per weapon bank,ignoring target armor,misses,travel and special effects;balancing estimate,not combat simulation.'])
(repo/'reports/borg-uniform-costs.json').write_text(json.dumps(report,indent=2));sfile=repo/'status.json';s=json.loads(sfile.read_text(encoding='utf-8-sig'));s['current']=('Staged'if running else'Installed')+f' uniform Borg pricing across{len(changes)} ship definitions:equal dilithium/metal,one strength formula and officer scale. Stats,crew and build times unchanged. Gameplay pending.';sfile.write_text(json.dumps(s,indent=2));(repo/'build.log').open('a').write('\n'+s['current']+'\n');print(json.dumps(dict(installed=not running,ships=len(changes),comparison=[x for x in changes if x['ship']in ['brenborg','bbattle1','bbattle2','bbattle3','xobbattle1']])))
