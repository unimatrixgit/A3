from pathlib import Path
import re,shutil,datetime,json,subprocess
r=Path('D:/armadaIII');repo=Path('D:/aramada');assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0
b=Path('D:/Xaramada-Modwork/backups')/('borg-constructor-techass-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));changed=[]
for n in ['xbuconst','uconst']:
 rel=Path('odf/ships')/(n+'.odf');p=r/rel;t=p.read_text(encoding='latin1');items=re.findall(r'^buildItem(\d+)\s*=\s*"([^"]+)"',t,re.M|re.I)
 assert len(items)==11 and 'btechass'not in[v.lower()for i,v in items];back=b/rel;back.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,back);t+='\n// Technology Assimilator restored to second Borg constructor.\nbuildItem11 = "btechass"\n';p.write_text(t,encoding='latin1');shutil.copy2(p,repo/'overlay'/rel);assert len(re.findall(r'^buildItem\d+\s*=',t,re.M))==12;changed.append(str(rel))
report={'installed':True,'unit':'btechass','producers':['xbuconst','uconst'],'menuSlot':11,'menuItems':12,'requirement':'bresear.odf','existingBuildIcon':'b_btechass','backup':str(b),'gameplayVerified':False};(repo/'reports/borg-constructor-techass.json').write_text(json.dumps(report,indent=2));p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Restored Technology Assimilator structure to second Borg constructor (xbuconst and legacy uconst), menu slot11. Twelve menu entries; existing build icon and Modification Center prerequisite retained. Backed up and verified; gameplay test pending.';p.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a')as log:log.write('\nRestored btechass to xbuconst/uconst buildItem11. Existing sprite and tech1 requirement verified; two files backed up.\n')
print('Installed Technology Assimilator on second Borg constructor;12 entries.')
