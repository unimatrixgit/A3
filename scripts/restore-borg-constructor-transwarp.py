from pathlib import Path
exec(Path('D:/aramada/scripts/build-mirror-ferengi-research.py').read_text().split('# Existing Cardassian artwork')[0])
import subprocess,shutil,hashlib,os
running=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-Process armada2 -ErrorAction SilentlyContinue).Count"],capture_output=True,text=True);assert running.stdout.strip()=='0','Game must be closed'
before=json.loads((repo/'reports/borg-constructor-transwarp-before.json').read_text());units={n:d for n,d in before.items()if d.get('race')=='borg'and d.get('classlabel','').lower()=='constructionrig'};assert len(units)==6
sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1');assert re.search(r'(?mi)^b_xabtrans5\s',sprite);assert num(before['twarpd']['specialenergycost'])==1000
backup=Path('D:/Xaramada-Modwork/backups')/('borg-constructor-transwarp-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));changes=[]
for n,d in units.items():
 hp='hp10'if n=='xbgconst'else'hp01';mn=d.get('basename',n)
 try:m=load(root/'SOD'/(mn+'.sod'))
 except Exception:
  with contextlib.redirect_stdout(io.StringIO()):m=SodIO().read_file(str(root/'SOD'/(mn+'.sod')))
 assert hp in {z['id'].lower()for z in m.nodes},(n,hp)
 t=update(text(n),{'weapon1':q('xabtrans5'),'weaponHardpoints1':q(hp),'maxSpecialEnergy':1000,'specialEnergyRate':10})
 # Preserve every constructor menu and its new resource costs.
 pending={};pending[Path(d['file']).relative_to(root).as_posix()]=t
 rd=resolve(n)
 for k,v in d.items():
  if re.fullmatch('builditem[0-9]+',k)or k in ['dilithiumcost','metalcost','crewcost','maximumcrew','basename']:assert rd[k]==v,(n,k)
 data=t.replace('\r','').replace('\n','\r\n').encode('latin1');changes.append((n,Path(d['file']).relative_to(root),data))
for n,rel,data in changes:
 for label,base in [('live',root),('repository',repo/'bajor/overlay')]:
  dst=base/rel;b=backup/label/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,b)
for n,rel,data in changes:
 for base in [root,repo/'bajor/overlay']:
  dst=base/rel;os.chmod(dst,0o666);dst.write_bytes(data);assert dst.read_bytes()==data
r={'applied':True,'backup':str(backup),'constructors':[n for n,_,_ in changes],'ability':'xabtrans5','energy':1000,'recharge':10,'energyCost':1000,'research':'borpod4 (unchanged)','menusAndCostsUnchanged':True,'runtimeVerified':False,'appliedAt':datetime.datetime.now().astimezone().isoformat()};(repo/'reports/borg-constructor-transwarp-restored.json').write_text(json.dumps(r,indent=2))
for name in ['constructor-mirror-applied.md','constructor-tier-plan.md']:
 f=repo/'reports'/name;t=f.read_text();t=t.replace('Constructors carry no weapons.','Constructors carry no combat weapons. All Borg constructors retain Transwarp Drive, 1,000 special energy and10 energy recharge per second.');f.write_text(t)
s=repo/'status.json';d=json.loads(s.read_text());d['current']='Restored Transwarp Drive to all6 Borg constructor definitions, including all tiers, Universal aliases and the Borg Ferengi constructor.1,000 special energy and10/sec recharge; existing borpod4 research gate and F5 button retained. Tier menus/costs unchanged. Backed up and file-validated; new-match test pending.';d['updated']=r['appliedAt'];s.write_text(json.dumps(d,indent=2))
with(repo/'build.log').open('a')as log:log.write('\n['+r['appliedAt']+'] '+d['current']+' Backup:'+str(backup)+'\n')
print(json.dumps(r,indent=2))
