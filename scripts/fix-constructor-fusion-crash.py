from pathlib import Path
exec(Path('D:/aramada/scripts/build-mirror-ferengi-research.py').read_text().split('# Existing Cardassian artwork')[0])
import shutil,subprocess,os,hashlib
pending={};changes=[];abilities=set()
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running; no files changed'
for n in index:
 d=resolve(n);banks=sorted([(int(k[6:]),v)for k,v in d.items()if re.fullmatch('weapon[0-9]+',k)])
 if not any(v.startswith('xcv_')for i,v in banks):continue
 abilities.update(v for i,v in banks if v.startswith('xcv_'));t=text(n);t=re.sub(r'(?mi)^\s*weapon(?:Hardpoints)?\d+\s*=[^\r\n]*','',t)
 kept=[(i,v)for i,v in banks if not v.startswith('xcv_')]
 for j,(i,v)in enumerate(kept,1):
  t=put(t,'weapon'+str(j),q(v));t=put(t,'weaponHardpoints'+str(j),q(d.get('weaponhardpoints'+str(i),'root')).replace('\\"','"'))
 pending[index[n].relative_to(root).as_posix()]=t;changes.append({'constructor':n,'removed':[v for i,v in banks if v.startswith('xcv_')],'remainingWeapons':[v for i,v in kept]})
for tree in ['tech1','earlytech','fulltech','nosci','nospweap','nosuper']:
 rel='techtree/'+tree+'.tt';lines=[]
 for line in(root/rel).read_text(encoding='latin1').splitlines():
  a=line.split('//')[0].split()
  if a and Path(a[0]).stem.lower()in abilities:continue
  lines.append(line)
 pending[rel]='\n'.join(lines)+'\n// Constructor fusion withdrawn after runtime null-object crash.\n'+'\n'.join(n+'.odf -1'for n in sorted(abilities))+'\n'
pending[index['unicomplex'].relative_to(root).as_posix()]=put(text('unicomplex'),'maximumCrew',10000)
assert resolve('unicomplex')['maximumcrew']=='10000'
# Preserve transwarp, weapon hardpoints and normal production of all three native tiers.
for n in ['bconst','bconst2','xbuconst']:
 assert 'xabtrans5'in resolve(n).values(),n
for n in ['dconst','xdconst2','xduconst']:assert any(resolve(k).get(x)==n for k in index for x in resolve(k)if re.fullmatch('builditem[0-9]+',x)),n
stamp=datetime.datetime.now().astimezone().isoformat();backup=Path('D:/Xaramada-Modwork/backups')/('constructor-fusion-crash-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));manifest=[]
for rel in pending:
 for label,base in [('live',root),('repository',repo/'bajor/overlay')]:
  src=base/rel;b=backup/label/rel;b.parent.mkdir(parents=True,exist_ok=True)
  if src.exists():shutil.copy2(src,b)
for rel,t in pending.items():
 data=t.replace('\r','').replace('\n','\r\n').encode('latin1')
 for base in [root,repo/'bajor/overlay']:
  out=base/rel;out.parent.mkdir(parents=True,exist_ok=True)
  if out.exists():os.chmod(out,0o666)
  out.write_bytes(data);assert out.read_bytes()==data
 manifest.append({'file':rel,'sha256':hashlib.sha256(data).hexdigest()})
r={'applied':True,'appliedAt':stamp,'backup':str(backup),'dump':'C:/Users/thoma/AppData/Local/CrashDumps/Armada2.exe.8420.dmp','fault':'0x437b30, called from0x66abda; target+0x128 was null; ecx=0x8','resolution':'Withdraw NX-derived constructor fusingweapon buttons from all affected constructors; retain normal production of tiers','constructors':changes,'disabledAbilities':sorted(abilities),'unicomplexMaximumCrew':10000,'unicomplexStartingCrew':resolve('unicomplex')['crewcost'],'files':list(pending),'manifest':manifest,'runtimeVerified':False}
(repo/'reports/constructor-fusion-crash-fix.json').write_text(json.dumps(r,indent=2))
s=repo/'status.json';d=json.loads(s.read_text(encoding='utf-8-sig'));d['current']='Applied constructor-upgrade crash recovery: removed20 NX-derived fusion upgrade buttons from20 constructors; tiers remain buildable normally. Latest dump null-object read in fusion path at0x437b30. Borg Central Unicomplex maximum crew reduced to10,000; starting crew150 unchanged. Runtime retest pending.';d['updated']=stamp;s.write_text(json.dumps(d,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n['+stamp+'] '+d['current']+' Backup:'+str(backup)+'\n')
print(json.dumps({'files':len(pending),'constructors':len(changes),'abilitiesWithdrawn':len(abilities),'unicomplexMaxCrew':10000,'backup':str(backup)}))
