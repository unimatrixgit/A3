from pathlib import Path
import json,re,shutil,subprocess,datetime
r=Path('D:/armadaIII');repo=Path('D:/aramada');o=Path('D:/Xaramada-Modwork/cube-tech-assimilation');caps={'bbattle':1,'bbattle1':1,'bbattle2':2,'bbattle3':3,'bbattle4':4,'bbattle5':4,'bbattle6':6,'bbattle8':1,'blocutus':3,'bmama':4,'bomega1':5,'bscout':1,'tcube':2,'xobbattle1':5,'xobbattle2':6,'xoblocutus':6}
def put(rel,t):
 p=o/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='latin1')
for n,cap in caps.items():
 rel=Path('odf/ships')/(n+'.odf');t=(r/rel).read_text(encoding='latin1');assert re.findall(r'^weapon(\d+)\s*=',t,re.M|re.I)==[str(i)for i in range(1,7)],n
 t=re.sub(r'^\s*maxExtraWeapons\s*=.*$','',t,flags=re.M|re.I);t+='\n// Technology assimilation: native beam and bounded captured-special capacity.\nweapon7 = "gTechAssimBeam"\nweaponHardpoints7 = "hp01"\nmaxExtraWeapons = '+str(cap)+'\n';put(rel,t)
rel=Path('odf/special_weapons/gTechAssim.odf');t=(r/rel).read_text(encoding='latin1');t=re.sub(r'^\s*assignClass\d+\s*=.*$','',t,flags=re.M|re.I);t+='\n// Compatible current cube variants.\n'+''.join(f'assignClass{i} = "{n}"\n'for i,n in enumerate(caps));put(rel,t)
# Native beam's icon, F7 button and ordnance remain intact; explicitly register tech availability.
for p in(r/'techtree').glob('*.tt'):
 t=p.read_text(encoding='latin1')
 if re.search(r'^bbattle(?:1)?\.odf\s',t,re.M|re.I)and not re.search(r'^gTechAssimBeam\.odf\s',t,re.M|re.I):put(p.relative_to(r),t+'\n// Native cube technology assimilation control.\ngTechAssimBeam.odf 0\n')
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running'
b=Path('D:/Xaramada-Modwork/backups')/('cube-tech-assimilation-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));files=[]
for p in o.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(o);dst=r/rel;back=b/rel;back.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,back);shutil.copy2(p,dst);assert dst.read_bytes()==p.read_bytes();dest=repo/'overlay'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);files.append(str(rel))
report={'installed':True,'capacities':caps,'weapon':'gTechAssimBeam','slot':7,'button':'F7','stationWeapon':'gTechAssim','stationCompatibleCubes':list(caps),'backup':str(b),'files':files,'gameplayVerified':False,'note':'Captured-ability caps are in addition to built-in weapons; native assimilatable target requirements still apply.'};(repo/'reports/cube-tech-assimilation.json').write_text(json.dumps(report,indent=2));p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Installed technology-assimilation beam F7 on all 16 cubes. Captured-special capacity: normal/scout 1, tactical 2, larger 3-4, Omega 5-6. Technology Assimilator compatibility updated; tech entries included. Existing weapons and passive detection retained. Runtime capture test pending.';s['features'].append({'id':'cube-tech-assimilation','title':'Cube technology assimilation','steps':[{'label':'Audit beam and capacity','done':True},{'label':'Install cubes, station and tech','done':True},{'label':'Gameplay test','done':False}]});s['steps']=[{'label':a['title']+': '+v['label'],'done':v['done']}for a in s['features']for v in a['steps']];p.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a')as log:log.write('\nInstalled native cube Tech Assimilation Beam F7, 16 capacity fixes, station compatibility and tech rows. Gameplay pending.\n')
print('Installed',len(files),'files; capacities:',json.dumps(caps))
