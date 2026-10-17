from pathlib import Path
import re,json,shutil,subprocess,datetime
r=Path('D:/armadaIII');repo=Path('D:/aramada');stage=Path('D:/Xaramada-Modwork/borg-station-target-controls');stage.mkdir(exist_ok=True)
def put(rel,t):
 p=stage/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='latin1')
def edit(t,k,v):return re.sub(r'^\s*'+k+r'\s*=.*$','',t,flags=re.M|re.I)+'\n'+k+' = '+v+'\n'
for unit,beam,manual,label in [('xbharvest','xbharvbeam','xbharvmanual','Harvest Crew'),('xbassimst','xbassimbeam','xbassimmanual','Assimilate Target')]:
 rel=Path('odf/special_weapons')/(beam+'.odf');t=(r/rel).read_text(encoding='latin1');t=edit(t,'ignoreValidAsTarget','0');t=t.replace('// don\'t check to see if is valid as target','// Respect native target validity and existing beam reservations.');put(rel,t)
 m=edit(t,'special','1');m=edit(m,'verboseTooltip',json.dumps('Manually target an enemy with '+label+'. Requires a valid native beam target.'));put(Path('odf/special_weapons')/(manual+'.odf'),m)
 rel=Path('odf/stations')/(unit+'.odf');t=(r/rel).read_text(encoding='latin1');assert not re.search(r'^weapon2\s*=',t,re.M|re.I);t+='\n// Manual beam control alongside automatic defense. Native validity prevents duplicate reservations.\nweapon2 = "'+manual+'"\nweaponHardpoints2 = "hp01"\n';put(rel,t)
rel=Path('Sprites/gui_global.spr');t=(r/rel).read_text(encoding='latin1');t+='\n// Manual station beam HUD controls\n@reference=64\n@tmaterial=default\nb_xbharvmanual gbbaabore00 0 0 64 64\nb_xbassimmanual gbholdbm00 0 0 64 64\n';put(rel,t)
for p in(r/'techtree').glob('*.tt'):
 t=p.read_text(encoding='latin1')
 if re.search(r'^xbharvbeam\.odf\s',t,re.M):put(p.relative_to(r),t+'\nxbharvmanual.odf 0\nxbassimmanual.odf 0\n')
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running'
b=Path('D:/Xaramada-Modwork/backups')/('station-target-controls-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));files=[]
for p in stage.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(stage);dst=r/rel
 if dst.exists():back=b/rel;back.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,back)
 else:b.mkdir(parents=True,exist_ok=True)
 shutil.copy2(p,dst);assert p.read_bytes()==dst.read_bytes();dest=repo/'overlay'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);files.append(str(rel))
report={'installed':True,'backup':str(b),'files':files,'manualHudControl':True,'autofireRetained':True,'nativeValidityRestored':True,'crewlessExclusionRuntimeVerified':False,'note':'ignoreValidAsTarget=0 restores native ordnance target validity; exact crewless exclusion and manual/auto coexistence require gameplay verification. No invented crew/race filter keys used.'};(repo/'reports/borg-station-target-controls.json').write_text(json.dumps(report,indent=2))
f=repo/'status.json';s=json.loads(f.read_text(encoding='utf-8-sig'));s['current']='Installed manual F4 station beam controls alongside autofire; restored native target-validity checks to reject unsuitable targets. Crewless/8472 exclusion and manual/auto behavior require fresh-game verification. Existing colored badges retained.';f.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a')as log:log.write('\nInstalled station manual HUD buttons and native target-validity checks. Crewless exclusion needs gameplay confirmation.\n')
print('Installed',len(files),'files with backups; runtime pending.')
