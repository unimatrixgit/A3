from pathlib import Path
import re,json,shutil,datetime,subprocess,stat
r=Path('D:/armadaIII');repo=Path('D:/aramada');stage=Path('D:/Xaramada-Modwork/cube-tech-assimilation');caps={'bbattle':1,'bbattle1':1,'bbattle2':2,'bbattle3':3,'bbattle4':4,'bbattle5':4,'bbattle6':6,'bbattle8':1,'blocutus':3,'bmama':4,'bomega1':5,'bscout':1,'tcube':2,'xobbattle1':5,'xobbattle2':6,'xoblocutus':6}
def edit(t,k,v):return re.sub(r'^\s*'+k+r'\s*=.*$','',t,flags=re.M|re.I)+'\n'+k+' = '+str(v)+'\n'
energy={}
for n,count in caps.items():
 p=stage/'odf/ships'/(n+'.odf');t=p.read_text(encoding='latin1');capacity=(4+count)*500;regen=(4+count)*5;t=edit(t,'maxSpecialEnergy',capacity);t=edit(t,'specialEnergyRate',regen);p.write_text(t,encoding='latin1');energy[n]={'capturedSlots':count,'builtInActiveAbilities':4,'capacity':capacity,'regenPerSecond':regen}
for n in ['xbharvest','xbassimst']:
 rel=Path('odf/stations')/(n+'.odf');p=stage/rel;p.parent.mkdir(parents=True,exist_ok=True);t=(r/rel).read_text(encoding='latin1');t=edit(edit(t,'maxSpecialEnergy',2500),'specialEnergyRate',25);p.write_text(t,encoding='latin1');energy[n]={'capacity':2500,'regenPerSecond':25,'note':'Matches normal cube; one effect shared by automatic/manual controls.'}
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running'
b=Path('D:/Xaramada-Modwork/backups')/('cube-tech-energy-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));files=[]
for p in stage.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(stage);dst=r/rel;back=b/rel;back.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,back)
 if not(dst.stat().st_mode&stat.S_IWRITE):dst.chmod(dst.stat().st_mode|stat.S_IWRITE)
 shutil.copy2(p,dst);assert dst.read_bytes()==p.read_bytes();dest=repo/'overlay'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():dest.chmod(dest.stat().st_mode|stat.S_IWRITE)
 shutil.copy2(p,dest);files.append(str(rel))
report={'installed':True,'capturedSpecialCapacities':caps,'cubeWeaponSlot':7,'cubeAssimilationWeapon':'gTechAssimBeam','cubeButton':'F7','stationTechnologyWeapon':'gTechAssim','stationCompatibility':list(caps),'energyCalculation':{'capacityPerActiveAbility':500,'regenPerActiveAbility':5,'builtInAbilities':['transwarp','shield remodulation','green assimilation','technology assimilation'],'passiveDetectionCounted':False,'note':'Baseline balance calculation, not gameplay simulation. 500 reserve funds 10 seconds of a 50-energy/sec beam before regeneration.'},'energy':energy,'backup':str(b),'priorPartialBackup':[str(p)for p in Path('D:/Xaramada-Modwork/backups').glob('cube-tech-assimilation-*')],'files':files,'gameplayVerified':False};(repo/'reports/cube-tech-assimilation.json').write_text(json.dumps(report,indent=2));p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Installed cube technology assimilation F7 and captured slots: normal1, tactical2, larger3-4, Omega5-6. Energy scaled to 500 capacity/5 regen per active or captured ability. Both new stations set to 2500/25. Technology Assimilator compatibility updated. Backup and reference checks complete; gameplay capture test pending.'
if not any(a['id']=='cube-tech-assimilation'for a in s['features']):s['features'].append({'id':'cube-tech-assimilation','title':'Cube technology assimilation and energy','steps':[{'label':'Calculate capacities','done':True},{'label':'Install cube/station/tech changes','done':True},{'label':'Gameplay test','done':False}]})
s['steps']=[{'label':a['title']+': '+v['label'],'done':v['done']}for a in s['features']for v in a['steps']];p.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a')as log:log.write('\nInstalled technology assimilation and calculated energy budgets for16 cubes plus2 stations; station compatibility and tech availability repaired. Runtime pending.\n')
print('Installed',len(files),'files. Energy:',json.dumps(energy))
