from pathlib import Path
import re,json,datetime,shutil,subprocess
repo=Path('D:/aramada');root=Path('D:/armadaIII');audit=json.loads((repo/'reports/repair-yard-production-20261028.json').read_text());assert subprocess.check_output(['powershell','-NoProfile','-Command','@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'],text=True).strip()=='0','Close Armada III before applying.'
backup=Path('D:/Xaramada-Modwork/backups')/('retain-repair-yard-rally-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));rows=[]
for row in audit['stations']:
 rel=Path('odf/stations')/(row['station']+'.odf');p=root/rel;t=p.read_text(encoding='latin1');old=t
 t,n=re.subn(r'(?mi)^alwaysRecomputeRallyPoint[ \t]*=[^\r\n]*','alwaysRecomputeRallyPoint = 0',t);assert n==1
 assert re.search(r'(?mi)^classLabel\s*=\s*"shipyard"',t)and re.search(r'(?mi)^buildItem\d+\s*=',t)
 b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b);data=t.replace('\r','').replace('\n','\r\n').encode('latin1');p.write_bytes(data);(repo/'bajor/overlay'/rel).write_bytes(data)
 rows.append({'station':row['station'],'alwaysRecomputeRallyPoint':0,'productionAndServicesPreserved':True})
# Correct generators so rerunning them cannot reintroduce the reset behavior.
p=repo/'scripts/add-repair-yard-production-20261028.py';s=p.read_text(encoding='utf-8-sig');assert "('alwaysRecomputeRallyPoint',1)"in s;s=s.replace("('alwaysRecomputeRallyPoint',1)","('alwaysRecomputeRallyPoint',0)");p.write_text(s,encoding='utf-8')
p=repo/'scripts/fix-repair-station-waypoints-20261028.py';s=p.read_text(encoding='utf-8-sig');s=s.replace("set_value(t,key,'1')","set_value(t,key,'0' if key=='alwaysRecomputeRallyPoint' else '1')");s=s.replace("after['alwaysrecomputerallypoint']=='1'","after['alwaysrecomputerallypoint']=='0'");s=s.replace('rally refresh set','automatic rally reset disabled');p.write_text(s,encoding='utf-8')
report={'backup':str(backup),'stations':rows,'nativeEvidence':{'Shipyard.GetRallyPoint':'0x4bbeb0 tests class flag at +0x4b4 and calls mRecomputeRallyPoint before returning saved vector +0x2c4','Shipyard.mRecomputeRallyPoint':'0x4bc150 derives a default point from station transform and bounding sphere then overwrites saved vector','OutputQueueManager.mOutputCraft':'0x53a500 calls Shipyard.GetRallyPoint at 0x53a527 and issues movement command at 0x53a532'},'runtimeVerified':False,'supersedes':'Earlier alwaysRecomputeRallyPoint=1 advice was incorrect for fixed stations with user-selected rally points.'}
(repo/'reports/retain-repair-yard-rally-20261028.json').write_text(json.dumps(report,indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Corrected all 12 repair yards: automatic rally reset disabled so the native exit path reads the saved user rally point. Prior recompute=1 setting was wrong; shipyard production/services preserved and generators corrected. Native code traced; gameplay verification pending.';p.write_text(json.dumps(s,indent=2))
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n'+datetime.datetime.now().isoformat()+' '+s['current']+'\n')
print('PASS: automatic rally reset disabled on all 12 repair yards; source generators corrected.')
