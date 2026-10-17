from pathlib import Path
import re,json,shutil,datetime,subprocess
r=Path('D:/armadaIII');repo=Path('D:/aramada');assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0
rel=Path('odf/ships/xobbattle1.odf');p=r/rel;t=p.read_text(encoding='latin1');b=Path('D:/Xaramada-Modwork/backups')/('omega-borg-cost-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))/rel;b.parent.mkdir(parents=True);shutil.copy2(p,b)
for k in ['dilithiumCost','metalCost']:
 t,n=re.subn(r'^\s*'+k+r'\s*=\s*12480\s*$',k+' = 1248',t,flags=re.M|re.I);assert n==1,k
p.write_text(t,encoding='latin1');shutil.copy2(p,repo/'overlay'/rel);assert p.read_bytes()==(repo/'overlay'/rel).read_bytes();(repo/'reports/omega-borg-cost.json').write_text(json.dumps({'unit':'xobbattle1','dilithium':{'before':12480,'after':1248},'metal':{'before':12480,'after':1248},'installed':True,'backup':str(b),'userFeedback':'User reports no other bugs found and all functions working; exact coverage unspecified.'},indent=2))
f=repo/'status.json';s=json.loads(f.read_text(encoding='utf-8-sig'));s['current']='Omega Borg Cube cost corrected:1248 dilithium and1248 metal (removed trailing zero). Other stats unchanged. User reports all functions working and no other bugs found; exact test coverage unspecified. Backed up and verified.';f.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a')as log:log.write('\nOmega Borg Cube resource costs12480->1248 each. User reports all functions working/no other bugs; exact coverage unspecified.\n')
print('Installed Omega Borg Cube costs:1248 dilithium,1248 metal.')
