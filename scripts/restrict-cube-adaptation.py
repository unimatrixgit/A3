from pathlib import Path
import re,json,shutil,datetime,subprocess
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
keep={'bscout','blocutus','xoblocutus'};names=list(json.loads((repo/'reports/cube-tech-assimilation.json').read_text())['capturedSpecialCapacities']);prepared={}
for n in names:
 if n in keep:continue
 d=props(n);items=[]
 for k,v in sorted(d.items(),key=lambda x:int(x[0][6:])if re.fullmatch('weapon[0-9]+',x[0])else 999):
  if re.fullmatch('weapon[0-9]+',k)and v.lower()!='xacremod':items.append((v,d['weaponhardpoints'+k[6:]]))
 assert len(items)==6,(n,items)
 p=root/'odf/ships'/(n+'.odf');t=p.read_text(encoding='latin1');t=re.sub(r'^\s*weapon(?:hardpoints)?\d+\s*=.*$','',t,flags=re.M|re.I);t+='\n// Shield adaptation restricted to Scout and Locutus variants.\n'
 for i,(w,hp)in enumerate(items,1):t+=f'weapon{i} = "{w}"\nweaponHardpoints{i} = "{hp}"\n'
 prepared[p]=t
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running'
b=Path('D:/Xaramada-Modwork/backups')/('restrict-cube-adaptation-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
for p,t in prepared.items():
 rel=p.relative_to(root);back=b/rel;back.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,back);p.write_text(t,encoding='latin1');shutil.copy2(p,repo/'overlay'/rel)
cache.clear();checks=[]
for n in names:
 d=props(n);w=[v.lower()for k,v in d.items()if re.fullmatch('weapon[0-9]+',k)];assert ('xacremod'in w)==(n in keep),(n,w);assert len(w)==(7 if n in keep else 6);assert 'gtechassimbeam'in w and 'gdetect3'in w and 'xacgreen'in w and 'xactwarp'in w;checks.append({'unit':n,'hasAdaptation':n in keep,'weapons':w})
f=repo/'AGENTS.md';t=f.read_text();t=t.replace('Keep green holding/assimilation, transwarp, remodulation and remaining weapons in their existing relative order with matching hardpoints;','Keep green holding/assimilation, transwarp and remaining weapons in their existing relative order with matching hardpoints;');t+='\nShield adaptation/remodulation is now restricted to Scout Cube (bscout) and Locutus variants (blocutus, xoblocutus). Do not restore it to other cubes. This supersedes historical all-cubes adaptation scripts.\n';f.write_text(t)
(repo/'reports/restrict-cube-adaptation.json').write_text(json.dumps({'installed':True,'retainedOn':sorted(keep),'removedFromCount':len(prepared),'backup':str(b),'energyBudgetsUnchanged':True,'checks':checks,'gameplayVerified':False},indent=2));f=repo/'status.json';s=json.loads(f.read_text(encoding='utf-8-sig'));s['current']='Installed adaptation restriction: Shield Remodulation only on Scout Cube, Locutus and Omega Locutus. Removed from13 other cubes; contiguous weapon slots and remaining order preserved. Tech assimilation, detector and energy budgets retained. Gameplay test pending.';f.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a')as log:log.write('\nRemoved built-in shield adaptation from13 cubes; retained bscout/blocutus/xoblocutus. All16 resolved loadouts checked.\n')
print('Verified16 cubes; adaptation retained on',sorted(keep),'and removed from',len(prepared))

